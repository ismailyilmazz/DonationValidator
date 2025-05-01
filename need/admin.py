from django.contrib import admin
from .models import Need, Kind

# Register your models here.
class NeedAdmin(admin.ModelAdmin):
    list_display = ['name','kind','needy','donor','status','address']
admin.site.register(Need,NeedAdmin)

class KindAdmin(admin.ModelAdmin):
    list_display = ['name']
admin.site.register(Kind,KindAdmin)