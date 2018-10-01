from django.test import TestCase
from board.common.idgen import IdGenerator

class IdGeneratorTestCase(TestCase):

	# def test_deterministic(self):
	def setUp(self):
		self.generator = IdGenerator()

	def test_unequal(self):
		"""
		Two randomly generated ids should not be equal
		"""
		id1 = self.generator.generate()
		id2 = self.generator.generate()
		self.assertNotEqual(id1, id2)

	def equal_length(self):
		"""
		Length should be equal
		"""
		id1 = self.generator.generate()
		id2 = self.generator.generate()
		self.AssertEqual(len(id1), len(id2))
		