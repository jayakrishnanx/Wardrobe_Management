from django.urls import path
from . import views

urlpatterns = [
    path('plan/<int:recommendation_id>/', views.plan_outfit, name='plan_outfit'),
    path('planner/', views.view_planner, name='view_planner'),
]