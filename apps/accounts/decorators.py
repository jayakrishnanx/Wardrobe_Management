from django.shortcuts import redirect
from functools import wraps


def role_required(required_role):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('user_login')

            if request.user.role != required_role:
                return redirect('user_login')

            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
