#!/usr/bin/python
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
import hashlib
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

def modifyText(w, (f, label)):
	nh = hashlib.sha224(w.get_text(w.get_start_iter(), w.get_end_iter())).hexdigest()
	fh = hashlib.sha224(file(f).read()).hexdigest()
	if (nh != fh):
		label.set_text(os.path.basename(f)+"*")
	else:
		label.set_text(os.path.basename(f))

def instext(obj, b):
	print gnomevfs.get_mime_type_for_data(b.get_text(b.get_start_iter(), b.get_end_iter()))


def create_source_view(label, f=None):
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
	sv.connect("paste-clipboard", instext, sbuffer)
	sbuffer.connect("changed", modifyText, (f, label))
	return sbuffer, sv
