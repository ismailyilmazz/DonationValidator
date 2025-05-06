from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class Role(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class AppUser(models.Model):
    
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    tel = models.IntegerField(max_length=10,unique=True)
    role = models.ForeignKey(Role,on_delete=models.CASCADE,default=1)
    address = models.JSONField(default=list,blank=True,null=True)
    current_address = models.IntegerField(default=0)

    def all_values(self):
        return {
            'first_name': self.user.first_name.capitalize(),
            'last_name': self.user.last_name.capitalize(),
            'email': self.user.email,
            'username': self.user.username,
            'tel': self.tel,
            'role': self.role,
            'address': self.address,
            'current_address': self.current_address
        }

    def delete(self):
        self.user.delete()
        super().delete(self)

    def __str__(self):
        return self.user.username