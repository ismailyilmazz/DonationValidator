from .models import AppUser
from django.shortcuts import redirect
from functools import wraps

def anyhave(a,b):
    for per in b:
        if per in a:
            return True
    return False


def permission_required_any(*perms):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('/user/login')  # Giriş yapmamış kullanıcılar için
            try:
                permissions = AppUser.objects.get(user=request.user).all_values()['permissions']
                if anyhave(permissions,perms):
                    return view_func(request, *args, **kwargs)
            except AttributeError:
                pass
            return redirect('/unauthorized')  # Yetkisi olmayanlar için
        return wrapper
    return decorator
