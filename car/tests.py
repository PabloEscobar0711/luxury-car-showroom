from datetime import timedelta

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Booking, Brand, Car, Wishlist


class ShowroomViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="tester", password="securepass123")
        self.brand = Brand.objects.create(name="BMW", slug="bmw")
        self.car_one = Car.objects.create(
            brand=self.brand,
            name="7 Series",
            slug="bmw-7-series",
            price="19500000",
            fuel_type="Hybrid",
            transmission="Automatic",
            model_year=2025,
            mileage="12 km/l",
            description="Flagship sedan.",
            is_featured=True,
        )
        self.car_two = Car.objects.create(
            brand=self.brand,
            name="i7",
            slug="bmw-i7",
            price="21500000",
            fuel_type="Electric",
            transmission="Automatic",
            model_year=2025,
            mileage="625 km range",
            description="Electric flagship sedan.",
        )

    def test_catalog_ajax_returns_json(self):
        response = self.client.get(
            reverse("car:car_list"),
            {"q": "BMW"},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("html", response.json())
        self.assertEqual(response.json()["count"], 2)

    def test_wishlist_requires_login(self):
        response = self.client.post(reverse("car:toggle_wishlist", args=[self.car_one.slug]))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("car:login"), response.url)

    def test_authenticated_user_can_toggle_wishlist(self):
        self.client.login(username="tester", password="securepass123")
        response = self.client.post(
            reverse("car:toggle_wishlist", args=[self.car_one.slug]),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Wishlist.objects.filter(user=self.user, car=self.car_one).exists())
        self.assertTrue(response.json()["wishlisted"])

    def test_booking_can_be_submitted_from_detail_page(self):
        self.client.login(username="tester", password="securepass123")
        response = self.client.post(
            reverse("car:car_detail", args=[self.car_one.slug]),
            {
                "action": "booking",
                "booking-preferred_date": timezone.localdate() + timedelta(days=1),
                "booking-notes": "Morning slot, please.",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Booking.objects.filter(user=self.user, car=self.car_one).exists())

    def test_compare_requires_two_cars(self):
        response = self.client.get(reverse("car:compare"), {"cars": [self.car_one.pk]})
        self.assertEqual(response.status_code, 302)
