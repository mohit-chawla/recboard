from __future__ import print_function
from __future__ import absolute_import

from django.shortcuts import render
from django.http import HttpResponse
import sys

import grpc
from rearpb import  rearpb_pb2_grpc,rearpb_pb2

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

# def create(request):
	