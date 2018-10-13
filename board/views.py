from __future__ import absolute_import

from django.shortcuts import render
from django.http import HttpResponse
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

logging.getLogger(__name__)

db = RecboardDB()
conn = db.connection    


def index(request):
    return HttpResponse("All good, server is up")

def save_uploaded_file(filename,file):
    directory = "board/data/"
    if not os.path.exists(directory):
        print("making dir ...")
        os.makedirs(directory)
    with open(directory+filename, 'wb+') as destination:
        #use chunks instead of read to avoid having large files in memory
        for chunk in file.chunks():
            destination.write(chunk)
            db.insert('dataset',Dataset(name=filename,tags=["tags"]))
        logging.info("Uploaded file saved","file:",filename,"location:",destination)

def upload(request):
    user_id = "1" #TODO: replace this with actual logged in user later
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            for _, file in request.FILES.items():
                save_uploaded_file(user_id+"_"+file.name, file)
    else:
        raise Exception("Invalid request")
    return HttpResponse("Uploaded")

def list_datasets(request):
    """Returns list of datasets"""
    return HttpResponse([ds.name for ds in db.select('dataset')])

def list_workspaces(request):
    """Returns list of datasets"""
    users = db.select('user')
    if not users:
        return None
    user = db.select('user')[0]
    return HttpResponse([workspace.name for workspace in user.workspaces])


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
    if not body:
        return HttpResponse("invalid request")
    if not "workspace_name" in body:
        return HttpResponse("Invalid request")
    
    if len(db.select('user')) == 0:
        create_dummy_user()

    user = db.select('user')[0]
    user.workspaces.append(Workspace(name="workspacename2"))
    db.insert('user',user)
    return HttpResponse()


class HomePage(TemplateView):
    """
        This is a class based view for home page (/home)
    """
    template_name = 'home.html'


def create(request):
    print ('Parent process pid:', os.getpid())
    PATH_TO_DATASET = '/ctrsr_datasets/citeulike-a/users.dat'
    model_controller_obj = ModelManager('BPR', 'train_samp', 'val_samp', 'test_samp', 'AUC', PATH_TO_DATASET)

    p = Process(target=ModelManager.sample_data_and_train, args=(model_controller_obj,))
    p.start()
    p.join(2)

    try:
        generated_model_id = model_controller_obj.model_id
        err = "No err "
        return HttpResponse(str(generated_model_id + err))
    except:
        print("Error in getting generated model-id")
        p.terminate() # Force terminate training
        return HttpResponse("Error in getting generated model-id")


if __name__ == "__main__":
    list_datasets()
