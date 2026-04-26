"""Domain models for the luxury car showroom."""

from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator, MinValueValidator
from django.db import models
from django.templatetags.static import static
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify


ALLOWED_IMAGE_EXTENSIONS = ["jpg", "jpeg", "png", "webp", "avif"]
MAX_IMAGE_SIZE_MB = 5


def validate_image_size(image):
    """Keep uploads reasonably sized for better storage and delivery."""
    if image and image.size > MAX_IMAGE_SIZE_MB * 1024 * 1024:
        raise ValidationError(
            f"Image size must be under {MAX_IMAGE_SIZE_MB} MB for fast performance."
        )


class Brand(models.Model):
    """Luxury car brand metadata."""

    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True)
    logo = models.ImageField(
        upload_to="brands/",
        blank=True,
        validators=[
            FileExtensionValidator(ALLOWED_IMAGE_EXTENSIONS),
            validate_image_size,
        ],
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._build_unique_slug()
        super().save(*args, **kwargs)

    def _build_unique_slug(self):
        base_slug = slugify(self.name) or "brand"
        slug = base_slug
        counter = 2
        while Brand.objects.exclude(pk=self.pk).filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        return slug


class Car(models.Model):
    """Represents a showroom vehicle with production-friendly metadata."""

    FUEL_CHOICES = [
        ("Petrol", "Petrol"),
        ("Diesel", "Diesel"),
        ("Electric", "Electric"),
        ("Hybrid", "Hybrid"),
    ]

    TRANSMISSION_CHOICES = [
        ("Automatic", "Automatic"),
        ("Manual", "Manual"),
    ]

    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name="cars")
    name = models.CharField(max_length=200, help_text="Car model name")
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
        help_text="Price in INR",
    )
    fuel_type = models.CharField(max_length=20, choices=FUEL_CHOICES, default="Petrol")
    transmission = models.CharField(
        max_length=20,
        choices=TRANSMISSION_CHOICES,
        default="Automatic",
    )
    model_year = models.PositiveIntegerField(help_text="Manufacturing year")
    mileage = models.CharField(max_length=50, help_text="Mileage (e.g. 15 km/l)")
    engine = models.CharField(max_length=120, blank=True)
    horsepower = models.PositiveIntegerField(blank=True, null=True)
    top_speed = models.PositiveIntegerField(blank=True, null=True, help_text="km/h")
    seating_capacity = models.PositiveSmallIntegerField(blank=True, null=True)
    description = models.TextField(help_text="Detailed description of the car")
    is_featured = models.BooleanField(default=False)
    date_added = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-date_added"]
        verbose_name = "Luxury Car"
        verbose_name_plural = "Luxury Cars"

    def __str__(self):
        return f"{self.brand.name} {self.name} ({self.model_year})"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._build_unique_slug()
        super().save(*args, **kwargs)

    def _build_unique_slug(self):
        brand_name = self.brand.name if self.brand_id else "car"
        base_slug = slugify(f"{brand_name}-{self.name}") or "car"
        slug = base_slug
        counter = 2
        while Car.objects.exclude(pk=self.pk).filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        return slug

    @property
    def gallery(self):
        cached_images = (
            self._prefetched_objects_cache.get("images")
            if hasattr(self, "_prefetched_objects_cache")
            else None
        )
        if cached_images is not None:
            return sorted(
                cached_images,
                key=lambda image: (0 if image.is_primary else 1, image.sort_order, image.pk),
            )
        return list(self.images.order_by("-is_primary", "sort_order", "pk"))

    @property
    def primary_gallery_image(self):
        images = self.gallery
        return images[0] if images else None

    @property
    def primary_image(self):
        primary = self.primary_gallery_image
        return primary.image if primary else None

    @property
    def primary_image_url(self):
        primary = self.primary_image
        return primary.url if primary else static("car/img/car-placeholder.svg")

    def get_absolute_url(self):
        return reverse("car:car_detail", kwargs={"slug": self.slug})


class CarImage(models.Model):
    """Unlimited gallery images for a car."""

    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(
        upload_to="cars/",
        validators=[
            FileExtensionValidator(ALLOWED_IMAGE_EXTENSIONS),
            validate_image_size,
        ],
    )
    alt_text = models.CharField(max_length=200, blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_primary = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-is_primary", "sort_order", "pk"]

    def __str__(self):
        return f"{self.car} - Image {self.pk}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.is_primary:
            self.car.images.exclude(pk=self.pk).filter(is_primary=True).update(is_primary=False)


class Wishlist(models.Model):
    """Cars saved by a user."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wishlist_items",
    )
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="wishlisted_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("user", "car")

    def __str__(self):
        return f"{self.user} -> {self.car}"


class Booking(models.Model):
    """Test drive bookings managed by admins."""

    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_REJECTED = "rejected"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_REJECTED, "Rejected"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bookings",
    )
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="bookings")
    preferred_date = models.DateField()
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("user", "car", "preferred_date")

    def __str__(self):
        return f"{self.user} - {self.car} on {self.preferred_date}"

    def clean(self):
        super().clean()
        if self.preferred_date and self.preferred_date < timezone.localdate():
            raise ValidationError({"preferred_date": "Please choose a future date for the test drive."})


class ContactInquiry(models.Model):
    """Dealer contact requests saved from forms."""

    name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    car = models.ForeignKey(
        Car,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="dealer_inquiries",
    )
    subject = models.CharField(max_length=160, blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Contact Inquiry"
        verbose_name_plural = "Contact Inquiries"

    def __str__(self):
        return f"{self.name} - {self.subject or 'General enquiry'}"
