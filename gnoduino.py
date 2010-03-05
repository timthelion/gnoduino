#!/usr/bin/python -t
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

import hashlib
import time
import tempfile
import os
import sys
import glib
import gobject
import gtk
import subprocess
import select
import shutil

import compiler
import srcview
import serialio

class popup:

	def __init__(self):
		print "constructor"
	def show(self, title):
		p = gtk.Dialog(title, None, gtk.DIALOG_DESTROY_WITH_PARENT, 
			(gtk.STOCK_OK, gtk.RESPONSE_ACCEPT, gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT))
		area = p.get_content_area()
		l = gtk.Label("simple text")
		l.show()
		area.pack_start(l, True, True)
		area.show()
		if p.run() == gtk.RESPONSE_ACCEPT:
			print "accept"
		p.destroy()

def replacePage(page):
	nb.remove_page(nb.page_num(page))

def destroyPage(w, b):
	nb.remove_page(nb.page_num(b))
	if nb.get_n_pages() < 1:
		createPage(nb)

def updatePageTitle(w, status):
	page = nb.get_nth_page(nb.get_current_page())
	f = page.get_data("file")
	l = page.get_data("label")
	nh = hashlib.sha224(w.get_text(w.get_start_iter(), w.get_end_iter())).hexdigest()
	if f != None:
		fh = hashlib.sha224(file(f).read()).hexdigest()
		name = os.path.basename(f)
	else:
		fh = 0
		name = "Untitled"

	if (nh != fh):
		l.set_text(name+"*")
	else:
		l.set_text(name)
	srcview.updatePos(w, status)

def createPage(nb, f=None):
	hbox = gtk.HBox(False, 0)
	flabel = gtk.Label(os.path.basename(f) if f else "Untitled")
	hbox.pack_start(flabel, False, False, 3)
	b = gtk.Button()
	img = gtk.Image()
	img.set_from_icon_name(gtk.STOCK_CLOSE, gtk.ICON_SIZE_MENU)
	img.set_pixel_size(8)
	b.set_image(img)
	b.set_relief(gtk.RELIEF_NONE)
	hbox.pack_start(b, True, True)
	hbox.show_all()
	(sbuf,sv) = srcview.createsrcview(sb2, f)
	sbuf.connect("changed", updatePageTitle, sb2)
	sw = gtk.ScrolledWindow()
	sw.add(sv)
	sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
	sw.set_placement(gtk.CORNER_BOTTOM_LEFT)
	sw.set_shadow_type(gtk.SHADOW_IN)
	sw.show_all()
	p = nb.append_page(sw, hbox)
	nb.set_current_page(p)
	sv.grab_focus()
	b.connect("clicked", destroyPage, sw)
	wp = nb.get_nth_page(p)
	wp.set_data("file", f)		#add file information to the page widget
	wp.set_data("buffer", sbuf)	#add buffer information to the page widget
	wp.set_data("label", flabel)	#add source view widget to the page widget
	return sv

def cnew(widget, data=None):
	createPage(nb, data)

def searchFile(nb, f):
	for i in range(nb.get_n_pages()):
		of = nb.get_nth_page(i).get_data("file")
		if of == f:
			nb.set_current_page(i)
			return True
	return False

def process_file(w, dialog):
	if searchFile(nb, w.get_filename()) == True:
		dialog.destroy()
		return

	page = nb.get_nth_page(nb.get_current_page())
	if page.get_data("label").get_text() == "Untitled":
		replacePage(page)

	createPage(nb, w.get_filename())
	dialog.destroy()

def saveAs():
	p = gtk.FileChooserDialog("Save file", None, gtk.FILE_CHOOSER_ACTION_OPEN,
		(gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT, 
		gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
	p.set_size_request(650, 500)
	p.connect("file-activated", process_file, p)
	if p.run() == gtk.RESPONSE_ACCEPT:
		f = p.get_filename()
		p.destroy()
		return f
	
def copen(widget, data=None):
	p = gtk.Dialog("Open file", None, gtk.DIALOG_DESTROY_WITH_PARENT, 
		(gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT, 
		gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
	p.set_size_request(650, 500)
	area = p.get_content_area()
	fc = gtk.FileChooserWidget()
	fc.connect("file-activated", process_file, p)
	area.pack_start(fc, True, True)
	p.show_all()
	if p.run() == gtk.RESPONSE_ACCEPT:
		createPage(nb, fc.get_filename())
	p.destroy()

def csave_as(w, data=None):
	csave(w, True)

def csave(w, data=None):
	page = nb.get_nth_page(nb.get_current_page())
	l = page.get_data("label")
	b = page.get_data("buffer")
	f = page.get_data("file") 
	if f == None or data == True:
		f = saveAs()
		l.set_text(os.path.basename(f) if f else "Untitled")
		page.set_data("file", f)
	F = open(f, "w")
	F.write(b.get_text(b.get_start_iter(), b.get_end_iter()))
	F.close()
	updatePageTitle(b, sb2)

def quit(widget, data=None):
	shutil.rmtree(id, True)
	gtk.main_quit()

def compile(widget, data=file):
	page = nb.get_nth_page(nb.get_current_page())
	compiler.compile(page.get_data("buffer"), id, tw, sb)

def stop(widget, data=None):
	print "stop"

def cserial(w, data=None):
	compiler.clearConsole(data)
	glib.timeout_add(1000,
		ser.updateConsole,
		data)

def menu(gui):
	menus = [
			("menu-new", cnew, (ord('n'), gtk.gdk.CONTROL_MASK)),
			("menu-open", copen, (ord('o'), gtk.gdk.CONTROL_MASK)),
			("menu-save", csave, (ord('s'), gtk.gdk.CONTROL_MASK)),
			("menu-save-as", csave_as, (ord('s'), gtk.gdk.CONTROL_MASK|gtk.gdk.SHIFT_MASK)),
			("menu-quit", quit, (ord('q'), gtk.gdk.CONTROL_MASK)),
		]
	[gui.get_object(i[0]).connect("activate", i[1]) for i in menus]
	accel = gtk.AccelGroup()
	[gui.get_object(i[0]).add_accelerator("activate", accel, i[2][0], i[2][1], 0) for i in menus]
	mainwin.add_accel_group(accel)

def makeWorkdir():
	return tempfile.mkdtemp("", "/tmp/build"+str(time.time()))

try:
	id = makeWorkdir()
	#p = popup()
	#p.show("popup text")
	ser = serialio.sconsole()
	gui = gtk.Builder()
	gui.add_from_file("./main.ui");
	mainwin = gui.get_object("top_win");
	vbox = gui.get_object("vpan");
	sb = gui.get_object("statusbar1");
	sb2 = gui.get_object("statusbar2");
	comp = gui.get_object("compile").connect("clicked", compile)
	gui.get_object("stop").connect("clicked", stop)
	gui.get_object("new").connect("clicked", cnew)
	gui.get_object("open").connect("clicked", copen)
	menu(gui)

	nb = gtk.Notebook()
	sv = createPage(nb)
	vbox.add(nb)
	sw = gtk.ScrolledWindow()
	sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
	sw.set_shadow_type(gtk.SHADOW_IN)
	tw = gtk.TextView()
	tw.set_size_request(-1, 200)
	tw.set_editable(False)
	twbuf = gtk.TextBuffer()
	tw.set_buffer(twbuf)
	tw.modify_base(gtk.STATE_NORMAL, gtk.gdk.Color(0,0,0))
	tw.modify_text(gtk.STATE_NORMAL, gtk.gdk.Color("#ffffff"))
	sw.add(tw)
	vbox.add(sw)
	mainwin.set_focus(sv)
	mainwin.show_all()
	mainwin.set_title("Arduino")
	mainwin.connect("destroy", quit)
	gui.get_object("serial").connect("clicked", cserial, tw)
	gtk.main()
except KeyboardInterrupt:
	print "\nExit on user cancel."
	sys.exit(1)
