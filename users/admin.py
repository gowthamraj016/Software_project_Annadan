from django.contrib import admin
from .models import Donor, Receiver, OTP

admin.site.register(Donor)
admin.site.register(Receiver)
admin.site.register(OTP)