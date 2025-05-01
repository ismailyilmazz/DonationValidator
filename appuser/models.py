from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class Role(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name

class AllValuesManager(models.Manager):
    def get(self):
        val = super(self)
        return{
            'first_name':val.user.first_name.capitalize(),
            'last_name':val.user.last_name.capitalize(),
            'email':val.user.email,
            'username':val.user.username,
            'tel':val.tel,
            'role':val.role
        }

class AppUser(models.Model):
    
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    tel = models.IntegerField(max_length=10,unique=True)
    role = models.ForeignKey(Role,on_delete=models.CASCADE,default=1)


    objects = models.Manager()
    all_values = AllValuesManager()

    def delete(self):
        self.user.delete()
        super().delete(self)

    def __str__(self):
        return self.user.username