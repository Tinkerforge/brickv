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

packages = find_packages(include=['brickv', 'brickv.*'])

# Collect non-frozen package_data
package_data = {}

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

data_files = [('/usr/share/pixmaps/', ['brickv/brickv-icon.png']),
              ('/usr/share/applications/', ['brickv/brickv.desktop'])]

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
    'data_files':   data_files,
    'scripts':      ['brickv/brickv']
}

setup(**setup_arguments)
