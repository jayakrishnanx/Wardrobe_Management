from django.contrib.auth import authenticate, login, logout, get_user_model
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.decorators import role_required
from .models import CustomUser
from accessories.models import Accessory
from orders.models import Order
from recommendations.models import OutfitRecommendation

User = get_user_model()


def index(request):
    return redirect('user_login')


#___________USER__________#


@role_required('user')
def user_home(request):
    return render(request, 'user/user_home.html')


@login_required
def user_profile(request):
    return render(request, 'user/profile.html', {'user': request.user})


@login_required
def edit_profile(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.phone_number = request.POST.get('phone_number', user.phone_number)
        user.address = request.POST.get('address', user.address)
        user.bio = request.POST.get('bio', user.bio)
        
        if 'profile_picture' in request.FILES:
            user.profile_picture = request.FILES['profile_picture']
            
        user.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('user_profile')
        
    return render(request, 'user/edit_profile.html', {'user': request.user})


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
                return redirect('supplier_home')
            else:
                return redirect('admin_dashboard')

        return render(request, 'auth/login.html', {
            'error': 'Invalid username or password'
        })

    return render(request, 'auth/login.html')


def user_logout(request):
    logout(request)
    return redirect('user_login')


def user_register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            return render(request, 'auth/register.html', {
                'error': 'Passwords do not match'
            })

        if CustomUser.objects.filter(username=username).exists():
            return render(request, 'auth/register.html', {
                'error': 'Username already exists'
            })

        user = CustomUser.objects.create_user(
            username=username,
            email=email,
            password=password1,
            role='user'
        )

        return redirect('user_login')

    return render(request, 'auth/register.html')


####________SUPPLIER________####


def supplier_register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            return render(request, 'auth/supplier_register.html', {
                'error': 'Passwords do not match'
            })

        if CustomUser.objects.filter(username=username).exists():
            return render(request, 'auth/supplier_register.html', {
                'error': 'Username already exists'
            })

        CustomUser.objects.create_user(
            username=username,
            email=email,
            password=password1,
            role='supplier'
        )

        return redirect('user_login')

    return render(request, 'auth/supplier_register.html')





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
    return render(request, 'admin/admin_dashboard.html', context)
