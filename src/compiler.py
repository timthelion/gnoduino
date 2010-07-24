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
import gtk
import logging
import select
import subprocess
import sys
import time
import tempfile
import gettext
import hashlib
#gettext.bindtextdomain('myapplication', '/path/to/my/language/directory')
#gettext.textdomain('myapplication')
_ = gettext.gettext

LOG_FILENAME = 'arduino.out'
logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG)

import board
import config
import misc
import preproc

#output = output buffer
#notify = notification bar
cobj = [
	"wiring_digital.c",
	"wiring_shift.c",
	"wiring_analog.c",
	"wiring_pulse.c",
#	"wiring_serial.c",
	"pins_arduino.c",
	"WInterrupts.c",
	"wiring.c"
	]

cppobj = [
	"WMath.cpp",
	"HardwareSerial.cpp",
	"Print.cpp",
	"main.cpp",
	"Tone.cpp"
	]

defc = [
	"/usr/bin/avr-gcc",
	"-c",
#	"-w",
	"-g",
	"-Os",
	"-ffunction-sections",
	"-fdata-sections",
	]

defcpp = [
	"/usr/bin/avr-g++",
	"-c",
	"-w",
	"-g",
	"-Os",
	"-fno-exceptions",
	"-ffunction-sections",
	"-fdata-sections",
	]

defar = [
	"/usr/bin/avr-ar",
	"rcs"
	]

link = [
	"/usr/bin/avr-gcc",
	"-Os",
	"-Wl,--gc-sections",
	]

eep = [
	"/usr/bin/avr-objcopy",
	"-O",
	"ihex",
	"-j .eeprom",
	"--set-section-flags=.eeprom=alloc,load",
	"--no-change-warnings",
	"--change-section-lma",
	".eeprom=0"
	]
hex = [
	"/usr/bin/avr-objcopy",
	"-O",
	"ihex",
	"-R .eeprom"
	]

arduino_path = "hardware/arduino/cores/arduino"

def stripOut(sout, pre):
	sout = sout.replace(pre+":", '').split(" ", 1)
	print len(sout)
	if len(sout) >= 2: return sout[1]
	else: return sout

def compile(tw, id, output, notify):
	context = notify.get_context_id("main")
	notify.pop(context)
	notify.push(context, _("Compilling..."))
	misc.clearConsole(output)
	tmpdir = id
	tempobj = tempfile.mktemp("", "Tempobj", id)
	b = board.Board()
	#compile inter c objects
	try:
		"""preproces pde"""
		pre_file = preproc.add_headers(id, tw.get_buffer())
		"""compile C targets"""
		for i in cobj:
			compline=[j for j in defc]
			compline.append("-mmcu="+b.getBoardMCU(b.getBoard()))
			compline.append("-DF_CPU="+b.getBoardFCPU(b.getBoard()))
			compline.append("-I"+os.getcwd()+"/"+arduino_path)
			compline.append(os.getcwd()+"/"+arduino_path+"/"+i)
			compline.append("-o"+id+"/"+i+".o")
			(run, sout) = misc.runProg(compline)
			if run == False:
				misc.printError(notify, output, stripOut(sout, pre_file))
				raise
		"""compile C++ targets"""
		for i in cppobj:
			compline = [j for j in defcpp]
			compline.append("-mmcu="+b.getBoardMCU(b.getBoard()))
			compline.append("-DF_CPU="+b.getBoardFCPU(b.getBoard()))
			compline.append("-I"+os.getcwd()+"/"+arduino_path)
			compline.append(os.getcwd()+"/"+arduino_path+"/"+i)
			compline.append("-o"+id+"/"+i+".o")
			(run, sout) = misc.runProg(compline)
			if run == False:
				misc.printError(notify, output, sout)
				raise
		"""generate archive objects"""
		for i in cobj+cppobj:
			compline = [j for j in defar]
			compline.append(id+"/core.a")
			compline.append(id+"/"+i+".o")
			(run, sout) = misc.runProg(compline)
			if run == False:
				misc.printError(notify, output, stripOut(sout, pre_file))
				raise
		"""precompile pde"""
		compline=[j for j in defcpp]
		compline.append("-mmcu="+b.getBoardMCU(b.getBoard()))
		compline.append("-DF_CPU="+b.getBoardFCPU(b.getBoard()))
		compline.append("-I"+os.getcwd()+"/"+arduino_path)
		compline.append(pre_file)
		compline.append("-o"+pre_file+".o")
		(run, sout) = misc.runProg(compline)
		if run == False:
			misc.printError(notify, output, stripOut(sout, pre_file))
			moveCursor(tw, int(getErrorLine(sout)))
			raise

		"""compile all objects"""
		compline = [i for i in link]
		compline.append("-mmcu="+b.getBoardMCU(b.getBoard()))
		compline.append("-o"+tempobj+".elf")
		compline.append(pre_file+".o")
		compline.append(id+"/core.a")
		compline.append("-L"+id)
		compline.append("-lm")
		(run, sout) = misc.runProg(compline)
		if run == False:
			misc.printError(notify, output, stripOut(sout, pre_file))
			raise NameError('linking-error')
		compline=[i for i in eep]
		compline.append(tempobj+".elf")
		compline.append(tempobj+".eep")
		(run, sout) = misc.runProg(compline)
		if run == False:
			misc.printError(notify, output, stripOut(sout, pre_file))
			raise
		compline=[i for i in hex]
		compline.append(tempobj+".elf")
		compline.append(tempobj+".hex")
		(run, sout) = misc.runProg(compline)
		if run == False:
			misc.printError(notify, output, stripOut(sout, pre_file))
			raise
		size = computeSize(tempobj+".hex")
		notify.pop(context)
		notify.push(context, _("Done compilling."))

		misc.printMessage(output, _("Binary sketch size: %s bytes (of a %s bytes maximum)") % (size, b.getBoardMemory(b.getBoard())))
	except StandardError as e:
		print "Error: %s" % e
	except:
		print "Error compiling. Op aborted!"
	return tempobj

def getErrorLine(buffer):
	return int(buffer.splitlines()[1].split(":")[1])-1-2; # -2 added by preprocesor

def moveCursor(view, line):
	b = view.get_buffer()
	mark = b.get_insert()
	iter = b.get_iter_at_mark(mark)
	iter.set_line(line);
	b.place_cursor(iter)
	view.scroll_mark_onscreen(mark)

def computeSize(f):
	p = subprocess.Popen(["/usr/bin/avr-size", f],
		stdout = subprocess.PIPE,
		stderr = subprocess.STDOUT,
		stdin = subprocess.PIPE,
		close_fds = True)
	poll = select.poll()
	poll.register(p.stdout, select.POLLIN)
	(sout,serr) = p.communicate()
	return sout.splitlines()[1].split()[3]
