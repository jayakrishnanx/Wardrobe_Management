from django.shortcuts import render, redirect, get_object_or_404
from wardrobe.models import Occasion, Season, WardrobeItem
from .models import OutfitRecommendation
from accounts.decorators import role_required
from .utils import generate_outfit_recommendations
from django.contrib import messages


@role_required('user')
def recommend_outfit(request):

    selected_occasion = None
    selected_season = None

    if request.method == 'POST':
        selected_occasion = request.POST.get('occasion') or None
        selected_season = request.POST.get('season') or None

        generate_outfit_recommendations(
            user=request.user,
            occasion_id=selected_occasion,
            season_id=selected_season
        )

        request.session['occasion'] = selected_occasion
        request.session['season'] = selected_season

        return redirect('recommend_outfit')

    # 🔹 Read last selection
    selected_occasion = request.session.get('occasion')
    selected_season = request.session.get('season')

    recommendations = OutfitRecommendation.objects.filter(user=request.user)

    # 🔹 Auto-generate if no recommendations exist and user has clothes
    if not recommendations.exists() and not selected_occasion and not selected_season:
        has_tops = WardrobeItem.objects.filter(user=request.user, category__name__iexact="top").exists()
        has_bottoms = WardrobeItem.objects.filter(user=request.user, category__name__iexact="bottom").exists()
        
        if has_tops and has_bottoms:
            generate_outfit_recommendations(user=request.user)
            recommendations = OutfitRecommendation.objects.filter(user=request.user)

    if selected_occasion:
        recommendations = recommendations.filter(
            top_item__occasion_id=selected_occasion,
            bottom_item__occasion_id=selected_occasion
        )

    if selected_season:
        recommendations = recommendations.filter(
            top_item__season_id=selected_season,
            bottom_item__season_id=selected_season
        )

    recommendations = recommendations.order_by('-match_score')

    return render(request, 'user/recommend.html', {
        'recommendations': recommendations,
        'occasions': Occasion.objects.all(),
        'seasons': Season.objects.all(),
        'selected_occasion': int(selected_occasion) if selected_occasion else None,
        'selected_season': int(selected_season) if selected_season else None,
    })


@role_required('user')
def wear_outfit(request, top_id, bottom_id):
    """
    Marks the top and bottom of an outfit as worn.
    If items reach their wear limit, they are marked as needing laundry.
    """
    top = get_object_or_404(WardrobeItem, id=top_id, user=request.user)
    bottom = get_object_or_404(WardrobeItem, id=bottom_id, user=request.user)

    top.mark_worn()
    bottom.mark_worn()

    # Check for laundry status
    messages.success(request, f"You wore {top.item_type} and {bottom.item_type}!")

    if not top.clean_status:
        messages.warning(request, f"⚠️ {top.item_type} needs laundry!")
    
    if not bottom.clean_status:
        messages.warning(request, f"⚠️ {bottom.item_type} needs laundry!")

    return redirect('recommend_outfit')


@role_required('user')
def toggle_favorite(request, recommendation_id):
    rec = get_object_or_404(OutfitRecommendation, id=recommendation_id, user=request.user)
    rec.is_favorite = not rec.is_favorite
    rec.save()
    
    status = "saved to favorites" if rec.is_favorite else "removed from favorites"
    messages.success(request, f"Outfit {status}.")
    
    return redirect('recommend_outfit')

