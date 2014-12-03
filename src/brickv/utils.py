# -*- coding: utf-8 -*-
"""
brickv (Brick Viewer)
Copyright (C) 2011 Bastian Nordmeyer <bastian@tinkerforge.com>
Copyright (C) 2014 Matthias Bolte <matthias@tinkerforge.com>

utils.py: General Utilites

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

from PyQt4.QtGui import QApplication, QMainWindow
import os
import sys

def get_program_path():
    # from http://www.py2exe.org/index.cgi/WhereAmI
    if hasattr(sys, 'frozen'):
        path = sys.executable
    else:
        path = __file__

    return str(os.path.dirname(os.path.realpath(unicode(path, sys.getfilesystemencoding()))))

def get_resources_path():
    if sys.platform == "darwin" and hasattr(sys, 'frozen'):
        return os.path.join(os.path.split(get_program_path())[0], 'Resources')
    else:
        return get_program_path()

def get_main_window():
    for widget in QApplication.topLevelWidgets():
        if isinstance(widget, QMainWindow):
            return widget

    return None
