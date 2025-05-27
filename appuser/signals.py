# appuser/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import AppUser, Role

@receiver(post_save, sender=User)
def create_app_user(sender, instance, created, **kwargs):
    if created:
        try:
            default_role = Role.objects.get(slug='admin')
        except Role.DoesNotExist:
            permissions = [permission[0] for permission in Role.PERMISSION_CHOICES ]
            default_role = Role(name='Admin',slug="admin",permissions=permissions)
            default_role.save()
        AppUser.objects.create(user=instance, role=default_role, tel=1000000000)
