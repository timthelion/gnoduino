#!/usr/bin/python

import glob
from distutils.core import setup

setup(name='gnoduino',
	version='1.0',
	package_dir={'gnoduino': 'src'},
	packages = ['gnoduino'],
	scripts = ['gnoduino'],
	data_files = [('share/gnoduino/ui', ['ui/main.ui']),
			('share/gnoduino/pixmaps', glob.glob('pixmaps/*.png'))
	]
)

