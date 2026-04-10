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
    # Filter to only show upcoming, non-worn plans
    plans = OutfitPlan.objects.filter(user=request.user, date__gte=today, worn=False).order_by('date')
    return render(request, 'user/planner.html', {'plans': plans})

@role_required('user')
def mark_plan_worn(request, plan_id):
    """
    Marks a specific planned outfit as worn.
    Keeps user on the planner page and avoids redundant success alerts.
    """
    plan = get_object_or_404(OutfitPlan, id=plan_id, user=request.user)
    
    # Mark the underlying clothes as worn
    top = plan.outfit.top_item
    bottom = plan.outfit.bottom_item
    
    top.mark_worn()
    bottom.mark_worn()
    
    # Mark the plan itself as worn
    plan.worn = True
    plan.save()
    
    # Only show critical laundry warnings, skip the generic 'You wore...' info message
    if not top.clean_status:
        messages.warning(request, f"⚠️ {top.item_type} reached its wear limit and needs laundry!")
    
    if not bottom.clean_status:
        messages.warning(request, f"⚠️ {bottom.item_type} reached its wear limit and needs laundry!")
        
    return redirect('view_planner')
