from django.urls import path
from .views import recommend_outfit, wear_outfit, toggle_favorite, submit_feedback

urlpatterns = [
    path('recommend/', recommend_outfit, name='recommend_outfit'),
    path('wear/<int:top_id>/<int:bottom_id>/', wear_outfit, name='wear_outfit'),
    path('favorite/<int:recommendation_id>/', toggle_favorite, name='toggle_favorite'),
    path('feedback/<int:recommendation_id>/', submit_feedback, name='submit_feedback'),
]
