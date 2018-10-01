import time
import random

class IdGenerator():
	def __init__(self):
		pass

	def generate(self):
		return str(abs(hash(str(random.getrandbits(128))+str(time.time()))))


if __name__ == "__main__":
	idgen = IdGenerator()
	print(idgen.generate())