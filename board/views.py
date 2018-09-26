from __future__ import print_function
from __future__ import absolute_import

from django.shortcuts import render
from django.http import HttpResponse
import sys
import os
from multiprocessing import Process

import grpc
from rearpb import  rearpb_pb2_grpc,rearpb_pb2

from .model_manager import ModelManager
from .common import exceptions

# Create your views here.
def get_client():
	""" Returns the GRPC client after performing a health check on the server"""
	try:
		channel =  grpc.insecure_channel('localhost:50051')
		client = rearpb_pb2_grpc.RearStub(channel)
		check = client.HealthCheck(rearpb_pb2.HealthCheckRequest())
		if check.ok:
			return client
	except:
		return None

def index(request):
	print("getting client")
	client = get_client()	
	if client is not None:
		response = client.SayHello(rearpb_pb2.HelloRequest(name='you'))
		print("Board client received: " + response.message)
		return HttpResponse(response.message)
	return HttpResponse("GRPC Server is unreachable")

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

	

	