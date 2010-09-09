
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
	m = re.match(r"""\s+|
		/\*[^*]*(?:\*(?!/)[^*]*)*\*/
		|\s+|
		(//.*\n)+"""
		, instr, re.VERBOSE)
	if not m: return 0
	return m.end(0)

def findPrototype(instr):
	res = ""
	m = re.findall(r"^\w+\s+\w+\([^)]*\)[\s+/*\w*\s+]*{", instr, re.M)
	for z in m:
		q = re.findall("\w+\s+\w+\([^)]*\)", z)
		res = res + q[0]+";\n";
	return res

def findIncludes(instr):
	res = ""
	m = re.findall(r"^#include\s+[\w+\".<>]+", instr, re.M)
	return [z.split()[1].strip('<>"').split('.')[0] for z in m]

def makeBufferTempfile(buffer):
	pass


def addHeaders(path, b):
	cont = b.get_text(b.get_start_iter(), b.get_end_iter())
	fs = firstStatement(cont)
	if fs != None:
		result = cont[:fs:]+"\n#include \"WProgram.h\"\n"+ findPrototype(cont) + cont[fs:]+"\n\n"
	else:
		result = "#include \"WProgram.h\"\n"+cont+"\n\n"
	of = tempfile.mktemp(".cpp", "", path)
	w = file(of, "w")
	w.write(result)
	w.close()
	return of

def generateCFlags(path, b):
	cont = b.get_text(b.get_start_iter(), b.get_end_iter())
	return ["-Ihardware/libraries/"+i for i in findIncludes(cont)]

def generateLibs(path, b):
	cont = b.get_text(b.get_start_iter(), b.get_end_iter())
	return [i+"/"+i for i in findIncludes(cont)]
