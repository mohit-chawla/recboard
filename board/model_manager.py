import numpy as np
import random
import os
import logging


from openrec.utils import Dataset
from openrec.utils.samplers import RandomPairwiseSampler
from openrec.utils.samplers import RandomPointwiseSampler
from openrec.utils.samplers import EvaluationSampler
from openrec.recommenders import BPR
from openrec.recommenders import PMF
from openrec.recommenders import UCML
from openrec.recommenders import VBPR
from openrec.recommenders import DRR
from openrec.recommenders import RNNRec
from openrec.utils.evaluators import AUC
from openrec import ModelTrainer

from .constants import *

FORMAT = '%(asctime)-15s %(message)s'

class ModelManager:
    def __init__(self,model_id, db, recommender_name, train_sampler, val_sampler, test_sampler, evaluation_metric, path_to_dataset):
        self.recommender_name = str(recommender_name).lower()
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

        print("#"*7) # TODO KS convert this to a log
        print(self.recommender_name, self.train_sampler, self.val_sampler, self.test_sampler, self.evaluation_metric, self.path_to_dataset,)
        print("#"*7)

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

        if self.recommender_name=="pmf" or self.recommender_name=="drr":
            train_sampler = RandomPointwiseSampler(batch_size=1000, 
                                                dataset=train_dataset,
                                                num_process=5)
        else:
            train_sampler = RandomPairwiseSampler(batch_size=1000, 
                                                dataset=train_dataset, 
                                                num_process=5)    
        val_sampler = EvaluationSampler(batch_size=1000, 
                                        dataset=val_dataset)
        test_sampler = EvaluationSampler(batch_size=1000, 
                                        dataset=test_dataset)

        self.logger.info("############ instantiating Recommender.. ############")

        
        model_save_dir = self.recommender_name+'_recommender/'
        if self.recommender_name=="bpr":
            print("recommender chosen is:", self.recommender_name)
            recommender_model = BPR(batch_size=1000, 
                            total_users=train_dataset.total_users(), 
                            total_items=train_dataset.total_items(), 
                            dim_user_embed=50, 
                            dim_item_embed=50, 
                            save_model_dir=model_save_dir, 
                            train=True, serve=True)
        elif self.recommender_name=="drr":
            print("recommender chosen is:", self.recommender_name)
            recommender_model = DRR(batch_size=1000, 
                            total_users=train_dataset.total_users(), 
                            total_items=train_dataset.total_items(), 
                            dim_user_embed=50, 
                            dim_item_embed=50, 
                            save_model_dir=model_save_dir, 
                            train=True, serve=True)
        elif self.recommender_name=="pmf":
            print("recommender chosen is:", self.recommender_name)
            recommender_model = PMF(batch_size=1000, 
                            total_users=train_dataset.total_users(), 
                            total_items=train_dataset.total_items(), 
                            dim_user_embed=50, 
                            dim_item_embed=50, 
                            save_model_dir=model_save_dir, 
                            train=True, serve=True)
        elif self.recommender_name=="rnnrec":
            print("recommender chosen is:", self.recommender_name,"BUT STILL USING BPR")
            print("So sorry! we need you to give us the max_seq_len, num_units as well, so switching to BPR")
            recommender_model = BPR(batch_size=1000, 
                            total_users=train_dataset.total_users(), 
                            total_items=train_dataset.total_items(), 
                            dim_user_embed=50, 
                            dim_item_embed=50, 
                            save_model_dir=model_save_dir, 
                            train=True, serve=True)
        elif self.recommender_name=="ucml":
            print("recommender chosen is:", self.recommender_name)
            recommender_model = UCML(batch_size=1000, 
                            total_users=train_dataset.total_users(), 
                            total_items=train_dataset.total_items(), 
                            dim_user_embed=50, 
                            dim_item_embed=50, 
                            save_model_dir=model_save_dir, 
                            train=True, serve=True)
        elif self.recommender_name=="vbpr":
            print("recommender chosen is:", self.recommender_name,"BUT STILL USING BPR")
            print("So sorry! we need you to give us the dim_v as well, so switching to BPR")
            recommender_model = BPR(batch_size=1000, 
                            total_users=train_dataset.total_users(), 
                            total_items=train_dataset.total_items(), 
                            dim_user_embed=50, 
                            dim_item_embed=50, 
                            save_model_dir=model_save_dir, 
                            train=True, serve=True)


        self.logger.info("############ instantiating Evaluator.. ############")
        

        auc_evaluator = AUC()

        self.logger.info("############ instantiating Model trainer.. ############")

        

        model_trainer = ModelTrainer(model=recommender_model)

        print("############ starting training.. ############")

        print("Fetching model for id:",self.model_id)
        model_db = self.db.get('model',id=self.model_id)
        print("model_found:",model_db.id)

        model_db.status = MODEL_STATUS_TRAINING
        self.db.insert('model',model_db)

        model_trainer.train(total_iter=self.train_iters,  # Total number of training iterations,             1000
                            eval_iter=self.eval_iters,    # Evaluate the model every "eval_iter" iterations, 10
                            save_iter=self.save_iters,   # Save the model every "save_iter" iterations,      10
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