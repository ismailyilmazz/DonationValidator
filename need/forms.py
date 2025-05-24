from django import forms
import re
from .models import Need, Kind, Offer
from django.core.exceptions import ValidationError
from appuser.models import AppUser


def validate_phone(value):
    if not re.match(r"^[1-9][0-9]{9}$", value):
        raise ValidationError(
            "Telefon numarası 0 ile başlayamaz ve en fazla 10 haneli olmalıdır."
        )


class AddNeedForm(forms.ModelForm):
    first_name = forms.CharField(max_length=40, label="İsim")
    last_name = forms.CharField(max_length=40, label="Soyisim")
    name = forms.CharField(max_length=40, label="Ürün isim")
    kind = forms.ModelChoiceField(queryset=Kind.objects.all(), label="Kategori")
    tel = forms.CharField(
        label="Telefon Numarası",
        max_length=10,
        min_length=10,
        validators=[validate_phone],
        help_text="Lütfen 0 ile başlamayan 10 haneli bir numara girin. (örn: 5312345678)",
        error_messages={
            "blank": "Telefon numarası boş bırakılamaz.",
            "invalid": "Geçerli bir telefon numarası girin.",
        },
    )
    address = forms.CharField(
        label="Adres",
        widget=forms.Textarea(
            attrs={
                "placeholder": "Adres",
                "class": "form-control",
                "style": "height:5em",
            }
        ),
    )

    class Meta:
        model = Need
        fields = ["first_name", "last_name", "name", "kind", "tel", "address"]
        
    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if user and user.is_authenticated:
            appuser = AppUser.objects.get(user=user)
            appuser = appuser.all_values()
            self.fields["first_name"].initial = appuser['first_name']
            self.fields["last_name"].initial = appuser['last_name']
            try:
                self.fields["address"].initial = appuser['address'][
                    appuser.current_address
                ]
            except:
                pass
            self.fields.pop("tel")

        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"


class OfferForm(forms.ModelForm):
    donor_first_name = forms.CharField(
        max_length=50, 
        label="İsim",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    donor_last_name = forms.CharField(
        max_length=50, 
        label="Soyisim",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    confirmed = forms.BooleanField(
        label="Bu bağışı yapacağımı onaylıyorum",
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    note = forms.CharField(
        label="Not (İsteğe bağlı)",
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'İsteğe bağlı bir not ekleyebilirsiniz...'
        })
    )

    class Meta:
        model = Offer
        fields = ['donor_first_name', 'donor_last_name', 'confirmed', 'note']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if user and user.is_authenticated:
            try:
                appuser = AppUser.objects.get(user=user)
                appuser_data = appuser.all_values()
                self.fields["donor_first_name"].initial = appuser_data.get('first_name', user.first_name)
                self.fields["donor_last_name"].initial = appuser_data.get('last_name', user.last_name)
            except AppUser.DoesNotExist:
                self.fields["donor_first_name"].initial = user.first_name
                self.fields["donor_last_name"].initial = user.last_name


#ismail
class NeedImportForm(forms.Form):
    csv_file= forms.FileField(label="İhtiyaçlar(CSV)")
#ismail