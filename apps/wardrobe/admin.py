from django.contrib import admin
from django.utils.html import format_html
from .models import WardrobeItem, Category, Occasion, Season

@admin.register(WardrobeItem)
class WardrobeItemAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'item_type', 'category', 
        'color_preview', 'wear_count', 'clean_status', 'image_thumbnail'
    )
    list_filter = ('category', 'occasion', 'season', 'clean_status', 'user')
    search_fields = ('item_type', 'color', 'user__username')
    readonly_fields = ('wear_count',)

    def color_preview(self, obj):
        if obj.color:
            return format_html(
                '<div style="width: 20px; height: 20px; background-color: {}; border: 1px solid #ccc;"></div>',
                obj.color
            )
        return "-"
    color_preview.short_description = 'Color'

    def image_thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover;" />', obj.image.url)
        return "No Image"
    image_thumbnail.short_description = 'Image'

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'max_wears')
    search_fields = ('name',)

@admin.register(Occasion)
class OccasionAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = ('name',)
