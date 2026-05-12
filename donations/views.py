# donations/views.py
import json
import math
from datetime import datetime
from collections import defaultdict
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.views.decorators.http import require_POST

from users.models import Donor, Receiver
from .models import Donation, DonationRequest, Pickup, Notification, ChatbotLog

FOOD_CATEGORIES = [
    'Cooked Food', 'Raw Ingredients', 'Packaged Food',
    'Baked Goods', 'Fruits & Vegetables', 'Dairy', 'Other'
]


# =================== DECORATORS ===================

def donor_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.session.get('role') != 'donor':
            messages.error(request, 'Access denied. Donor account required.')
            return redirect('/login/')
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper


def receiver_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.session.get('role') != 'receiver':
            messages.error(request, 'Access denied. NGO account required.')
            return redirect('/login/')
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper


def login_required_any(view_func):
    def wrapper(request, *args, **kwargs):
        if 'role' not in request.session:
            return redirect('/login/')
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper


# =================== SIDEBAR CONTEXT HELPERS ===================

def get_donor_sidebar_context(donor):
    """Return badge counts for donor sidebar."""
    donations = Donation.objects.filter(donor=donor)
    pending = DonationRequest.objects.filter(donation__in=donations, status='pending').count()
    active = donations.filter(status='active').count()
    unread = Notification.objects.filter(
        user_type='donor', user_id=donor.donor_id, is_read=False
    ).count()
    return {
        'layout_role': 'donor',
        'sidebar_pending_count': pending or '',
        'sidebar_active_count': active or '',
        'sidebar_unread_count': unread or '',
    }


def get_receiver_sidebar_context(receiver):
    """Return badge counts for NGO sidebar."""
    unread = Notification.objects.filter(
        user_type='receiver', user_id=receiver.receiver_id, is_read=False
    ).count()
    pending = DonationRequest.objects.filter(receiver=receiver, status='pending').count()
    return {
        'layout_role': 'receiver',
        'sidebar_pending_count': pending or '',
        'sidebar_unread_count': unread or '',
    }


# =================== HELPERS ===================

def send_notification(user_type, user_id, message, link=''):
    Notification.objects.create(
        user_type=user_type, user_id=user_id, message=message, link=link,
    )


def send_email_notification(to_email, subject, body):
    try:
        send_mail(subject, body, settings.EMAIL_HOST_USER, [to_email], fail_silently=True)
    except Exception:
        pass


def mark_expired_donations():
    Donation.objects.filter(status='active', expiry_date__lt=timezone.now()).update(status='expired')


# =================== SPRINT 2: DONATION CRUD ===================

@donor_required
def create_donation(request):
    donor = Donor.objects.get(donor_id=request.session['user_id'])
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        quantity_raw = request.POST.get('quantity', '')
        expiry_date_raw = request.POST.get('expiry_date', '')
        food_type = request.POST.get('food_type', '').strip()
        lat_raw = request.POST.get('lat', '')
        lng_raw = request.POST.get('lng', '')
        address = request.POST.get('address', '').strip()

        errors = []
        if not title:
            errors.append('Title is required.')
        try:
            quantity = float(quantity_raw)
            if quantity <= 0:
                errors.append('Quantity must be positive.')
        except (ValueError, TypeError):
            errors.append('Quantity must be a valid number.')
            quantity = 0

        expiry_dt = None
        try:
            expiry_dt = datetime.strptime(expiry_date_raw, '%Y-%m-%dT%H:%M')
            expiry_dt = timezone.make_aware(expiry_dt)
            if expiry_dt <= timezone.now():
                errors.append('Expiry date must be in the future.')
        except ValueError:
            errors.append('Invalid expiry date.')

        if errors:
            for e in errors:
                messages.error(request, e)
            return render(request, 'donations/create_donation.html', {
                'donor': donor, 'food_categories': FOOD_CATEGORIES,
                'default_lat': donor.location_lat, 'default_lng': donor.location_long,
                **get_donor_sidebar_context(donor),
            })

        try:
            lat = float(lat_raw) if lat_raw else donor.location_lat
            lng = float(lng_raw) if lng_raw else donor.location_long
        except (TypeError, ValueError):
            lat, lng = donor.location_lat, donor.location_long

        if not address:
            address = f"{donor.address_line1}, {donor.city}"

        Donation.objects.create(
            donor=donor, title=title, description=description,
            quantity=quantity, expiry_date=expiry_dt, food_type=food_type,
            location_lat=lat, location_long=lng, address=address, status='active',
        )
        messages.success(request, f'Donation "{title}" created successfully!')
        return redirect('/donations/my-donations/')

    return render(request, 'donations/create_donation.html', {
        'donor': donor, 'food_categories': FOOD_CATEGORIES,
        'default_lat': donor.location_lat, 'default_lng': donor.location_long,
        **get_donor_sidebar_context(donor),
    })


@donor_required
def edit_donation(request, donation_id):
    donor = Donor.objects.get(donor_id=request.session['user_id'])
    donation = get_object_or_404(Donation, donation_id=donation_id, donor=donor)

    if donation.status not in ('active',):
        messages.error(request, 'Only active donations can be edited.')
        return redirect('/donations/my-donations/')

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        quantity_raw = request.POST.get('quantity', '')
        expiry_date_raw = request.POST.get('expiry_date', '')
        food_type = request.POST.get('food_type', '').strip()
        lat_raw = request.POST.get('lat', '')
        lng_raw = request.POST.get('lng', '')
        address = request.POST.get('address', '').strip()

        errors = []
        if not title:
            errors.append('Title is required.')
        try:
            quantity = float(quantity_raw)
            if quantity <= 0:
                errors.append('Quantity must be positive.')
        except (ValueError, TypeError):
            errors.append('Quantity must be a valid number.')
            quantity = donation.quantity

        expiry_dt = None
        try:
            expiry_dt = datetime.strptime(expiry_date_raw, '%Y-%m-%dT%H:%M')
            expiry_dt = timezone.make_aware(expiry_dt)
            if expiry_dt <= timezone.now():
                errors.append('Expiry date must be in the future.')
        except ValueError:
            errors.append('Invalid expiry date.')

        if errors:
            for e in errors:
                messages.error(request, e)
        else:
            try:
                lat = float(lat_raw) if lat_raw else donation.location_lat
                lng = float(lng_raw) if lng_raw else donation.location_long
            except (TypeError, ValueError):
                lat, lng = donation.location_lat, donation.location_long

            donation.title = title
            donation.description = description
            donation.quantity = quantity
            donation.expiry_date = expiry_dt
            donation.food_type = food_type
            donation.location_lat = lat
            donation.location_long = lng
            if address:
                donation.address = address
            donation.save()
            messages.success(request, f'Donation "{title}" updated successfully!')
            return redirect('/donations/my-donations/')

    return render(request, 'donations/create_donation.html', {
        'donor': donor, 'donation': donation, 'edit_mode': True,
        'food_categories': FOOD_CATEGORIES,
        'default_lat': donation.location_lat, 'default_lng': donation.location_long,
        **get_donor_sidebar_context(donor),
    })


@require_POST
@donor_required
def delete_donation(request, donation_id):
    donor = Donor.objects.get(donor_id=request.session['user_id'])
    donation = get_object_or_404(Donation, donation_id=donation_id, donor=donor)

    if donation.status in ('requested', 'completed'):
        messages.error(request, 'Cannot delete a donation that has been accepted or completed.')
        return redirect('/donations/my-donations/')

    title = donation.title
    donation.delete()
    messages.success(request, f'Donation "{title}" deleted.')
    return redirect('/donations/my-donations/')


@receiver_required
def list_donations(request):
    mark_expired_donations()
    receiver = Receiver.objects.get(receiver_id=request.session['user_id'])
    donations = Donation.objects.filter(status='active').select_related('donor')

    search = request.GET.get('search', '').strip()
    food_type = request.GET.get('food_type', '').strip()
    max_hours = request.GET.get('max_hours', '').strip()

    if search:
        donations = donations.filter(title__icontains=search)
    if food_type:
        donations = donations.filter(food_type__icontains=food_type)
    if max_hours:
        try:
            cutoff = timezone.now() + timezone.timedelta(hours=float(max_hours))
            donations = donations.filter(expiry_date__lte=cutoff)
        except (ValueError, TypeError):
            pass

    scored = []
    for d in donations:
        score = d.get_priority_score(receiver.location_lat, receiver.location_long)
        already = DonationRequest.objects.filter(donation=d, receiver=receiver).exists()
        scored.append({
            'donation': d, 'score': score, 'already_requested': already,
            'hours_left': round(d.hours_to_expiry, 1),
        })
    scored.sort(key=lambda x: x['score'], reverse=True)

    return render(request, 'donations/list_donations.html', {
        'scored_donations': scored, 'receiver': receiver,
        'search': search, 'food_type': food_type, 'max_hours': max_hours,
        'food_categories': FOOD_CATEGORIES,
        **get_receiver_sidebar_context(receiver),
    })


@login_required_any
def donation_detail(request, donation_id):
    donation = get_object_or_404(Donation, donation_id=donation_id)
    role = request.session.get('role')
    already_requested = False
    existing_request = None
    score = None
    requests_list = []
    donor = None
    receiver = None

    if role == 'receiver':
        receiver = Receiver.objects.get(receiver_id=request.session['user_id'])
        existing_request = DonationRequest.objects.filter(
            donation=donation, receiver=receiver
        ).first()
        already_requested = existing_request is not None
        score = donation.get_priority_score(receiver.location_lat, receiver.location_long)
        sidebar_ctx = get_receiver_sidebar_context(receiver)
    elif role == 'donor':
        donor = Donor.objects.get(donor_id=request.session['user_id'])
        if donation.donor == donor:
            requests_list = DonationRequest.objects.filter(
                donation=donation
            ).select_related('receiver').order_by('-requested_at')
        sidebar_ctx = get_donor_sidebar_context(donor)
    else:
        sidebar_ctx = {}

    return render(request, 'donations/donation_detail.html', {
        'donation': donation, 'role': role,
        'already_requested': already_requested, 'existing_request': existing_request,
        'score': score, 'requests_list': requests_list,
        'hours_left': round(donation.hours_to_expiry, 1),
        'layout_role': role,
        **sidebar_ctx,
    })


@receiver_required
def create_request(request, donation_id):
    donation = get_object_or_404(Donation, donation_id=donation_id, status='active')
    receiver = Receiver.objects.get(receiver_id=request.session['user_id'])

    if DonationRequest.objects.filter(donation=donation, receiver=receiver).exists():
        messages.warning(request, 'You have already requested this donation.')
        return redirect(f'/donations/{donation_id}/')

    if request.method == 'POST':
        message_text = request.POST.get('message', '').strip()[:1000]
        DonationRequest.objects.create(
            donation=donation, receiver=receiver,
            message=message_text, status='pending',
        )
        send_notification(
            'donor', donation.donor.donor_id,
            f'{receiver.name} requested your donation: "{donation.title}"',
            f'/donations/{donation_id}/'
        )
        send_email_notification(
            donation.donor.email, 'New Donation Request – AnnaDaan',
            f'Hi {donation.donor.name},\n\n{receiver.name} requested "{donation.title}".\n\nLog in to accept or reject.\n\n– Team AnnaDaan'
        )
        messages.success(request, 'Request sent successfully!')
        return redirect('/donations/my-requests/')

    return render(request, 'donations/create_request.html', {
        'donation': donation, 'receiver': receiver,
        **get_receiver_sidebar_context(receiver),
    })


@donor_required
def manage_requests(request):
    donor = Donor.objects.get(donor_id=request.session['user_id'])
    donations = Donation.objects.filter(donor=donor)
    all_requests = DonationRequest.objects.filter(
        donation__in=donations
    ).select_related('receiver', 'donation').order_by('-requested_at')

    status_filter = request.GET.get('status', '').strip()
    if status_filter:
        filtered = all_requests.filter(status=status_filter)
    else:
        filtered = all_requests

    # Filter by donation id if provided
    donation_filter = request.GET.get('donation', '').strip()
    if donation_filter:
        filtered = filtered.filter(donation__donation_id=donation_filter)

    # Mark notifications read
    Notification.objects.filter(
        user_type='donor', user_id=donor.donor_id, is_read=False
    ).update(is_read=True)

    pending_count = all_requests.filter(status='pending').count()
    all_count = all_requests.count()

    return render(request, 'donations/manage_requests.html', {
        'pending_requests': filtered,
        'donor': donor,
        'status_filter': status_filter,
        'pending_count': pending_count,
        'all_count': all_count,
        **get_donor_sidebar_context(donor),
    })


@donor_required
def accept_request(request, request_id):
    req = get_object_or_404(DonationRequest, request_id=request_id)
    donor = Donor.objects.get(donor_id=request.session['user_id'])

    if req.donation.donor != donor:
        messages.error(request, 'Unauthorized.')
        return redirect('/donations/manage-requests/')

    if req.status != 'pending':
        messages.warning(request, 'This request has already been processed.')
        return redirect('/donations/manage-requests/')

    if request.method == 'POST':
        scheduled_time_str = request.POST.get('scheduled_time', '')
        driver_name = request.POST.get('driver_name', '').strip()[:100]
        driver_contact = request.POST.get('driver_contact', '').strip()[:15]

        try:
            scheduled_dt = datetime.strptime(scheduled_time_str, '%Y-%m-%dT%H:%M')
            scheduled_dt = timezone.make_aware(scheduled_dt)
            if scheduled_dt <= timezone.now():
                messages.error(request, 'Scheduled time must be in the future.')
                return redirect('/donations/manage-requests/')
        except (ValueError, TypeError):
            messages.error(request, 'Invalid scheduled time.')
            return redirect('/donations/manage-requests/')

        req.status = 'accepted'
        req.save()

        # Reject all other pending requests for same donation
        DonationRequest.objects.filter(
            donation=req.donation, status='pending'
        ).exclude(request_id=request_id).update(status='rejected')

        req.donation.status = 'requested'
        req.donation.save()

        Pickup.objects.create(
            donation_request=req,
            scheduled_time=scheduled_dt,
            driver_name=driver_name,
            driver_contact=driver_contact,
            status='scheduled',
        )

        send_notification(
            'receiver', req.receiver.receiver_id,
            f'Your request for "{req.donation.title}" was accepted! Pickup scheduled.',
            f'/donations/my-requests/'
        )
        send_email_notification(
            req.receiver.email, 'Donation Request Accepted – AnnaDaan',
            f'Hi {req.receiver.name},\n\nYour request for "{req.donation.title}" was accepted!\n'
            f'Pickup: {scheduled_dt.strftime("%d %b %Y, %I:%M %p")}\n'
            f'Driver: {driver_name} ({driver_contact})\n\n– Team AnnaDaan'
        )
        messages.success(request, f'Request accepted and pickup scheduled for {scheduled_dt.strftime("%d %b, %I:%M %p")}.')

    return redirect('/donations/manage-requests/')


@require_POST
@donor_required
def reject_request(request, request_id):
    req = get_object_or_404(DonationRequest, request_id=request_id)
    donor = Donor.objects.get(donor_id=request.session['user_id'])

    if req.donation.donor != donor:
        messages.error(request, 'Unauthorized.')
        return redirect('/donations/manage-requests/')

    if req.status != 'pending':
        messages.warning(request, 'This request has already been processed.')
        return redirect('/donations/manage-requests/')

    req.status = 'rejected'
    req.save()

    send_notification(
        'receiver', req.receiver.receiver_id,
        f'Your request for "{req.donation.title}" was not accepted. Try other donations.',
        '/donations/browse/'
    )
    messages.success(request, 'Request rejected.')
    return redirect('/donations/manage-requests/')


@receiver_required
def my_requests(request):
    receiver = Receiver.objects.get(receiver_id=request.session['user_id'])
    status_filter = request.GET.get('status', '').strip()
    all_reqs = DonationRequest.objects.filter(
        receiver=receiver
    ).select_related('donation', 'donation__donor').order_by('-requested_at')

    filtered = all_reqs.filter(status=status_filter) if status_filter else all_reqs

    Notification.objects.filter(
        user_type='receiver', user_id=receiver.receiver_id, is_read=False
    ).update(is_read=True)

    return render(request, 'donations/my_requests.html', {
        'my_requests': filtered,
        'receiver': receiver,
        'status_filter': status_filter,
        **get_receiver_sidebar_context(receiver),
    })


@donor_required
def my_donations(request):
    mark_expired_donations()
    donor = Donor.objects.get(donor_id=request.session['user_id'])
    donations_qs = Donation.objects.filter(donor=donor).prefetch_related('requests')

    search = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '').strip()

    if search:
        donations_qs = donations_qs.filter(title__icontains=search)
    if status_filter:
        donations_qs = donations_qs.filter(status=status_filter)

    Notification.objects.filter(
        user_type='donor', user_id=donor.donor_id, is_read=False
    ).update(is_read=True)

    donations_with_counts = []
    total_pending = 0
    for d in donations_qs:
        rc = d.requests.count()
        pc = d.requests.filter(status='pending').count()
        total_pending += pc
        donations_with_counts.append({'donation': d, 'request_count': rc, 'pending_count': pc})

    all_donations = Donation.objects.filter(donor=donor)
    food_saved = sum(d.quantity for d in all_donations if d.status == 'completed')
    active_count = all_donations.filter(status='active').count()

    return render(request, 'donations/my_donations.html', {
        'donations_with_counts': donations_with_counts,
        'donor': donor, 'search': search, 'status_filter': status_filter,
        'food_saved': food_saved, 'active_count': active_count,
        'total_count': all_donations.count(), 'total_pending': total_pending,
        **get_donor_sidebar_context(donor),
    })


# =================== SPRINT 3: PICKUP & TRACKING ===================

@login_required_any
def track_pickup(request, pickup_id):
    pickup = get_object_or_404(Pickup, pickup_id=pickup_id)
    req = pickup.donation_request
    role = request.session.get('role')
    user_id = request.session.get('user_id')

    authorized = False
    if role == 'donor' and req.donation.donor.donor_id == user_id:
        authorized = True
    elif role == 'receiver' and req.receiver.receiver_id == user_id:
        authorized = True
    elif role == 'admin':
        authorized = True

    if not authorized:
        messages.error(request, 'Unauthorized.')
        return redirect('/dashboard/')

    donor_obj = req.donation.donor
    receiver_obj = req.receiver
    tracking_updates = pickup.tracking_updates

    if role == 'donor':
        sidebar_ctx = get_donor_sidebar_context(donor_obj)
    elif role == 'receiver':
        sidebar_ctx = get_receiver_sidebar_context(receiver_obj)
    else:
        sidebar_ctx = {}

    return render(request, 'donations/track_pickup.html', {
        'pickup': pickup, 'req': req,
        'tracking_updates': json.dumps(tracking_updates),
        'latest': pickup.latest_location,
        'role': role, 'donor': donor_obj, 'receiver': receiver_obj,
        'layout_role': role,
        **sidebar_ctx,
    })


@login_required_any
def update_pickup_status(request, pickup_id):
    pickup = get_object_or_404(Pickup, pickup_id=pickup_id)
    req = pickup.donation_request
    role = request.session.get('role')
    user_id = request.session.get('user_id')

    authorized = (
        (role == 'receiver' and req.receiver.receiver_id == user_id) or
        (role == 'admin')
    )
    if not authorized:
        messages.error(request, 'Unauthorized.')
        return redirect('/dashboard/')

    if request.method == 'POST':
        new_status = request.POST.get('status', '')
        lat_raw = request.POST.get('lat', '')
        lng_raw = request.POST.get('lng', '')

        valid_statuses = ['scheduled', 'in_transit', 'delivered', 'cancelled']
        if new_status in valid_statuses:
            pickup.status = new_status
            if new_status == 'delivered':
                pickup.actual_pickup_time = timezone.now()
                req.donation.status = 'completed'
                req.donation.save()
                send_notification(
                    'donor', req.donation.donor.donor_id,
                    f'Your donation "{req.donation.title}" has been delivered!'
                )
            pickup.save()

            if lat_raw and lng_raw:
                try:
                    pickup.add_tracking_update(float(lat_raw), float(lng_raw), new_status)
                except Exception:
                    pass
            messages.success(request, f'Status updated to {new_status}.')

    return redirect(f'/donations/pickup/{pickup_id}/track/')


# =================== SPRINT 4: CHATBOT ===================

def chatbot_explain(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    donation_id = data.get('donation_id')
    user_question = data.get('question', '').strip()[:500]
    role = request.session.get('role', 'guest')
    user_id = request.session.get('user_id', 0)

    if not donation_id:
        return JsonResponse({'reply': 'Please click "Explain" on a donation card first.'})

    try:
        donation = Donation.objects.get(donation_id=donation_id)
    except Donation.DoesNotExist:
        return JsonResponse({'reply': 'Donation not found.'})

    receiver_lat = receiver_lng = None
    if role == 'receiver' and user_id:
        try:
            rcv = Receiver.objects.get(receiver_id=user_id)
            receiver_lat = rcv.location_lat
            receiver_lng = rcv.location_long
        except Receiver.DoesNotExist:
            pass

    score = donation.get_priority_score(receiver_lat, receiver_lng)
    hours = round(donation.hours_to_expiry, 1)
    qty = donation.quantity

    urgency_part = round((1 / (hours + 1)) * 50, 1)
    qty_part = round(min(qty / 100, 1.0) * 30, 1)
    dist_part = round(max(score - urgency_part - qty_part, 0), 1)

    urgency_label = (
        'critically urgent – collect immediately!' if hours < 3
        else 'high urgency' if hours < 12
        else 'moderate' if hours < 24
        else 'low urgency'
    )
    qty_label = 'large' if qty >= 50 else 'medium' if qty >= 20 else 'small'

    reply = (
        f"**Priority Score: {score}/100**\n\n"
        f"**🕐 Urgency ({urgency_part}/50):** {hours}h until expiry → {urgency_label}\n\n"
        f"**⚖️ Quantity ({qty_part}/30):** {qty} kg → {qty_label} quantity\n\n"
        f"**📍 Distance ({dist_part}/20):** Based on your location vs donation pickup point\n\n"
        f"{'🔴 Collect immediately!' if score >= 70 else '🟡 High priority' if score >= 40 else '🟢 Can plan ahead'}"
    )

    ChatbotLog.objects.create(
        user_type=role, user_id=user_id,
        question=user_question or f'Explain donation #{donation_id}',
        answer=reply, donation_id=donation_id,
    )
    return JsonResponse({'reply': reply, 'score': score})


# =================== NOTIFICATIONS API ===================

@login_required_any
def get_notifications(request):
    role = request.session.get('role')
    user_id = request.session.get('user_id')
    notifs = Notification.objects.filter(
        user_type=role, user_id=user_id
    ).order_by('-created_at')[:20]
    data = [{
        'id': n.notification_id, 'message': n.message,
        'link': n.link, 'is_read': n.is_read,
        'created_at': n.created_at.strftime('%d %b, %I:%M %p'),
    } for n in notifs]
    return JsonResponse({'notifications': data})


@login_required_any
def mark_notifications_read(request):
    role = request.session.get('role')
    user_id = request.session.get('user_id')
    Notification.objects.filter(
        user_type=role, user_id=user_id, is_read=False
    ).update(is_read=True)
    return JsonResponse({'success': True})


# =================== NOTIFICATIONS PAGE ===================

@login_required_any
def notifications_page(request):
    role = request.session.get('role')
    user_id = request.session.get('user_id')
    notifications = Notification.objects.filter(
        user_type=role, user_id=user_id
    ).order_by('-created_at')[:50]

    if role == 'donor':
        donor = Donor.objects.get(donor_id=user_id)
        sidebar_ctx = get_donor_sidebar_context(donor)
    elif role == 'receiver':
        receiver = Receiver.objects.get(receiver_id=user_id)
        sidebar_ctx = get_receiver_sidebar_context(receiver)
    else:
        sidebar_ctx = {}

    return render(request, 'notifications.html', {
        'notifications': notifications,
        'layout_role': role,
        **sidebar_ctx,
    })


@login_required_any
def mark_all_notifications_read(request):
    role = request.session.get('role')
    user_id = request.session.get('user_id')
    Notification.objects.filter(user_type=role, user_id=user_id, is_read=False).update(is_read=True)
    messages.success(request, 'All notifications marked as read.')
    return redirect('/notifications/')


# =================== ANALYTICS ===================

@donor_required
def donor_analytics(request):
    donor = Donor.objects.get(donor_id=request.session['user_id'])
    donations = Donation.objects.filter(donor=donor).prefetch_related('requests')

    # Basic stats
    total = donations.count()
    active = donations.filter(status='active').count()
    requested = donations.filter(status='requested').count()
    completed = donations.filter(status='completed').count()
    expired = donations.filter(status='expired').count()
    food_saved = sum(d.quantity for d in donations if d.status == 'completed')
    all_reqs = DonationRequest.objects.filter(donation__in=donations)
    accepted_reqs = all_reqs.filter(status='accepted').count()
    acceptance_rate = round((accepted_reqs / max(all_reqs.count(), 1)) * 100)

    # Monthly trend (last 6 months)
    from django.utils import timezone
    from dateutil.relativedelta import relativedelta
    import calendar
    now = timezone.now()
    monthly_labels = []
    monthly_counts = []
    for i in range(5, -1, -1):
        month_date = now - relativedelta(months=i)
        label = month_date.strftime('%b %Y')
        count = donations.filter(
            created_at__year=month_date.year,
            created_at__month=month_date.month
        ).count()
        monthly_labels.append(label)
        monthly_counts.append(count)

    return render(request, 'donations/donor_analytics.html', {
        'stats': {
            'total': total, 'active': active, 'requested': requested,
            'completed': completed, 'expired': expired,
            'food_saved_kg': food_saved, 'acceptance_rate': acceptance_rate,
        },
        'monthly_labels': json.dumps(monthly_labels),
        'monthly_counts': json.dumps(monthly_counts),
        'recent_donations': donations.order_by('-created_at')[:10],
        **get_donor_sidebar_context(donor),
    })


@receiver_required
def ngo_analytics(request):
    receiver = Receiver.objects.get(receiver_id=request.session['user_id'])
    my_reqs = DonationRequest.objects.filter(receiver=receiver).select_related(
        'donation', 'donation__donor'
    )

    total_requests = my_reqs.count()
    pending = my_reqs.filter(status='pending').count()
    accepted = my_reqs.filter(status='accepted').count()
    rejected = my_reqs.filter(status='rejected').count()
    food_received = sum(
        r.donation.quantity for r in my_reqs
        if r.status == 'accepted' and r.donation.status == 'completed'
    )

    # Active pickups
    accepted_ids = my_reqs.filter(status='accepted').values_list('request_id', flat=True)
    active_pickups = Pickup.objects.filter(
        donation_request__in=accepted_ids
    ).exclude(status__in=['delivered','cancelled']).select_related(
        'donation_request__donation'
    ).order_by('scheduled_time')[:5]

    # Monthly food received (last 6 months)
    from django.utils import timezone
    try:
        from dateutil.relativedelta import relativedelta
        has_dateutil = True
    except ImportError:
        has_dateutil = False

    now = timezone.now()
    monthly_labels = []
    monthly_kg = []
    if has_dateutil:
        from dateutil.relativedelta import relativedelta
        for i in range(5, -1, -1):
            month_date = now - relativedelta(months=i)
            label = month_date.strftime('%b %Y')
            kg = sum(
                r.donation.quantity for r in my_reqs
                if r.status == 'accepted'
                and r.requested_at.year == month_date.year
                and r.requested_at.month == month_date.month
            )
            monthly_labels.append(label)
            monthly_kg.append(round(kg, 1))
    else:
        monthly_labels = ['6m ago','5m ago','4m ago','3m ago','2m ago','This month']
        monthly_kg = [0]*6

    return render(request, 'donations/ngo_analytics.html', {
        'stats': {
            'total_requests': total_requests, 'pending': pending,
            'accepted': accepted, 'rejected': rejected,
            'food_received_kg': food_received, 'active_pickups': active_pickups.count(),
        },
        'active_pickups': active_pickups,
        'monthly_labels': json.dumps(monthly_labels),
        'monthly_kg': json.dumps(monthly_kg),
        'recent_requests': my_reqs.order_by('-requested_at')[:10],
        **get_receiver_sidebar_context(receiver),
    })
