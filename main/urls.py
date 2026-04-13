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
    path('manifest.json', TemplateView.as_view(template_name='pwa/manifest.json', content_type='application/json'), name='manifest'),
    path('sw.js', TemplateView.as_view(template_name='pwa/sw.js', content_type='application/javascript'), name='service_worker'),
]

from django.views.generic.base import TemplateView

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
