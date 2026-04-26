"""Admin configuration for the luxury car showroom."""

from django.contrib import admin

from .models import Booking, Brand, Car, CarImage, ContactInquiry, Wishlist


class CarImageInline(admin.TabularInline):
    model = CarImage
    extra = 1
    fields = ("image", "alt_text", "sort_order", "is_primary")


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "brand",
        "price",
        "model_year",
        "fuel_type",
        "transmission",
        "is_featured",
        "date_added",
    )
    list_filter = ("brand", "fuel_type", "transmission", "model_year", "is_featured")
    search_fields = ("name", "brand__name", "description", "engine")
    readonly_fields = ("slug", "date_added")
    list_select_related = ("brand",)
    list_per_page = 25
    inlines = [CarImageInline]

    fieldsets = (
        ("Basic Information", {"fields": ("brand", "name", "slug", "price", "is_featured")}),
        (
            "Specifications",
            {
                "fields": (
                    "fuel_type",
                    "transmission",
                    "model_year",
                    "mileage",
                    "engine",
                    "horsepower",
                    "top_speed",
                    "seating_capacity",
                )
            },
        ),
        ("Description", {"fields": ("description",)}),
        ("Metadata", {"fields": ("date_added",)}),
    )


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("user", "car", "preferred_date", "status", "created_at")
    list_filter = ("status", "preferred_date", "car__brand")
    search_fields = ("user__username", "user__email", "car__name", "car__brand__name")
    list_select_related = ("user", "car", "car__brand")
    actions = ("mark_approved", "mark_rejected")

    @admin.action(description="Mark selected bookings as approved")
    def mark_approved(self, request, queryset):
        queryset.update(status=Booking.STATUS_APPROVED)

    @admin.action(description="Mark selected bookings as rejected")
    def mark_rejected(self, request, queryset):
        queryset.update(status=Booking.STATUS_REJECTED)


@admin.register(ContactInquiry)
class ContactInquiryAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone", "car", "subject", "is_resolved", "created_at")
    list_filter = ("is_resolved", "created_at", "car__brand")
    search_fields = ("name", "email", "phone", "subject", "message", "car__name")
    list_select_related = ("car", "car__brand")


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ("user", "car", "created_at")
    search_fields = ("user__username", "car__name", "car__brand__name")
    list_select_related = ("user", "car", "car__brand")


admin.site.site_header = "Luxury Car Showroom Admin"
admin.site.site_title = "Luxury Car Showroom"
admin.site.index_title = "Premium inventory management"
