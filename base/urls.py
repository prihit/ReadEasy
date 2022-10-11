from django.urls import path,include
from . import views

urlpatterns = [
    path('',views.home ),
    path('getImage', views.getImage),
    path('viewImage', views.viewImage),
    path('run', views.run),
]