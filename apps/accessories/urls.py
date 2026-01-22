from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('supplier/home/', views.supplier_home, name='supplier_home'),
    path('manage/', views.manage_accessories, name='manage_accessories'),
    path('add/', views.add_accessories, name='add_accessories'),
    path('orders/', views.supplier_orders, name='supplier_orders'),
    path('shop/', views.shop_accessories, name='shop_accessories'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('manage/', views.manage_accessories, name='manage_accessories'),
    path('update-stock/<int:accessory_id>/', views.update_stock, name='update_stock'),
    path('delete/<int:accessory_id>/', views.delete_accessory, name='delete_accessory'),
    path('edit/<int:accessory_id>/', views.edit_accessory, name='edit_accessory'),
     path('orders/', views.supplier_orders, name='supplier_orders'),
    path('orders/ship/<int:order_id>/', views.mark_shipped, name='mark_shipped'),
]
