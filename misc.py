
import gtk
import logging
import select
import subprocess
import gettext
_ = gettext.gettext

LOG_FILENAME = 'arduino.out'
logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG)

def runProg(cmdline):
	sout = ""
	serr = ""
	logging.debug("CMD:-%s", cmdline)
	try:
		p = subprocess.Popen(cmdline,
			stdout = subprocess.PIPE,
			stderr = subprocess.STDOUT,
			stdin = subprocess.PIPE,
			close_fds = True)
		poll = select.poll()
		poll.register(p.stdout, select.POLLIN)
		(sout,serr) = p.communicate()
		if p.poll()==1: raise
	except:
		logging.debug("ERR:%s", sout)
		return (False, sout)
	return (True, sout)

def printError(notify, console, message):
	console.modify_text(gtk.STATE_NORMAL, gtk.gdk.Color(red=1.0))
	b = console.get_buffer()
	context = notify.get_context_id("main")
	notify.pop(context)
	notify.push(context, _("Error compilling."))
	b.delete(b.get_start_iter(), b.get_end_iter())
	b.set_text(message)
