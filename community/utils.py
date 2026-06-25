from django.contrib import messages
from django.shortcuts import redirect


def get_user_role(user):
    if user.is_superuser:
        return 'super_admin'
    profile = getattr(user, 'profile', None)
    return profile.role if profile else 'member'


def staff_or_admin_check(user):
    if user.is_staff or user.is_superuser:
        return True
    role = get_user_role(user)
    return role in ['super_admin', 'admin', 'organizer', 'mentor', 'moderator']


def profile_required(view_func):
    from functools import wraps
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            if not hasattr(request.user, 'profile'):
                from .models import Profile
                Profile.objects.get_or_create(user=request.user)
        return view_func(request, *args, **kwargs)
    return wrapper
