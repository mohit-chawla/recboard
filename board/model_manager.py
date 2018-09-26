import numpy as np
import random
import os

class ModelManager:
    def __init__(self, recommender_name, train_sampler, val_sampler, test_sampler, evaluation_metric, path_to_dataset):
        self.recommender_name = recommender_name
        self.train_sampler = train_sampler
        self.val_sampler = val_sampler
        self.test_sampler = test_sampler
        self.evaluation_metric = evaluation_metric
        self.path_to_dataset = path_to_dataset

        self.model_id = '100xxks'
        print("ModelManager init generated model id=", self.model_id)

        
    def sample_data_and_train(self):
        print("sample_data_and_train called, pid =", os.getpid())
        print("-------- sample_data_and_train starts --------")
        total_users = 0
        interactions_count = 0
        with open(os.path.dirname(os.path.abspath(__file__))+self.path_to_dataset, 'r') as fin:
            for line in fin:
                interactions_count += int(line.split()[0])
                total_users += 1
        print("############ collecting data.. ############")

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


        print("############ instantiating dataset.. ############")

        from openrec.utils import Dataset

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

        print("############ instantiating Samplers.. ############")

        from openrec.utils.samplers import RandomPairwiseSampler
        from openrec.utils.samplers import EvaluationSampler

        train_sampler = RandomPairwiseSampler(batch_size=1000, 
                                            dataset=train_dataset, 
                                            num_process=5)
        val_sampler = EvaluationSampler(batch_size=1000, 
                                        dataset=val_dataset)
        test_sampler = EvaluationSampler(batch_size=1000, 
                                        dataset=test_dataset)

        print("############ instantiating Recommender.. ############")

        from openrec.recommenders import BPR

        bpr_model = BPR(batch_size=1000, 
                        total_users=train_dataset.total_users(), 
                        total_items=train_dataset.total_items(), 
                        dim_user_embed=50, 
                        dim_item_embed=50, 
                        save_model_dir='bpr_recommender/', 
                        train=True, serve=True)


        print("############ instantiating Evaluator.. ############")

        from openrec.utils.evaluators import AUC

        auc_evaluator = AUC()

        print("############ instantiating Model trainer.. ############")

        from openrec import ModelTrainer

        model_trainer = ModelTrainer(model=bpr_model)

        print("############ starting training.. ############")

        model_trainer.train(total_iter=10000,  # Total number of training iterations
                            eval_iter=1000,    # Evaluate the model every "eval_iter" iterations
                            save_iter=10000,   # Save the model every "save_iter" iterations
                            train_sampler=train_sampler, 
                            eval_samplers=[val_sampler, test_sampler], 
                            evaluators=[auc_evaluator])
        # print("THIS IS WHEN MODEL WILL START TRAINING... returning")
        print("-------- sample_data_and_train ends --------")