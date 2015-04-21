# -*- coding: utf-8 -*-
"""
brickv (Brick Viewer)
Copyright (C) 2013 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2015 Matthias Bolte <matthias@tinkerforge.com>

setup.py: Setuptools script for Brick Viewer

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public
License along with this program; if not, write to the
Free Software Foundation, Inc., 59 Temple Place - Suite 330,
Boston, MA 02111-1307, USA.
"""

import os
import sys
import glob
from setuptools import setup, find_packages
from brickv.config import BRICKV_VERSION

BRICKV_DESCRIPTION = 'Small Qt GUI to control and test all Bricks and Bricklets from Tinkerforge'

# Find brickv packages
if sys.platform == 'darwin':
    packages = find_packages() # FIXME: setuptools on our macbook doesn't understand 'include'
else:
    packages = find_packages(include=['brickv', 'brickv.*'])

# Collect non-frozen package_data
package_data = {}

if sys.platform.startswith('linux'):
    image_patterns = ['*.bmp', '*.png', '*.jpg']

    for package in packages:
        package_path = os.path.join(*package.split('.'))
        images = []

        for pattern in image_patterns:
            images += glob.glob(os.path.join(package_path, pattern))

        if len(images) > 0:
            package_data[package] = [os.path.basename(d) for d in images]

    package_data['brickv'].append('brickv.desktop')

# Collect platform specific data_files
def collect_data_files(path, excludes=None):
    path = os.path.normcase(path)
    files = []

    for root, dirnames, names in os.walk(path):
        for name in names:
            if excludes != None and name in excludes:
                continue

            full_name = os.path.join(root, name)

            if os.path.isfile(full_name):
                files.append((os.path.join(root.replace(path, '')), [full_name]))

    return files

data_files = []

if sys.platform.startswith('linux'):
    data_files.append(('/usr/share/pixmaps/', ['brickv/brickv-icon.png']))
    data_files.append(('/usr/share/applications/', ['brickv/brickv.desktop']))
elif sys.platform == 'win32':
    data_files += collect_data_files('build_data/windows/', ['brickv-icon.ico'])
elif sys.platform == 'darwin':
    data_files += collect_data_files('build_data/macosx/')

# Run setup
setup_arguments = {
    'name':         'brickv',
    'version':      BRICKV_VERSION,
    'author':       'Tinkerforge',
    'author_email': 'info@tinkerforge.com',
    'url':          'http://www.tinkerforge.com',
    'license':      'GPL v2',
    'description':  BRICKV_DESCRIPTION,
    'packages':     packages,
    'package_data': package_data,
    'data_files':   data_files
}

if sys.platform.startswith('linux'):
    setup_arguments['scripts'] = ['brickv/brickv']
elif sys.platform == 'win32':
    import py2exe

    options = {
        'py2exe' : {
            'dll_excludes': ['MSVCP90.dll'],
            'includes':     ['sip',
                             'PyQt4.QtCore',
                             'PyQt4.QtGui',
                             'PyQt4.QtOpenGL',
                             'OpenGL.GL',
                             'ctypes.util',
                             'serial',
                             'colorsys',
                             'win32com.client',
                             'win32con',
                             'winerror',
                             'pywintypes',
                             'win32file',
                             'win32api'],
            'excludes':     ['config_linux',
                             'config_macosx',
                             '_gtkagg',
                             '_tkagg',
                             'Tkconstants',
                             'Tkinter',
                             'tcl',
                             'pydoc',
                             'email',
                             'nose',
                             'inspect',
                             'ctypes.macholib',
                             'win32pdh',
                             'win32ui']
        }
    }

    windows = [{
        'script':        'brickv/main.py',
        'dest_base':     'brickv',
        'icon_resources': [(0, os.path.normcase('build_data/windows/brickv-icon.ico'))]
    }]

    setup_arguments['options'] = options
    setup_arguments['windows'] = windows
    setup_arguments['zipfile'] = None
elif sys.platform == 'darwin':
    options = {
        'py2app': {
            'argv_emulation': True,
            'iconfile':       'build_data/macosx/brickv-icon.icns',
            'site_packages':  True,
            'includes':       ['atexit',
                               'sip',
                               'PyQt4.QtCore',
                               'PyQt4.QtGui',
                               'PyQt4.QtOpenGL',
                               'OpenGL.GL',
                               'ctypes.util',
                               'serial',
                               'colorsys'],
            'excludes':       ['scipy',
                               'distutils',
                               'setuptools',
                               'email',
                               'matplotlib',
                               'PyQt4.QtDeclarative',
                               'PyQt4.QtDesigner',
                               'PyQt4.QtHelp',
                               'PyQt4.QtMultimedia',
                               'PyQt4.QtNetwork',
                               'PyQt4.QtScript',
                               'PyQt4.QtScriptTools',
                               'PyQt4.QtSql',
                               'PyQt4.QtTest',
                               'PyQt4.QtWebKit',
                               'PyQt4.QtXml',
                               'PyQt4.QtXmlPatterns']
        }
    }

    app = [{
        'script': 'brickv/main.py',
        'plist': {
            'CFBundleName':               'Brickv',
            'CFBundleVersion':            BRICKV_VERSION,
            'CFBundleShortVersionString': BRICKV_VERSION,
            'CFBundleGetInfoString':      BRICKV_DESCRIPTION,
            'CFBundleExecutable':         'brickv',
            'CFBundleIdentifier':         'com.tinkerforge.brickv',
            'CFBundleIconFile':           'brickv-icon.icns',
            'NSHumanReadableCopyright':   'Tinkerforge GmbH 2011-2015'
        }
    }]

    setup_arguments['options']   = options
    setup_arguments['scripts']   = ['brickv/main.py']
    setup_arguments['app']       = app

setup(**setup_arguments)
