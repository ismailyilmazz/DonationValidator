from django.urls import path
from .views import register_view,login_view

appname='user'
urlpatterns=[
    path('register/',register_view),
    path('login/',login_view)
]