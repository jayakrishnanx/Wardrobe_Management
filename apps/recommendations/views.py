from django.shortcuts import render, redirect, get_object_or_404
from wardrobe.models import Occasion, Season, WardrobeItem
from .models import OutfitRecommendation
from accounts.decorators import role_required
from .utils import generate_outfit_recommendations, generate_ai_chat_response
from django.contrib import messages


@role_required('user')
def recommend_outfit(request):
    ai_chat_message = None
    ai_filtered_outfits = None

    if request.method == 'POST':
        user_prompt = request.POST.get('user_prompt')
        if user_prompt and user_prompt.strip():
            ai_data = generate_ai_chat_response(user_prompt, request.user)
            if isinstance(ai_data, dict):
                ai_chat_message = ai_data.get('message', '')
                ai_filtered_outfits = ai_data.get('outfits', [])
            else:
                ai_chat_message = str(ai_data)
        else:
            generate_outfit_recommendations(user=request.user)
            return redirect('recommend_outfit')

    recommendations = OutfitRecommendation.objects.filter(user=request.user)

    # 🔹 Auto-generate if no recommendations exist and user has clothes
    if not recommendations.exists():
        has_tops = WardrobeItem.objects.filter(user=request.user, category__name__iexact="top").exists()
        has_bottoms = WardrobeItem.objects.filter(user=request.user, category__name__iexact="bottom").exists()
        
        if has_tops and has_bottoms:
            generate_outfit_recommendations(user=request.user)
            recommendations = OutfitRecommendation.objects.filter(user=request.user)

    # Filter to only show CLEAN items
    recommendations = recommendations.filter(
        top_item__clean_status=True,
        bottom_item__clean_status=True
    ).order_by('-is_favorite', '-match_score')

    # 🔹 Apply AI Filter if AI provided specific combinations
    if ai_filtered_outfits:
        from django.db.models import Q
        ai_query = Q()
        for outfit in ai_filtered_outfits:
            top_id = outfit.get('top_id')
            bottom_id = outfit.get('bottom_id')
            if top_id and bottom_id:
                ai_query |= Q(top_item_id=top_id, bottom_item_id=bottom_id)
        
        if ai_query:
            recommendations = recommendations.filter(ai_query)
        else:
            recommendations = recommendations.none()

    # 🔹 Ensure accessories are recommended for the shown outfits
    # (In case they were generated before this feature was enabled or need refreshing)
    from .utils import recommend_accessories, GET_CLOTHING_KEYWORDS
    from .models import AccessoryRecommendation
    from django.db.models import Q
    
    # Pre-emptive cleanup of any existing "clothing" accessory suggestions
    clothing_q = Q()
    for kw in GET_CLOTHING_KEYWORDS():
        clothing_q |= Q(accessory__name__icontains=kw) | Q(accessory__category__icontains=kw)
    
    if clothing_q:
        AccessoryRecommendation.objects.filter(clothing_q).delete()

    for rec in recommendations[:20]: # Only do it for the top ones to save time
        if not rec.accessory_recommendations.exists():
            recommend_accessories(rec, rec.top_item, rec.bottom_item)

    return render(request, 'user/recommend_fixed.html', {
        'recommendations': recommendations,
        'ai_chat_message': ai_chat_message,
    })


@role_required('user')
def wear_outfit(request, top_id, bottom_id):
    """
    Marks the top and bottom of an outfit as worn.
    If items reach their wear limit, they are marked as needing laundry.
    Also marks matching today's outfit plan as worn.
    """
    top = get_object_or_404(WardrobeItem, id=top_id, user=request.user)
    bottom = get_object_or_404(WardrobeItem, id=bottom_id, user=request.user)

    top.mark_worn()
    bottom.mark_worn()

    # Mark today's outfit plan as worn if it matches
    from django.utils import timezone
    from reminders.models import OutfitPlan
    today = timezone.now().date()
    OutfitPlan.objects.filter(
        user=request.user,
        date=today,
        outfit__top_item=top,
        outfit__bottom_item=bottom,
        worn=False
    ).update(worn=True)

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


@role_required('user')
def submit_feedback(request, recommendation_id):
    rec = get_object_or_404(OutfitRecommendation, id=recommendation_id, user=request.user)

    if request.method == 'POST':
        rating = float(request.POST.get('rating'))
        feedback_text = request.POST.get('feedback_text')

        from .models import OutfitFeedback
        
        # 1. Save Feedback
        OutfitFeedback.objects.create(
            recommendation=rec,
            user=request.user,
            rating=rating,
            feedback_text=feedback_text
        )

        # 2. Adjust Match Score based on User Rating (1-5 scale)
        if rating <= 2:
            new_score = 0.25  # Bad
            quality = "Bad"
        elif rating >= 5:
            new_score = 0.95  # Excellent
            quality = "Excellent"
        else:
            new_score = 0.75  # Good (2.5 - 4.0)
            quality = "Good"

        rec.match_score = new_score
        rec.save()

        messages.success(request, f'Thank you! We marked this outfit as "{quality}" and updated its score.')
    
    return redirect('recommend_outfit')

