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
import hashlib
import glib
import gobject
import gtk
import subprocess
import select
import shutil

import gettext
_ = lambda x: gettext.ldgettext(NAME, x)

import board
import compiler
import misc
import prefs
import uploader
import srcview
import serialio

font = "Monospace 10"

def setupPage(w, page, p):
	pg = w.get_nth_page(p)
	cl = pg.get_data("close");
	if cl == None: return
	accel = gtk.AccelGroup()
	cl.add_accelerator("activate", accel, ord("w"), gtk.gdk.CONTROL_MASK, 0)
	mainwin.add_accel_group(accel)
	srcview.updatePos(pg.get_data("buffer"), sb2)

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

def switchPage(page, a, b, c):
	nb.set_current_page(int(chr(b-1)))

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
	wp = nb.get_nth_page(p)
	wp.set_data("file", f)		#add file information to the page widget
	wp.set_data("buffer", sbuf)	#add buffer information to the page widget
	wp.set_data("view", sv)	#add buffer information to the page widget
	wp.set_data("label", flabel)	#add source view widget to the page widget
	wp.set_data("close", b)	#add close widget to the page widget
	nb.set_current_page(p)
	page = nb.get_nth_page(p)
	nb.set_scrollable(True);
	nb.set_tab_reorderable(page, True);
	accel = gtk.AccelGroup()
	for i in range(1, 10):
		accel.connect_group(ord(str(i)), gtk.gdk.MOD1_MASK, 0,
			switchPage)
	mainwin.add_accel_group(accel)
	sv.grab_focus()
	b.connect("clicked", destroyPage, sw)
	srcview.updatePos(sbuf, sb2)
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

def processFile(w):
	if searchFile(nb, w.get_filename()) == True:
		w.destroy()
		return
	page = nb.get_nth_page(nb.get_current_page())
	createPage(nb, w.get_filename())
	if page.get_data("label").get_text() == "Untitled":
		replacePage(page)

def saveAs():
	p = gtk.FileChooserDialog("Save file", None, gtk.FILE_CHOOSER_ACTION_OPEN,
		(gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
		gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
	p.set_size_request(650, 500)
	p.show_all()
	if p.run() == gtk.RESPONSE_ACCEPT:
		f = p.get_filename()
		p.destroy()
		return f
	p.destroy()
	return None

def copen(widget, data=None):
	p = gtk.FileChooserDialog("Open file", None, gtk.FILE_CHOOSER_ACTION_OPEN,
		(gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
		gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
	p.set_size_request(650, 500)
	p.show_all()
	if p.run() == gtk.RESPONSE_ACCEPT:
		processFile(p)
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
		if f == None: return
		else:
			p = misc.MessageBox()
			res = p.show("""<b>A file named %s already exists. Do you want to replace it?</b>""" % f,
			"The file already exists in \"%s\". Replacing it will overwrite its contents." % os.path.dirname(f))
			if not res: return
			l.set_text(os.path.basename(f))
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
	obj = compiler.compile(page.get_data("view"), id, tw, sb) #page.get_data("buffer")
	return obj

def upload(widget, serial, data=file):
	obj = compile(widget, data)
	while (gtk.events_pending()):
		gtk.main_iteration()
	uploader.upload(obj, serial, tw, sb)

def menuUpload(widget, data=None):
	upload(widget, ser, data)

def about(widget, data=None):
	about = gui.get_object("about")
	about.show_all()

def preferences(widget, data=None):
	pref = gui.get_object("preferences")
	fs = gui.get_object("fontsize")
	p = prefs.preferences()
	print p.getValue("editor.font")
	fs.set_value(10)
	pref.show_all()

def stop(widget, data=None):
	print "stop"

def cserial(w, st, data=None):

	global sertime
	#compiler.clearConsole(data)
	if (sertime == None):
		sertime = glib.timeout_add(1000,
			ser.updateConsole,
			data)
		vbox.remove(con)
		vbox.add(scon)
	else:
		glib.source_remove(sertime)
		sertime = None
		vbox.remove(scon)
		vbox.add(con)

def avrisp(w, data=None):
	print "avrisp"

def setBaud(w, data=None):
	ser.resetBoard()
	ser.serial.close()
	ser.serial.baudrate = baud[w.get_active()]
	ser.serial.open()

menus = [
		("menu-new", cnew, (ord('n'), gtk.gdk.CONTROL_MASK)),
		("menu-open", copen, (ord('o'), gtk.gdk.CONTROL_MASK)),
		("menu-save", csave, (ord('s'), gtk.gdk.CONTROL_MASK)),
		("menu-save-as", csave_as, (ord('s'), gtk.gdk.CONTROL_MASK|gtk.gdk.SHIFT_MASK)),
		("menu-quit", quit, (ord('q'), gtk.gdk.CONTROL_MASK)),
		("menu-compile", compile, (ord('r'), gtk.gdk.CONTROL_MASK)),
		("menu-preferences", preferences, (ord(','), gtk.gdk.CONTROL_MASK)),
		("menu-upload", menuUpload, (ord('u'), gtk.gdk.CONTROL_MASK)),
		("menu-about", about, (ord('a'), gtk.gdk.CONTROL_MASK)),
		("avrisp", avrisp, (ord('a'), gtk.gdk.CONTROL_MASK)),
	]

def menu(gui):
	[gui.get_object(i[0]).connect("activate", i[1]) for i in menus]
	accel = gtk.AccelGroup()
	[gui.get_object(i[0]).add_accelerator("activate", accel, i[2][0], i[2][1], 0) for i in menus]
	mainwin.add_accel_group(accel)

def createCon():
	sw = gtk.ScrolledWindow()
	sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
	sw.set_shadow_type(gtk.SHADOW_IN)
	tw = gtk.TextView()
	tw.set_size_request(-1, 150)
	tw.set_editable(False)
	twbuf = gtk.TextBuffer()
	tw.set_buffer(twbuf)
	tw.modify_base(gtk.STATE_NORMAL, gtk.gdk.Color(0,0,0))
	tw.modify_text(gtk.STATE_NORMAL, gtk.gdk.Color("#ffffff"))
	misc.set_widget_font(tw, p.getValue("editor.font").replace(",", " "))
	sw.add(tw)
	sw.show_all()
	return (sw,tw)

def createScon():
	global baud
	sw = gtk.ScrolledWindow()
	sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
	sw.set_shadow_type(gtk.SHADOW_IN)
	tw = gtk.TextView()
	tw.set_size_request(-1, 150)
	tw.set_editable(False)
	twbuf = gtk.TextBuffer()
	tw.set_buffer(twbuf)
	tw.modify_base(gtk.STATE_NORMAL, gtk.gdk.Color(0,0,0))
	tw.modify_text(gtk.STATE_NORMAL, gtk.gdk.Color("#ffffff"))
	misc.set_widget_font(tw, p.getValue("editor.font").replace(",", " "))
	sw.add(tw)
	hbox = gtk.HBox(False, 0)
	s = gtk.Button("Send")
	c = gtk.Button("Clear")
	c.connect("clicked", ser.clearConsole, tw)
	l = gtk.Label("Baud:")
	b = gtk.combo_box_new_text()
	baud = ["300", "1200", "2400", "4800", "9600", "14400", "19200", "28800", "38400", "57600", "115200"]
	[b.append_text(i) for i in baud]
	b.connect("changed", setBaud)
	b.set_active(4)
	text = gtk.Entry()
	hbox.pack_start(text, False, False, 3)
	hbox.pack_start(s, False, False, 3)
	hbox.pack_start(c, False, False, 3)
	hbox.pack_start(l, False, False, 3)
	hbox.pack_start(b, False, False, 3)
	vbox = gtk.VBox(False, 0)
	vbox.pack_start(hbox, False, False, 3)
	vbox.pack_start(sw, False, False, 3)
	vbox.show_all()
	return (vbox, tw)

buttons = [
		("compile", "compile.png", compile),
		("stop", "stop.png", stop),

		("open", "open.png", copen),
		("new", "new.png", cnew),

		("save", "save.png", None),
		("upload", "upload.png", None),
		("serial", "serial.png", None)
	]

def selectBoard(w, id):
	b.setBoard(id)

def run():
	try:
		global gui
		global mainwin
		global sb2
		global ser
		global id
		global nb
		global tw
		global sb
		global sertime
		global vbox
		global con
		global scon
		global p
		global b
		id = misc.makeWorkdir()
		ser = serialio.sconsole()
		p = prefs.preferences()
		sertime = None
		gui = gtk.Builder()
		try:
			gui.add_from_file(os.path.join(os.getcwd(), "ui", "main.ui"))
		except:
			try:
				gui.add_from_file(os.path.join(sys.prefix, "share", "gnoduino", "ui", "main.ui"))
			except Exception,e:
				print(e)
				raise SystemExit(_("Cannot load ui file"))
		mainwin = gui.get_object("top_win")
		vbox = gui.get_object("vpan")
		sb = gui.get_object("statusbar1")
		sb2 = gui.get_object("statusbar2")
		menu(gui)
		sub = gtk.Menu()
		b = board.Board()
		maingroup = gtk.RadioMenuItem(None, None)
		for i in b.getBoards():
			menuItem = gtk.RadioMenuItem(maingroup, i[2])
			if i[0] == b.getBoard() + 1:
				menuItem.set_active(True)
			menuItem.connect('toggled', selectBoard, i[0])
			sub.append(menuItem)

		gui.get_object("board").set_submenu(sub)

		nb = gtk.Notebook()
		nb.connect("switch-page", setupPage)
		sv = createPage(nb)
		vbox.add(nb)

		(con, tw) = createCon()
		(scon,sctw) = createScon()
		vbox.add(con)

		mainwin.set_focus(sv)
		mainwin.show_all()
		mainwin.set_title("Arduino")
		mainwin.connect("destroy", quit)
		gui.get_object("serial").connect("clicked", cserial, sertime, sctw)
		gui.get_object("upload").connect("clicked", upload, ser)
		for i in buttons:
			w = gtk.Image()
			try:
				if (os.path.exists(os.path.join(os.getcwd(), "pixmaps", i[1]))):
					w.set_from_file(os.path.join(os.getcwd(), "pixmaps", i[1]))
				else: raise
			except:
				try:
					if os.path.exists((os.path.join(sys.prefix, 'share', 'gnoduino', "pixmaps", i[1]))):
						w.set_from_file(os.path.join(sys.prefix, 'share', 'gnoduino', "pixmaps", i[1]))
					else: raise
				except Exception,e:
					print(e)
					raise SystemExit(_("Cannot load pixmap files"))
			o = gui.get_object(i[0])
			o.set_icon_widget(w)
			o.show_all()
			if i[2] != None:
				o.connect("clicked", i[2])
		gtk.main()
	except KeyboardInterrupt:
		print "\nExit on user cancel."
		sys.exit(1)
