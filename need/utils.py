from django.shortcuts import redirect
from functools import wraps
from appuser.models import AppUser

def permission_required(permission):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('/user/login')  # Giriş yapmamış kullanıcılar için
            try:
                permissions = AppUser.objects.get(user=request.user).all_values()['permissions']
                if permission in permissions:
                    return view_func(request, *args, **kwargs)
            except AttributeError:
                pass
            return redirect('/unauthorized')  # Yetkisi olmayanlar için
        return wrapper
    return decorator
