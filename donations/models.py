# donations/models.py
from django.db import models
from django.utils import timezone
import json


class Donation(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('requested', 'Requested'),
        ('completed', 'Completed'),
        ('expired', 'Expired'),
    ]

    donation_id = models.AutoField(primary_key=True)
    donor = models.ForeignKey('users.Donor', on_delete=models.CASCADE, related_name='donations')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    quantity = models.FloatField(help_text="Quantity in kg")
    expiry_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    location_lat = models.FloatField()
    location_long = models.FloatField()
    address = models.CharField(max_length=500, blank=True)
    food_type = models.CharField(max_length=100, blank=True, help_text="e.g. Cooked, Raw, Packaged")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} by {self.donor.name}"

    @property
    def hours_to_expiry(self):
        delta = self.expiry_date - timezone.now()
        return max(delta.total_seconds() / 3600, 0)

    @property
    def is_expired(self):
        return timezone.now() > self.expiry_date

    def get_priority_score(self, receiver_lat=None, receiver_lng=None):
        """Compute AI priority score (0-100). Higher = more urgent."""
        import math
        hours = self.hours_to_expiry
        max_quantity = 100  # kg normalization constant

        # Urgency component (50 points max)
        urgency = (1 / (hours + 1)) * 50

        # Quantity component (30 points max)
        quantity_score = min(self.quantity / max_quantity, 1.0) * 30

        # Distance component (20 points max) – closer = higher score
        distance_factor = 1.0
        if receiver_lat and receiver_lng:
            try:
                lat1, lon1 = math.radians(self.location_lat), math.radians(self.location_long)
                lat2, lon2 = math.radians(float(receiver_lat)), math.radians(float(receiver_lng))
                dlat = lat2 - lat1
                dlon = lon2 - lon1
                a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
                dist_km = 2 * 6371 * math.asin(math.sqrt(a))
                distance_factor = max(1 - dist_km / 50, 0)  # 50 km normalization
            except Exception:
                distance_factor = 0.5

        distance_score = distance_factor * 20

        total = urgency + quantity_score + distance_score
        return round(min(total, 100), 1)


class DonationRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]

    request_id = models.AutoField(primary_key=True)
    donation = models.ForeignKey(Donation, on_delete=models.CASCADE, related_name='requests')
    receiver = models.ForeignKey('users.Receiver', on_delete=models.CASCADE, related_name='donation_requests')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    message = models.TextField(blank=True, help_text="Optional message from NGO")
    requested_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-requested_at']

    def __str__(self):
        return f"Request #{self.request_id} by {self.receiver.name}"


class Pickup(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    pickup_id = models.AutoField(primary_key=True)
    donation_request = models.OneToOneField(DonationRequest, on_delete=models.CASCADE, related_name='pickup')
    scheduled_time = models.DateTimeField()
    actual_pickup_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    driver_name = models.CharField(max_length=100, blank=True)
    driver_contact = models.CharField(max_length=15, blank=True)
    tracking_updates_json = models.TextField(default='[]', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Pickup #{self.pickup_id} – {self.status}"

    @property
    def tracking_updates(self):
        try:
            return json.loads(self.tracking_updates_json)
        except Exception:
            return []

    def add_tracking_update(self, lat, lng, status_msg):
        updates = self.tracking_updates
        updates.append({
            'timestamp': timezone.now().isoformat(),
            'lat': float(lat),
            'lng': float(lng),
            'status': status_msg,
        })
        self.tracking_updates_json = json.dumps(updates)
        self.save()

    @property
    def latest_location(self):
        updates = self.tracking_updates
        if updates:
            return updates[-1]
        return None


class Notification(models.Model):
    notification_id = models.AutoField(primary_key=True)
    user_type = models.CharField(max_length=20, choices=[('donor', 'Donor'), ('receiver', 'Receiver')])
    user_id = models.IntegerField()
    message = models.TextField()
    link = models.CharField(max_length=200, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.user_type} #{self.user_id}"


class ChatbotLog(models.Model):
    log_id = models.AutoField(primary_key=True)
    user_type = models.CharField(max_length=20)
    user_id = models.IntegerField()
    question = models.TextField()
    answer = models.TextField()
    donation_id = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
