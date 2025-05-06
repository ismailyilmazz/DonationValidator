from django.urls import path
from .views import list_view,add_view,detail_view,kind_view,search_view

app_name="need"
urlpatterns=[
    path('',list_view),
    path('add/',add_view),
    path('<int:year>/<int:month>/<int:day>/<slug:slug>/',detail_view,name="detail_view"),
    path('kind/<slug:slug>/',kind_view,name="detail_view"),
    path('search',search_view)
]