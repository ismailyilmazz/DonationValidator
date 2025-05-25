from django.shortcuts import render,redirect, get_object_or_404
from .forms import RegisterForm, LoginForm, ProfileForm,UserForm,AppUserForm,AddressForm
from django.contrib.auth import login,logout
from .models import AppUser
from need.models import Need, Offer
from need.views import get_month_name
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordResetConfirmView
from .forms import CustomSetPasswordForm
from .utils import permission_required_any
from django.core.paginator import Paginator

    
class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = CustomSetPasswordForm
# Create your views here.

def logout_view(request):
    logout(request)
    return redirect('/user/login/')

@login_required
def logout_confirm_view(request):
    return render(request, 'user/logout_confirm.html')

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

from django.contrib import messages

def profile_view(request):
    if not request.user.is_authenticated:
        return redirect('/user/login/')

    appuser = AppUser.objects.get(user=request.user)
    user_needs = Need.objects.filter(needy=request.user).order_by('-created')
    user_offers = Offer.objects.filter(donor=request.user).order_by('-created')
    user_dict = appuser.all_values()
    needs = Need.objects.filter(needy=request.user)
    get_month_name(needs)

    form = ProfileForm(user=request.user)
    
    if request.method == 'POST':
        if 'profile_update' in request.POST:
            form = ProfileForm(request.POST, user=request.user)
            if form.is_valid():
                user = request.user
                user.first_name = form.cleaned_data['first_name']
                user.last_name = form.cleaned_data['last_name']
                user.username = form.cleaned_data['username']
                user.email = form.cleaned_data['email']
                user.save()

                appuser.tel = form.cleaned_data['tel']
                appuser.save()

                login(request, user=user)
                messages.success(request, "Profil başarıyla güncellendi.")
                return redirect('/user/profile/')
            else:
                messages.error(request, "Lütfen formdaki hataları düzeltin.")

        elif 'address_update' in request.POST:
            new_address = request.POST.get('new_address')
            current_index = request.POST.get('current_address')

            if new_address:
                addresses = appuser.address or []
                addresses.append(new_address)
                appuser.address = addresses
                appuser.save()
                messages.success(request, "Adres eklendi.")

            if current_index is not None:
                try:
                    appuser.current_address = int(current_index)
                    appuser.save()
                    messages.success(request, "Mevcut adres güncellendi.")
                except ValueError:
                    messages.error(request, "Geçersiz adres seçimi.")

            return redirect('/user/profile/')

    return render(
        request,
        'user/profile.html',
        {
            'user': user_dict,
            'needs': needs,
            'form': form,
            'user_needs': user_needs,
            'user_offers': user_offers,
        }
    )



@login_required
def delete_address(request, index):
    appuser = get_object_or_404(AppUser, user=request.user)

    if index == appuser.current_address:
        messages.error(request, "Seçili adresi silemezsiniz.")
    elif 0 <= index < len(appuser.address):
        appuser.address.pop(index)
        if index < appuser.current_address:
            appuser.current_address -= 1
        elif index > appuser.current_address:
            pass
        appuser.save()
        messages.success(request, "Adres başarıyla silindi.")
    else:
        messages.error(request, "Geçersiz adres seçimi.")

    return redirect('user:profile')



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


############ USER MANAGEMENT ##################



@permission_required_any('user_information', 'user_delete')
def user_list(request):
    query = request.GET.get('q', '')
    users = AppUser.objects.select_related('user', 'role').all()
    if query:
        users = users.filter(
            user__username__icontains=query
        ) | users.filter(
            tel__icontains=query
        )
    paginator = Paginator(users, 10)  # 10 user per page
    page = request.GET.get('page')
    users = paginator.get_page(page)
    return render(request, 'user/user_list.html', {'users': users, 'query': query})

@permission_required_any('user_information', 'user_delete')
def user_detail(request, username):
    user = get_object_or_404(AppUser, user__username=username)
    return render(request, 'user/user_detail.html', {'user_obj': user})

@permission_required_any('user_update', 'user_information')
def user_update(request, username):
    app_user = get_object_or_404(AppUser, user__username=username)
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=app_user.user)
        appuser_form = AppUserForm(request.POST, instance=app_user)
        if user_form.is_valid() and appuser_form.is_valid():
            user_form.save()
            appuser_form.save()
            return redirect('user:user_list')
    else:
        user_form = UserForm(instance=app_user.user)
        appuser_form = AppUserForm(instance=app_user)
    return render(request, 'user/user_form.html', {'user_form': user_form, 'appuser_form': appuser_form})

@permission_required_any('user_delete')
def user_delete(request, username):
    app_user = get_object_or_404(AppUser, user__username=username)
    if request.method == 'POST':
        app_user.delete()
        return redirect('user:user_list')
    return render(request, 'user/user_confirm_delete.html', {'user_obj': app_user})

################


