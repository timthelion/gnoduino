#!/usr/bin/python

import glob
from distutils.core import setup

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
			('share/gnoduino/pixmaps', glob.glob('pixmaps/*.png'))
	]
)

