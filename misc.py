
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
		while gtk.events_pending():
			gtk.main_iteration()
		(sout,serr) = p.communicate()
		while gtk.events_pending():
			gtk.main_iteration()
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

class MessageBox:

	def __init__(self):
		pass
	def show(self, message, message2):
		p = gtk.MessageDialog(None,
			gtk.DIALOG_MODAL,
			gtk.MESSAGE_INFO,
			gtk.BUTTONS_OK_CANCEL)
		p.set_markup(message)
		p.format_secondary_markup(message2)
		if p.run() == gtk.RESPONSE_OK:
			p.destroy()
			return True
		p.destroy()
		return False
