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
import queue

from PyQt5.QtCore import QObject, pyqtSignal

class CallbackEmulator(QObject):
    qtcb_result = pyqtSignal(object)
    qtcb_error = pyqtSignal(object)
    qtcb_error_with_exception = pyqtSignal(object, object)

    def __init__(self, function, arguments, result_callback, error_callback,
                 pass_arguments_to_result_callback=False, pass_exception_to_error_callback=False,
                 expand_arguments_tuple_for_callback=False, expand_result_tuple_for_callback=False,
                 use_result_signal=True, debug_exception=False):
        super().__init__()

        if pass_arguments_to_result_callback:
            assert arguments != None

        self.function = function
        self.arguments = arguments
        self.result_callback = result_callback
        self.error_callback = error_callback
        self.pass_arguments_to_result_callback = pass_arguments_to_result_callback
        self.pass_exception_to_error_callback = pass_exception_to_error_callback
        self.expand_arguments_tuple_for_callback = expand_arguments_tuple_for_callback
        self.expand_result_tuple_for_callback = expand_result_tuple_for_callback
        self.use_result_signal = use_result_signal
        self.debug_exception = debug_exception
        self.thread = None
        self.period_queue = None
        self.enable_ref = None

        if self.use_result_signal:
            self.qtcb_result.connect(self.cb_result)

        if self.error_callback != None:
            if self.pass_exception_to_error_callback:
                self.qtcb_error_with_exception.connect(self.error_callback)
            else:
                self.qtcb_error.connect(self.error_callback)

    def set_period(self, period): # milliseconds
        assert period >= 0, period

        if self.thread == None:
            if period > 0:
                self.enable_ref = [True]

                self.period_queue = queue.Queue()
                self.period_queue.put(period / 1000)

                self.thread = threading.Thread(target=self.loop, args=(self.period_queue, self.enable_ref), daemon=True)
                self.thread.start()
        else:
            if period != 0:
                self.period_queue.put(period)
            else:
                self.enable_ref[0] = False

                self.period_queue.put(None)
                self.period_queue = None

                self.thread = None

    def cb_result(self, result):
        arguments = tuple()

        if self.pass_arguments_to_result_callback:
            if self.expand_arguments_tuple_for_callback:
                assert isinstance(self.arguments, tuple)

                arguments += self.arguments
            elif self.arguments != None:
                arguments += (self.arguments,)

        if self.expand_result_tuple_for_callback:
            assert isinstance(result, tuple)

            arguments += result
        elif result != None:
            arguments += (result,)

        self.result_callback(*arguments)

    def loop(self, period_queue, enable_ref):
        period = 0
        monotonic_timestamp = time.monotonic()

        while enable_ref[0]:
            elapsed = time.monotonic() - monotonic_timestamp
            remaining = max(period - elapsed, 0)

            try:
                period = period_queue.get(timeout=remaining)
            except queue.Empty:
                pass

            monotonic_timestamp = time.monotonic()

            if period == None:
                break

            try:
                if self.arguments == None:
                    result = self.function()
                elif isinstance(self.arguments, tuple):
                    result = self.function(*self.arguments)
                else:
                    result = self.function(self.arguments)
            except Exception as e:
                if self.debug_exception:
                    logging.exception('Error while getting callback result')

                if not enable_ref[0]:
                    break

                if self.pass_exception_to_error_callback:
                    self.qtcb_error_with_exception.emit(e)
                else:
                    self.qtcb_error.emit(e)
            else:
                if not enable_ref[0]:
                    break

                if self.use_result_signal:
                    self.qtcb_result.emit(result)
                else:
                    self.cb_result(result)
