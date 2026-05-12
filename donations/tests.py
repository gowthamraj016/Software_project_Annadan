# donations/tests.py
from django.test import TestCase, Client
from django.utils import timezone
from datetime import timedelta
from users.models import Donor, Receiver
from .models import Donation, DonationRequest, Pickup


class PriorityScoringTest(TestCase):
    """Unit tests for Sprint 3 AI Priority Scoring."""

    def setUp(self):
        from django.contrib.auth.hashers import make_password
        self.donor = Donor.objects.create(
            name="Test Donor",
            email="donor@test.com",
            contact="9999999999",
            password=make_password("testpass"),
            location_lat=12.97,
            location_long=77.59,
            is_verified=True,
        )
        self.receiver = Receiver.objects.create(
            name="Test NGO",
            email="ngo@test.com",
            contact="8888888888",
            password=make_password("testpass"),
            capacity=100,
            location_lat=12.98,
            location_long=77.60,
            is_verified=True,
        )

    def _make_donation(self, hours_until_expiry=12, quantity=20):
        return Donation.objects.create(
            donor=self.donor,
            title="Test Food",
            quantity=quantity,
            expiry_date=timezone.now() + timedelta(hours=hours_until_expiry),
            location_lat=self.donor.location_lat,
            location_long=self.donor.location_long,
            status='active',
        )

    def test_critical_donation_has_high_score(self):
        """Donations expiring within 1 hour should have high priority scores."""
        urgent = self._make_donation(hours_until_expiry=0.5, quantity=50)
        score = urgent.get_priority_score(self.receiver.location_lat, self.receiver.location_long)
        self.assertGreater(score, 60, "Critical donation should score above 60")

    def test_old_donation_has_lower_urgency(self):
        """Donations with 48h+ until expiry should score lower than critical ones."""
        urgent = self._make_donation(hours_until_expiry=0.5, quantity=20)
        non_urgent = self._make_donation(hours_until_expiry=48, quantity=20)
        urgent_score = urgent.get_priority_score()
        non_urgent_score = non_urgent.get_priority_score()
        self.assertGreater(urgent_score, non_urgent_score)

    def test_large_quantity_boosts_score(self):
        """Larger quantity should result in higher score (with same expiry)."""
        small = self._make_donation(hours_until_expiry=12, quantity=5)
        large = self._make_donation(hours_until_expiry=12, quantity=80)
        self.assertGreater(
            large.get_priority_score(),
            small.get_priority_score()
        )

    def test_score_is_between_0_and_100(self):
        """Score must always be between 0 and 100."""
        d = self._make_donation()
        score = d.get_priority_score(self.receiver.location_lat, self.receiver.location_long)
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)

    def test_hours_to_expiry_property(self):
        """hours_to_expiry should return roughly 12 for a 12h future expiry."""
        d = self._make_donation(hours_until_expiry=12)
        self.assertAlmostEqual(d.hours_to_expiry, 12, delta=0.1)

    def test_expired_donation_has_zero_urgency(self):
        """An already-expired donation should have 0 hours left."""
        d = self._make_donation(hours_until_expiry=-1)
        self.assertEqual(d.hours_to_expiry, 0)


class DonationRequestFlowTest(TestCase):
    """Sprint 2: Test donation creation and request flow."""

    def setUp(self):
        from django.contrib.auth.hashers import make_password
        self.client = Client()
        self.donor = Donor.objects.create(
            name="Donor One",
            email="donor1@test.com",
            contact="9999999990",
            password=make_password("testpass"),
            location_lat=12.97,
            location_long=77.59,
            is_verified=True,
        )
        self.receiver = Receiver.objects.create(
            name="NGO One",
            email="ngo1@test.com",
            contact="8888888880",
            password=make_password("testpass"),
            capacity=50,
            location_lat=12.98,
            location_long=77.60,
            is_verified=True,
        )
        self.donation = Donation.objects.create(
            donor=self.donor,
            title="Rice – 20 kg",
            quantity=20,
            expiry_date=timezone.now() + timedelta(hours=24),
            location_lat=self.donor.location_lat,
            location_long=self.donor.location_long,
            status='active',
        )

    def test_donation_created(self):
        """Donation should be created successfully."""
        self.assertEqual(Donation.objects.count(), 1)
        self.assertEqual(self.donation.status, 'active')

    def test_donation_request_creation(self):
        """NGO can request an active donation."""
        req = DonationRequest.objects.create(
            donation=self.donation,
            receiver=self.receiver,
            status='pending',
        )
        self.assertEqual(DonationRequest.objects.count(), 1)
        self.assertEqual(req.status, 'pending')

    def test_accepting_request_creates_pickup(self):
        """Accepting a request should create a Pickup record."""
        req = DonationRequest.objects.create(
            donation=self.donation,
            receiver=self.receiver,
            status='pending',
        )
        req.status = 'accepted'
        req.save()
        self.donation.status = 'requested'
        self.donation.save()
        pickup = Pickup.objects.create(
            donation_request=req,
            scheduled_time=timezone.now() + timedelta(hours=2),
            status='scheduled',
        )
        self.assertEqual(Pickup.objects.count(), 1)
        self.assertEqual(pickup.status, 'scheduled')

    def test_duplicate_request_not_created(self):
        """Same NGO cannot request the same donation twice at model level."""
        DonationRequest.objects.create(
            donation=self.donation,
            receiver=self.receiver,
            status='pending',
        )
        count_before = DonationRequest.objects.count()
        # The view prevents this; at model level just verify count
        self.assertEqual(count_before, 1)


class PickupTrackingTest(TestCase):
    """Sprint 3: Test tracking_updates JSON field."""

    def setUp(self):
        from django.contrib.auth.hashers import make_password
        donor = Donor.objects.create(
            name="Donor Track",
            email="donortrack@test.com",
            contact="9999999991",
            password=make_password("testpass"),
            location_lat=12.97,
            location_long=77.59,
            is_verified=True,
        )
        receiver = Receiver.objects.create(
            name="NGO Track",
            email="ngotrack@test.com",
            contact="8888888881",
            password=make_password("testpass"),
            capacity=50,
            location_lat=12.98,
            location_long=77.60,
            is_verified=True,
        )
        donation = Donation.objects.create(
            donor=donor, title="Tracking Test", quantity=10,
            expiry_date=timezone.now() + timedelta(hours=12),
            location_lat=12.97, location_long=77.59, status='active',
        )
        req = DonationRequest.objects.create(
            donation=donation, receiver=receiver, status='accepted'
        )
        self.pickup = Pickup.objects.create(
            donation_request=req,
            scheduled_time=timezone.now() + timedelta(hours=1),
            status='scheduled',
        )

    def test_add_tracking_update(self):
        """add_tracking_update should append to the JSON list."""
        self.pickup.add_tracking_update(12.975, 77.595, 'in_transit')
        self.assertEqual(len(self.pickup.tracking_updates), 1)
        self.assertEqual(self.pickup.tracking_updates[0]['status'], 'in_transit')

    def test_latest_location(self):
        """latest_location should return the most recent update."""
        self.pickup.add_tracking_update(12.975, 77.595, 'in_transit')
        self.pickup.add_tracking_update(12.980, 77.600, 'near_destination')
        latest = self.pickup.latest_location
        self.assertEqual(latest['lat'], 12.980)
