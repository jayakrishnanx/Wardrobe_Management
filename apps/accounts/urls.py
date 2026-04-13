from django.urls import path
from .views import *

urlpatterns = [
    path('', index, name='index'),

    # auth
    path('login/', user_login, name='user_login'),
    path('register/', user_register, name='user_register'),
    path('logout/', user_logout, name='user_logout'),
    path('register/supplier/', supplier_register, name='supplier_register'),

    # user
    path('user/home/', user_home, name='user_home'),
    path('profile/', user_profile, name='user_profile'),
    path('profile/edit/', edit_profile, name='edit_profile'),
    path('offline/', offline_view, name='offline'),

    # CUSTOM ADMIN
    path('admin/dashboard/', admin_dashboard, name='admin_dashboard'),
    path('admin/users/', admin_users_list, name='admin_users_list'),
    path('admin/users/delete/<int:pk>/', admin_delete_user, name='admin_delete_user'),
    path('admin/suppliers/', admin_suppliers_list, name='admin_suppliers_list'),
    path('admin/suppliers/delete/<int:pk>/', admin_delete_supplier, name='admin_delete_supplier'),
    path('admin/orders/', admin_orders_list, name='admin_orders_list'),
    path('admin/accessories/', admin_accessories_list, name='admin_accessories_list'),
    path('admin/accessories/delete/<int:pk>/', admin_delete_accessory, name='admin_delete_accessory'),
    path('admin/recommendations/outfitrecommendation/', admin_recommendations_list, name='admin_recommendations_list'),
    path('admin/recommendations/delete/<int:pk>/', admin_delete_recommendation, name='admin_delete_recommendation'),
    path('admin/recommendations/edit/<int:pk>/', admin_edit_recommendation, name='admin_edit_recommendation'),
    path('admin/suppliers/pending/', admin_pending_suppliers, name='admin_pending_suppliers'),
    path('admin/suppliers/approve/<int:pk>/', admin_approve_supplier, name='admin_approve_supplier'),
    path('admin/suppliers/reject/<int:pk>/', admin_reject_supplier, name='admin_reject_supplier'),
    path('admin/feedback/', admin_feedback_list, name='admin_feedback_list'),
    path('admin/feedback/analyze/<int:pk>/', admin_analyze_feedback, name='admin_analyze_feedback'),
]
