from django.db import models
from mongoengine import *

#  #WARNING: NOT USED AS OF NOW
# class UploadFile(models.Model):
#     file = models.FileField(upload_to='files/%Y/%m/%d')



# class Dataset(EmbeddedDocument):
class Dataset(EmbeddedDocument):
	name = StringField(max_length=120, required=True)
	tags = ListField(StringField(max_length=120, required=True))
	#TODO: switch from auto indexing to manual later

class Model(EmbeddedDocument):
	name = StringField(max_length=120, required=True)
	#TODO: switch from auto indexing to manual later
	status = StringField(max_length=120, required=True)
	dataset = EmbeddedDocumentField(Dataset)
	logdir = StringField(max_length=120, required=True)	
	port = StringField(max_length=5, required=True)	
	
class Workspace(EmbeddedDocument):
	name = StringField(max_length=120, required=True)
	models = ListField(EmbeddedDocumentField(Model))
	
class User(Document):
	name = StringField(max_length=120, required=True)
	datasets = ListField(EmbeddedDocumentField(Dataset)) #reference
	#TODO: switch from auto indexing to manual later
	phones = ListField(StringField(max_length=120, required=True))
	workspaces = ListField(EmbeddedDocumentField(Workspace))
	meta = {'collection': 'user'}



