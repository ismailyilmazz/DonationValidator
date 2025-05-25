from django.contrib import admin
from .models import AppUser,Role
from .forms import AdminRoleForm

# Register your models here.
class AppUserAdmin(admin.ModelAdmin):
    list_display = ['user','tel','role']
admin.site.register(AppUser,AppUserAdmin)

class RoleAdmin(admin.ModelAdmin):
    form = AdminRoleForm
    list_display = ['name', 'slug']
    prepopulated_fields = {"slug":("name",)}
admin.site.register(Role,RoleAdmin)