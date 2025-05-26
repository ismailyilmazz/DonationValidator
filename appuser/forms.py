from django import forms
import re
from .models import AppUser, Role
from django.core.exceptions import ValidationError,ObjectDoesNotExist
from django.contrib.auth.models import User
from django.contrib.auth.forms import SetPasswordForm


class AdminRoleForm(forms.ModelForm):
    permissions = forms.MultipleChoiceField(
        choices=Role.PERMISSION_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Role
        fields = '__all__'

    def clean_permissions(self):
        return self.cleaned_data.get('permissions', [])


class CustomSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

def validate_phone(value):
    if not re.match(r'^[1-9][0-9]{9}$', value):
        raise ValidationError("Telefon numarası 0 ile başlayamaz ve en fazla 10 haneli olmalıdır.")
    

class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=20, label='İsim')
    last_name = forms.CharField(max_length=20, label='Soyisim')
    username = forms.CharField(max_length=16, label="Kullanıcı Adı")
    tel = forms.CharField(
        label='Telefon Numarası',
        max_length=10,
        min_length=10,
        validators=[validate_phone],
        help_text="Lütfen 0 ile başlamayan 10 haneli bir numara girin. (örn: 5312345678)"
    )
    email = forms.EmailField()

    class Meta:
        model = AppUser
        fields = ['first_name', 'last_name', 'username', 'tel', 'email']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        appuser = AppUser.objects.get(user=self.user)
        values = appuser.all_values()
        self.fields['first_name'].initial = values['first_name']
        self.fields['last_name'].initial = values['last_name']
        self.fields['username'].initial = values['username']
        self.fields['tel'].initial = values['tel']
        self.fields['email'].initial = values['email']

        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"

    def clean_username(self):
        username = self.cleaned_data.get('username')
        qs = User.objects.filter(username=username).exclude(pk=self.user.pk)
        if qs.exists():
            raise ValidationError("Bu kullanıcı adı zaten kullanımda. Lütfen başka bir kullanıcı adı seçin.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        qs = User.objects.filter(email=email).exclude(pk=self.user.pk)
        if qs.exists():
            raise ValidationError("Bu email zaten kullanımda.")
        return email

    def clean_tel(self):
        tel = self.cleaned_data.get('tel')
        qs = AppUser.objects.filter(tel=tel).exclude(user=self.user)
        if qs.exists():
            raise ValidationError("Bu telefon numarası zaten kullanımda.")
        return tel


class AddressForm(forms.Form):
    new_address = forms.CharField(
        label="Yeni Adres",
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Yeni adres ekleyin...', 'class': 'form-control'})
    )
    current_address = forms.ChoiceField(
        label="Mevcut Adres Seçimi",
        choices=[],
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=False
    )

    def __init__(self, *args, **kwargs):
        address_list = kwargs.pop('address_list', [])
        current_index = kwargs.pop('current_index', 0)
        super().__init__(*args, **kwargs)

        choices = [(i, addr) for i, addr in enumerate(address_list)]
        self.fields['current_address'].choices = choices
        self.fields['current_address'].initial = current_index




class RegisterForm(forms.Form):
    first_name = forms.CharField(max_length=20, label="İsim")
    last_name = forms.CharField(max_length=20, label="Soyisim")
    tel = forms.CharField(
        label="Telefon Numarası",
        max_length=10,
        min_length=10,
        validators=[validate_phone],
        help_text="Lütfen 0 ile başlamayan 10 haneli bir numara girin. (örn: 5312345678)"
    )
    email = forms.EmailField(label="Email")
    password = forms.CharField(max_length=16, widget=forms.PasswordInput, label="Şifre")

    def clean_tel(self):
        tel = self.cleaned_data['tel']
        if User.objects.filter(username=tel).exists():
            raise forms.ValidationError("Bu telefon numarasıyla kayıtlı bir kullanıcı zaten var.")
        return tel

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Bu e-posta adresiyle kayıtlı bir kullanıcı zaten var.")
        return email

    def save(self):
        try:
            role = Role.objects.get(slug="user")
        except Role.DoesNotExist:
            role = Role.objects.create(name="User", slug="user")

        user = User(
            username=self.cleaned_data['tel'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            email=self.cleaned_data['email']
        )
        user.set_password(self.cleaned_data['password'])
        user.save()

        appuser = AppUser(
            user=user,
            tel=self.cleaned_data['tel'],
            role=role
        )
        appuser.save()

        return user

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"



class LoginForm(forms.Form):  # ModelForm değil Form olsun (User modelini kullanmıyorsun burada)
    username = forms.CharField(label='Telefon Numarası', help_text="Lütfen 0 ile başlamayan 10 haneli bir numara girin. (örn: 5312345678)")
    password = forms.CharField(max_length=16, widget=forms.PasswordInput, label="Şifre")


    def loginControl(self):
        return self.cleaned_data.get('user', None)


    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and password:
            try:
                user = User.objects.get(username=username)
                if not user.check_password(password):
                    self.add_error('password', 'Şifre yanlış.')
                else:
                    cleaned_data['user'] = user  # Login için view'da kullanabilmek için
            except User.DoesNotExist:
                self.add_error('username', 'Kullanıcı bulunamadı.')

        return cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"

class AppUserForm(forms.ModelForm):
    class Meta:
        model = AppUser
        fields = ['tel', 'role']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"
