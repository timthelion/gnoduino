
# Arduino python implementation
# Copyright (C) 2010  Lucian Langa
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.


import re
import os
import tempfile

MAIN = "hardware/arduino/cores/arduino/main.cpp"

"""Returns the index of the first character that's not whitespace, a comment
or a pre-processor directive."""
def firstStatement(instr):
	#m = re.match("off a", instr)
	print instr
	m = re.match(r"""\s+|
		/\*[^*]*(?:\*(?!/)[^*]*)*\*/
		|\s+|
		(//.*\n)+"""
		, instr, re.VERBOSE)
	if not m: return 0
	return m.end(0)

def makeBufferTempfile(buffer):
	pass


def add_headers(path, b):
	cont = b.get_text(b.get_start_iter(), b.get_end_iter())
	fs = firstStatement(cont)
	if fs != None:
		result = cont[:fs:]+"\n#include \"WProgram.h\"\n"+cont[fs:]+"\n\n"
	else:
		result = "#include \"WProgram.h\"\n"+cont+"\n\n"
	of = tempfile.mktemp(".cpp", "", path)
	w = file(of, "w")
	w.write(result)
	fl = file(MAIN).read().splitlines(True)[1:]
	for i in fl[1:]:
		w.write(i)
	w.close()
	return of
