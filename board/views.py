from __future__ import absolute_import

from django.shortcuts import render
from django.http import HttpResponse
import sys
import os
from multiprocessing import Process

from .model_manager import ModelManager
from .common import exceptions

def index(request):
	return HttpResponse("All good, server is up")

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
