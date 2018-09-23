from django.urls import path
from django.conf.urls import include, url
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('upload', views.upload, name='upload'),
    url(r'^home/$', views.HomePage.as_view()),
]