# administration/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin_login, name='admin_login'),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('users/', views.admin_users, name='admin_users'),
    path('verify/<str:user_type>/<int:user_id>/', views.admin_verify_user, name='admin_verify_user'),
    path('delete/<str:user_type>/<int:user_id>/', views.admin_delete_user, name='admin_delete_user'),
    path('logs/', views.admin_activity_logs, name='admin_logs'),
    # Sprint 4
    path('analytics/', views.admin_analytics, name='admin_analytics'),
    path('donations/', views.admin_donations, name='admin_donations'),
    path('pickups/', views.admin_pickups, name='admin_pickups'),
    path('pickups/<int:pickup_id>/deliver/', views.admin_mark_pickup_delivered, name='admin_deliver_pickup'),
    path('export/donations/', views.admin_export_donations, name='admin_export_donations'),
    path('export/users/', views.admin_export_users, name='admin_export_users'),
    path('logout/', views.admin_logout, name='admin_logout'),
]