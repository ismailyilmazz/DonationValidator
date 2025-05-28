from rest_framework import serializers
from need.models import Need, Kind
from django.contrib.auth.models import User
from appuser.models import AppUser, Role
from appuser.utils import add_control 
from django.core.exceptions import ValidationError
from django.contrib.auth import login

class NeedSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(write_only=True, required=False)
    last_name = serializers.CharField(write_only=True, required=False)
    tel = serializers.CharField(write_only=True, required=False)

    kind = serializers.StringRelatedField(read_only=True)
    kind_id = serializers.PrimaryKeyRelatedField(
        queryset=Kind.objects.all(), write_only=True, source='kind'
    )

    class Meta:
        model = Need
        fields = ['name', 'slug', 'address', 'created', 'kind', 'kind_id', 'first_name', 'last_name', 'tel']
        read_only_fields = ['slug', 'created', 'kind']

    def create(self, validated_data):
        request = self.context['request']
        kind = validated_data.pop('kind')
        first_name = validated_data.pop('first_name', None)
        last_name = validated_data.pop('last_name', None)
        tel = validated_data.pop('tel', None)

        if request.user.is_authenticated:
            user = request.user
            appuser = AppUser.objects.get(user=user)
            address = validated_data.get('address')
            all_values = appuser.all_values()

            if len(all_values["address"]) == 0:
                appuser.address = [address]
                appuser.current_address = 0
            elif all_values["address"][all_values["current_address"]] != address:
                appuser.address = all_values["address"] + [address]
                appuser.current_address = len(appuser.address) - 1
            appuser.save()

        else:
            if not (first_name and last_name and tel):
                raise serializers.ValidationError("İsim , soyisim ve telefon numarası zorunludur!")

            try:
                add_control(tel=tel)
                role, _ = Role.objects.get_or_create(slug="user", defaults={"name": "User"})
                user, created = User.objects.get_or_create(
                    username=tel,
                    defaults={"first_name": first_name, "last_name": last_name}
                )
                if created:
                    user.set_password(tel)
                    user.save()
                    AppUser.objects.create(
                        tel=tel,
                        user=user,
                        role=role,
                        address=[validated_data.get('address')] if validated_data.get('address') else [],
                        current_address=0 if validated_data.get('address') else -1
                    )
                login(request, user)
            except ValidationError as e:
                raise serializers.ValidationError({"tel": e.message})
        need = Need.objects.create(
            **validated_data,
            kind=kind,
            needy=user
        )
        return need
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request', None)
        if request and request.user.is_authenticated:
            self.fields.pop('first_name', None)
            self.fields.pop('last_name', None)
            self.fields.pop('tel', None)

