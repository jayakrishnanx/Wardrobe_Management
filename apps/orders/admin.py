from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('price',)
    can_delete = False

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'total_amount', 'status', 
        'payment_mode', 'order_date', 'item_count'
    )
    list_filter = ('status', 'payment_mode', 'order_date')
    search_fields = ('user__username', 'id', 'full_name', 'phone')
    inlines = [OrderItemInline]
    readonly_fields = ('order_date', 'total_amount')
    actions = ['mark_shipped', 'mark_delivered', 'mark_cancelled']

    def item_count(self, obj):
        return obj.items.count()
    item_count.short_description = 'Items'

    @admin.action(description='Mark selected orders as Shipped')
    def mark_shipped(self, request, queryset):
        queryset.update(status='shipped')

    @admin.action(description='Mark selected orders as Delivered')
    def mark_delivered(self, request, queryset):
        queryset.update(status='delivered')
    
    @admin.action(description='Mark selected orders as Cancelled')
    def mark_cancelled(self, request, queryset):
        queryset.update(status='cancelled')

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'accessory', 'quantity', 'price')
    list_filter = ('order__status',)
