from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from accounts.decorators import role_required
from .models import Accessory


@role_required('supplier')
def manage_accessories(request):
    accessories = Accessory.objects.filter(supplier=request.user)
    return render(request, 'accessories/manage.html', {
        'accessories': accessories
    })
