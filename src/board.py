# Arduino python implementation
# Copyright (C) 2010  Lucian Langa <cooly@gnome.eu.org>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#

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
		self.programmers = []
		self.defaults = []
		conf = ConfigParser.RawConfigParser()
		conf.read('BOARDS')
		c = 1
		for i in conf.sections():
			v = dict(conf.items(i))
			v['id'] = c
			v['desc'] = i
			self.boards.append(v)
			c = c + 1
		p = prefs.preferences()
		if config.cur_board == -1:
			config.cur_board = self.getBoardIdByName(p.getValue("board")) - 1

	def getBoards(self):
		return self.boards

	def getBoard(self):
		return config.cur_board

	def getBoardMemory(self, id):
		return self.boards[id]['maximum_size']

	def getBoardMCU(self, id):
		return self.boards[id]['mcu']

	def getBoardFCPU(self, id):
		return self.boards[id]['f_cpu']

	def getPGM(self, id):
		return self.boards[id]['protocol']

	def getPGMSpeed(self, id):
		return self.boards[id]['speed']

	def getFuseLock(self, id):
		return self.boards[id]['lock_bits']

	def getFuseUnlock(self, id):
		return self.boards[id]['unlock_bits']

	def getFuseHigh(self, id):
		return self.boards[id]['high_fuses']

	def getFuseLow(self, id):
		return self.boards[id]['low_fuses']

	def getPath(self, id):
		return self.boards[id]['path']

	def getBootloader(self, id):
		return self.boards[id]['file']

	def setBoard(self, id):
		print "set board %d" % (id -1)
		config.cur_board = (id - 1)

	def getBoardIdByName(self, name):
		for i in self.boards:
			if i['name'] == name:
				return i['id']
