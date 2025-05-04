from django.contrib import admin
from .models import Need, Kind

# Register your models here.
class NeedAdmin(admin.ModelAdmin):
    list_display = ('name','kind','needy','donor','status','address')
    list_filter = ("kind","status")
    search_fields = ("name","address")
    raw_id_fields = ("needy","donor")
    ordering = ('created',)

admin.site.register(Need,NeedAdmin)

class KindAdmin(admin.ModelAdmin):
    list_display = ('name',)
    prepopulated_fields = {"slug":("name",)}
admin.site.register(Kind,KindAdmin)