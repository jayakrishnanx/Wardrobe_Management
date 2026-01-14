from django.db import models
from accounts.models import CustomUser
from wardrobe.models import Occasion, Season


class Accessory(models.Model):
    supplier = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50)

    occasion = models.ForeignKey(Occasion, on_delete=models.CASCADE)
    season = models.ForeignKey(Season, on_delete=models.CASCADE)

    price = models.DecimalField(max_digits=8, decimal_places=2)
    stock = models.IntegerField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
