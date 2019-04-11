# -*- coding: utf-8 -*-
"""
brickv (Brick Viewer)
Copyright (C) 2015, 2017, 2019 Matthias Bolte <matthias@tinkerforge.com>

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
import time

from PyQt5.QtCore import QObject, pyqtSignal

from brickv.bindings.ip_connection import Error

class CallbackEmulator(QObject):
    qtcb_data = pyqtSignal(object)
    qtcb_error = pyqtSignal()

    def __init__(self, data_getter, data_callback, error_callback, use_data_signal=True,
                 ignore_last_data=False, debug_exception=False):
        super().__init__()

        self.thread = None
        self.thread_id = 0
        self.data_getter = data_getter
        self.use_data_signal = use_data_signal
        self.data_callback = data_callback
        self.error_callback = error_callback
        self.ignore_last_data = ignore_last_data
        self.debug_exception = debug_exception
        self.last_data = None

        if self.use_data_signal:
            self.qtcb_data.connect(self.data_callback)

        if error_callback != None:
            self.qtcb_error.connect(self.error_callback)

    def set_period(self, period): # milliseconds
        self.thread_id += 1 # force current thread (if any) to exit eventually

        if period > 0:
            self.thread = threading.Thread(target=self.loop, args=(self.thread_id, period), daemon=True)
            self.thread.start()

    def loop(self, thread_id, period):
        monotonic_timestamp = time.monotonic()
        first = True
        ignore_last_data_override = True

        while thread_id == self.thread_id:
            if not first:
                elapsed = time.monotonic() - monotonic_timestamp
                remaining = max(period / 1000.0 - elapsed, 0)
                time.sleep(remaining)

                monotonic_timestamp = time.monotonic()

            first = False

            if thread_id != self.thread_id:
                break

            try:
                data = self.data_getter()
            except Error:
                if self.debug_exception:
                    logging.exception('Error while getting callback data')

                self.qtcb_error.emit()
                continue

            if self.ignore_last_data or ignore_last_data_override or self.last_data != data:
                self.last_data = data

                if self.use_data_signal:
                    self.qtcb_data.emit(data)
                else:
                    self.data_callback(data)

            ignore_last_data_override = False
