from django.urls import path
from .views import *


urlpatterns = [
    path('', index, name='index'),
    path('login/', user_login, name='user_login'),
    path('register/', user_register, name='user_register'),
    path('logout/', user_logout, name='user_logout'),
    path('register/supplier',supplier_register,name='supplier_register'),
    path('user/home/', user_home, name='user_home'),

    
]
