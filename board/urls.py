from django.urls import path, re_path
from django.conf.urls import include, url
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('upload', views.upload, name='upload'),
    url(r'^home/$', TemplateView.as_view(template_name='index.html')),
    # url(r'^home/$', views.HomePage.as_view()),
    path('create', views.create, name='index'),
]
