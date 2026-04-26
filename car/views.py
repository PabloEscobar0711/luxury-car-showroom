"""Views for the premium luxury car showroom."""

from urllib.parse import urlencode

from django import forms
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.core.paginator import Paginator
from django.db.models import Count, Prefetch, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.views.decorators.http import require_POST

from .forms import (
    CarFilterForm,
    ContactDealerForm,
    ShowroomAuthenticationForm,
    SignUpForm,
    TestDriveBookingForm,
)
from .models import Booking, Brand, Car, CarImage, Wishlist


CATALOG_PAGE_SIZE = 6


def _car_queryset():
    return (
        Car.objects.select_related("brand")
        .prefetch_related(
            Prefetch("images", queryset=CarImage.objects.order_by("-is_primary", "sort_order", "pk"))
        )
        .order_by("-is_featured", "-date_added")
    )


def _wishlist_ids(user, cars):
    if not user.is_authenticated or not cars:
        return set()
    car_ids = [car.pk for car in cars]
    return set(
        Wishlist.objects.filter(user=user, car_id__in=car_ids).values_list("car_id", flat=True)
    )


def _filter_cars(queryset, form):
    if not form.is_valid():
        return queryset

    filters = form.cleaned_data
    search_query = (filters.get("q") or "").strip()
    if search_query:
        queryset = queryset.filter(
            Q(name__icontains=search_query) | Q(brand__name__icontains=search_query)
        )

    if filters.get("brand"):
        queryset = queryset.filter(brand=filters["brand"])

    if filters.get("fuel_type"):
        queryset = queryset.filter(fuel_type=filters["fuel_type"])

    if filters.get("min_price") is not None:
        queryset = queryset.filter(price__gte=filters["min_price"])

    if filters.get("max_price") is not None:
        queryset = queryset.filter(price__lte=filters["max_price"])

    return queryset


def _prefilled_contact_initial(request, car=None):
    initial = {}
    if request.user.is_authenticated:
        initial["name"] = request.user.get_full_name() or request.user.username
        initial["email"] = request.user.email
    if car:
        initial["car"] = car
        initial["subject"] = f"Interested in {car.brand.name} {car.name}"
    return initial


class ShowroomLoginView(LoginView):
    template_name = "car/auth/login.html"
    authentication_form = ShowroomAuthenticationForm
    redirect_authenticated_user = True

    def get_success_url(self):
        return self.get_redirect_url() or reverse_lazy("car:home")


class ShowroomLogoutView(LogoutView):
    next_page = reverse_lazy("car:home")


def signup_view(request):
    form = SignUpForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Your account is ready. Welcome to the showroom.")
        return redirect("car:home")

    return render(request, "car/auth/signup.html", {"form": form})


def home(request):
    featured_cars = list(_car_queryset().filter(is_featured=True)[:6])
    if len(featured_cars) < 6:
        featured_cars = list(_car_queryset()[:6])

    wishlist_ids = _wishlist_ids(request.user, featured_cars)
    brand_stats = Brand.objects.annotate(car_count=Count("cars")).order_by("-car_count", "name")[:5]

    context = {
        "featured_cars": featured_cars,
        "wishlist_ids": wishlist_ids,
        "brand_stats": brand_stats,
        "inventory_count": Car.objects.count(),
        "brand_count": Brand.objects.count(),
        "pending_bookings": Booking.objects.filter(status=Booking.STATUS_PENDING).count(),
        "hero_car": featured_cars[0] if featured_cars else None,
    }
    return render(request, "car/home.html", context)


def car_list(request):
    brand_queryset = Brand.objects.order_by("name")
    filter_form = CarFilterForm(request.GET or None, brand_queryset=brand_queryset)
    queryset = _filter_cars(_car_queryset(), filter_form)

    paginator = Paginator(queryset, CATALOG_PAGE_SIZE)
    page_obj = paginator.get_page(request.GET.get("page", 1))
    cars = list(page_obj.object_list)
    wishlist_ids = _wishlist_ids(request.user, cars)

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        html = render_to_string(
            "car/partials/car_cards.html",
            {
                "cars": cars,
                "wishlist_ids": wishlist_ids,
            },
            request=request,
        )
        return JsonResponse(
            {
                "html": html,
                "has_next": page_obj.has_next(),
                "next_page": page_obj.next_page_number() if page_obj.has_next() else None,
                "count": paginator.count,
                "page": page_obj.number,
            }
        )

    context = {
        "filter_form": filter_form,
        "page_obj": page_obj,
        "total_count": paginator.count,
        "wishlist_ids": wishlist_ids,
    }
    return render(request, "car/car_list.html", context)


def car_detail(request, slug):
    car = get_object_or_404(_car_queryset(), slug=slug)
    related_cars = list(_car_queryset().filter(brand=car.brand).exclude(pk=car.pk)[:3])

    booking_form = TestDriveBookingForm(prefix="booking")
    contact_form = ContactDealerForm(prefix="contact", initial=_prefilled_contact_initial(request, car))
    contact_form.fields["car"].widget = forms.HiddenInput()

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "booking":
            if not request.user.is_authenticated:
                login_url = f"{reverse('car:login')}?{urlencode({'next': request.path})}"
                messages.info(request, "Please log in to request a test drive.")
                return redirect(login_url)

            booking_form = TestDriveBookingForm(request.POST, prefix="booking")
            if booking_form.is_valid():
                booking = booking_form.save(commit=False)
                booking.user = request.user
                booking.car = car
                booking.save()
                messages.success(request, "Your test drive request has been submitted.")
                return redirect(f"{car.get_absolute_url()}#booking-panel")
        elif action == "contact":
            contact_form = ContactDealerForm(request.POST, prefix="contact")
            contact_form.fields["car"].widget = forms.HiddenInput()
            if contact_form.is_valid():
                inquiry = contact_form.save(commit=False)
                inquiry.car = inquiry.car or car
                inquiry.save()
                messages.success(request, "Your message was sent to the dealer team.")
                return redirect(f"{car.get_absolute_url()}#contact-panel")

    context = {
        "car": car,
        "related_cars": related_cars,
        "booking_form": booking_form,
        "contact_form": contact_form,
        "is_wishlisted": request.user.is_authenticated
        and Wishlist.objects.filter(user=request.user, car=car).exists(),
        "wishlist_ids": _wishlist_ids(request.user, related_cars),
    }
    return render(request, "car/car_detail.html", context)


def legacy_car_detail_redirect(request, pk):
    car = get_object_or_404(Car, pk=pk)
    return redirect("car:car_detail", slug=car.slug)


def compare_cars(request):
    selected_ids = request.GET.getlist("cars")
    if len(selected_ids) == 1 and "," in selected_ids[0]:
        selected_ids = [car_id for car_id in selected_ids[0].split(",") if car_id]

    selected_ids = selected_ids[:3]
    if len(selected_ids) < 2:
        messages.warning(request, "Select at least two cars to compare.")
        return redirect("car:car_list")

    cars = {
        str(car.pk): car
        for car in _car_queryset().filter(pk__in=selected_ids)
    }
    ordered_cars = [cars[car_id] for car_id in selected_ids if car_id in cars][:3]

    if len(ordered_cars) < 2:
        messages.warning(request, "The selected comparison set is incomplete.")
        return redirect("car:car_list")

    return render(request, "car/compare.html", {"cars": ordered_cars})


@login_required
def wishlist_view(request):
    wishlist_items = (
        Wishlist.objects.filter(user=request.user)
        .select_related("car", "car__brand")
        .prefetch_related(
            Prefetch("car__images", queryset=CarImage.objects.order_by("-is_primary", "sort_order", "pk"))
        )
    )
    return render(request, "car/wishlist.html", {"wishlist_items": wishlist_items})


@login_required
def my_bookings(request):
    bookings = (
        Booking.objects.filter(user=request.user)
        .select_related("car", "car__brand")
        .prefetch_related(
            Prefetch("car__images", queryset=CarImage.objects.order_by("-is_primary", "sort_order", "pk"))
        )
    )
    return render(request, "car/bookings.html", {"bookings": bookings})


@login_required
@require_POST
def toggle_wishlist(request, slug):
    car = get_object_or_404(Car, slug=slug)
    wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, car=car)

    if created:
        wishlisted = True
        message = f"{car.brand.name} {car.name} was added to your wishlist."
    else:
        wishlist_item.delete()
        wishlisted = False
        message = f"{car.brand.name} {car.name} was removed from your wishlist."

    count = Wishlist.objects.filter(user=request.user).count()
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"wishlisted": wishlisted, "message": message, "count": count})

    messages.success(request, message)
    return redirect(request.POST.get("next") or car.get_absolute_url())


def contact(request):
    form = ContactDealerForm(request.POST or None, initial=_prefilled_contact_initial(request))
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Thanks for reaching out. Our concierge team will contact you shortly.")
        return redirect("car:contact")

    return render(request, "car/contact.html", {"form": form})


def about(request):
    brands = Brand.objects.annotate(car_count=Count("cars")).order_by("name")
    return render(request, "car/about.html", {"brands": brands})
