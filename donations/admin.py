# donations/admin.py
from django.contrib import admin
from .models import Donation, DonationRequest, Pickup, Notification, ChatbotLog

@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ['donation_id', 'title', 'donor', 'quantity', 'status', 'expiry_date', 'created_at']
    list_filter = ['status', 'food_type']
    search_fields = ['title', 'donor__name']

@admin.register(DonationRequest)
class DonationRequestAdmin(admin.ModelAdmin):
    list_display = ['request_id', 'donation', 'receiver', 'status', 'requested_at']
    list_filter = ['status']

@admin.register(Pickup)
class PickupAdmin(admin.ModelAdmin):
    list_display = ['pickup_id', 'donation_request', 'status', 'scheduled_time', 'driver_name']
    list_filter = ['status']

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['notification_id', 'user_type', 'user_id', 'is_read', 'created_at']

@admin.register(ChatbotLog)
class ChatbotLogAdmin(admin.ModelAdmin):
    list_display = ['log_id', 'user_type', 'user_id', 'donation_id', 'created_at']
