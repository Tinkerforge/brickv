# -*- coding: utf-8 -*-
"""
brickv (Brick Viewer)
Copyright (C) 2012 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2014-2015, 2017 Matthias Bolte <matthias@tinkerforge.com>

async_call.py: Asynchronous call for Brick/Bricklet functions

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

from threading import Lock
from collections import namedtuple
import logging
import functools
from queue import Queue

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QThread, QEvent

from brickv.bindings import ip_connection

ASYNC_EVENT = 12345

async_call_queue = Queue()
async_event_queue = Queue()
async_session_lock = Lock()
async_session_id = 1

AsyncCall = namedtuple('AsyncCall', 'function parameter result_callback error_callback pass_exception_to_error_callback debug_exception session_id')

def stop_async_thread():
    with async_session_lock:
        async_call_queue.put(None)

def async_call(function, parameter=None, result_callback=None, error_callback=None,
               pass_exception_to_error_callback=False, debug_exception=False):
    with async_session_lock:
        async_call_queue.put(AsyncCall(function, parameter, result_callback,
                                       error_callback, pass_exception_to_error_callback,
                                       debug_exception, async_session_id))

def async_event_handler():
    while not async_event_queue.empty():
        try:
            func = async_event_queue.get(False, 0)

            if func:
                func()
        except StopIteration:
            pass
        except:
            logging.exception('Error while delivering async call result')

def async_next_session():
    with async_session_lock:
        global async_session_id
        async_session_id += 1

        with async_call_queue.mutex:
            async_call_queue.queue.clear()

def async_start_thread(parent):
    class AsyncThread(QThread):
        def run(self):
            while True:
                ac = async_call_queue.get()

                if ac is None:
                    break

                if not ac.function:
                    continue

                result = None

                try:
                    if ac.parameter == None:
                        result = ac.function()
                    elif isinstance(ac.parameter, tuple):
                        result = ac.function(*ac.parameter)
                    else:
                        result = ac.function(ac.parameter)
                except Exception as e:
                    with async_session_lock:
                        if ac.session_id != async_session_id:
                            continue

                    if ac.error_callback != None:
                        if ac.debug_exception:
                            logging.exception('Error while doing async call')

                        if ac.pass_exception_to_error_callback:
                            async_event_queue.put(functools.partial(ac.error_callback, e))
                        else:
                            async_event_queue.put(ac.error_callback)

                        if isinstance(e, ip_connection.Error):
                            # clear the async call queue if an IPConnection
                            # error occurred. in this case we assume that the
                            # next calls will also fail
                            with async_call_queue.mutex:
                                async_call_queue.queue.clear()

                        QApplication.postEvent(self, QEvent(ASYNC_EVENT))
                        continue

                if ac.result_callback != None:
                    with async_session_lock:
                        if ac.session_id != async_session_id:
                            continue

                    if result == None:
                        async_event_queue.put(ac.result_callback)
                    else:
                        async_event_queue.put(functools.partial(ac.result_callback, result))

                    QApplication.postEvent(self, QEvent(ASYNC_EVENT))

    async_thread = AsyncThread(parent)
    async_thread.start()

    return async_thread
