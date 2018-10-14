from __future__ import absolute_import

from django.shortcuts import render
from django.http import *
import sys
import os
from multiprocessing import Process

from .model_manager import ModelManager
from .common import exceptions
from django.views.generic.base import TemplateView
import logging

from .forms import UploadFileForm
# from .models import UploadFile
from .db import RecboardDB
from .models import *
import json
from random import randint
logging.getLogger(__name__)

db = RecboardDB()
conn = db.connection    


def index(request):
    return HttpResponse("All good, server is up")

def save_uploaded_file(user,filename,file):
    directory = "board/data/"
    if not os.path.exists(directory):
        print("making dir ...")
        os.makedirs(directory)
    with open(directory+str(user.id) + "_file_" + filename, 'wb+') as destination:
        #use chunks instead of read to avoid having large files in memory
        for chunk in file.chunks():
            destination.write(chunk)
            
        user.datasets.append(Dataset(name=filename,tags=["tags"]))#add this dataset to user
        db.insert('user',user)  #update user doc
        logging.info("Uploaded file saved","file:",filename,"location:",destination)

def upload(request):
    user = get_dummy_user() #TODO: replace this with actual logged in user later
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            for _, file in request.FILES.items():
                save_uploaded_file(user,file.name, file)
    else:
        return HttpResponseBadRequest("Bad request")
    return HttpResponse("Uploaded")

def list_datasets(request):
    """Returns list of datasets"""
    user = get_dummy_user()
    u = db.get('user',name=user.name)
    return HttpResponse([ds.name for ds in u.datasets])

def list_workspaces(request):
    """Returns list of datasets"""
    user = get_dummy_user()
    u = db.get('user',name=user.name) #TODO: replace with actual user
    return HttpResponse([workspace.name for workspace in u.workspaces])

def get_dummy_user():
    if len(db.select('user')) == 0:
        create_dummy_user()
    user = db.select('user')[0]
    return user

def create_dummy_user():
    db.insert('user',User(name="Mohit",phones=['1','2']))

def get_request_body(request):
    if not request or not request.body:
        return None
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)

    return body

def create_workspace(request):
    """Creates a new workspace for userid"""
    body = get_request_body(request)
    if not body or not "workspace_name" in body:
        HttpResponseBadRequest("Bad request")
    
    dummy = get_dummy_user()
    user = db.get('user',name=dummy.name) #TODO: replace with actual user
    #TODO: replace with actual update op using addset for better perf
    user.workspaces.append(Workspace(name="workspacename2"))
    db.insert('user',user)
    return HttpResponse()


class HomePage(TemplateView):
    """
        This is a class based view for home page (/home)
    """
    template_name = 'home.html'

LOG_DIR = "/Users/kay/recboard/model_summaries"

def create(request):
    print ('Parent process pid:', os.getpid())
    PATH_TO_DATASET = '/files/data/users.dat'
    model_controller_obj = ModelManager('BPR', 'train_samp', 'val_samp', 'test_samp', 'AUC', PATH_TO_DATASET)
    
    p = Process(target=ModelManager.sample_data_and_train, args=(model_controller_obj,))
    p.start()
    p.join(2)

    # try:
    generated_model_id = model_controller_obj.model_id
    err = "No err "
    user = get_dummy_user()
    if not user.datasets: 
        return JsonResponse({'msg':'No datasets found'})

    if not user.workspaces:
        user.workspaces.append(Workspace(name="workspacename2"))
        db.insert('user',user)
    
    # TODO: maintain a list of available ports later
    tensorboard_port = str(randint(6000,7000)) 
    print("port generated", tensorboard_port,"Starting tb")

    # TODO: add try catch here (in case the tensorboard couldnt be started)
    
    cmd = "tensorboard --logdir "+LOG_DIR+" --port "+tensorboard_port 
    tb_p = Process(target=os.system, args=(cmd,))
    tb_p.start()
    tb_p.join(2)
    
    print("TB started")

    model = Model(name="myModel",status="just created", dataset=user.datasets[0],logdir=LOG_DIR, port=tensorboard_port)
    user.workspaces[-1].models.append(model)
    db.insert('user',user)

    return JsonResponse({'msg':tensorboard_port})
    # except:
    #     print("Error in getting generated model-id")
    #     p.terminate() # Force terminate training
    #     return JsonResponse({'msg':"Error in getting generated model-id"})


if __name__ == "__main__":
    list_datasets()




    
    