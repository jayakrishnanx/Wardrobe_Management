from django.shortcuts import render, redirect, get_object_or_404
from accounts.decorators import role_required
from .models import WardrobeItem

from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import WardrobeItem




@role_required('user')
def wardrobe_home(request):
    items = WardrobeItem.objects.filter(user=request.user)
    return render(request, 'wardrobe/wardrobe_home.html', {'items': items})


@role_required('user')
def add_wardrobe_item(request):
    categories = Category.objects.all()
    occasions = Occasion.objects.all()
    seasons = Season.objects.all()

    if request.method == 'POST':
        WardrobeItem.objects.create(
            user=request.user,
            item_type=request.POST['item_type'],
            category_id=request.POST['category'],
            occasion_id=request.POST['occasion'],
            season_id=request.POST['season'],
            color=request.POST['color'],
            image=request.FILES.get('image')
        )
        return redirect('wardrobe_home')

    return render(request, 'wardrobe/add_item.html', {
        'categories': categories,
        'occasions': occasions,
        'seasons': seasons
    })



@role_required('user')
def delete_wardrobe(request, item_id):
    item = get_object_or_404(WardrobeItem, id=item_id, user=request.user)
    item.delete()
    return redirect('wardrobe_home')

from .models import WardrobeItem, Category, Occasion, Season


@role_required('user')
def add_wardrobe(request):
    categories = Category.objects.all()
    occasions = Occasion.objects.all()
    seasons = Season.objects.all()

    if request.method == 'POST':
        WardrobeItem.objects.create(
            user=request.user,
            item_type=request.POST.get('item_type'),
            category_id=request.POST.get('category'),
            color=request.POST.get('color'),
            occasion_id=request.POST.get('occasion'),
            season_id=request.POST.get('season'),
            image=request.FILES.get('image') 
        )
        return redirect('wardrobe_home')

    return render(request, 'wardrobe/add_wardrobe.html', {
        'categories': categories,
        'occasions': occasions,
        'seasons': seasons
    })

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import WardrobeItem, Category

@login_required
def view_clothes(request):
    categories = Category.objects.all()
    items = WardrobeItem.objects.filter(user=request.user)

    category_id = request.GET.get('category')
    if category_id:
        items = items.filter(category_id=category_id)

    return render(request, 'wardrobe/view_clothes.html', {
        'items': items,
        'categories': categories
    })


@login_required
def mark_as_worn(request, item_id):
    item = get_object_or_404(WardrobeItem, id=item_id, user=request.user)
    item.mark_worn()
    return redirect('view_clothes')


@login_required
def send_to_laundry(request, item_id):
    item = get_object_or_404(
        WardrobeItem,
        id=item_id,
        user=request.user
    )

    # Reset laundry state
    item.wear_count = 0
    item.clean_status = True
    item.save()

    return redirect('view_clothes')
