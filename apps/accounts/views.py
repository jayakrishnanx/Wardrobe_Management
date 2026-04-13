from django.contrib.auth import authenticate, login, logout, get_user_model
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from accounts.decorators import role_required
from .models import CustomUser
from accessories.models import Accessory
from orders.models import Order
from recommendations.models import OutfitRecommendation
from wardrobe.models import WardrobeItem
from .utils import (
    send_welcome_email, 
    send_supplier_registration_email, 
    send_supplier_approval_email
)

User = get_user_model()


def index(request):
    return redirect('user_login')


# ================= USER ================= #

@role_required('user')
def user_home(request):
    from django.utils import timezone
    from reminders.models import OutfitPlan

    dirty_clothes_count = WardrobeItem.objects.filter(user=request.user, clean_status=False).count()

    today = timezone.now().date()
    todays_plan = OutfitPlan.objects.filter(user=request.user, date=today, worn=False).select_related(
        'outfit', 'outfit__top_item', 'outfit__bottom_item'
    ).first()

    context = {
        'dirty_clothes_count': dirty_clothes_count,
        'todays_plan': todays_plan,
    }
    return render(request, 'user/user_home.html', context)


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
        user.gender = request.POST.get('gender', user.gender)

        if 'profile_picture' in request.FILES:
            user.profile_picture = request.FILES['profile_picture']

        user.save()
        messages.success(request, 'Profile updated successfully')
        return redirect('user_profile')

    return render(request, 'user/edit_profile.html', {'user': request.user})


# ================= AUTH ================= #

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
                return redirect('supplier_home')  # must exist
            elif user.role == 'admin':
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
            role='user',
            gender=request.POST.get('gender', 'other')
        )

        send_welcome_email(user)

        return redirect('user_login')

    return render(request, 'auth/register.html')


# ================= SUPPLIER ================= #

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

        user = CustomUser.objects.create_user(
            username=username,
            email=email,
            password=password1,
            role='supplier'
        )
        user.is_active = False  # Wait for admin approval
        user.save()
        
        send_supplier_registration_email(user)
        
        messages.success(request, 'Registration successful. Please wait for admin approval.')
        return redirect('user_login')

    return render(request, 'auth/supplier_register.html')


# ================= CUSTOM ADMIN ================= #

@role_required('admin')
def admin_dashboard(request):
    from recommendations.models import OutfitFeedback
    
    pending_suppliers_count = CustomUser.objects.filter(role='supplier', is_active=False).count()
    feedback_count = OutfitFeedback.objects.count()
    
    context = {
        'total_users': User.objects.filter(role='user').count(),
        'total_suppliers': User.objects.filter(role='supplier').count(),
        'total_accessories': Accessory.objects.count(),
        'total_orders': Order.objects.count(),
        'total_recommendations': OutfitRecommendation.objects.count(),
        'pending_suppliers_count': pending_suppliers_count,
        'feedback_count': feedback_count,
    }
    return render(request, 'admin/admin_dashboard.html', context)


@role_required('admin')
def admin_users_list(request):
    users = CustomUser.objects.filter(role='user').order_by('-date_joined')
    return render(request, 'admin/users_list.html', {'users': users})


@role_required('admin')
def admin_delete_user(request, pk):
    if request.method == 'POST':
        user = get_object_or_404(CustomUser, pk=pk)
        if user.role == 'user':
            user.delete()
            messages.success(request, 'User deleted successfully.')
        else:
            messages.error(request, 'Cannot delete non-user accounts from this view.')
    return redirect('admin_users_list')


@role_required('admin')
def admin_suppliers_list(request):
    suppliers = CustomUser.objects.filter(role='supplier').order_by('-date_joined')
    return render(request, 'admin/suppliers_list.html', {'suppliers': suppliers})


@role_required('admin')
def admin_delete_supplier(request, pk):
    if request.method == 'POST':
        supplier = get_object_or_404(CustomUser, pk=pk)
        if supplier.role == 'supplier':
            supplier.delete()
            messages.success(request, 'Supplier deleted successfully.')
        else:
            messages.error(request, 'Cannot delete non-supplier accounts from this view.')
    return redirect('admin_suppliers_list')


@role_required('admin')
def admin_orders_list(request):
    orders = Order.objects.all().select_related('user').order_by('-order_date')
    return render(request, 'admin/orders_list.html', {'orders': orders})


@role_required('admin')
def admin_accessories_list(request):
    accessories = Accessory.objects.all().select_related('supplier')
    return render(request, 'admin/accessories_list.html', {'accessories': accessories})


@role_required('admin')
def admin_delete_accessory(request, pk):
    if request.method == 'POST':
        accessory = get_object_or_404(Accessory, pk=pk)
        accessory.delete()
        messages.success(request, 'Accessory deleted successfully.')
    return redirect('admin_accessories_list')


@role_required('admin')
def admin_recommendations_list(request):
    recommendations = OutfitRecommendation.objects.all().select_related('user', 'top_item', 'bottom_item').order_by('-match_score')
    return render(request, 'admin/recommendations_list.html', {'recommendations': recommendations})


@role_required('admin')
def admin_delete_recommendation(request, pk):
    if request.method == 'POST':
        rec = get_object_or_404(OutfitRecommendation, pk=pk)
        rec.delete()
        messages.success(request, 'Recommendation deleted successfully.')
    return redirect('admin_recommendations_list')


@role_required('admin')
def admin_edit_recommendation(request, pk):
    rec = get_object_or_404(OutfitRecommendation, pk=pk)
    
    if request.method == 'POST':
        try:
            new_score = float(request.POST.get('match_score'))
            if 0.0 <= new_score <= 1.0:
                rec.match_score = new_score
                rec.save()
                messages.success(request, 'Match score updated successfully.')
                return redirect('admin_recommendations_list')
            else:
                messages.error(request, 'Score must be between 0.0 and 1.0')
        except ValueError:
            messages.error(request, 'Invalid score format.')
            
    return render(request, 'admin/edit_recommendation.html', {'rec': rec})


@role_required('admin')
def admin_pending_suppliers(request):
    pending_suppliers = CustomUser.objects.filter(role='supplier', is_active=False).order_by('-date_joined')
    return render(request, 'admin/pending_suppliers.html', {'pending_suppliers': pending_suppliers})


@role_required('admin')
def admin_approve_supplier(request, pk):
    if request.method == 'POST':
        supplier = get_object_or_404(CustomUser, pk=pk)
        supplier.is_active = True
        supplier.save()
        
        send_supplier_approval_email(supplier)
        
        messages.success(request, f'Supplier {supplier.username} approved successfully.')
    return redirect('admin_pending_suppliers')


@role_required('admin')
def admin_reject_supplier(request, pk):
    if request.method == 'POST':
        supplier = get_object_or_404(CustomUser, pk=pk)
        supplier.delete()
        messages.success(request, 'Supplier request rejected and removed.')
    return redirect('admin_pending_suppliers')


@role_required('admin')
def admin_feedback_list(request):
    from recommendations.models import OutfitFeedback
    feedbacks = OutfitFeedback.objects.all().select_related('user', 'recommendation').order_by('-created_at')
    return render(request, 'admin/feedback_list.html', {'feedbacks': feedbacks})

@role_required('admin')
def admin_analyze_feedback(request, pk):
    from recommendations.models import OutfitFeedback
    from recommendations.utils import analyze_feedback_with_ai
    
    feedback = get_object_or_404(OutfitFeedback, pk=pk)
    success, message = analyze_feedback_with_ai(feedback)
    
    if not success:
        messages.error(request, message)
        
    return redirect('admin_feedback_list')
