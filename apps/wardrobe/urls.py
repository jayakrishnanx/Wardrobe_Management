from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.wardrobe_home, name='wardrobe_home'),
    path('add/', views.add_wardrobe, name='add_wardrobe'),
    path('delete/<int:item_id>/', views.delete_wardrobe, name='delete_wardrobe'),

    path('view/', views.view_clothes, name='view_clothes'),
    path('wear/<int:item_id>/', views.mark_as_worn, name='mark_as_worn'),
    path('laundry/<int:item_id>/', views.send_to_laundry, name='send_to_laundry'),
    path('laundry/', views.laundry_list, name='laundry_list'),
    path('laundry/done/<int:item_id>/', views.send_to_laundry, name='send_to_laundry'),
    path('laundry/clean/<int:item_id>/', views.mark_as_clean, name='mark_as_clean'),
    path('laundry/send/<int:item_id>/', views.send_to_laundry, name='send_to_laundry'),
    path('stats/', views.wardrobe_stats, name='wardrobe_stats'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
