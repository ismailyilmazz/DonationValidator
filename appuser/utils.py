from .models import AppUser
from django.shortcuts import redirect
from functools import wraps
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.template.defaultfilters import slugify


def anyhave(a,b):
    for per in b:
        if per in a:
            return True
    return False



def add_control(tel):
    if AppUser.objects.filter(tel=tel).exists():
        raise ValidationError('Telefon numarası zaten kayıtlı. Lütfen giriş yapınız.')

def create_username(firstname):
    username = slugify(firstname)
    counter = 0
    while User.objects.filter(username = username+str(counter)).exists():
        counter +=1
    return username+str(counter)

def permission_required_any(*perms):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('/user/login') 
            try:
                permissions = AppUser.objects.get(user=request.user).all_values()['permissions']
                if anyhave(permissions,perms):
                    return view_func(request, *args, **kwargs)
            except AttributeError:
                pass
            return redirect('/unauthorized')
        return wrapper
    return decorator
