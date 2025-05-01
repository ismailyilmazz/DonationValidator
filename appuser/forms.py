from django import forms
import re
from .models import AppUser, Role
from django.core.exceptions import ValidationError,ObjectDoesNotExist
from django.contrib.auth.models import User
from django.contrib.auth import login,logout

def validate_phone(value):
    if not re.match(r'^[1-9][0-9]{9}$', value):
        raise ValidationError("Telefon numarası 0 ile başlayamaz ve en fazla 10 haneli olmalıdır.")


class RegisterForm(forms.ModelForm):
    first_name = forms.CharField(max_length=20,label="İsim")
    last_name = forms.CharField(max_length=20,label='Soyisim')
    tel = forms.CharField(label='Telefon Numarası',max_length=10,min_length=10,validators=[validate_phone],help_text="Lütfen 0 ile başlamayan 10 haneli bir numara girin. (örn: 5312345678)")
    email = forms.EmailField()
    password = forms.CharField(max_length=16,widget=forms.PasswordInput)

    def save(self):
        user = User(username=self.cleaned_data['tel'],first_name = self.cleaned_data['first_name'],last_name = self.cleaned_data['last_name'],email = self.cleaned_data['email'])
        user.set_password(self.cleaned_data['password'])
        user.save()
        appuser = AppUser(
            user=user,
            tel=self.cleaned_data['tel']
        )
        appuser.save()


    class Meta:
        model = AppUser
        fields = ['first_name','last_name','tel','email','password']

class LoginForm(forms.ModelForm):
    tel = forms.CharField(label='Telefon Numarası',max_length=10,min_length=10,validators=[validate_phone],help_text="Lütfen 0 ile başlamayan 10 haneli bir numara girin. (örn: 5312345678)")
    password = forms.CharField(max_length=16,widget=forms.PasswordInput)
    try:   
        user = User.objects.get(username=tel) 
        if user.check_password(password):
            login(user)

    except ObjectDoesNotExist:
        pass    

    class Meta:
        model = AppUser
        fields = ['tel','password']