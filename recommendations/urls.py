from django.urls import path
from .views import recommend_outfit

urlpatterns = [
    path('recommend/', recommend_outfit, name='recommend_outfit'),
]
