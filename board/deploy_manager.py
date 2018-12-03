# from openrec.recommenders import recommender

# print("hi")
# r = recommender.Recommender(save_model_dir="data/5bea1974d7bea809715eee1a",train=False,serve=True)
# print(r._save_model_dir)
# r.build()
# r.restore(restore_serve=True)
# # r.serve(batch_data=[1])


from openrec.recommenders import BPR
import numpy as np
from openrec.utils import Dataset
import pickle
from openrec.utils.samplers import EvaluationSampler
from openrec.utils.evaluators import EvalManager
from openrec.utils.evaluators import AUC
from openrec import ModelTrainer
from .db import RecboardDB
import os
from .common.exceptions import *

# # 5551 16980

# total_users = 5551
# total_items = 16980
# interactions_count = 204986
# # users:  5551 interactions_count: 204986
# # r = BPR(save_model_dir="data/5bea1974d7bea809715eee1a",train=False,serve=True)
# r= BPR(batch_size=1000,total_users=5551, total_items=16980, dim_user_embed=50, dim_item_embed=50, 
#                         save_model_dir='data/5bff520409a9a5d3c9b0569f', 
#                         train=False, serve=True)
# print(r._save_model_dir)
# r.build()
# r.restore(restore_serve=True)

# map_to_item_id = {1:1}

# data_structured_arr = np.zeros(interactions_count-total_users * 2, 
#                                         dtype=[('user_id', np.int32), 
#                                             ('item_id', np.int32)])

# map_to_item_id = pickle.load(open("data/5bff520409a9a5d3c9b0569f/5bff520409a9a5d3c9b0569f_pickle",'rb'))

# users = [0,1,2]
# items = ['70','5','6']

# for i,user in enumerate(users):
# 	data_structured_arr[users[i]] = (users[i],map_to_item_id[items[i]])

# dataset =  Dataset(raw_data=data_structured_arr,
#                                 total_users=total_users, 
#                                 total_items=len(map_to_item_id), 
#                                 name='Test')

# sampler = EvaluationSampler(batch_size=1000, dataset=dataset)
# auc_evaluator = AUC()
# model_trainer = ModelTrainer(model=r)
# model_trainer.train(total_iter=0,  # Total number of training iterations
#                     eval_iter=0,    # Evaluate the model every "eval_iter" iterations
#                     save_iter=0,   # Save the model every "save_iter" iterations
#                     train_sampler=sampler, 
#                     eval_samplers=[sampler], 
#                     evaluators=[auc_evaluator])
# result = model_trainer._evaluate(sampler)
# print("result was:",result)


class DeployManager():

	def __init__(self):
		self.model_objects = {} #model_id:model_object
		self.model_maps = {} # model_id:map_to_item_ids
		self.model_details = {} # model_id: {'interactions_count':, 'total_users': }
		self.db = RecboardDB()
		self.conn = self.db.connection 

	def deploy(self, model_id):
		"""Deploys a model with id:model_id"""
		assert(type(model_id)==str)

		if model_id not in self.model_objects:
			print(model_id,"not found in model_objects")
			try:
				self._create(model_id)
			except:
				return False
				
		return True

	def is_deployed(self, model_id):
		"""Check if a model is deployed"""
		assert(type(model_id)==str)
		return model_id in self.model_objects


	def predict(self, model_id, users_arr, items_arr):
		print("PREDICT CALLED,model_id",model_id, type(model_id), users_arr, items_arr)
		# assert(type(model_id) == str)
		print("HERE>....")
		
		if model_id not in self.model_objects:
			print(model_id,"not found in model_objects")
			self._create(model_id)

		print(self.model_objects)
		# print(self.model_maps)
		# print(self.model_details)

		interactions_count = self.model_details[model_id]['interactions_count']
		total_users = self.model_details[model_id]['total_users']
		data_structured_arr = np.zeros(interactions_count-total_users * 2, 
		                                        dtype=[('user_id', np.int32), 
		                                            ('item_id', np.int32)])

		print("interactions_count:",interactions_count,"users:",total_users)

		for i in range(len(items_arr)):
			if items_arr[i] not in self.model_maps[model_id]:
				raise InvalidItemException("item "+items_arr[i]+" not found in training data")

			data_structured_arr[users_arr[i]] = (users_arr[i],self.model_maps[model_id][items_arr[i]])

		print("creating dataset ...")
		dataset =  Dataset(raw_data=data_structured_arr, total_users=total_users, total_items=len(self.model_maps[model_id]), name='Test')
		print("initiating sampler ...")
		sampler = EvaluationSampler(batch_size=1000, dataset=dataset)
		print("initiating evaluator ...")
		auc_evaluator = AUC() #TODO
		print("trainer evaluator ...")
		model_trainer = ModelTrainer(model=self.model_objects[model_id])
		#need to call train to set eval manager and stuff
		model_trainer.train(total_iter=0, eval_iter=0, save_iter=0, train_sampler=sampler, eval_samplers=[sampler], evaluators=[auc_evaluator])
		print("evaulating results ...")
		result = model_trainer._evaluate(sampler)
		print("final result for users:",users_arr,"items:",items_arr,"is:",result)
		return result

	
	def _get_model_dir(self, model_id):
		return os.path.dirname(os.path.abspath(__file__))+"/data/"+model_id

	def _load_model_map(self, model_id):
		return pickle.load(open(self._get_model_dir(model_id)+'/'+model_id+"_pickle", 'rb'))

	def _create(self, model_id):
		print("trying to create model_object...")
		assert(type(model_id) == str) #None auto checked
		# get model_details_from db 
		# details needed =  model_type, batch_size=1000,total_users=5551, total_items=16980, interactions_count, dim_user_embed=50, dim_item_embed=50, save_model_dir
		# based on model_type, create an object
		# return object
		model_db = self.db.get('model',id=model_id)
		recommender = model_db['recommender']
		# total_users = model_db['total_users']
		# total_items = model_db['total_items']
		# batch_size = model_db['batch_size']
		# dim_user_embed = model_db['dim_user_embed']
		# dim_item_embed = model_db['dim_item_embed']
		# interactions_count = model_db['interactions_count']
		print("RECOMMENDER IN DB:",recommender,type(recommender))
		total_users = 5551
		total_items = 16980
		interactions_count = 204986
		model_dir = self._get_model_dir(model_id)
		r = None
		if recommender == "BPR":
			r= BPR(batch_size=1000,total_users=total_users, total_items=16980, dim_user_embed=50, dim_item_embed=50, save_model_dir=model_dir, train=False, serve=True)
			print("recommender created...")
		if not r:
			raise InvalidRecommenderException

		print("populating model details in map...",r)
		# model goes into memory
		self.model_objects[model_id] = r
		self.model_maps[model_id] = self._load_model_map(model_id)
		self.model_details[model_id] = {'total_users':total_users, 'total_items':total_items , 'interactions_count':interactions_count}



