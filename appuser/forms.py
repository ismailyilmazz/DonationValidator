from django import forms
import re
from .models import AppUser, Role
from django.core.exceptions import ValidationError,ObjectDoesNotExist
from django.contrib.auth.models import User

def validate_phone(value):
    if not re.match(r'^[1-9][0-9]{9}$', value):
        raise ValidationError("Telefon numarası 0 ile başlayamaz ve en fazla 10 haneli olmalıdır.")


class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=20,label='İsim')
    last_name = forms.CharField(max_length=20,label='Soyisim')
    username = forms.CharField(max_length=16,label="Kullanıcı Adı")
    tel = forms.CharField(label='Telefon Numarası',max_length=10,min_length=10,validators=[validate_phone],help_text="Lütfen 0 ile başlamayan 10 haneli bir numara girin. (örn: 5312345678)")
    email = forms.EmailField()

    class Meta:
        model = AppUser
        fields = ['first_name','last_name','username','tel','email']
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user',None)
        super().__init__(*args, **kwargs)

        appuser = AppUser.objects.get(user=user)
        values = appuser.all_values()
        self.fields['first_name'].initial = values['first_name']
        self.fields['last_name'].initial = values['last_name']
        self.fields['username'].initial = values['username']
        self.fields['tel'].initial = values['tel']
        self.fields['email'].initial = values['email']
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"

class LoginForm(forms.ModelForm):
    username = forms.CharField(label='Telefon Numarası',help_text="Lütfen 0 ile başlamayan 10 haneli bir numara girin. (örn: 5312345678)")
    password = forms.CharField(max_length=16,widget=forms.PasswordInput)

    class Meta:
        model = AppUser
        fields = ['username','password']
    
    def loginControl(self):
        username=self.cleaned_data['username']
        password = self.cleaned_data['password']
        try:   
            user = User.objects.get(username=username) 
            if user.check_password(password):
                return user
            else:
                return None

        except ObjectDoesNotExist:
            return None  
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"
