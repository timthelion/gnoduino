
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

