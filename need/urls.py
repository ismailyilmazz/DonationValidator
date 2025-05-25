from django.urls import path
from .views import list_view,add_view,detail_view,kind_view,search_view,offer_view,mark_received_view,delete_need,unauthorized_view
from . import views

app_name = 'need'
urlpatterns=[
    path('',list_view),
    path('add/',add_view),
    path('<int:year>/<int:month>/<int:day>/<slug:slug>/',detail_view,name="detail_view"),
    path('kind/<slug:slug>/',kind_view,name="detail_view"),
    path('search',search_view),
    path('offer/<int:need_id>/',offer_view,name="offer"),
    path('mark-received/<int:need_id>/',mark_received_view,name="mark_received"),
    path('delete/<int:year>/<int:month>/<int:day>/<slug:slug>/',delete_need,name="delete_need"),
    ##KIND
    path('kinds/', views.kind_list, name='kind_list'),
    path('kinds/<slug:slug>/update/', views.kind_update, name='kind_update'),
    ##
    ## Roles
    path('roles/', views.role_list, name='role_list'),
    path('roles/create/', views.role_create, name='role_create'),
    path('roles/<slug:slug>/update/', views.role_update, name='role_update'),
    ####

    path('unauthorized/',unauthorized_view,name="unauthorized"),

#İmport-export, -uygun yönlendirmeleri yap aga-
    path("import/", views.import_needs, name="import_needs"),
    path("export/needs/", views.export_needs, name="export_needs"),
    path("export/offers/", views.export_offers, name="export_offers"),
#import-export
]