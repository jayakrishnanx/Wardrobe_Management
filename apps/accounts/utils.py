from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import logging
import random
from datetime import timedelta
from django.utils import timezone
import threading

logger = logging.getLogger(__name__)

def _send_email_thread(msg, to_email, email_type):
    """
    Background thread worker for sending emails.
    """
    try:
        msg.send()
        logger.info(f"{email_type} sent successfully to {to_email} (Background)")
    except Exception as e:
        logger.error(f"Failed to send {email_type} to {to_email} in background: {str(e)}")


def send_welcome_email(user):
    """
    Sends a welcome email to a newly registered user (Asynchronously).
    """
    subject = 'Welcome to Wardrobe Management!'
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = user.email
    
    if not to_email:
        logger.warning(f"No email address found for user {user.username}. Welcome email not sent.")
        return False

    context = {
        'username': user.username,
        'login_url': 'http://127.0.0.1:8000/login/',
    }

    html_content = render_to_string('emails/welcome_email.html', context)
    text_content = render_to_string('emails/welcome_email.txt', context)

    try:
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
        msg.attach_alternative(html_content, "text/html")
        
        # Start background thread
        thread = threading.Thread(target=_send_email_thread, args=(msg, to_email, "Welcome email"))
        thread.start()
        
        return True
    except Exception as e:
        logger.error(f"Failed to initialize welcome email for {to_email}: {str(e)}")
        return False


def send_supplier_registration_email(user):
    """
    Sends a welcome email to a newly registered supplier (Asynchronously).
    """
    subject = 'Supplier Registration Received - Wardrobe Management'
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = user.email
    
    if not to_email: return False

    context = {
        'username': user.username,
    }

    html_content = render_to_string('emails/supplier_registration_email.html', context)
    text_content = render_to_string('emails/supplier_registration_email.txt', context)

    try:
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
        msg.attach_alternative(html_content, "text/html")
        
        # Start background thread
        thread = threading.Thread(target=_send_email_thread, args=(msg, to_email, "Supplier registration email"))
        thread.start()
        
        return True
    except Exception as e:
        logger.error(f"Failed to initialize supplier registration email: {str(e)}")
        return False


def send_supplier_approval_email(user):
    """
    Sends an approval email to a supplier (Asynchronously).
    """
    subject = 'Congratulations! Your Supplier Account is Approved'
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = user.email
    
    if not to_email: return False

    context = {
        'username': user.username,
        'login_url': 'http://127.0.0.1:8000/login/',
    }

    html_content = render_to_string('emails/supplier_approval_email.html', context)
    text_content = render_to_string('emails/supplier_approval_email.txt', context)

    try:
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
        msg.attach_alternative(html_content, "text/html")
        
        # Start background thread
        thread = threading.Thread(target=_send_email_thread, args=(msg, to_email, "Supplier approval email"))
        thread.start()
        
        return True
    except Exception as e:
        logger.error(f"Failed to initialize supplier approval email: {str(e)}")
        return False


def send_shipment_notification_email(order):
    """
    Sends a shipment notification email (Asynchronously).
    """
    subject = f'Your Order #{order.id} has been Shipped! 🚚'
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = order.user.email
    
    if not to_email: return False

    # 1. Prepare items data
    items_data = []
    base_url = "http://127.0.0.1:8000" # Should be dynamic in production
    
    for item in order.items.all():
        image_url = f"{base_url}{item.accessory.image.url}" if item.accessory.image else None
        items_data.append({
            'name': item.accessory.name,
            'quantity': item.quantity,
            'price': item.price,
            'image_url': image_url
        })

    context = {
        'username': order.user.username,
        'order_id': order.id,
        'total_amount': order.total_amount,
        'items': items_data,
        'orders_url': f"{base_url}/orders/my-orders/",
    }

    html_content = render_to_string('emails/shipment_notification_email.html', context)
    text_content = render_to_string('emails/shipment_notification_email.txt', context)

    try:
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
        msg.attach_alternative(html_content, "text/html")
        
        # Start background thread
        thread = threading.Thread(target=_send_email_thread, args=(msg, to_email, "Shipment notification email"))
        thread.start()
        
        return True
    except Exception as e:
        logger.error(f"Failed to initialize shipment notification email: {str(e)}")
        return False


def send_order_confirmation_email(order):
    """
    Sends a "Bill" style order confirmation email (Asynchronously).
    """
    subject = f'Order Confirmation # {order.id} - Wardrobe Management'
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = order.user.email
    
    if not to_email: return False

    # 1. Use the pre-calculated expected_delivery_date from the database
    delivery_date_str = "Within 7 days"
    if order.expected_delivery_date:
        delivery_date_str = order.expected_delivery_date.strftime('%B %d, %Y')

    # 2. Prepare items data
    items_data = []
    base_url = "http://127.0.0.1:8000" # Should be dynamic in production
    
    for item in order.items.all():
        image_url = f"{base_url}{item.accessory.image.url}" if item.accessory.image else None
        items_data.append({
            'name': item.accessory.name,
            'quantity': item.quantity,
            'price': item.price,
            'image_url': image_url
        })

    # 3. Get first item name for the summary message
    product_name = items_data[0]['name'] if items_data else "items"

    # 4. Get Human-readable payment mode
    payment_display = dict(order.PAYMENT_CHOICES).get(order.payment_mode, order.payment_mode)

    context = {
        'username': order.user.username,
        'order_id': order.id,
        'total_amount': order.total_amount,
        'delivery_date': delivery_date_str,
        'items': items_data,
        'orders_url': f"{base_url}/orders/my-orders/",
        
        # Shipping Details
        'full_name': order.full_name,
        'phone': order.phone,
        'address': order.address,
        'city': order.city,
        'state': order.state,
        'pincode': order.pincode,
        'payment_mode': payment_display,
        'product_name': product_name,
    }

    html_content = render_to_string('emails/order_confirmation_email.html', context)
    text_content = render_to_string('emails/order_confirmation_email.txt', context)

    try:
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
        msg.attach_alternative(html_content, "text/html")
        
        # Start background thread
        thread = threading.Thread(target=_send_email_thread, args=(msg, to_email, "Order confirmation email"))
        thread.start()
        
        return True
    except Exception as e:
        logger.error(f"Failed to initialize order confirmation email: {str(e)}")
        return False
