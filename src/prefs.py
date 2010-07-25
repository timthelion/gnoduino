
import os

class preferences(object):

	def __init__(self):
		self.defaults = []
		f = open(os.path.expanduser('~/.arduino/preferences.txt'))
		for i in f:
			self.defaults.append(i.rstrip("\n").split("="))

	def getValue(self, value):
		for i in self.defaults:
			if i[0] == 'board':
				return i[1]
