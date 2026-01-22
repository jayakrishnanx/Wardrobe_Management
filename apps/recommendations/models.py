from django.db import models
from accounts.models import CustomUser
from wardrobe.models import WardrobeItem
from accessories.models import Accessory


from django.core.validators import MinValueValidator, MaxValueValidator

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
    is_favorite = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'top_item', 'bottom_item')
        indexes = [
            models.Index(fields=['user', 'match_score']),
        ]

    def __str__(self):
        return f"Outfit ({self.top_item} + {self.bottom_item})"

class ColorMatchingRule(models.Model):
    """
    Stores specific color combination rules to override ML predictions.
    Example: Red + Green = 0.20 (Bad), Black + White = 0.90 (Good).
    """
    color_1 = models.CharField(max_length=50, help_text="First color (e.g., 'red')")
    color_2 = models.CharField(max_length=50, help_text="Second color (e.g., 'green')")
    score = models.FloatField(
        help_text="Match score from 0.0 (Bad) to 1.0 (Excellent)",
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )

    class Meta:
        unique_together = ('color_1', 'color_2')
        verbose_name = "Color Matching Rule"
        verbose_name_plural = "Color Matching Rules"

    def __str__(self):
        return f"{self.color_1} + {self.color_2} = {self.score}"

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
