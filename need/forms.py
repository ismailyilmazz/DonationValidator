from django import forms
import re
from .models import Need,Kind
from django.core.exceptions import ValidationError 

def validate_phone(value):
    if not re.match(r'^[1-9][0-9]{9}$', value):
        raise ValidationError("Telefon numarası 0 ile başlayamaz ve en fazla 10 haneli olmalıdır.")


class AddNeedForm(forms.ModelForm):
    name = forms.CharField(max_length=40,label='Ürün isim')
    kind = forms.ModelChoiceField(queryset=Kind.objects.all(),label='Kategori')
    tel = forms.CharField(label='Telefon Numarası',max_length=10,min_length=10,validators=[validate_phone],help_text="Lütfen 0 ile başlamayan 10 haneli bir numara girin. (örn: 5312345678)")

    class Meta:
        model = Need
        fields = ['name','kind','tel']