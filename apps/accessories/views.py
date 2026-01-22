from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum, F
from accounts.decorators import role_required
from .models import Accessory
from wardrobe.models import Category, Occasion, Season, WardrobeItem
from recommendations.models import ColorMatchingRule
from orders.models import OrderItem, Order


@role_required('supplier')
def supplier_home(request):
    total_items = Accessory.objects.filter(supplier=request.user).count()
    total_orders = OrderItem.objects.filter(accessory__supplier=request.user).count()
    
    # Calculate revenue using DB aggregation for efficiency
    revenue_data = OrderItem.objects.filter(
        accessory__supplier=request.user
    ).aggregate(
        total_revenue=Sum(F('price') * F('quantity'))
    )
    revenue = revenue_data['total_revenue'] or 0

    return render(request, 'supplier/supplier_home.html', {
        'total_items': total_items,
        'total_orders': total_orders,
        'revenue': revenue
    })


def manage_accessories(request):
    accessories = Accessory.objects.filter(supplier=request.user)
    return render(request, 'supplier/manage.html', {
        'accessories': accessories
    })


@role_required('supplier')
def update_stock(request, accessory_id):
    if request.method == 'POST':
        accessory = get_object_or_404(
            Accessory,
            id=accessory_id,
            supplier=request.user
        )
        try:
            new_stock = int(request.POST.get('stock', accessory.stock))
            if new_stock < 0:
                raise ValueError("Stock cannot be negative")
            accessory.stock = new_stock
            accessory.save()
        except ValueError:
            # Optionally add a message here
            pass
    return redirect('manage_accessories')


@role_required('supplier')
def delete_accessory(request, accessory_id):
    if request.method == 'POST':
        accessory = get_object_or_404(
            Accessory,
            id=accessory_id,
            supplier=request.user
        )
        accessory.delete()
    return redirect('manage_accessories')


@role_required('supplier')
def edit_accessory(request, accessory_id):
    accessory = get_object_or_404(
        Accessory,
        id=accessory_id,
        supplier=request.user
    )

    if request.method == 'POST':
        accessory.name = request.POST['name']
        accessory.price = request.POST['price']
        accessory.category = request.POST['category']
        
        # Handle Occasion and Season if they are provided (assuming IDs)
        if 'occasion' in request.POST and request.POST['occasion']:
            try:
                accessory.occasion = Occasion.objects.get(id=request.POST['occasion'])
            except Occasion.DoesNotExist:
                pass
                
        if 'season' in request.POST and request.POST['season']:
            try:
                accessory.season = Season.objects.get(id=request.POST['season'])
            except Season.DoesNotExist:
                pass

        if 'image' in request.FILES:
            accessory.image = request.FILES['image']
            
        accessory.save()
        return redirect('manage_accessories')

    return render(request, 'supplier/edit_accessory.html', {
        'accessory': accessory,
        'categories': Category.objects.all(),
        'occasions': Occasion.objects.all(),
        'seasons': Season.objects.all(),
    })

@role_required('supplier')
def supplier_orders(request):
    items = OrderItem.objects.filter(
        accessory__supplier=request.user
    ).select_related('order', 'accessory')

    return render(request, 'supplier/supplier_orders.html', {
        'items': items
    })


@role_required('supplier')
def mark_shipped(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if order.status == 'ordered':
        order.status = 'shipped'
        order.save()

    return redirect('supplier_orders')

@role_required('supplier')
def add_accessories(request):
    if request.method == 'POST':
        try:
            name = request.POST['name']
            category = request.POST['category']
            occasion_id = request.POST['occasion']
            season_id = request.POST['season']
            price = float(request.POST['price'])
            stock = int(request.POST['stock'])
            image = request.FILES.get('image')

            if price < 0 or stock < 0:
                raise ValueError("Price and stock must be non-negative")

            Accessory.objects.create(
                supplier=request.user,
                name=name,
                category=category,
                occasion_id=occasion_id,
                season_id=season_id,
                price=price,
                stock=stock,
                image=image
            )
            return redirect('manage_accessories')
        except (ValueError, KeyError):
            # Handle invalid input
            return render(request, 'supplier/add_accessories.html', {
                'categories': Category.objects.all(),
                'occasions': Occasion.objects.all(),
                'seasons': Season.objects.all(),
                'error': 'Invalid input data'
            })

    return render(request, 'supplier/add_accessories.html', {
        'categories': Category.objects.all(),
        'occasions': Occasion.objects.all(),
        'seasons': Season.objects.all()
    })


@login_required
def shop_accessories(request):
    accessories = Accessory.objects.filter(is_active=True, stock__gt=0)
    categories = Category.objects.all()

    query = request.GET.get('q')
    category = request.GET.get('category')

    if query:
        accessories = accessories.filter(
            Q(name__icontains=query) |
            Q(category__icontains=query)
        )

    if category:
        accessories = accessories.filter(category=category)

    # 🔹 Recommendation System
    recommended_accessories = []
    if request.user.role == 'user':
        # 1. Get user's wardrobe colors
        user_items = WardrobeItem.objects.filter(user=request.user)
        user_colors = set(item.color.lower() for item in user_items if item.color)

        # 2. Find matching colors based on rules
        matching_colors = set()
        rules = ColorMatchingRule.objects.all()
        
        for rule in rules:
            c1 = rule.color_1.lower()
            c2 = rule.color_2.lower()
            
            if c1 in user_colors:
                matching_colors.add(c2)
            if c2 in user_colors:
                matching_colors.add(c1)
        
        # Also allow direct color matches (monochromatic)
        matching_colors.update(user_colors)

        # 3. Filter accessories
        if matching_colors:
            color_query = Q()
            for color in matching_colors:
                if color:  # avoid empty strings
                    color_query |= Q(color__icontains=color)
            
            recommended_accessories = Accessory.objects.filter(
                color_query,
                is_active=True,
                stock__gt=0
            ).exclude(id__in=[a.id for a in accessories])[:4]  # Show different items or top 4

            # If exclude removes everything (e.g. if we are showing all items), 
            # we might want to just prioritize them. 
            # For now, let's just fetch them as "Recommended" even if they appear below.
            recommended_accessories = Accessory.objects.filter(
                color_query,
                is_active=True,
                stock__gt=0
            ).order_by('?')[:4] # Randomize slightly for variety

    return render(request, 'user/shop.html', {
        'accessories': accessories,
        'categories': categories,
        'recommended_accessories': recommended_accessories
    })
