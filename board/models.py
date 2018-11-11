from django.db import models
from mongoengine import *
from bson import ObjectId

#  #WARNING: NOT USED AS OF NOW
# class UploadFile(models.Model):
#     file = models.FileField(upload_to='files/%Y/%m/%d')



# class Dataset(EmbeddedDocument):
class Dataset(Document):
	name = StringField(max_length=120, required=True)
	tags = ListField(StringField(max_length=120, required=True))
	meta = {'collection': 'dataset'}
	owner  = ObjectIdField()
	path = StringField(max_length=120, required=True)
	#TODO: switch from auto indexing to manual later

class Model(Document):
	name = StringField(max_length=120, required=True)
	#TODO: switch from auto indexing to manual later
	status = StringField(max_length=120, required=True)
	train_dataset = ObjectIdField()
	test_dataset = ObjectIdField()
	logdir = StringField(max_length=120, required=True)	
	port = StringField(max_length=5, required=True)
	file_location = StringField(max_length=120)
	workspace_id = ObjectIdField()
	meta = {'collection': 'model'}

	
class Workspace(Document):
	name = StringField(max_length=120, required=True)
	models = ListField(ObjectIdField())
	meta = {'collection': 'workspace'}
	user_id = ObjectIdField()
	
class User(Document):
	name = StringField(max_length=120, required=True)
	datasets = ListField(ObjectIdField()) #reference
	#TODO: switch from auto indexing to manual later
	phones = ListField(StringField(max_length=120, required=True))
	workspaces = ListField(ObjectIdField())
	meta = {'collection': 'user'}



