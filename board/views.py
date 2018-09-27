from __future__ import absolute_import

from django.shortcuts import render
from django.http import HttpResponse
import sys

from .common import exceptions

def index(request):
	return HttpResponse("All good, server is up")