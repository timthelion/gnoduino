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

import gettext
_ = gettext.gettext
import misc
import time

import misc

avr = [
	"avrdude",
	"-Chardware/tools/avrdude.conf",
	"-v",
	"-v",
	"-v",
	"-F",	#force write to ignore signature check
	"-pm8",
	"-cstk500v1",
	"-P/dev/ttyS0",
	"-b19200",
	"-D"
]

def upload(obj, serial, output, notify):
	context = notify.get_context_id("main")
	notify.pop(context)
	notify.push(context, _("Flashing..."))
	serial.resetBoard()
	compline=[i for i in avr]
	compline.append("-Uflash:w:"+obj+".hex:i")
	print compline
	(run, sout) = misc.runProg(compline)
	print sout
	if run == False:
		misc.printError(notify, output, sout)
		raise
	notify.pop(context)
	notify.push(context, _("Flashing complete."))

