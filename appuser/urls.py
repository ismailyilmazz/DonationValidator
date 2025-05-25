from django.contrib.auth import views as auth_views
from django.urls import path
from .views import register_view,login_view,profile_view,logout_view,account_summary_view,stk_page_view,logout_confirm_view
from . import views
from .views import CustomPasswordResetConfirmView


appname='user'
urlpatterns=[
    path('register/',register_view),
    path('login/',login_view),
    path('profile/',profile_view),
    path('logout/', logout_confirm_view, name='logout_confirm'),
    path('logout/confirmed/', logout_view, name='logout'),
    path('stk_page/', stk_page_view, name='stk_page'),
    path('account-summary/', account_summary_view, name='account-summary'),
    path('user/profile/', views.profile_view, name='profile'),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='user/password_reset.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='user/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/',CustomPasswordResetConfirmView.as_view(template_name='user/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='user/password_reset_complete.html'), name='password_reset_complete'),
    ###### USER
    path('users/', views.user_list, name='user_list'),
    path('users/<slug:username>/', views.user_detail, name='user_detail'),
    path('users/<slug:username>/update/', views.user_update, name='user_update'),
    path('users/<slug:username>/delete/', views.user_delete, name='user_delete'),
    #####
]