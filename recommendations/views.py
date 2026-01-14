from django.shortcuts import render, redirect
from wardrobe.models import Occasion, Season
from .models import OutfitRecommendation
from .utils import generate_outfit_recommendations
from accounts.decorators import role_required


@role_required('user')
def recommend_outfit(request):

    if request.method == 'POST':
        occasion_id = request.POST.get('occasion')
        season_id = request.POST.get('season')


        OutfitRecommendation.objects.filter(user=request.user).delete()

        generate_outfit_recommendations(
            user=request.user,
            occasion_id=occasion_id,
            season_id=season_id
        )


        return redirect('recommend_outfit')

    
    recommendations = OutfitRecommendation.objects.filter(user=request.user)

    return render(request, 'recommendations/recommend.html', {
        'recommendations': recommendations,
        'occasions': Occasion.objects.all(),
        'seasons': Season.objects.all(),
    })
