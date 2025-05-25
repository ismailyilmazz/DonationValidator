from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class Role(models.Model):
    name = models.CharField(max_length=20)
    slug = models.SlugField(max_length=40,unique=True)

    PERMISSION_CHOICES = (
        ("need_confirmation","Need_Confirmation"),
        ("need_update","Need_Update"),
        ("need_information","Need_Information"),
        ("need_delete","Need_Delete"),
        ("role_add","Role_Add"),
        ("user_delete","User_Delete"),
        ("user_information","User_Information"),
        ("data_import","Data_Import"),
        ("data_export","Data_Export"),
        ("role_update","Role_Update"),
        ("offer_update","Offer_Update"),
        ("category","Category")
    )
    permissions = models.JSONField(default=list,blank=True)


    def __str__(self):
        return self.name


class AppUser(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    tel = models.IntegerField(unique=True)
    role = models.ForeignKey(Role,on_delete=models.CASCADE)
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
            'current_address': self.current_address,
            'permissions':self.role.permissions
        }

    def delete(self):
        self.user.delete()
        super().delete()

    def __str__(self):
        return self.user.username