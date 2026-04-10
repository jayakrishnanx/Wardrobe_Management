from django.contrib import admin
from .models import OutfitRecommendation, AccessoryRecommendation, ColorMatchingRule, OutfitFeedback

@admin.register(OutfitFeedback)
class OutfitFeedbackAdmin(admin.ModelAdmin):
    list_display = ('recommendation', 'user', 'rating', 'feedback_text', 'is_read', 'created_at')
    list_filter = ('is_read', 'rating', 'created_at')
    search_fields = ('user__username', 'feedback_text')
    actions = ['mark_as_read']

    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
    mark_as_read.short_description = "Mark selected feedback as Read"

    def get_queryset(self, request):
        """Show unread items first"""
        return super().get_queryset(request).order_by('is_read', '-created_at')

class OutfitFeedbackInline(admin.TabularInline):
    model = OutfitFeedback
    extra = 0
    readonly_fields = ('user', 'rating', 'feedback_text', 'created_at')

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
    inlines = [OutfitFeedbackInline]

@admin.register(AccessoryRecommendation)
class AccessoryRecommendationAdmin(admin.ModelAdmin):
    list_display = ('outfit', 'accessory', 'score')
    list_filter = ('score',)
