# annadaan/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Django's built-in admin
    path('admin/', admin.site.urls),

    # Custom admin panel
    path('panel/', include('administration.urls')),

    # Donation management (Sprint 2-4)
    path('donations/', include('donations.urls')),

    # Notifications page (accessible at /notifications/)
    path('notifications/', include([
        path('', getattr(__import__('donations.views', fromlist=['views']), 'notifications_page'), name='notifications_page'),
        path('mark-all-read/', getattr(__import__('donations.views', fromlist=['views']), 'mark_all_notifications_read'), name='mark_all_read'),
    ])),

    # User URLs
    path('', include('users.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
