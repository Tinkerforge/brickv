#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
brickv (Brick Viewer)
Copyright (C) 2014 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2017 Matthias Bolte <matthias@tinkerforge.com>

object_creator.py: Creates objects in Qt main thread

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

import threading

from PyQt5 import QtCore

# Usage:
# object_instance = create_object_in_qt_main_thread(Class, (data_1, data_2, ..., data_n))

def create_object_in_qt_main_thread(cls, data):
    oc = ObjectCreator(cls, data)
    QtCore.QCoreApplication.instance().object_creator_signal.emit(oc)
    oc.semaphore.acquire()
    return oc.obj

class ObjectCreator(object):
    def __init__(self, cls, data):
        self.cls = cls
        self.data = data
        self.semaphore = threading.Semaphore(0)
        self.obj = None

    def create(self):
        self.obj = self.cls(*self.data)
        self.semaphore.release()
