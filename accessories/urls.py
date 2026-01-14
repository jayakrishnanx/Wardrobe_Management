from django.urls import path
from .views import manage_accessories

urlpatterns = [
    path('manage/', manage_accessories, name='manage_accessories'),
]
