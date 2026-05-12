# users/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_page, name='home'),
    path('register/', views.register_page, name='register'),
    path('login/', views.login_page, name='login'),
    path('verify/', views.verify_page, name='verify'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile_page, name='profile'),
    path('logout/', views.logout_view, name='logout'),
    path('change-password/', views.change_password, name='change_password'),
    
    # API Endpoints
    path('api/get-location/', views.get_location_from_address, name='get_location'),
    path('api/get-address/', views.get_address_from_location, name='get_address'),
]