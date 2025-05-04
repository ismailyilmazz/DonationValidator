from django.shortcuts import render,redirect
from .forms import RegisterForm, LoginForm
from django.contrib.auth import login,logout

# Create your views here.

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
                    return redirect('/admin/')
                else:
                    return redirect('/admin/')
        else:
            form = LoginForm()
        return render(request,'user/login.html',{'form':form})
    return redirect('/admin/')