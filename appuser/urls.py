from django.contrib.auth import views as auth_views
from django.urls import path
from .views import register_view,login_view,profile_view,logout_view,account_summary_view,stk_page_view,logout_confirm_view,delete_address
from . import views
from .views import CustomPasswordResetConfirmView


app_name='user'
urlpatterns=[
    path('register/',register_view),
    path('login/',login_view,name='login'),
    path('profile/',profile_view),
    path('profile/address/delete/<int:index>/', views.delete_address, name='delete_address'),
    path('logout/', logout_confirm_view, name='logout_confirm'),
    path('logout/confirmed/', logout_view, name='logout'),
    path('stk_page/', stk_page_view, name='stk_page'),
    path('account-summary/', account_summary_view, name='account-summary'),
    path('user/profile/', views.profile_view, name='profile'),
    #### ESET PASSWORD
    path('password-reset/', views.request_password_reset, name='request_password_reset'),
    path('reset-password/<str:token>/', views.reset_password, name='reset_password'),

    #######
    ###### USER
    path('users/', views.user_list, name='user_list'),
    path('users/<slug:username>/', views.user_detail, name='user_detail'),
    path('users/<slug:username>/update/', views.user_update, name='user_update'),
    path('users/<slug:username>/delete/', views.user_delete, name='user_delete'),
    #####
]