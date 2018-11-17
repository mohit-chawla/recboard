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
from .constants import *
from .models import *
import json
from random import randint

from django.shortcuts import render_to_response,redirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from openrec import recommenders
from time import time
from bson import ObjectId
from django.utils.encoding import smart_str

logging.getLogger(__name__)

db = RecboardDB()
conn = db.connection    


# def index(request):
#     return HttpResponse("All good, server is up")

class Index(TemplateView):
    """
        This is a class based view for home page (/home)
    """
    template_name = 'index.html'


def login_user(request):
    logout(request)
    username = password = ''
    context = {}
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect(BOARD_HOME)
    return redirect(BOARD_HOME)


def save_uploaded_file(user,filename,file):
    directory = "data/"
    if not os.path.exists(directory):
        print("making dir ...")
        os.makedirs(directory)
    print("saving file:", directory+str(user.id) + "_file_" + filename)
    with open(directory+str(user.id) + "_file_" + filename, 'wb+') as destination:
        #use chunks instead of read to avoid having large files in memory
        for chunk in file.chunks():
            destination.write(chunk)
        
        new_dataset=  Dataset(name=filename,tags=["tags"])
        db.insert('dataset',new_dataset)
        user.datasets.append(new_dataset.id)#add this dataset to user
        db.insert('user',user)  #update user doc
        logging.info("Uploaded file saved","file:",filename,"location:",destination)

@login_required(login_url=BOARD_HOME)
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

@login_required(login_url=BOARD_HOME)
def list_models(request):
    """Returns list of datasets"""
    print(request)
    wid = request.GET.get('wid','')

    models = db.select('model',workspace_id=ObjectId(wid))
    print("LISTING MODELS FOR WID:",wid)
    print("models:",models)
    models_dict = {}
    for model in models:
        models_dict[str(model.id)] = [model.status,model.port,model.file_location,model.name,model.notes,model.train_iters,model.eval_iters,model.save_iters,model.start_time,model.recommender]
    print("models_dict:",models_dict)
    return JsonResponse(models_dict,safe=False)

@login_required(login_url=BOARD_HOME)
def list_datasets(request):
    """Returns list of datasets"""
    user = get_dummy_user()
    u = db.get('user',name=user.name)
    user_datasets = [db.get('dataset',id=did) for did in u.datasets]
    return JsonResponse([[str(ds.id),ds.name] for ds in user_datasets],safe=False)

@login_required(login_url=BOARD_HOME)
def list_workspaces(request):
    """Returns list of datasets"""
    user = get_dummy_user()
    u = db.get('user',name=user.name) #TODO: replace with actual user
    # return JsonResponse([workspace.name for workspace in db.select('workspace',user_id=u.id)],safe=False)
    workspaces = {}
    for workspace_doc in db.select('workspace',user_id=u.id):
        workspaces[str(workspace_doc.id)] = [workspace_doc.name] #should be dict but json parsing in js in tideous
    return JsonResponse(workspaces)

@login_required(login_url=BOARD_HOME)
def get_model_status(request):
    """
        Get status of a model
        returns one of constants MODEL_STATUS_*
    """
    mid = request.GET.get('mid','')
    print("checking model status for",mid)
    if not mid:
        return JsonResponse("",safe=False)

    model = db.get('model',id=ObjectId(mid))
    return JsonResponse(model.status,safe=False)

@login_required(login_url=BOARD_HOME)
def list_recommenders(request):
    """List available recommenders with openrec"""
    _recs = []
    for func in dir(recommenders):
        if callable(getattr(recommenders, func)) and func.lower()!="recommender":
            _recs.append(func)
    return JsonResponse(_recs,safe=False)


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
    """
        @Returns: new workspace id , name(custom or default)
    """
    body = get_request_body(request)
    if not body or not "workspace_name" in body:
        HttpResponseBadRequest("Bad request")
    
    dummy = get_dummy_user()
    user = db.get('user',name=dummy.name) #TODO: replace with actual user
    #TODO: replace with actual update op using addset for better perf
    new_workspace = Workspace(name=body['workspace_name'],user_id=user.id)
    db.insert('workspace', new_workspace)
    user.workspaces.append(new_workspace.id)
    db.insert('user',user)
    return JsonResponse([str(new_workspace.id), body['workspace_name']],safe=False)

def get_model_port(request):
    dummy = get_dummy_user()
    user = db.get('user',name=dummy.name) #TODO: replace with actual user
    #TODO: replace with actual update op using addset for better perf
    if not user or not user.workspaces or not user.workspaces.models:
        return HttpResponseBadRequest("No workspace or model")
    return JsonResponse({"port":user.workspaces.models[-1].port})

def get_model_default_name(user):
    """creates default name for a model"""
    name = ""
    if user:
        name += (user.name + "_")
    name += str(time())
    return name

@login_required(login_url=BOARD_HOME)
def delete_model(request):
    body = get_request_body(request)

    if not body or not 'mid' in body:
        return HttpResponseBadRequest("Bad request")

    mid = body['mid']
    db.delete('model',id=ObjectId(mid)) 
    return JsonResponse("Deleted",safe=False)

@login_required(login_url=BOARD_HOME)
def delete_workspace(request):
    """Deletes a workspace and related models"""
    #find all models in that workspace and delete them
    #delete the workspace
    body = get_request_body(request)

    if not  body or not 'wid' in body:
        return HttpResponseBadRequest("Bad request")
    wid = body['wid']
    models = db.select('model',workspace_id=ObjectId(wid))
    for model in models:
        db.delete('model',id=model.id)
    db.delete('workspace',id=ObjectId(wid))
    return JsonResponse("Deleted",safe=False)


def _serve(filename,file_path):
    """Serves a file"""
    if not filename or not file_path:
        raise InvalidArgumentException

    response = HttpResponse(content_type='application/force-download') 
    response['Content-Disposition'] = 'attachment; filename=%s' % smart_str(filename)
    response['X-Sendfile'] = smart_str(file_path)
    
    return response


def download_model(request):
    """Serves a model file with model-id:mid"""
    mid = request.GET.get('mid','')
    if not mid:
        return JsonResponse("",safe=False)

    print("requested mdoel file for",mid)   
    
    filename = "model.ckpt.index"
    file_path = "data/"+mid+"/{0}".format(filename)

    try:
        response = _serve(filename, file_path)
    except:
        response = HttpResponseBadRequest("Model file not found")

    return response


class HomePage(TemplateView):
    """
        This is a class based view for home page (/home)
    """
    template_name = 'home.html'

def create(request):
    body = get_request_body(request)
    _required = ['recommender','train_dataset','test_dataset',"workspace_id","train_iters","eval_iters","save_iters"]
    for key in _required:
        if not key in body:
            return HttpResponseBadRequest("Bad request")

    recommender = body['recommender']
    workspace_id = ObjectId(body['workspace_id'])
    train_dataset = db.get('dataset',id=ObjectId(body['train_dataset']))
    test_dataset = db.get('dataset',id=ObjectId(body['test_dataset']))

    train_iters = int(body['train_iters'])
    eval_iters = int(body['eval_iters'])
    save_iters = int(body['save_iters'])

    print ('Parent process pid:', os.getpid())
    user = get_dummy_user()
    body = get_request_body(request)
    
    if 'name' in body:
        model_name =body['name'] #user provided custom name
    else:
        model_name = get_model_default_name(user) #user did not provide name, create a name

    notes = ""
    if 'notes' in body:
        notes = body['notes']

    print("MODEL NAME:",model_name)
    print("MODEL NOTES:",notes)
    # TODO: maintain a list of available ports later
    tensorboard_port = str(randint(6000,7000)) 
    print("port generated", tensorboard_port,"Starting tb")

    model = Model(name=model_name,recommender=recommender,train_iters=train_iters,eval_iters=eval_iters,save_iters=save_iters,notes=notes,status=MODEL_STATUS_CREATED, train_dataset= train_dataset.id,test_dataset=test_dataset.id,logdir=LOG_DIR, port=tensorboard_port,workspace_id=workspace_id)
    db.insert('model', model) #insert new model
    workspace = db.get('workspace',id=workspace_id)
    workspace.models.append(model.id)
    db.insert('workspace',workspace)
    model_id = model.id #id of newly created model
    print("created new model id:",model_id,"for workspace id:",workspace.id)

    # TODO: ensure user.id is not None
    dataset_path = DATASET_PATH_PREFIX+str(user.id)+"_file_"+train_dataset.name
    print("\n\n Fetching dataset from path = ", dataset_path ,"\n\n")
    model_controller_obj = ModelManager(model_id, db, recommender, train_iters, eval_iters, save_iters, 'train_samp', 'val_samp', 'test_samp', 'AUC', dataset_path)
    
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
    
    
    # TODO: add try catch here (in case the tensorboard couldnt be started)
    
    cmd = "tensorboard --logdir "+LOG_DIR+" --host localhost --port "+tensorboard_port 
    tb_p = Process(target=os.system, args=(cmd,))
    tb_p.start()
    tb_p.join(2)
    
    print("TB started")

    return JsonResponse({'msg':tensorboard_port,'mid':str(model_id)})
    # except:
    #     print("Error in getting generated model-id")
    #     p.terminate() # Force terminate training
    #     return JsonResponse({'msg':"Error in getting generated model-id"})


if __name__ == "__main__":
    list_datasets()
    