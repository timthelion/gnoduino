# Arduino python implementation
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
import fnmatch
import gtksourceview2
import gnomevfs

def get_lang_for_file(f):
	manager = gtksourceview2.language_manager_get_default()
	languages = gtksourceview2.LanguageManager.get_language_ids(manager)
	for l in languages:
		lang = manager.get_language(l)
		if lang == None: return None
		globs = gtksourceview2.Language.get_globs(lang)
		if globs == None: continue
		for p in globs:
			if fnmatch.fnmatch(f, p):
				return lang

def get_lang_for_content(content):
	mime = gnomevfs.get_mime_type_for_data(content)
	manager = gtksourceview2.language_manager_get_default()
	languages = gtksourceview2.LanguageManager.get_language_ids(manager)
	for l in languages:
		lang = manager.get_language(l)
		if lang == None: return None
		globs = gtksourceview2.Language.get_mime_types(lang)
		if globs == None: continue
		for p in globs:
			if p == mime: 
				return lang

def instext(b, iter, text, len) :
	b.set_language(get_lang_for_content(text))

def updatePos(buffer, sb):
	sb.pop(1)
	iter = buffer.get_iter_at_mark(buffer.get_insert())
	row = iter.get_line();
	col = iter.get_line_offset();
	msg = "Ln %d, Col %d" % (row+1, col+1)
	sb.push(1, msg);

def markCb(buffer, iter, mark, data):
	updatePos(buffer, data)

def resetCursor(buffer):
	mark = buffer.get_insert()
	iter = buffer.get_iter_at_mark(mark)
	iter.set_line(0);
	buffer.place_cursor(iter)

def createsrcview(status, f=None):
	sbuffer = gtksourceview2.Buffer()
	if f: 
		content = file(f).read()
		sbuffer.set_language(get_lang_for_content(content))
		sbuffer.set_text(content)
	sv = gtksourceview2.View(sbuffer)
	manager = gtksourceview2.StyleSchemeManager()
#	for i in gtksourceview2.StyleSchemeManager.get_scheme_ids(manager):
#		print i
	scheme =  manager.get_scheme("tango")
	sbuffer.set_style_scheme(scheme);
	sv.set_size_request(500, 450)
	sv.set_editable(True)
	sv.set_cursor_visible(True)
#	sv.set_show_line_numbers(True)
	sv.set_wrap_mode(gtk.WRAP_CHAR)
	sv.set_right_margin_position(80)
	updatePos(sbuffer, status)
	sbuffer.connect("mark_set", markCb, status)
	sbuffer.connect("insert_text", instext)
	sv.set_highlight_current_line(True)
	resetCursor(sbuffer)
	return sbuffer, sv
