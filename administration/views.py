# administration/views.py
import csv
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Count, Sum, Avg, Q
from datetime import timedelta
from .models import Admin, AdminActivityLog
from users.models import Donor, Receiver


def admin_login(request):
    """Custom admin login page"""
    if request.session.get('admin_logged_in'):
        return redirect('/panel/dashboard/')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            admin = Admin.objects.get(username=username)
            if admin.check_password(password):
                request.session['admin_logged_in'] = True
                request.session['admin_id'] = admin.admin_id
                request.session['admin_username'] = admin.username
                request.session['admin_name'] = admin.full_name

                # Log activity
                AdminActivityLog.objects.create(
                    admin=admin,
                    action='LOGIN',
                    details=f'Admin {username} logged in',
                    ip_address=request.META.get('REMOTE_ADDR')
                )

                messages.success(request, f'Welcome back, {admin.full_name}!')
                return redirect('/panel/dashboard/')
            else:
                messages.error(request, 'Invalid password')
        except Admin.DoesNotExist:
            messages.error(request, 'Admin account not found')

    return render(request, 'admin/login.html')


def admin_required(view_func):
    """Decorator to check admin login"""
    def wrapper(request, *args, **kwargs):
        if not request.session.get('admin_logged_in'):
            messages.error(request, 'Please login to access admin panel')
            return redirect('/panel/')
        return view_func(request, *args, **kwargs)
    return wrapper


@admin_required
def admin_dashboard(request):
    """Admin dashboard with analytics overview"""
    admin = Admin.objects.get(admin_id=request.session.get('admin_id'))

    # Try to get donation stats
    donation_stats = {}
    try:
        from donations.models import Donation, DonationRequest, Pickup
        now = timezone.now()
        thirty_days_ago = now - timedelta(days=30)

        total_donations = Donation.objects.count()
        active_donations = Donation.objects.filter(status='active').count()
        completed_donations = Donation.objects.filter(status='completed').count()
        total_food_saved = Donation.objects.filter(status='completed').aggregate(
            total=Sum('quantity')
        )['total'] or 0

        total_requests = DonationRequest.objects.count()
        accepted_requests = DonationRequest.objects.filter(status='accepted').count()
        acceptance_rate = round((accepted_requests / total_requests * 100) if total_requests else 0, 1)

        total_pickups = Pickup.objects.count()
        delivered_pickups = Pickup.objects.filter(status='delivered').count()
        pickup_rate = round((delivered_pickups / total_pickups * 100) if total_pickups else 0, 1)

        active_donors = Donor.objects.filter(
            donations__created_at__gte=thirty_days_ago
        ).distinct().count()
        active_receivers = Receiver.objects.filter(
            donation_requests__requested_at__gte=thirty_days_ago
        ).distinct().count()

        donation_stats = {
            'total_donations': total_donations,
            'active_donations': active_donations,
            'completed_donations': completed_donations,
            'total_food_saved': round(total_food_saved, 1),
            'total_requests': total_requests,
            'accepted_requests': accepted_requests,
            'acceptance_rate': acceptance_rate,
            'total_pickups': total_pickups,
            'delivered_pickups': delivered_pickups,
            'pickup_rate': pickup_rate,
            'active_donors': active_donors,
            'active_receivers': active_receivers,
        }
    except Exception:
        pass

    context = {
        'admin': admin,
        'total_donors': Donor.objects.count(),
        'total_receivers': Receiver.objects.count(),
        'verified_donors': Donor.objects.filter(is_verified=True).count(),
        'verified_receivers': Receiver.objects.filter(is_verified=True).count(),
        'pending_donors': Donor.objects.filter(is_verified=False).count(),
        'pending_receivers': Receiver.objects.filter(is_verified=False).count(),
        'recent_donors': Donor.objects.all().order_by('-created_at')[:5],
        'recent_receivers': Receiver.objects.all().order_by('-created_at')[:5],
        **donation_stats,
    }

    return render(request, 'admin/dashboard.html', context)


@admin_required
def admin_users(request):
    """Manage users"""
    admin = Admin.objects.get(admin_id=request.session.get('admin_id'))

    user_type = request.GET.get('type', 'all')
    status = request.GET.get('status', 'all')
    search = request.GET.get('search', '')

    donors = list(Donor.objects.all())
    receivers = list(Receiver.objects.all())

    # Tag each user with their type
    for d in donors:
        d._type = 'donor'
    for r in receivers:
        r._type = 'receiver'

    if user_type == 'donor':
        users = donors
    elif user_type == 'receiver':
        users = receivers
    else:
        users = donors + receivers

    if search:
        users = [u for u in users if search.lower() in u.name.lower() or search.lower() in u.email.lower()]

    if status == 'verified':
        users = [u for u in users if u.is_verified]
    elif status == 'pending':
        users = [u for u in users if not u.is_verified]

    context = {
        'admin': admin,
        'users': users,
        'user_type': user_type,
        'status': status,
        'search': search,
        'donors_count': len(donors),
        'receivers_count': len(receivers),
    }

    return render(request, 'admin/users.html', context)


@admin_required
def admin_verify_user(request, user_type, user_id):
    """Verify a user"""
    admin = Admin.objects.get(admin_id=request.session.get('admin_id'))
    try:
        if user_type == 'donor':
            user = Donor.objects.get(donor_id=user_id)
        else:
            user = Receiver.objects.get(receiver_id=user_id)

        user.is_verified = True
        user.save()

        AdminActivityLog.objects.create(
            admin=admin,
            action='VERIFY_USER',
            details=f'Verified {user_type} {user.name} ({user.email})',
            ip_address=request.META.get('REMOTE_ADDR')
        )

        messages.success(request, f'✅ {user.name} has been verified!')
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')

    return redirect('/panel/users/')


@admin_required
def admin_delete_user(request, user_type, user_id):
    """Delete a user"""
    admin = Admin.objects.get(admin_id=request.session.get('admin_id'))
    try:
        if user_type == 'donor':
            user = Donor.objects.get(donor_id=user_id)
        else:
            user = Receiver.objects.get(receiver_id=user_id)

        user_name = user.name
        user_email = user.email
        user.delete()

        AdminActivityLog.objects.create(
            admin=admin,
            action='DELETE_USER',
            details=f'Deleted {user_type} {user_name} ({user_email})',
            ip_address=request.META.get('REMOTE_ADDR')
        )

        messages.success(request, f'✅ {user_name} has been deleted!')
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')

    return redirect('/panel/users/')


@admin_required
def admin_activity_logs(request):
    """Admin activity logs"""
    admin = Admin.objects.get(admin_id=request.session.get('admin_id'))
    logs = AdminActivityLog.objects.select_related('admin').order_by('-created_at')[:100]
    return render(request, 'admin/logs.html', {'admin': admin, 'logs': logs})


@admin_required
def admin_analytics(request):
    """Analytics dashboard – Sprint 4"""
    admin_obj = Admin.objects.get(admin_id=request.session.get('admin_id'))

    context = {'admin': admin_obj}

    try:
        from donations.models import Donation, DonationRequest, Pickup
        from django.db.models.functions import TruncDay, TruncMonth

        now = timezone.now()
        thirty_days_ago = now - timedelta(days=30)

        # --- Core Metrics ---
        total_donations = Donation.objects.count()
        completed_donations = Donation.objects.filter(status='completed').count()
        total_food_saved = Donation.objects.filter(status='completed').aggregate(
            total=Sum('quantity')
        )['total'] or 0
        avg_food_per_day = round(total_food_saved / 30, 2) if total_food_saved else 0

        total_requests = DonationRequest.objects.count()
        accepted_requests = DonationRequest.objects.filter(status='accepted').count()
        acceptance_rate = round((accepted_requests / total_requests * 100) if total_requests else 0, 1)

        total_pickups = Pickup.objects.count()
        delivered_pickups = Pickup.objects.filter(status='delivered').count()
        pickup_rate = round((delivered_pickups / total_pickups * 100) if total_pickups else 0, 1)

        # Avg pickup delay (scheduled vs actual)
        completed_pickups = Pickup.objects.filter(status='delivered', actual_pickup_time__isnull=False)
        total_delay = 0
        count_delay = 0
        for p in completed_pickups:
            delay = (p.actual_pickup_time - p.scheduled_time).total_seconds() / 3600
            total_delay += delay
            count_delay += 1
        avg_delay = round(total_delay / count_delay, 1) if count_delay else 0

        # Active users (30 days)
        active_donors_count = Donor.objects.filter(
            donations__created_at__gte=thirty_days_ago
        ).distinct().count()
        active_receivers_count = Receiver.objects.filter(
            donation_requests__requested_at__gte=thirty_days_ago
        ).distinct().count()

        # City hotspots
        city_hotspots = (
            Donation.objects.values('donor__city')
            .annotate(count=Count('donation_id'))
            .order_by('-count')[:10]
        )

        # Donations per day (last 30 days) – for chart
        daily_donations = list(
            Donation.objects.filter(created_at__gte=thirty_days_ago)
            .annotate(day=TruncDay('created_at'))
            .values('day')
            .annotate(count=Count('donation_id'))
            .order_by('day')
        )
        chart_labels = [str(d['day'].strftime('%d %b')) for d in daily_donations]
        chart_data = [d['count'] for d in daily_donations]

        # Status breakdown for doughnut chart
        status_counts = {
            'active': Donation.objects.filter(status='active').count(),
            'requested': Donation.objects.filter(status='requested').count(),
            'completed': Donation.objects.filter(status='completed').count(),
            'expired': Donation.objects.filter(status='expired').count(),
        }

        # Food type breakdown
        food_types = (
            Donation.objects.exclude(food_type='')
            .values('food_type')
            .annotate(count=Count('donation_id'))
            .order_by('-count')[:6]
        )

        # Recent pickups
        recent_pickups = Pickup.objects.select_related(
            'donation_request__donation__donor',
            'donation_request__receiver'
        ).order_by('-created_at')[:10]

        context.update({
            'total_donations': total_donations,
            'completed_donations': completed_donations,
            'total_food_saved': round(total_food_saved, 1),
            'avg_food_per_day': avg_food_per_day,
            'total_requests': total_requests,
            'accepted_requests': accepted_requests,
            'acceptance_rate': acceptance_rate,
            'total_pickups': total_pickups,
            'delivered_pickups': delivered_pickups,
            'pickup_rate': pickup_rate,
            'avg_delay': avg_delay,
            'active_donors_count': active_donors_count,
            'active_receivers_count': active_receivers_count,
            'city_hotspots': city_hotspots,
            'chart_labels': chart_labels,
            'chart_data': chart_data,
            'status_counts': status_counts,
            'food_types': food_types,
            'recent_pickups': recent_pickups,
            'total_donors': Donor.objects.count(),
            'total_receivers': Receiver.objects.count(),
        })
    except Exception as e:
        messages.warning(request, f'Analytics partially unavailable: {e}')

    return render(request, 'admin/analytics.html', context)


@admin_required
def admin_donations(request):
    """Manage all donations"""
    admin_obj = Admin.objects.get(admin_id=request.session.get('admin_id'))
    context = {'admin': admin_obj, 'donations': []}

    try:
        from donations.models import Donation
        donations = Donation.objects.select_related('donor').order_by('-created_at')
        status_filter = request.GET.get('status', '')
        if status_filter:
            donations = donations.filter(status=status_filter)
        context['donations'] = donations
        context['status_filter'] = status_filter
    except Exception:
        pass

    return render(request, 'admin/donations.html', context)


@admin_required
def admin_pickups(request):
    """Manage all pickups"""
    admin_obj = Admin.objects.get(admin_id=request.session.get('admin_id'))
    context = {'admin': admin_obj, 'pickups': []}

    try:
        from donations.models import Pickup
        pickups = Pickup.objects.select_related(
            'donation_request__donation__donor',
            'donation_request__receiver'
        ).order_by('-created_at')
        context['pickups'] = pickups
    except Exception:
        pass

    return render(request, 'admin/pickups.html', context)


@admin_required
def admin_mark_pickup_delivered(request, pickup_id):
    """Mark a pickup as delivered from admin panel"""
    admin_obj = Admin.objects.get(admin_id=request.session.get('admin_id'))
    try:
        from donations.models import Pickup
        pickup = Pickup.objects.get(pickup_id=pickup_id)
        pickup.status = 'delivered'
        pickup.actual_pickup_time = timezone.now()
        pickup.save()
        pickup.donation_request.donation.status = 'completed'
        pickup.donation_request.donation.save()

        AdminActivityLog.objects.create(
            admin=admin_obj,
            action='MARK_PICKUP_DELIVERED',
            details=f'Marked pickup #{pickup_id} as delivered',
            ip_address=request.META.get('REMOTE_ADDR')
        )
        messages.success(request, f'✅ Pickup #{pickup_id} marked as delivered.')
    except Exception as e:
        messages.error(request, f'Error: {e}')
    return redirect('/panel/pickups/')


@admin_required
def admin_export_donations(request):
    """Export donations as CSV"""
    try:
        from donations.models import Donation
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="annadaan_donations.csv"'

        writer = csv.writer(response)
        writer.writerow(['ID', 'Title', 'Donor', 'Quantity (kg)', 'Status', 'Food Type', 'Expiry', 'Created'])
        for d in Donation.objects.select_related('donor').all():
            writer.writerow([
                d.donation_id, d.title, d.donor.name, d.quantity,
                d.status, d.food_type, d.expiry_date.strftime('%Y-%m-%d %H:%M'),
                d.created_at.strftime('%Y-%m-%d %H:%M')
            ])
        return response
    except Exception as e:
        messages.error(request, f'Export failed: {e}')
        return redirect('/panel/analytics/')


@admin_required
def admin_export_users(request):
    """Export users as CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="annadaan_users.csv"'

    writer = csv.writer(response)
    writer.writerow(['Type', 'Name', 'Email', 'City', 'State', 'Verified', 'Joined'])
    for d in Donor.objects.all():
        writer.writerow(['Donor', d.name, d.email, d.city, d.state, d.is_verified, d.created_at.strftime('%Y-%m-%d')])
    for r in Receiver.objects.all():
        writer.writerow(['Receiver/NGO', r.name, r.email, r.city, r.state, r.is_verified, r.created_at.strftime('%Y-%m-%d')])

    return response


def admin_logout(request):
    """Admin logout"""
    admin_id = request.session.get('admin_id')
    try:
        admin = Admin.objects.get(admin_id=admin_id)
        AdminActivityLog.objects.create(
            admin=admin,
            action='LOGOUT',
            details=f'Admin {admin.username} logged out',
            ip_address=request.META.get('REMOTE_ADDR')
        )
    except Exception:
        pass
    request.session.flush()
    messages.info(request, 'You have been logged out')
    return redirect('/panel/')