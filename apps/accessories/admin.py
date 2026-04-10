from django.contrib import admin
from django.utils.html import format_html
from .models import Accessory

@admin.register(Accessory)
class AccessoryAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'supplier', 'category', 'price', 
        'stock', 'stock_status', 'is_active', 'image_thumbnail'
    )
    list_filter = ('category', 'is_active', 'occasion', 'season', 'supplier')
    search_fields = ('name', 'supplier__username', 'color')
    list_editable = ('price', 'stock', 'is_active')

    def stock_status(self, obj):
        if obj.stock == 0:
            return format_html('<span style="color: red; font-weight: bold;">Out of Stock</span>')
        elif obj.stock < 5:
            return format_html('<span style="color: orange; font-weight: bold;">Low Stock</span>')
        return format_html('<span style="color: green;">In Stock</span>')
    stock_status.short_description = 'Stock Status'

    def image_thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover;" />', obj.image.url)
        return "No Image"
    image_thumbnail.short_description = 'Image'
