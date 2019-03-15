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

packages = find_packages(include=['brickv', 'brickv.*'])

package_data = {}

image_patterns = ['*.bmp', '*.png', '*.jpg']

for package in packages:
    package_path = os.path.join(*package.split('.'))
    images = []

    for pattern in image_patterns:
        images += glob.glob(os.path.join(package_path, pattern))

    if len(images) > 0:
        package_data[package] = [os.path.basename(name) for name in images]

setup_arguments = {
    'name':         'brickv',
    'version':      BRICKV_VERSION,
    'author':       'Tinkerforge',
    'author_email': 'info@tinkerforge.com',
    'url':          'http://www.tinkerforge.com',
    'license':      'GPL v2',
    'description':  'Small Qt GUI to control and test all Bricks and Bricklets from Tinkerforge',
    'packages':     packages,
    'package_data': package_data,
    'scripts':      ['brickv/brickv']
}

setup(**setup_arguments)
