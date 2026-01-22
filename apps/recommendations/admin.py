from django.contrib import admin
from .models import OutfitRecommendation, AccessoryRecommendation, ColorMatchingRule

@admin.register(ColorMatchingRule)
class ColorMatchingRuleAdmin(admin.ModelAdmin):
    list_display = ('color_1', 'color_2', 'score', 'score_label')
    list_filter = ('score',)
    search_fields = ('color_1', 'color_2')
    ordering = ('-score',)

    def score_label(self, obj):
        if obj.score >= 0.8:
            return "Excellent"
        elif obj.score >= 0.5:
            return "Good"
        return "Bad"
    score_label.short_description = 'Label'

@admin.register(OutfitRecommendation)
class OutfitRecommendationAdmin(admin.ModelAdmin):
    list_display = ('user', 'top_item', 'bottom_item', 'match_score', 'created_at')
    list_filter = ('created_at', 'match_score')
    search_fields = ('user__username', 'top_item__item_type', 'bottom_item__item_type')
    readonly_fields = ('created_at',)

@admin.register(AccessoryRecommendation)
class AccessoryRecommendationAdmin(admin.ModelAdmin):
    list_display = ('outfit', 'accessory', 'score')
    list_filter = ('score',)
