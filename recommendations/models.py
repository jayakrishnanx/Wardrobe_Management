from django.db import models
from accounts.models import CustomUser
from wardrobe.models import WardrobeItem
from accessories.models import Accessory


class OutfitRecommendation(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='outfit_recommendations'
    )
    top_item = models.ForeignKey(
        WardrobeItem,
        on_delete=models.CASCADE,
        related_name='top_recommendations'
    )
    bottom_item = models.ForeignKey(
        WardrobeItem,
        on_delete=models.CASCADE,
        related_name='bottom_recommendations'
    )
    match_score = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Outfit ({self.top_item} + {self.bottom_item})"

class AccessoryRecommendation(models.Model):
    outfit = models.ForeignKey(
        OutfitRecommendation,
        on_delete=models.CASCADE,
        related_name='accessory_recommendations'
    )
    accessory = models.ForeignKey(
        Accessory,
        on_delete=models.CASCADE
    )
    score = models.FloatField()

    def __str__(self):
        return f"{self.accessory} for outfit {self.outfit.id}"
