"""from odb.odb_firmware import Odb

class odb_extended(Odb):

	def checkPoint(self):
		for x in self.modules:
			print(x.name + ' : ' + str(x.ready))

	def sendModuleUsed(self):
		if 'nrf24' in self.modules:
			data = {}
			for x in self.modules:
				data[x.name] = ''
			return data


	def go(self):
		self._init()
		self.checkPoint()
		while True:
			self._main_loop()

"""
from odb.odb_firmware import Odb

class odb_extended(Odb):

	def checkPoint(self):
		for x in self.modules:
			print(x.name + ' : ' + str(x.ready))

	def sendModuleUsed(self):
		if 'nrf24' in (x.name for x in self.modules):
			data = None
			data = {}
			data['modules'] = {}
			for x in self.modules:
				data['modules'][x.name] = str(x.ready)
			return data

	def go(self):
		self._init()
		self.checkPoint()
		print(self.sendModuleUsed())
		for x in self.modules:
			if x.name == 'nrf24':
				x.send_data(self.sendModuleUsed())
		while True:
			self._main_loop()
