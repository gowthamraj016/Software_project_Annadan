# donations/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Donation CRUD
    path('create/', views.create_donation, name='create_donation'),
    path('<int:donation_id>/', views.donation_detail, name='donation_detail'),
    path('<int:donation_id>/edit/', views.edit_donation, name='edit_donation'),
    path('<int:donation_id>/delete/', views.delete_donation, name='delete_donation'),

    # Donor management
    path('my-donations/', views.my_donations, name='my_donations'),
    path('manage-requests/', views.manage_requests, name='manage_requests'),
    path('request/<int:request_id>/accept/', views.accept_request, name='accept_request'),
    path('request/<int:request_id>/reject/', views.reject_request, name='reject_request'),

    # NGO
    path('browse/', views.list_donations, name='list_donations'),
    path('<int:donation_id>/request/', views.create_request, name='create_request'),
    path('my-requests/', views.my_requests, name='my_requests'),

    # Pickup & tracking
    path('pickup/<int:pickup_id>/track/', views.track_pickup, name='track_pickup'),
    path('pickup/<int:pickup_id>/update/', views.update_pickup_status, name='update_pickup_status'),

    # Chatbot & notifications API
    path('api/chatbot/', views.chatbot_explain, name='chatbot_explain'),
    path('api/notifications/', views.get_notifications, name='get_notifications'),
    path('api/notifications/read/', views.mark_notifications_read, name='mark_notifications_read'),

    # Analytics
    path('analytics/donor/', views.donor_analytics, name='donor_analytics'),
    path('analytics/ngo/', views.ngo_analytics, name='ngo_analytics'),
]
