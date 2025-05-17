from django import forms
import re
from .models import Need, Kind
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

#ismail
class NeedImportForm(forms.Form):
    csv_file= forms.FileField(label="İhtiyaçlar(CSV)")
#ismail
