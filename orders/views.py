from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from .models import Order, OrderItem
from accessories.models import Accessory

@login_required
def place_order(request):
    if request.method == 'POST':
        accessory_id = request.POST.get('accessory_id')
        quantity = int(request.POST.get('quantity', 1))

        accessory = Accessory.objects.get(id=accessory_id)

        order = Order.objects.create(
            user=request.user,
            total_amount=accessory.price * quantity
        )

        OrderItem.objects.create(
            order=order,
            accessory=accessory,
            quantity=quantity,
            price=accessory.price
        )

        accessory.stock -= quantity
        accessory.save()

    return redirect('recommend_outfit')
