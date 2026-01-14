from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.shortcuts import render
from accounts.decorators import role_required


def index(request):
    return render(request, 'accounts/index.html')

def index(request):
    if request.user.is_authenticated:
        return redirect('user_home')
    return render(request, 'accounts/index.html')


#___________USER__________#


@role_required('user')

def user_home(request):
    return render(request, 'accounts/user_home.html')

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)

            if user.role == 'user':
                return redirect('user_home')
            elif user.role == 'supplier':
                return redirect('/accessories/manage/')
            else:
                return redirect('admin_dashboard')

        return render(request, 'accounts/login.html', {
            'error': 'Invalid username or password'
        })

    return render(request, 'accounts/login.html')


def user_logout(request):
    logout(request)
    return redirect('user_login')

from django.contrib.auth.models import User
from django.contrib import messages
from .models import CustomUser




def user_register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            return render(request, 'accounts/register.html', {
                'error': 'Passwords do not match'
            })

        if CustomUser.objects.filter(username=username).exists():
            return render(request, 'accounts/register.html', {
                'error': 'Username already exists'
            })

        user = CustomUser.objects.create_user(
            username=username,
            email=email,
            password=password1,
            role='user'
        )

        return redirect('user_login')

    return render(request, 'accounts/register.html')

from accounts.decorators import role_required
from django.contrib.auth import get_user_model
from accessories.models import Accessory
from orders.models import Order
from recommendations.models import OutfitRecommendation

User = get_user_model()

####________SUPPLIER________####

def supplier_register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            return render(request, 'accounts/supplier_register.html', {
                'error': 'Passwords do not match'
            })

        if CustomUser.objects.filter(username=username).exists():
            return render(request, 'accounts/supplier_register.html', {
                'error': 'Username already exists'
            })

        CustomUser.objects.create_user(
            username=username,
            email=email,
            password=password1,
            role='supplier'
        )

        return redirect('user_login')

    return render(request, 'accounts/supplier_register.html')


########_________ADMIN_______########

@role_required('admin')
def admin_dashboard(request):
    context = {
        'total_users': User.objects.filter(role='user').count(),
        'total_suppliers': User.objects.filter(role='supplier').count(),
        'total_accessories': Accessory.objects.count(),
        'total_orders': Order.objects.count(),
        'total_recommendations': OutfitRecommendation.objects.count(),
    }
    return render(request, 'accounts/admin_dashboard.html', context)
