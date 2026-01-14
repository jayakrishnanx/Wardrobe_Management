from wardrobe.models import WardrobeItem
from accessories.models import Accessory
from .models import OutfitRecommendation, AccessoryRecommendation


def generate_outfit_recommendations(user, occasion_id=None, season_id=None):
    """
    Rule-based outfit recommendation logic
    """

    # TOPS
    tops = WardrobeItem.objects.filter(
        user=user,
        category__name='Top',
        clean_status=True
    )

    # BOTTOMS
    bottoms = WardrobeItem.objects.filter(
        user=user,
        category__name='Bottom',
        clean_status=True
    )

    if occasion_id:
        tops = tops.filter(occasion__id=occasion_id)
        bottoms = bottoms.filter(occasion__id=occasion_id)

    if season_id:
        tops = tops.filter(season__id=season_id)
        bottoms = bottoms.filter(season__id=season_id)

    recommendations = []

    for top in tops:
        for bottom in bottoms:
            score = calculate_match_score(top, bottom)

            if score >= 0.5:
                rec = OutfitRecommendation.objects.create(
                    user=user,
                    top_item=top,
                    bottom_item=bottom,
                    match_score=score
                )
                recommendations.append(rec)

                recommend_accessories(rec, occasion_id, season_id)

    return recommendations

def calculate_match_score(top, bottom):
    score = 0.0

    if top.color.lower() == bottom.color.lower():
        score += 0.4

    if top.occasion_id == bottom.occasion_id:
        score += 0.3

    if top.season_id == bottom.season_id:
        score += 0.3

    return round(score, 2)

def recommend_accessories(outfit, occasion_id, season_id):
    accessories = Accessory.objects.filter(
        is_active=True,
        stock__gt=0
    )

    if occasion_id:
        accessories = accessories.filter(occasion__id=occasion_id)

    if season_id:
        accessories = accessories.filter(season__id=season_id)

    for accessory in accessories:
        AccessoryRecommendation.objects.create(
            outfit=outfit,
            accessory=accessory,
            score=0.7
        )
