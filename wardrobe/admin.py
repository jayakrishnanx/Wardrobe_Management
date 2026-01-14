from django.contrib import admin
from .models import WardrobeItem, Category, Occasion, Season

admin.site.register(WardrobeItem)
admin.site.register(Category)
admin.site.register(Occasion)
admin.site.register(Season)
