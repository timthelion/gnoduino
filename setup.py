#!/usr/bin/python

import glob
import misc
from distutils.core import setup

compline = "./gen_boards.py"
(run, sout) = misc.runProg(compline)
compline = "./gen_programmers.py"
(run, sout) = misc.runProg(compline)

setup(name='gnoduino',
	version='0.1.0',
	description='Gnome Arduino IDE implementation',
	package_dir={'gnoduino': 'src'},
	packages = ['gnoduino'],
	scripts = ['gnoduino'],

	author='Lucian Langa',
	author_email='lucilanga@gnome.org',
	url='http://gnome.eu.org/evo/index.php/Gnoduino',
	license='GPL',
	platforms='linux',

	data_files = [('share/gnoduino/ui', ['ui/main.ui']),
			('share/gnoduino/', ['BOARDS', 'PROGRAMMERS']),
			('share/gnoduino/pixmaps', glob.glob('pixmaps/*.png'))
	]
)

