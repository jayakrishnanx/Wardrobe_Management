from django.contrib import admin
from .models import LaundryReminder, OccasionEvent

@admin.register(LaundryReminder)
class LaundryReminderAdmin(admin.ModelAdmin):
    list_display = ('user', 'item', 'reminder_date', 'status')
    list_filter = ('status', 'reminder_date')
    search_fields = ('user__username', 'item__item_type')
    actions = ['mark_sent']

    @admin.action(description='Mark selected reminders as Sent')
    def mark_sent(self, request, queryset):
        queryset.update(status='sent')

@admin.register(OccasionEvent)
class OccasionEventAdmin(admin.ModelAdmin):
    list_display = ('user', 'event_name', 'event_date', 'created_at')
    list_filter = ('event_date',)
    search_fields = ('user__username', 'event_name')
