from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from functools import wraps


def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            from django.shortcuts import redirect
            return redirect('login')
        if request.user.is_superuser or request.user.is_staff:
            return view_func(request, *args, **kwargs)
        profile = getattr(request.user, 'profile', None)
        if profile and profile.role in ['super_admin', 'admin']:
            return view_func(request, *args, **kwargs)
        raise PermissionDenied
    return _wrapped_view


def organizer_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            from django.shortcuts import redirect
            return redirect('login')
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        profile = getattr(request.user, 'profile', None)
        if profile and profile.role in ['super_admin', 'admin', 'organizer']:
            return view_func(request, *args, **kwargs)
        raise PermissionDenied
    return _wrapped_view


def mentor_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            from django.shortcuts import redirect
            return redirect('login')
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        profile = getattr(request.user, 'profile', None)
        if profile and profile.role in ['super_admin', 'admin', 'mentor']:
            return view_func(request, *args, **kwargs)
        raise PermissionDenied
    return _wrapped_view


def moderator_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            from django.shortcuts import redirect
            return redirect('login')
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        profile = getattr(request.user, 'profile', None)
        if profile and profile.role in ['super_admin', 'admin', 'moderator']:
            return view_func(request, *args, **kwargs)
        raise PermissionDenied
    return _wrapped_view


def staff_or_admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            from django.shortcuts import redirect
            return redirect('login')
        if request.user.is_staff or request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        profile = getattr(request.user, 'profile', None)
        if profile and profile.role in ['super_admin', 'admin', 'organizer', 'mentor', 'moderator']:
            return view_func(request, *args, **kwargs)
        raise PermissionDenied
    return _wrapped_view
