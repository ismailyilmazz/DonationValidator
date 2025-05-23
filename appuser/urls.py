from django.contrib.auth import views as auth_views
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
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='user/password_reset.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='user/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='user/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='user/password_reset_complete.html'), name='password_reset_complete'),
]