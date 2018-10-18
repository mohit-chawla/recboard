from django.urls import path
from django.conf.urls import include, url
from . import views
from django.conf.urls import url


urlpatterns = [
    path('', views.Index.as_view(), name='index'),
    path('home/login', views.login_user),
    path('upload', views.upload, name='upload'),
    url(r'^home/$', views.HomePage.as_view(), name='home'),
    path('user/workspace/model/train', views.create, name='index'),
    path('user/workspace/model/port', views.get_model_port, name='index'),
    path('user/dataset/list',views.list_datasets,name='index'),
    path('user/workspace/create',views.create_workspace,name='index'),
    path('user/workspace/list',views.list_workspaces,name='index'),
]
