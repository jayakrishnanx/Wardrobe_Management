from recommendations.models import OutfitRecommendation, AccessoryRecommendation
from recommendations.utils import recommend_accessories

recs = OutfitRecommendation.objects.all()[:5]
for r in recs:
    print(f"Processing outfit {r.id}...")
    recommend_accessories(r, r.top_item, r.bottom_item)

print(f"Processed {recs.count()} outfits.")
print(f"New total accessory recs: {AccessoryRecommendation.objects.count()}")
