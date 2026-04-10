from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', include('accounts.urls')),
    path('recommendations/', include('recommendations.urls')),
    path('orders/', include('orders.urls')),
    path('accessories/', include('accessories.urls')),
    path('wardrobe/', include('wardrobe.urls')),
    path('reminders/', include('reminders.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
