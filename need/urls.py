from django.urls import path
from .views import list_view,add_view,detail_view,kind_view,search_view,offer_view,mark_received_view
from . import views

app_name="need"
urlpatterns=[
    path('',list_view),
    path('add/',add_view),
    path('<int:year>/<int:month>/<int:day>/<slug:slug>/',detail_view,name="detail_view"),
    path('kind/<slug:slug>/',kind_view,name="detail_view"),
    path('search',search_view),
    path('offer/<int:need_id>/',offer_view,name="offer"),
    path('mark-received/<int:need_id>/',mark_received_view,name="mark_received"),
#ismail
    path("import/", views.import_needs, name="import"),
    path("export/needs/", views.export_needs, name="export_needs"),
    path("export/offers/", views.export_offers, name="export_offers"),
#ismail
]