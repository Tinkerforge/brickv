# -*- coding: utf-8 -*-
"""
brickv (Brick Viewer)
Copyright (C) 2015, 2017 Matthias Bolte <matthias@tinkerforge.com>

callback_emulator.py: Emulate callback using getters and threads

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
import logging

from PyQt5.QtCore import QObject, pyqtSignal

from brickv.bindings.ip_connection import Error

class CallbackEmulator(QObject):
    qtcb_data = pyqtSignal(object)
    qtcb_error = pyqtSignal()

    def __init__(self, data_getter, data_callback, error_callback, use_data_signal=True,
                 ignore_last_data=False, log_exception=False):
        QObject.__init__(self)

        self.period = 0 # milliseconds
        self.timer = None
        self.data_getter = data_getter
        self.use_data_signal = use_data_signal
        self.data_callback = data_callback
        self.error_callback = error_callback
        self.ignore_last_data = ignore_last_data
        self.log_exception = log_exception
        self.last_data = None

        if self.use_data_signal:
            self.qtcb_data.connect(self.data_callback)

        if error_callback != None:
            self.qtcb_error.connect(self.error_callback)

    def set_period(self, period):
        self.period = period

        if self.period > 0 and self.timer == None:
            self.timer = threading.Timer(self.period / 1000.0, self.update)
            self.timer.start()

    def update(self):
        self.timer = None

        if self.period < 1:
            # period was set to 0 in the meantime, ignore update
            return

        try:
            data = self.data_getter()
        except Error:
            if self.log_exception:
                logging.exception('Error while getting callback data')

            self.qtcb_error.emit()

            # an error occurred, retry in 5 seconds if period was not set
            # to 0 in the meantime
            if self.period > 0:
                self.timer = threading.Timer(5, self.update)
                self.timer.start()

            return

        if self.ignore_last_data or self.last_data != data:
            self.last_data = data

            if self.use_data_signal:
                self.qtcb_data.emit(data)
            else:
                self.data_callback(data)

        if self.period > 0:
            self.timer = threading.Timer(self.period / 1000.0, self.update)
            self.timer.start()
