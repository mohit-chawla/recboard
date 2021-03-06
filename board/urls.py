from django.urls import path
from django.conf.urls import include, url
from . import views
from django.conf.urls import url


urlpatterns = [
    path('', views.Index.as_view(), name='index'),
    path('home/login', views.login_user),
    path('upload', views.upload, name='upload'),
    url(r'^home/$', views.HomePage.as_view(), name='home'),
    url(r'^home/monitor', views.MonitorPage.as_view(), name='monitor'),
    path('user/workspace/recommender/list',views.list_recommenders,name='recommenders'),
    path('user/workspace/evaluator/list',views.list_evaluators,name='evaluators'),
    path('user/workspace/sampler/list',views.list_samplers,name='samplers'),
    path('user/workspace/delete',views.delete_workspace,name='delete workspace'),
    path('user/workspace/model/delete',views.delete_model,name='delete model'),
    path('user/workspace/model/train', views.create, name='index'),
    path('user/workspace/model/port', views.get_model_port, name='index'),
    path('user/workspace/model/list', views.list_models, name='list workspace models'),
    path('user/workspace/model/details', views.model_details, name='model details'),
    path('user/dataset/list',views.list_datasets,name='index'),
    path('user/workspace/create',views.create_workspace,name='index'),
    path('user/workspace/list',views.list_workspaces,name='index'),
    path('user/workspace/model/status', views.get_model_status, name='get_model_status'),
    path('home/user/workspace/model/download',views.download_model),
    path('user/workspace/model/predict',views.predict, name='predict'),
    path('user/workspace/model/deploy',views.deploy, name="deploy_model"),
    path('user/workspace/model/undeploy',views.undeploy, name="undeploy_model"),
    path('user/workspace/model/deploy/check',views.is_deployed, name="check_deploy_model")
]
