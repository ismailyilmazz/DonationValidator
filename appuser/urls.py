from django.urls import path
from .views import register_view,login_view,profile_view,logout_view,account_summary_view,stk_page_view
from . import views

appname='user'
urlpatterns=[
    path('register/',register_view),
    path('login/',login_view),
    path('profile/',profile_view),
    path('logout/',logout_view),
    path('stk_page/', stk_page_view, name='stk_page'),
    path('account-summary/', account_summary_view, name='account-summary'),
    path('user/profile/', views.profile_view, name='profile'),
]