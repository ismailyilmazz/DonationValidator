from django.shortcuts import render,redirect
from .forms import RegisterForm, LoginForm, ProfileForm
from django.contrib.auth import login,logout
from .models import AppUser
from need.models import Need
from need.views import get_month_name
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

# Create your views here.

def logout_view(request):
    logout(request)
    return redirect('/user/login/')

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/user/login')
    else:
        form = RegisterForm()
    return render(request,'user/register.html',{'form':form})

def login_view(request):
    if not request.user.is_authenticated:
        if request.method == 'POST':
            form = LoginForm(request.POST)
            if form.is_valid():
                user = form.loginControl()
                if user != None:
                    login(request,user)
                    return redirect('/user/profile/')
                else:
                    return redirect('/user/profile/')
        else:
            form = LoginForm()
        return render(request,'user/login.html',{'form':form})
    return redirect('/user/profile/')

def profile_view(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = ProfileForm(request.POST,user=request.user)
            appuser = AppUser.objects.get(user=request.user)
            user = appuser.all_values()
            needs = Need.objects.filter(needy=request.user)
            get_month_name(needs)

            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            username = request.POST.get('username')
            tel = request.POST.get('tel')
            email = request.POST.get('email')

            user = User.objects.get(username=request.user.username)
            appuser = AppUser.objects.get(user=user)

            user.first_name=first_name
            user.last_name=last_name
            user.username = username
            user.email = email
            appuser.tel = tel

            user.save()
            appuser.save()
            login(request,user=user)
            return redirect('/user/profile/')
            


        else:
            appuser = AppUser.objects.get(user=request.user)
            user = appuser.all_values()
            needs = Need.objects.filter(needy=request.user)
            get_month_name(needs)
            form = ProfileForm(user=request.user)
            return render(request,'user/profile.html',{'user':user,'needs':needs,'form':form})
    else:
        return redirect('/user/login/')

@login_required
def account_summary_view(request):
    appuser = AppUser.objects.get(user=request.user)
    needs = Need.objects.filter(needy=request.user).order_by('-created')

    return render(request, 'user/account_summary.html', {
        'appuser': appuser,
        'needs': needs
    })

def stk_page_view(request):
    return render(request, 'user/stk_page.html')