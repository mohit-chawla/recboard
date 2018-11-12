from mongoengine import *
from .common import exceptions
from .models import *

class RecboardDB:
	config = {}
	db_type = 'mongodb'
	# folder = 'databases'
	host = 'localhost'
	port = 27017
	name = 'recboard_db'
	collections = {
		'index' : 'index',
		'user' : 'User',
		'dataset': 'Dataset',
		'model' : 'Model',
		'workspace' : 'Workspace'
	}

	def __init__(self):
		pass

	def get_db_name(self):
		"""return db_name """
		if self.db_type == "mongod":
			return self.name

	def get_collection(self, collection):
		"""Get the corresponding database collection/table"""
		if collection not in self.collections:
			raise InvalidCollectionName
		# return Model class name eval here User, Model ...
		return eval(self.collections[collection])



	@property
	def connection(self):
		"""
			Get mongo connection
			
			Note: Every mongo client maintains a pool of connections
			capped at maxPoolSize internally, so only one client is
			enough.

		"""
		if getattr(self, '_connection', None) is None:
			if self.db_type == 'mongodb':
				self._connection = connect(self.name,
					# host=self.host,
					port=self.port
				)
		return self._connection

	# def generate_id(self):
	#     return generate_id()

	def select(self, colname, *args, **kwargs):
		"""Get all document(s) in collection colname with filter in **kwargs"""
		return self.get_collection(colname).objects(*args, **kwargs)

	def count(self, colname, *args, **kwargs):
		"""Get count of  document in collection colname with filter in **kwargs"""
		return self.get_collection(colname).objects(*args, **kwargs).count()

	def get(self, colname, *args, **kwargs):
		"""Get first document in collection colname with filter in **kwargs"""
		col = self.get_collection(colname)
		if not args and not kwargs:
			return col.objects
		return col.objects(*args, **kwargs)[0]

	def insert(self, colname, *args, **kwargs):
		"""Insert all documents in collection colname"""
		for doc in args:
			doc.save()

	def update(self,colname, *args, **kwargs):
		"""Update all documents in collection colname with filter in **kwargs"""
		# doc_to_update = self.get(colname,*args)
		# doc_to_update.update(kwargs)
		raise NotImplementedError
	
	def delete(self, colname, *args, **kwargs):
		"""Delete ALL documents in collection colname with filter in **kwargs"""
		return self.get_collection(colname).objects(*args, **kwargs).delete()

	def __dir__(self):
		"""
		Implement when needed
		"""
		pass

if __name__ == "__main__":
	db = RecboardDB()
	conn = db.connection
	# #insert example
	# # kriti = User(name="Kriti")
	# # db.insert('user',kriti)
	# mohit = User(name="Mohit",phones=['9294714415'])
	# db.insert('user',mohit)
	# # get collection usage 
	# print(db.get_collection('user'))
	# # get all 
	# db.select('user',name='Mohit')
	# got = db.get('user',name='Mohit')
	# print("name:",got.name,"phones:",got.phones)
	# got.phones.append('9939')
	# print(got.phones)
	# db.insert('user',got)
	# # print(got.phones)
	# # db.update('user',name='Mohit',phones = ['9999'])
	# #get first
	# print(db.get('user',name='Mohit').name)
	# #get count
	# print(db.count('user',name='Mohit'))
	# db.insert('dataset',Dataset(name="mohit_dataset",tags=["tags"]))
	user = db.get('user',id="5be64272d7bea8481dd4a569")
	print(user.id)