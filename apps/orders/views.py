from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.db import transaction
from .models import Order, OrderItem
from accessories.models import Accessory

@login_required
def user_orders(request: HttpRequest) -> HttpResponse:
    """
    Displays the user's order history, optionally filtered by status.
    """
    status = request.GET.get('status')
    orders = Order.objects.filter(user=request.user)

    if status:
        orders = orders.filter(status=status)

    orders = orders.order_by('-order_date')

    return render(request, 'user/user_orders.html', {
        'orders': orders,
        'selected_status': status
    })

@login_required
def cancel_order(request: HttpRequest, order_id: int) -> HttpResponse:
    """
    Cancels an order if it is still in 'ordered' status.
    """
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.status == 'ordered':
        order.status = 'cancelled'
        order.save()

    return redirect('user_orders')

@login_required
def checkout(request: HttpRequest) -> HttpResponse:
    """
    Prepares the checkout page. Stores order details in session.
    """
    if request.method == 'POST':
        accessory = get_object_or_404(
            Accessory, id=request.POST['accessory_id']
        )
        quantity = int(request.POST['quantity'])

        if quantity > accessory.stock:
            return redirect('shop_accessories')

        total = accessory.price * quantity

        request.session['order_data'] = {
            'accessory_id': accessory.id,
            'quantity': quantity,
            'total': float(total)
        }

        return render(request, 'user/checkout.html', {
            'accessory': accessory,
            'quantity': quantity,
            'total': total
        })
    return redirect('shop_accessories')

@login_required
def place_order(request: HttpRequest) -> HttpResponse:
    """
    Finalizes the order using data from the session and POSTed address/payment info.
    Uses atomic transaction to ensure data integrity.
    """
    if request.method != 'POST':
        return redirect('shop_accessories')

    data = request.session.get('order_data')
    if not data:
        return redirect('shop_accessories')

    full_name = request.POST.get('full_name')
    phone = request.POST.get('phone')
    address = request.POST.get('address')
    city = request.POST.get('city')
    state = request.POST.get('state')
    pincode = request.POST.get('pincode')
    payment_mode = request.POST.get('payment_mode')

    if not address or not payment_mode:
        messages.error(request, "Please provide all required shipping details.")
        return redirect('shop_accessories')

    try:
        with transaction.atomic():
            # Lock the accessory row for update to prevent race conditions
            accessory = Accessory.objects.select_for_update().get(id=data['accessory_id'])
            quantity = data['quantity']

            if quantity > accessory.stock:
                # Stock changed while checkout was happening
                messages.error(request, "Sorry, this item is out of stock.")
                return redirect('shop_accessories')

            # Deduct stock
            accessory.stock -= quantity
            accessory.save()

            # Create Order
            order = Order.objects.create(
                user=request.user,
                full_name=full_name,
                phone=phone,
                address=address,
                city=city,
                state=state,
                pincode=pincode,
                payment_mode=payment_mode,
                total_amount=accessory.price * quantity
            )

            # Create Order Item
            OrderItem.objects.create(
                order=order,
                accessory=accessory,
                quantity=quantity,
                price=accessory.price
            )

            # Clear session data
            del request.session['order_data']
            
            messages.success(request, "Order placed successfully!")
            return redirect('order_confirmation', order_id=order.id)
            
    except Accessory.DoesNotExist:
        messages.error(request, "The item you are trying to buy no longer exists.")
        return redirect('shop_accessories')
    except Exception as e:
        # Handle other errors gracefully
        messages.error(request, f"An error occurred while placing your order: {str(e)}")
        return redirect('shop_accessories')

@login_required
def order_confirmation(request: HttpRequest, order_id: int) -> HttpResponse:
    """
    Displays the bill/confirmation for a placed order.
    """
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'user/bill.html', {'order': order})
