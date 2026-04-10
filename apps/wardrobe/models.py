from django.db import models
from accounts.models import CustomUser
from .utils import extract_dominant_color
from django.db.models.signals import post_delete
from django.dispatch import receiver
import os


import logging

logger = logging.getLogger(__name__)

class Occasion(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Season(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=50)
    max_wears = models.PositiveIntegerField(default=1, help_text="Number of wears before cleaning is needed")

    def __str__(self):
        return self.name


class WardrobeItem(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    item_type = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    occasion = models.ForeignKey(Occasion, on_delete=models.CASCADE)
    season = models.ForeignKey(Season, on_delete=models.CASCADE)

    color = models.CharField(max_length=50, null=True, blank=True)
    image = models.ImageField(upload_to='wardrobe/', null=True, blank=True)

    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Purchase price")
    purchase_date = models.DateField(null=True, blank=True)

    wear_count = models.PositiveIntegerField(default=0, help_text="Current wears since last wash")
    total_wears = models.PositiveIntegerField(default=0, help_text="Lifetime wear count")
    clean_status = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if self.image and (not self.color or is_new):
            try:
                self.color = extract_dominant_color(self.image.path)
                super().save(update_fields=['color'])
            except Exception as e:
                logger.warning(f"Failed to extract color for wardrobe item {self.id}: {e}")

    def mark_worn(self):
        """
        Increments wear count and updates clean status based on category limits.
        """
        self.wear_count += 1
        self.total_wears += 1
        
        # Use the category's max_wears setting instead of hardcoded strings
        if self.wear_count >= self.category.max_wears:
            self.clean_status = False

        self.save()

    def __str__(self):
        return self.item_type

    class Meta:
        indexes = [
            models.Index(fields=['user', 'clean_status']),
            models.Index(fields=['user', 'category']),
        ]


@receiver(post_delete, sender=WardrobeItem)
def delete_image_file(sender, instance, **kwargs):
    if instance.image and instance.image.path:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)
