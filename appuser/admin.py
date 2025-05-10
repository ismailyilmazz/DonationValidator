from django.contrib import admin
from .models import AppUser,Role
# Register your models here.
class AppUserAdmin(admin.ModelAdmin):
    list_display = ['user','tel','role']
admin.site.register(AppUser,AppUserAdmin)

class RoleAdmin(admin.ModelAdmin):
    list_display = ['name']
    prepopulated_fields = {"slug":("name",)}
admin.site.register(Role,RoleAdmin)