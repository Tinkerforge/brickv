# -*- coding: utf-8 -*-
"""
brickv (Brick Viewer)
Copyright (C) 2012 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2014-2015, 2017 Matthias Bolte <matthias@tinkerforge.com>
Copyright (C) 2021 Erik Fleckstein <erik@tinkerforge.com>

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

import sys
from threading import Lock
from collections import namedtuple
import logging
import functools
from queue import Queue

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QThread, QEvent, QTimer

ASYNC_EVENT = 12345

async_call_queue = Queue()
async_event_queue = Queue()
async_session_lock = Lock()
async_session_id = 1

AsyncCall = namedtuple('AsyncCall', 'function arguments result_callback error_callback pass_arguments_to_result_callback pass_arguments_to_error_callback pass_exception_to_error_callback expand_arguments_tuple_for_callback expand_result_tuple_for_callback debug_exception retry_on_exception session_id')

def async_stop_thread():
    async_call_queue.put(None)

def async_call(function, arguments, result_callback, error_callback,
               pass_arguments_to_result_callback=False, pass_arguments_to_error_callback=False, pass_exception_to_error_callback=False,
               expand_arguments_tuple_for_callback=False, expand_result_tuple_for_callback=False,
               debug_exception=False, retry_on_exception=False, delay=None):
    if pass_arguments_to_result_callback or pass_arguments_to_error_callback:
        assert arguments != None

    with async_session_lock:
        session_id = async_session_id

    ac = AsyncCall(function, arguments, result_callback, error_callback,
                   pass_arguments_to_result_callback, pass_arguments_to_error_callback, pass_exception_to_error_callback,
                   expand_arguments_tuple_for_callback, expand_result_tuple_for_callback,
                   debug_exception, retry_on_exception, session_id)

    if delay != None:
        QTimer.singleShot(int(delay * 1000), functools.partial(async_call_queue.put, ac))
    else:
        async_call_queue.put(ac)

def async_event_handler():
    while not async_event_queue.empty():
        try:
            event = async_event_queue.get(False)

            if event == None:
                continue

            ac, success, result = event

            if not success:
                arguments = tuple()

                if ac.pass_arguments_to_error_callback:
                    if ac.expand_arguments_tuple_for_callback:
                        assert isinstance(ac.arguments, tuple)

                        arguments += ac.arguments
                    elif ac.arguments != None:
                        arguments += (ac.arguments,)

                if ac.pass_exception_to_error_callback:
                    arguments += (result,)

                ac.error_callback(*arguments)
            else:
                arguments = tuple()

                if ac.pass_arguments_to_result_callback:
                    if ac.expand_arguments_tuple_for_callback:
                        assert isinstance(ac.arguments, tuple)

                        arguments += ac.arguments
                    elif ac.arguments != None:
                        arguments += (ac.arguments,)

                if ac.expand_result_tuple_for_callback:
                    assert isinstance(result, (tuple, list)), repr(result)

                    arguments += tuple(result)
                elif result != None:
                    arguments += (result,)

                ac.result_callback(*arguments)
        except StopIteration:
            pass
        except:
            sys.excepthook(*sys.exc_info())

def async_next_session():
    global async_session_id

    with async_session_lock:
        async_session_id += 1

        with async_call_queue.mutex:
            async_call_queue.queue.clear()

class AsyncThread(QThread):
    def run(self):
        while True:
            ac = async_call_queue.get()

            if ac == None:
                break

            if ac.function == None:
                continue

            with async_session_lock:
                if ac.session_id != async_session_id:
                    continue

            result = None

            try:
                retry_on_exception = ac.retry_on_exception

                for _ in range(2):
                    try:
                        if ac.arguments == None:
                            result = ac.function()
                        elif isinstance(ac.arguments, tuple):
                            result = ac.function(*ac.arguments)
                        else:
                            result = ac.function(ac.arguments)
                    except:
                        if not retry_on_exception:
                            raise

                        retry_on_exception = False
                        continue

                    break
            except Exception as e:
                with async_session_lock:
                    if ac.session_id != async_session_id:
                        continue

                if ac.debug_exception:
                    logging.exception('Error while doing async call')

                if ac.error_callback != None:
                    async_event_queue.put((ac, False, e))

                    QApplication.postEvent(self, QEvent(ASYNC_EVENT))

                continue

            if ac.result_callback != None:
                with async_session_lock:
                    if ac.session_id != async_session_id:
                        continue

                async_event_queue.put((ac, True, result))

                QApplication.postEvent(self, QEvent(ASYNC_EVENT))

def async_start_thread(parent):
    async_thread = AsyncThread(parent)
    async_thread.start()

    return async_thread
