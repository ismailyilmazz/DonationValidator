from django.urls import path
from .views import list_view,add_view,detail_view,offer_view,mark_received_view,delete_need,unauthorized_view,courier_request_list,generate_code
from . import views

app_name = 'need'
urlpatterns=[
    path('',list_view, name='needs_list'),
    path('add/',add_view),
    path('<int:year>/<int:month>/<int:day>/<slug:slug>/',detail_view,name="detail_view"),
    path('offer/<int:need_id>/',offer_view,name="offer"),
    path('mark-received/<int:need_id>/',mark_received_view,name="mark_received"),
    path('delete/<int:year>/<int:month>/<int:day>/<slug:slug>/',delete_need,name="delete_need"),
    path('<int:year>/<int:month>/<int:day>/<slug:slug>/generate-code/', generate_code, name='generate_code'),
    ##KIND
    path('kinds/', views.kind_list, name='kind_list'),
    path('kinds/<slug:slug>/update/', views.kind_update, name='kind_update'),
    path('kind/<slug:slug>/delete/', views.kind_delete, name='kind_delete'),
    ##
    ## Roles
    path('roles/', views.role_list, name='role_list'),
    path('roles/create/', views.role_create, name='role_create'),
    path('roles/<slug:slug>/update/', views.role_update, name='role_update'),
    path('roles/delete/<slug:slug>/', views.role_delete, name='role_delete'),
    ####
    #### COURIER
    path('courier/requests/', courier_request_list, name='request_list'),
    path('courier/assigned/', views.my_courier_needs, name='my_courier_needs'),
    ####
    path('unauthorized/',unauthorized_view,name="unauthorized"),

    #### İmport-export,
    path('import/', views.import_needs, name='import_needs'),
    path('import/confirm/', views.import_confirm, name='import_confirm'),
    path('export/', views.export_needs, name='export_needs'),
    path('import-export-dashboard/', views.import_export_dashboard, name='import_export_dashboard'),
    ####
]