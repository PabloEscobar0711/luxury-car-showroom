"""Template context shared across the showroom."""

from .models import Wishlist


def showroom_context(request):
    wishlist_count = 0
    if request.user.is_authenticated:
        wishlist_count = Wishlist.objects.filter(user=request.user).count()

    return {
        "wishlist_count": wishlist_count,
    }
