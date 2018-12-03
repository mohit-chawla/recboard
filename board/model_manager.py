import numpy as np
import random
import os
import logging
import pickle

from openrec.utils import Dataset
from openrec.utils.samplers import RandomPairwiseSampler
from openrec.utils.samplers import EvaluationSampler
from openrec.recommenders import BPR
from openrec.utils.evaluators import AUC
from openrec import ModelTrainer

from .constants import *

FORMAT = '%(asctime)-15s %(message)s'

class ModelManager:
    def __init__(self,model_id, db, recommender_name, train_iters, eval_iters, save_iters, train_sampler, val_sampler, test_sampler, evaluation_metric, path_to_dataset):
        self.recommender_name = recommender_name
        self.train_sampler = train_sampler
        self.val_sampler = val_sampler
        self.test_sampler = test_sampler
        self.evaluation_metric = evaluation_metric
        self.path_to_dataset = path_to_dataset
        
        self.train_iters = train_iters
        self.eval_iters = eval_iters
        self.save_iters = save_iters

        logging.basicConfig(format=FORMAT)
        self.logger = logging.getLogger(__name__)

        self.model_id = model_id
        self.db = db

        self.logger.info("ModelManager init generated model id=", self.model_id)

        
    def sample_data_and_train(self):
        self.logger.warning('sample_data_and_train called, pid = %d Please kill process on unsuccessful training', os.getpid())
        self.logger.info('-------- sample_data_and_train starts --------')
        
        total_users = 0
        interactions_count = 0
        with open(os.path.dirname(os.path.abspath(__file__))+self.path_to_dataset, 'r') as fin:
            for line in fin:
                interactions_count += int(line.split()[0])
                total_users += 1
        self.logger.info('############ collecting data.. ############')
        print("users: ",total_users,"interactions_count:", interactions_count)
        # radomly hold out an item per user for validation and testing respectively.
        val_structured_arr = np.zeros(total_users, dtype=[('user_id', np.int32), 
                                                        ('item_id', np.int32)]) 
        test_structured_arr = np.zeros(total_users, dtype=[('user_id', np.int32), 
                                                        ('item_id', np.int32)])
        train_structured_arr = np.zeros(interactions_count-total_users * 2, 
                                        dtype=[('user_id', np.int32), 
                                            ('item_id', np.int32)])

        interaction_ind = 0
        next_user_id = 0
        next_item_id = 0
        map_to_item_id = dict()  # Map item id from 0 to len(items)-1

        with open(os.path.dirname(os.path.abspath(__file__))+self.path_to_dataset, 'r') as fin:
            for line in fin:
                item_list = line.split()[1:]
                random.shuffle(item_list)
                for ind, item in enumerate(item_list):
                    if item not in map_to_item_id:
                        map_to_item_id[item] = next_item_id
                        next_item_id += 1
                    if ind == 0:
                        val_structured_arr[next_user_id] = (next_user_id, 
                                                            map_to_item_id[item])
                    elif ind == 1:
                        test_structured_arr[next_user_id] = (next_user_id, 
                                                            map_to_item_id[item])
                    else:
                        train_structured_arr[interaction_ind] = (next_user_id, 
                                                                map_to_item_id[item])
                        interaction_ind += 1
                next_user_id += 1
        model_dir = os.path.dirname(os.path.abspath(__file__))+"/data/"+str(self.model_id)
        if not os.path.exists(model_dir):
            os.makedirs(model_dir)
        pickle.dump( map_to_item_id, open(model_dir+"/"+str(self.model_id)+"_pickle", "wb" ) )

        self.logger.info('############ instantiating dataset.. ############')

        

        train_dataset = Dataset(raw_data=train_structured_arr,
                                total_users=total_users, 
                                total_items=len(map_to_item_id), 
                                name='Train')
        val_dataset = Dataset(raw_data=val_structured_arr,
                            total_users=total_users,
                            total_items=len(map_to_item_id),
                            num_negatives=500,
                            name='Val')
        test_dataset = Dataset(raw_data=test_structured_arr,
                            total_users=total_users,
                            total_items=len(map_to_item_id),
                            num_negatives=500,
                            name='Test')

        self.logger.info("############ instantiating Samplers.. ############")

        

        train_sampler = RandomPairwiseSampler(batch_size=1000, 
                                            dataset=train_dataset, 
                                            num_process=5)
        val_sampler = EvaluationSampler(batch_size=1000, 
                                        dataset=val_dataset)
        test_sampler = EvaluationSampler(batch_size=1000, 
                                        dataset=test_dataset)

        self.logger.info("############ instantiating Recommender.. ############")

        

        bpr_model = BPR(batch_size=1000, 
                        total_users=train_dataset.total_users(), 
                        total_items=train_dataset.total_items(), 
                        dim_user_embed=50, 
                        dim_item_embed=50, 
                        save_model_dir='data/'+str(self.model_id)+'/', 
                        train=True, serve=True)
        print("dataset specs,",train_dataset.total_users(),train_dataset.total_items())

        self.logger.info("############ instantiating Evaluator.. ############")
        

        auc_evaluator = AUC()

        self.logger.info("############ instantiating Model trainer.. ############")

        

        model_trainer = ModelTrainer(model=bpr_model)

        print("############ starting training.. ############")

        print("Fetching model for id:",self.model_id)
        model_db = self.db.get('model',id=self.model_id)
        print("model_found:",model_db.id)

        model_db.status = MODEL_STATUS_TRAINING
        self.db.insert('model',model_db)

        model_trainer.train(total_iter=self.train_iters,  # Total number of training iterations
                            eval_iter=self.eval_iters,    # Evaluate the model every "eval_iter" iterations
                            save_iter=self.save_iters,   # Save the model every "save_iter" iterations
                            train_sampler=train_sampler, 
                            eval_samplers=[val_sampler, test_sampler], 
                            evaluators=[auc_evaluator])
        # self.logger.info("THIS IS WHEN MODEL WILL START TRAINING... returning")
        self.logger.info("-------- sample_data_and_train ends --------")

        model_db = self.db.get('model',id=self.model_id)
        print("model_found:",model_db.id)

        model_db.status = MODEL_STATUS_TRAINED
        model_db.file_location = "/mohit"
        self.db.insert('model',model_db)