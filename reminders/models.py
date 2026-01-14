from django.db import models
from accounts.models import CustomUser
from wardrobe.models import WardrobeItem


class LaundryReminder(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('sent', 'Sent'),
    )

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='laundry_reminders'
    )
    item = models.ForeignKey(
        WardrobeItem,
        on_delete=models.CASCADE
    )
    reminder_date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    def __str__(self):
        return f"Laundry reminder for {self.item.item_type}"


class OccasionEvent(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='occasion_events'
    )
    event_name = models.CharField(max_length=100)
    event_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.event_name
