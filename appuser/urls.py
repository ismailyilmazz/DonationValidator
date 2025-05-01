from django.urls import path
from .views import register_view

appname='user'
urlpatterns=[
    path('register/',register_view)
]