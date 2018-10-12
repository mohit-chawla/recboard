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

from django.http import JsonResponse

logging.getLogger(__name__)


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


class HomePage(TemplateView):
    """
        This is a class based view for home page (/home)
    """
    template_name = 'home.html'


def create(request):
    print ('Parent process pid:', os.getpid())
    PATH_TO_DATASET = '/files/data/users.dat'
    model_controller_obj = ModelManager('BPR', 'train_samp', 'val_samp', 'test_samp', 'AUC', PATH_TO_DATASET)

    p = Process(target=ModelManager.sample_data_and_train, args=(model_controller_obj,))
    p.start()
    p.join(2)

    try:
        generated_model_id = model_controller_obj.model_id
        err = "No err "
        # return HttpResponse(str(generated_model_id + err))
        return JsonResponse({'generated_model_id': generated_model_id, 'err':err})
    except:
        print("Error in getting generated model-id")
        p.terminate() # Force terminate training
        # return HttpResponse("Error in getting generated model-id")
        return JsonResponse({'generated_model_id': '', 'err':'Error in getting generated model-id'})
