# gnoduino - Python Arduino IDE implementation
# Copyright (C) 2010  Lucian Langa
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


import os
import sys

import gettext
_ = gettext.gettext

import misc

defaultFile = "preferences.txt"
defaultPath = os.path.expanduser('~/.arduino/preferences.txt')

class preferences(object):

	def __init__(self):
		self.defaults = []
		path = misc.getArduinoFile(defaultFile)
		if path is None: raise SystemExit(_("Cannot find %s") % defaultFile)
		for i in open(path):
			self.defaults.append(i.rstrip("\n").split("="))

	def getValue(self, value):
		for i in self.defaults:
			if i[0] == value:
				return i[1]
		return None

	def getSafeValue(self, value, fail):
		for i in self.defaults:
			if i[0] == value:
				return i[1]
		return fail

	def setValue(self, key, value):
		update = False
		for i in self.defaults:
			if i[0] == key:
				i[1] = str(value)
				update = True

		self.defaults.append([key, str(value)]) if update is not True else ""

	def saveValues(self):
		#fixme add backup copy in case things go wrong
		w = open(defaultPath, "w")
		for i in self.defaults:
			w.write(i[0]+"="+i[1]+"\n")
		w.close()
