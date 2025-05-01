from django.urls import path
from .views import list_view,add_view

app_name="need"
urlpatterns=[
    path('',list_view),
    path('add/',add_view),
]