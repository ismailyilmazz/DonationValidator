from django.contrib import admin
from .models import Need, Kind, Offer

# Register your models here.
class NeedAdmin(admin.ModelAdmin):
    list_display = ('name','kind','needy','donor','status','address')
    list_filter = ("kind","status")
    search_fields = ("name","address")
    raw_id_fields = ("needy","donor")
    ordering = ('created',)

admin.site.register(Need,NeedAdmin)

class OfferAdmin(admin.ModelAdmin):
    list_display = ('need','donor','courier','status','confirmed')
    list_filter = ("confirmed","status")
    raw_id_fields = ("donor",)
    ordering = ("created","updated")

admin.site.register(Offer,OfferAdmin)

class KindAdmin(admin.ModelAdmin):
    list_display = ('name',)
    prepopulated_fields = {"slug":("name",)}
admin.site.register(Kind,KindAdmin)

