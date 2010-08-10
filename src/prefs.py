
import os

class preferences(object):

	def __init__(self):
		self.defaults = []
		try:
			f = open(os.path.expanduser('~/.arduino/preferences.txt'))
			for i in f:
				self.defaults.append(i.rstrip("\n").split("="))
		except:	None

	def getValue(self, value):
		for i in self.defaults:
			if i[0] == value:
				return i[1]
