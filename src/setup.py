# -*- coding: utf-8 -*-

# Copyright (C) 2011 Chris Dekter
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from distutils.core import setup 
from pkgutil import walk_packages

import brickv

def find_packages(path, prefix):
    yield prefix
    prefix = prefix + "."
    for _, name, ispkg in walk_packages(path, prefix):
        if ispkg:
            yield name

setup(
      name="brickv",
      version="2.0.7",
      author="Olaf Lüke",
      author_email="olaf@tinkerforge.com",
      url="http://www.tinkerforge.com",
      license="GPL v2",
      description="Brick Viewer",
      long_description="""Brick Viewer is a small Qt GUI with which one can control and test all Bricks and Bricklets from Tinkerforge""",
      packages=list(find_packages(brickv.__path__, brickv.__name__)),
      scripts=['brickv/brickv'],
      )
