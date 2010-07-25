
import os
import ConfigParser
import config
import prefs

def readRefaults():
	f = open(os.path.expanduser('~/.arduino/preferences.txt'))
	for i in f:
		self.defaults.append(i.split("="))
	for i in self.defaults:
		if i[0] == 'board':
			print i


class Board(object):
	def __init__(self):
		self.board = 0
		self.boards = []
		self.defaults = []
		conf = ConfigParser.RawConfigParser()
		conf.read('BOARDS')
		c = 1
		for i in conf.sections():
			self.boards.append([c, conf.get(i, "name"), i, conf.get(i, 'max_size'), conf.get(i, 'mcu'), conf.get(i, "f_cpu")])
			c = c + 1
		#print self.boards
		p = prefs.preferences()
		if config.cur_board == -1:
			config.cur_board = self.getBoardIdByName(p.getValue("board")) - 1

	def getBoards(self):
		return self.boards

	def getBoard(self):
		return config.cur_board

	def getBoardMemory(self, id):
		return self.boards[id][3]

	def getBoardMCU(self, id):
		return self.boards[id][4]

	def getBoardFCPU(self, id):
		return self.boards[id][5]

	def setBoard(self, id):
		print "set board %d" % (id -1)
		config.cur_board = (id - 1)

	def getBoardIdByName(self, name):
		for i in self.boards:
			if i[1] == name:
				return i[0]
