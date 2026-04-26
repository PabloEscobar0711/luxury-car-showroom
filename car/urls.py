"""URL patterns for the premium showroom app."""

from django.urls import path

from . import views


app_name = "car"


urlpatterns = [
    path("", views.home, name="home"),
    path("cars/", views.car_list, name="car_list"),
    path("cars/compare/", views.compare_cars, name="compare"),
    path("cars/<slug:slug>/", views.car_detail, name="car_detail"),
    path("car/<int:pk>/", views.legacy_car_detail_redirect, name="legacy_car_detail"),
    path("wishlist/", views.wishlist_view, name="wishlist"),
    path("wishlist/<slug:slug>/toggle/", views.toggle_wishlist, name="toggle_wishlist"),
    path("bookings/", views.my_bookings, name="my_bookings"),
    path("signup/", views.signup_view, name="signup"),
    path("login/", views.ShowroomLoginView.as_view(), name="login"),
    path("logout/", views.ShowroomLogoutView.as_view(), name="logout"),
    path("contact/", views.contact, name="contact"),
    path("about/", views.about, name="about"),
]
