# -*- coding: utf-8 -*-
"""
brickv (Brick Viewer)
Copyright (C) 2011 Bastian Nordmeyer <bastian@tinkerforge.com>
Copyright (C) 2014-2015, 2017 Matthias Bolte <matthias@tinkerforge.com>

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

import os
import sys

from PyQt5.QtCore import Qt, QDir
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog

def get_resources_path(relativePath):
    try:
        # PyInstaller stores data files in a tmp folder refered to as _MEIPASS
        basePath = sys._MEIPASS
    except Exception:
        basePath = os.path.dirname(os.path.realpath(__file__))

    path = os.path.join(basePath, relativePath)

    # If the path still doesn't exist, this function won't help you
    if not os.path.exists(path):
        print("Resource not found: " + relativePath)
        return None

    return path

def get_home_path():
    return QDir.toNativeSeparators(QDir.homePath())

def get_open_file_name(*args, **kwargs):
    filename, selected_filter = QFileDialog.getOpenFileName(*args, **kwargs)

    if len(filename) > 0:
        filename = QDir.toNativeSeparators(filename)

    return filename

def get_open_file_names(*args, **kwargs):
    filenames = []

    names, selected_filter = QFileDialog.getOpenFileNames(*args, **kwargs)

    for filename in names:
        filenames.append(QDir.toNativeSeparators(filename))

    return filenames

def get_save_file_name(*args, **kwargs):
    filename, selected_filter = QFileDialog.getSaveFileName(*args, **kwargs)

    if len(filename) > 0:
        filename = QDir.toNativeSeparators(filename)

    return filename

def get_existing_directory(*args, **kwargs):
    directory = QFileDialog.getExistingDirectory(*args, **kwargs)

    if len(directory) > 0:
        directory = QDir.toNativeSeparators(directory)

        # FIXME: on macOS the getExistingDirectory() might return the directory with
        #        the last part being invalid, try to find the valid part of the directory
        if sys.platform == 'darwin':
            while len(directory) > 0 and not os.path.isdir(directory):
                directory = os.path.split(directory)[0]

    return directory

def get_main_window():
    for widget in QApplication.topLevelWidgets():
        if isinstance(widget, QMainWindow):
            return widget

    return None

def get_modeless_dialog_flags(default=Qt.WindowFlags(1)):
    # FIXME: on macOS (at least since 10.10) modeless QDialogs don't work
    # properly anymore. they don't show up if the programs is run from an .app
    # container. Setting the tool window flag for such dialogs works around this
    if sys.platform == 'darwin':
        return Qt.Tool
    else:
        return default

def format_voltage(value): # float, V
    if abs(value) < 1:
        return str(int(round(value * 1000.0))) + ' mV'
    else:
        return format(value, '.3f') + ' V'

def format_current(value): # float, A
    if abs(value) < 1:
        return str(int(round(value * 1000.0))) + ' mA'
    else:
        return format(value, '.3f') + ' A'
