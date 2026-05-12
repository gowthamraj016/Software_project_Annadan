# users/views.py
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib.auth.hashers import check_password
from django.conf import settings
from django.contrib import messages
from django.http import JsonResponse
import json
import random
import requests
import time

from .models import Donor, Receiver, OTP
from administration.models import Admin


# ================= HELPER FUNCTIONS =================

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp_email(email, otp):
    send_mail(
        '🔐 Verify Your AnnaDaan Account',
        f"""
        🌟 Welcome to AnnaDaan! 🌟
        
        Your One-Time Password (OTP) is: {otp}
        
        This OTP is valid for 5 minutes.
        
        Use this code to verify your email and complete registration.
        
        Thank you for joining us in reducing food waste! 🙏
        
        - Team AnnaDaan
        """,
        settings.EMAIL_HOST_USER,
        [email],
        fail_silently=False,
    )

def reverse_geocode(lat, lng):
    """Get address from coordinates using OpenStreetMap Nominatim"""
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lng}&addressdetails=1"
        response = requests.get(url, headers={'User-Agent': 'AnnaDaan/1.0'})
        data = response.json()
        
        if data and 'address' in data:
            address = data['address']
            return {
                'address_line1': address.get('road', '') + ' ' + address.get('house_number', ''),
                'city': address.get('city', address.get('town', address.get('village', ''))),
                'state': address.get('state', ''),
                'pincode': address.get('postcode', ''),
                'country': address.get('country', 'India'),
                'full_address': data.get('display_name', '')
            }
    except:
        pass
    return None

def geocode_address(address):
    """Get coordinates from address"""
    try:
        url = f"https://nominatim.openstreetmap.org/search?format=json&q={address}"
        response = requests.get(url, headers={'User-Agent': 'AnnaDaan/1.0'})
        data = response.json()
        
        if data and len(data) > 0:
            return {
                'lat': float(data[0]['lat']),
                'lng': float(data[0]['lon'])
            }
    except:
        pass
    return None


# ================= HOME PAGE =================

def home_page(request):
    if "role" in request.session:
        return redirect("/dashboard/")
    return render(request, "home.html")


# ================= REGISTER =================

def register_page(request):
    if "role" in request.session:
        return redirect("/dashboard/")
        
    if request.method == "POST":
        role = request.POST.get("role")
        email = request.POST.get("email")
        password = request.POST.get("password")
        name = request.POST.get("name")
        contact = request.POST.get("contact")
        
        # Validation
        if not all([email, password, name, contact]):
            messages.error(request, "⚠️ All fields are required")
            return render(request, "register.html")
        
        # Check existing user
        if Donor.objects.filter(email=email).exists() or Receiver.objects.filter(email=email).exists():
            messages.error(request, "⚠️ User already exists with this email")
            return render(request, "register.html")
        
        # Get location coordinates
        lat = request.POST.get("lat")
        lng = request.POST.get("lng")
        
        if not lat or not lng:
            messages.error(request, "📍 Please select your location on the map or use current location")
            return render(request, "register.html")
        
        try:
            lat = float(lat)
            lng = float(lng)
        except:
            messages.error(request, "📍 Invalid location coordinates")
            return render(request, "register.html")
        
        # Get address from form or reverse geocode
        address_line1 = request.POST.get("address_line1", "")
        city = request.POST.get("city", "")
        state = request.POST.get("state", "")
        pincode = request.POST.get("pincode", "")
        
        # If address is empty, try to get from coordinates
        if not address_line1:
            address_data = reverse_geocode(lat, lng)
            if address_data:
                address_line1 = address_data.get('address_line1', '')
                city = address_data.get('city', '')
                state = address_data.get('state', '')
                pincode = address_data.get('pincode', '')
        
        # Create user
        if role == "donor":
            Donor.objects.create(
                name=name,
                email=email,
                contact=contact,
                password=password,
                address_line1=address_line1,
                city=city,
                state=state,
                pincode=pincode,
                location_lat=lat,
                location_long=lng,
            )
        elif role == "receiver":
            capacity = request.POST.get("capacity")
            ngo_registration_no = request.POST.get("ngo_registration_no", "")
            
            if not capacity:
                messages.error(request, "🏢 Capacity required for NGO")
                return render(request, "register.html")
            
            Receiver.objects.create(
                name=name,
                email=email,
                contact=contact,
                password=password,
                capacity=int(capacity),
                ngo_registration_no=ngo_registration_no,
                address_line1=address_line1,
                city=city,
                state=state,
                pincode=pincode,
                location_lat=lat,
                location_long=lng,
            )
        else:
            messages.error(request, "❌ Invalid role selected")
            return render(request, "register.html")
        
        # Send OTP
        otp = generate_otp()
        OTP.objects.create(email=email, otp=otp)
        send_otp_email(email, otp)
        
        messages.success(request, "✅ Registration successful! Please verify your email.")
        return redirect(f"/verify/?email={email}")
    
    return render(request, "register.html")


# ================= VERIFY OTP =================

def verify_page(request):
    if "role" in request.session:
        return redirect("/dashboard/")
        
    email = request.GET.get("email")
    
    if not email:
        return redirect("/login/")
    
    if request.method == "POST":
        otp_input = request.POST.get("otp")
        
        try:
            otp_obj = OTP.objects.filter(email=email).latest('created_at')
        except OTP.DoesNotExist:
            messages.error(request, "❌ No OTP found. Please register again.")
            return redirect("/register/")
        
        if not otp_obj.is_valid():
            messages.error(request, "⏰ OTP expired. Please register again.")
            return redirect("/register/")
        
        if otp_obj.otp != otp_input:
            messages.error(request, "❌ Invalid OTP. Please try again.")
            return render(request, "verify_otp.html", {"email": email})
        
        # Verify user
        if Donor.objects.filter(email=email).exists():
            user = Donor.objects.get(email=email)
        else:
            user = Receiver.objects.get(email=email)
        
        user.is_verified = True
        user.save()
        otp_obj.delete()
        
        messages.success(request, "🎉 Email verified successfully! You can now login.")
        return redirect("/login/")
    
    return render(request, "verify_otp.html", {"email": email})


# ================= LOGIN =================

def login_page(request):
    if "role" in request.session:
        return redirect("/dashboard/")
        
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        
        # Check admin
        try:
            admin = Admin.objects.get(username=username)
            if check_password(password, admin.password):
                request.session["role"] = "admin"
                request.session["user"] = admin.username
                request.session["user_id"] = admin.admin_id
                request.session["user_name"] = admin.username
                messages.success(request, f"👋 Welcome back, {admin.username}!")
                return redirect("/dashboard/")
        except Admin.DoesNotExist:
            pass
        
        # Check donor
        try:
            donor = Donor.objects.get(email=username)
            if not donor.is_verified:
                messages.error(request, "📧 Please verify your email first")
                return render(request, "login.html")
            
            if check_password(password, donor.password):
                request.session["role"] = "donor"
                request.session["user"] = donor.email
                request.session["user_id"] = donor.donor_id
                request.session["user_name"] = donor.name
                messages.success(request, f"👋 Welcome back, {donor.name}!")
                return redirect("/dashboard/")
        except Donor.DoesNotExist:
            pass
        
        # Check receiver
        try:
            receiver = Receiver.objects.get(email=username)
            if not receiver.is_verified:
                messages.error(request, "📧 Please verify your email first")
                return render(request, "login.html")
            
            if check_password(password, receiver.password):
                request.session["role"] = "receiver"
                request.session["user"] = receiver.email
                request.session["user_id"] = receiver.receiver_id
                request.session["user_name"] = receiver.name
                messages.success(request, f"👋 Welcome back, {receiver.name}!")
                return redirect("/dashboard/")
        except Receiver.DoesNotExist:
            pass
        
        messages.error(request, "❌ Invalid credentials. Please try again.")
    
    return render(request, "login.html")


# ================= DASHBOARD =================

def dashboard(request):
    if "role" not in request.session:
        return redirect("/login/")

    role = request.session.get("role")
    context = {
        "role": role,
        "user": request.session.get("user"),
        "user_name": request.session.get("user_name"),
        "layout_role": role,
    }

    if role == "donor":
        try:
            user_data = Donor.objects.get(email=request.session.get("user"))
            context["user_data"] = user_data
            try:
                from donations.models import Donation, DonationRequest
                from django.utils import timezone as tz
                donations = Donation.objects.filter(donor=user_data)
                context["donations_count"] = donations.count()
                context["active_donations"] = donations.filter(status='active').count()
                context["pending_request_count"] = DonationRequest.objects.filter(
                    donation__in=donations, status='pending'
                ).count()
                context["food_saved_kg"] = round(sum(
                    d.quantity for d in donations if d.status == 'completed'
                ), 1)
                # Sidebar context
                context["sidebar_pending_count"] = context["pending_request_count"] or ''
                context["sidebar_active_count"] = context["active_donations"] or ''
                from donations.models import Notification
                context["sidebar_unread_count"] = Notification.objects.filter(
                    user_type='donor', user_id=user_data.donor_id, is_read=False
                ).count() or ''
            except Exception:
                pass
        except Donor.DoesNotExist:
            pass

    elif role == "receiver":
        try:
            user_data = Receiver.objects.get(email=request.session.get("user"))
            context["user_data"] = user_data
            try:
                from donations.models import Donation, DonationRequest, Pickup, Notification
                from django.utils import timezone as tz
                my_reqs = DonationRequest.objects.filter(receiver=user_data)
                context["requests_count"] = my_reqs.count()
                context["accepted_requests"] = my_reqs.filter(status='accepted').count()
                context["active_donations_count"] = Donation.objects.filter(
                    status='active', expiry_date__gt=tz.now()
                ).count()
                accepted_req_ids = my_reqs.filter(status='accepted').values_list('request_id', flat=True)
                context["pickups_in_transit"] = Pickup.objects.filter(
                    donation_request__in=accepted_req_ids, status='in_transit'
                ).count()
                # Sidebar
                context["sidebar_pending_count"] = my_reqs.filter(status='pending').count() or ''
                context["sidebar_unread_count"] = Notification.objects.filter(
                    user_type='receiver', user_id=user_data.receiver_id, is_read=False
                ).count() or ''
            except Exception:
                pass
        except Receiver.DoesNotExist:
            pass

    return render(request, "dashboard.html", context)



# ================= PROFILE MANAGEMENT =================

def profile_page(request):
    if "role" not in request.session:
        return redirect("/login/")
    
    role = request.session.get("role")
    email = request.session.get("user")
    
    if role == "donor":
        user = Donor.objects.get(email=email)
    elif role == "receiver":
        user = Receiver.objects.get(email=email)
    else:
        return redirect("/dashboard/")
    
    if request.method == "POST":
        # Update personal info
        user.name = request.POST.get("name")
        user.contact = request.POST.get("contact")
        
        # Update address
        user.address_line1 = request.POST.get("address_line1", "")
        user.city = request.POST.get("city", "")
        user.state = request.POST.get("state", "")
        user.pincode = request.POST.get("pincode", "")
        
        # Update location coordinates
        try:
            lat = float(request.POST.get("lat"))
            lng = float(request.POST.get("lng"))
            user.location_lat = lat
            user.location_long = lng
        except (TypeError, ValueError):
            pass
        
        # Update NGO specific fields
        if role == "receiver":
            capacity = request.POST.get("capacity")
            if capacity:
                user.capacity = int(capacity)
            user.ngo_registration_no = request.POST.get("ngo_registration_no", "")
        
        user.save()
        request.session["user_name"] = user.name
        
        messages.success(request, "✅ Profile updated successfully!")
        return redirect("/profile/")
    
    return render(request, "profile.html", {"user": user, "role": role})

def change_password(request):
    if "role" not in request.session:
        return redirect("/login/")
    
    if request.method == "POST":
        current_password = request.POST.get("current_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")
        
        if new_password != confirm_password:
            messages.error(request, "❌ Passwords do not match")
            return redirect("/profile/")
        
        if len(new_password) < 6:
            messages.error(request, "❌ Password must be at least 6 characters")
            return redirect("/profile/")
        
        role = request.session.get("role")
        email = request.session.get("user")
        
        if role == "donor":
            user = Donor.objects.get(email=email)
        elif role == "receiver":
            user = Receiver.objects.get(email=email)
        else:
            return redirect("/profile/")
        
        if check_password(current_password, user.password):
            user.password = new_password
            user.save()
            messages.success(request, "🔒 Password changed successfully!")
        else:
            messages.error(request, "❌ Current password is incorrect")
        
        return redirect("/profile/")
    
    return redirect("/profile/")

def logout_view(request):
    request.session.flush()
    messages.info(request, "👋 You have been logged out")
    return redirect("/")

# ================= API ENDPOINTS =================

def get_location_from_address(request):
    """API endpoint to get coordinates from address"""
    if request.method == "POST":
        data = json.loads(request.body)
        address = data.get("address", "")
        
        if address:
            result = geocode_address(address)
            if result:
                return JsonResponse({"success": True, "lat": result["lat"], "lng": result["lng"]})
        
        return JsonResponse({"success": False, "error": "Address not found"})
    
    return JsonResponse({"error": "Invalid request"}, status=400)

def get_address_from_location(request):
    """API endpoint to get address from coordinates"""
    if request.method == "POST":
        data = json.loads(request.body)
        lat = data.get("lat")
        lng = data.get("lng")
        
        if lat and lng:
            result = reverse_geocode(lat, lng)
            if result:
                return JsonResponse({"success": True, **result})
        
        return JsonResponse({"success": False, "error": "Location not found"})
    
    return JsonResponse({"error": "Invalid request"}, status=400)