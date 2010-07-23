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
import gtk
import logging
import select
import subprocess
import pango
import time
import tempfile
import gettext
_ = gettext.gettext

LOG_FILENAME = 'arduino.out'
logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG)

def makeWorkdir():
	return tempfile.mkdtemp("", os.path.join(tempfile.gettempdir(), "build"+str(time.time())))

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

def set_widget_font(widget, font):
	context = widget.get_pango_context()
	font_desc = context.get_font_description()
	cur_font = pango.FontDescription(font)
	font_desc.merge(cur_font, True)
	widget.modify_font(font_desc)

def clearConsole(console):
	b = console.get_buffer()
	b.delete(b.get_start_iter(), b.get_end_iter())
	b.set_text("")

def printError(notify, console, message):
	console.modify_text(gtk.STATE_NORMAL, gtk.gdk.Color(red=1.0))
	b = console.get_buffer()
	context = notify.get_context_id("main")
	notify.pop(context)
	notify.push(context, _("Error compilling."))
	b.delete(b.get_start_iter(), b.get_end_iter())
	b.set_text(message)

def printMessage(console, message):
	console.modify_text(gtk.STATE_NORMAL, gtk.gdk.Color("#ffffff"))
	b = console.get_buffer()
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
