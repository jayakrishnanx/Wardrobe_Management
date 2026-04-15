from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from accounts.decorators import role_required
from .models import WardrobeItem, Category
from .forms import WardrobeItemForm
from recommendations.models import OutfitRecommendation


@role_required('user')
def wardrobe_home(request: HttpRequest) -> HttpResponse:
    """
    Displays the user's wardrobe items.
    """
    items = WardrobeItem.objects.filter(user=request.user)
    return render(request, 'user/manage_wardrobe.html', {'items': items})


@role_required('user')
def add_wardrobe(request: HttpRequest) -> HttpResponse:
    """
    Handles adding a new item to the wardrobe using a form.
    """
    if request.method == 'POST':
        form = WardrobeItemForm(request.POST, request.FILES)
        if form.is_valid():
            wardrobe_item = form.save(commit=False)
            wardrobe_item.user = request.user
            wardrobe_item.save()
            
            # Invalidate recommendations when wardrobe changes
            OutfitRecommendation.objects.filter(user=request.user).delete()
            
            return redirect('wardrobe_home')
    else:
        form = WardrobeItemForm()

    return render(request, 'user/add_wardrobe.html', {'form': form})


@role_required('user')
def bulk_add_wardrobe(request: HttpRequest) -> HttpResponse:
    """
    Handles adding multiple wardrobe items for a single category at once via bulk image upload.
    """
    from .models import Occasion, Season, Category
    categories = Category.objects.all()

    if request.method == 'POST':
        category_id = request.POST.get('category')
        images = request.FILES.getlist('images')

        if not category_id:
            messages.error(request, "Please select a category.")
            return render(request, 'user/bulk_add_wardrobe.html', {'categories': categories})
            
        if not images:
            messages.error(request, "Please select at least one image.")
            return render(request, 'user/bulk_add_wardrobe.html', {'categories': categories})

        category = get_object_or_404(Category, id=category_id)
        
        # Get or create default occasion and season
        occasion, _ = Occasion.objects.get_or_create(name='Casual')
        season, _ = Season.objects.get_or_create(name='All Seasons')
        
        items_created = 0
        errors = []

        for image in images:
            try:
                item_type = f"{category.name} Item"
                item = WardrobeItem(
                    user=request.user,
                    item_type=item_type,
                    category=category,
                    occasion=occasion,
                    season=season,
                    image=image,
                )
                item.save()
                items_created += 1
            except Exception as e:
                errors.append(f"Error saving an image: {str(e)}")

        if items_created > 0:
            # Invalidate recommendations when wardrobe changes
            OutfitRecommendation.objects.filter(user=request.user).delete()
            messages.success(request, f'Successfully added {items_created} item{"s" if items_created > 1 else ""} to your wardrobe!')

        if errors:
            for err in errors:
                messages.error(request, err)

        if items_created > 0 and not errors:
            return redirect('wardrobe_home')

    context = {
        'categories': categories,
    }
    return render(request, 'user/bulk_add_wardrobe.html', context)


@role_required('user')
def delete_wardrobe(request: HttpRequest, item_id: int) -> HttpResponse:
    """
    Deletes a specific wardrobe item.
    """
    item = get_object_or_404(WardrobeItem, id=item_id, user=request.user)
    item.delete()
    
    # Invalidate recommendations when wardrobe changes
    OutfitRecommendation.objects.filter(user=request.user).delete()
    
    return redirect('wardrobe_home')

@role_required('user')
def bulk_delete_wardrobe(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        item_ids = request.POST.getlist('item_ids')
        if item_ids:
            WardrobeItem.objects.filter(id__in=item_ids, user=request.user).delete()
            # Invalidate recommendations when wardrobe changes
            OutfitRecommendation.objects.filter(user=request.user).delete()
            messages.success(request, f'Successfully deleted {len(item_ids)} item(s) from your wardrobe.')
    return redirect('wardrobe_home')


@login_required
def view_clothes(request: HttpRequest) -> HttpResponse:
    """
    Displays clothes, optionally filtered by category.
    """
    categories = Category.objects.all()
    items = WardrobeItem.objects.filter(user=request.user)

    category_id = request.GET.get('category')
    if category_id:
        items = items.filter(category_id=category_id)

    return render(request, 'user/view_clothes.html', {
        'items': items,
        'categories': categories
    })


@role_required('user')
def mark_as_worn(request: HttpRequest, item_id: int) -> HttpResponse:
    """
    Marks an item as worn and updates its status.
    """
    item = get_object_or_404(WardrobeItem, id=item_id, user=request.user)
    item.mark_worn()
    return redirect('view_clothes')


@role_required('user')
def send_to_laundry(request: HttpRequest, item_id: int) -> HttpResponse:
    """
    Manually marks an item as needing laundry.
    """
    item = get_object_or_404(
        WardrobeItem,
        id=item_id,
        user=request.user
    )
    item.clean_status = False
    item.save()
    return redirect('view_clothes')


@role_required('user')
def laundry_list(request: HttpRequest) -> HttpResponse:
    """
    Displays items that are currently in the laundry (clean_status=False).
    """
    laundry_items = WardrobeItem.objects.filter(
        user=request.user,
        clean_status=False
    )
    return render(request, 'user/laundry_list.html', {
        'laundry_items': laundry_items
    })

from django.db.models import Sum, F, ExpressionWrapper, FloatField

@role_required('user')
def wardrobe_stats(request):
    items = WardrobeItem.objects.filter(user=request.user)
    
    total_items = items.count()
    total_value = items.aggregate(Sum('price'))['price__sum'] or 0
    
    most_worn = items.order_by('-total_wears')[:5]
    
    # Calculate Cost Per Wear (avoid division by zero)
    # We can do this in Python for simplicity or DB. Let's do DB.
    # Actually, SQLite might complain about division by zero.
    # Let's filter items with wear_count > 0 for CPW.
    
    worn_items = items.filter(total_wears__gt=0, price__isnull=False)
    # Calculate CPW manually to be safe and simple
    best_value_items = []
    for item in worn_items:
        cpw = item.price / item.total_wears
        best_value_items.append({
            'item': item,
            'cpw': cpw
        })
    
    # Sort by CPW ascending (lower is better)
    best_value_items.sort(key=lambda x: x['cpw'])
    best_value_items = best_value_items[:5]
    
    context = {
        'total_items': total_items,
        'total_value': total_value,
        'most_worn': most_worn,
        'best_value_items': best_value_items
    }
    
    return render(request, 'user/wardrobe_stats.html', context)


@role_required('user')
def mark_as_clean(request: HttpRequest, item_id: int) -> HttpResponse:
    item = get_object_or_404(
        WardrobeItem,
        id=item_id,
        user=request.user
    )
    item.clean_status = True
    item.wear_count = 0
    item.save()
    return redirect('laundry_list')

@role_required('user')
def bulk_send_to_laundry(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        item_ids = request.POST.getlist('item_ids')
        if item_ids:
            WardrobeItem.objects.filter(id__in=item_ids, user=request.user).update(clean_status=False)
            messages.success(request, f'Successfully sent {len(item_ids)} items to laundry.')
    return redirect('view_clothes')


@role_required('user')
def bulk_mark_as_clean(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        item_ids = request.POST.getlist('item_ids')
        if item_ids:
            WardrobeItem.objects.filter(id__in=item_ids, user=request.user).update(clean_status=True, wear_count=0)
            messages.success(request, f'Successfully marked {len(item_ids)} items as clean.')
    return redirect('laundry_list')
