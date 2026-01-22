from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from accounts.decorators import role_required
from .models import OutfitPlan
from recommendations.models import OutfitRecommendation
from django.utils import timezone

@role_required('user')
def plan_outfit(request, recommendation_id):
    outfit = get_object_or_404(OutfitRecommendation, id=recommendation_id, user=request.user)
    
    if request.method == 'POST':
        date_str = request.POST.get('date')
        if date_str:
            # Create or update plan for this date
            plan, created = OutfitPlan.objects.update_or_create(
                user=request.user,
                date=date_str,
                defaults={'outfit': outfit}
            )
            messages.success(request, f"Outfit planned for {date_str}!")
            return redirect('view_planner')
            
    return render(request, 'user/plan_outfit.html', {'outfit': outfit})

@role_required('user')
def view_planner(request):
    today = timezone.now().date()
    plans = OutfitPlan.objects.filter(user=request.user, date__gte=today).order_by('date')
    return render(request, 'user/planner.html', {'plans': plans})
