# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014 Matthias Bolte <matthias@tinkerforge.com>

api.py: RED Brick API wrapper

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

from collections import namedtuple
import functools
import traceback
import weakref
import threading
from PyQt4 import QtCore
from brickv.bindings.brick_red import BrickRED
from brickv.object_creator import create_object_in_qt_main_thread

class REDError(Exception):
    E_SUCCESS                  = 0
    E_UNKNOWN_ERROR            = 1
    E_INVALID_OPERATION        = 2
    E_OPERATION_ABORTED        = 3
    E_INTERNAL_ERROR           = 4
    E_UNKNOWN_SESSION_ID       = 5
    E_NO_FREE_SESSION_ID       = 6
    E_UNKNOWN_OBJECT_ID        = 7
    E_NO_FREE_OBJECT_ID        = 8
    E_OBJECT_IS_LOCKED         = 9
    E_NO_MORE_DATA             = 10
    E_WRONG_LIST_ITEM_TYPE     = 11
    E_PROGRAM_IS_PURGED        = 12
    E_INVALID_PARAMETER        = 128
    E_NO_FREE_MEMORY           = 129
    E_NO_FREE_SPACE            = 130
    E_ACCESS_DENIED            = 131
    E_ALREADY_EXISTS           = 132
    E_DOES_NOT_EXIST           = 133
    E_INTERRUPTED              = 134
    E_IS_DIRECTORY             = 135
    E_NOT_A_DIRECTORY          = 136
    E_WOULD_BLOCK              = 137
    E_OVERFLOW                 = 138
    E_BAD_FILE_DESCRIPTOR      = 139
    E_OUT_OF_RANGE             = 140
    E_NAME_TOO_LONG            = 141
    E_INVALID_SEEK             = 142
    E_NOT_SUPPORTED            = 143
    E_TOO_MANY_OPEN_FILES      = 144

    _error_code_names = {
        E_SUCCESS                  : 'E_SUCCESS',
        E_UNKNOWN_ERROR            : 'E_UNKNOWN_ERROR',
        E_INVALID_OPERATION        : 'E_INVALID_OPERATION',
        E_OPERATION_ABORTED        : 'E_OPERATION_ABORTED',
        E_INTERNAL_ERROR           : 'E_INTERNAL_ERROR',
        E_UNKNOWN_SESSION_ID       : 'E_UNKNOWN_SESSION_ID',
        E_NO_FREE_SESSION_ID       : 'E_NO_FREE_SESSION_ID',
        E_UNKNOWN_OBJECT_ID        : 'E_UNKNOWN_OBJECT_ID',
        E_NO_FREE_OBJECT_ID        : 'E_NO_FREE_OBJECT_ID',
        E_OBJECT_IS_LOCKED         : 'E_OBJECT_IS_LOCKED',
        E_NO_MORE_DATA             : 'E_NO_MORE_DATA',
        E_WRONG_LIST_ITEM_TYPE     : 'E_WRONG_LIST_ITEM_TYPE',
        E_PROGRAM_IS_PURGED        : 'E_PROGRAM_IS_PURGED',
        E_INVALID_PARAMETER        : 'E_INVALID_PARAMETER',
        E_NO_FREE_MEMORY           : 'E_NO_FREE_MEMORY',
        E_NO_FREE_SPACE            : 'E_NO_FREE_SPACE',
        E_ACCESS_DENIED            : 'E_ACCESS_DENIED',
        E_ALREADY_EXISTS           : 'E_ALREADY_EXISTS',
        E_DOES_NOT_EXIST           : 'E_DOES_NOT_EXIST',
        E_INTERRUPTED              : 'E_INTERRUPTED',
        E_IS_DIRECTORY             : 'E_IS_DIRECTORY',
        E_NOT_A_DIRECTORY          : 'E_NOT_A_DIRECTORY',
        E_WOULD_BLOCK              : 'E_WOULD_BLOCK',
        E_OVERFLOW                 : 'E_OVERFLOW',
        E_BAD_FILE_DESCRIPTOR      : 'E_BAD_FILE_DESCRIPTOR',
        E_OUT_OF_RANGE             : 'E_OUT_OF_RANGE',
        E_NAME_TOO_LONG            : 'E_NAME_TOO_LONG',
        E_INVALID_SEEK             : 'E_INVALID_SEEK',
        E_NOT_SUPPORTED            : 'E_NOT_SUPPORTED',
        E_TOO_MANY_OPEN_FILES      : 'E_TOO_MANY_OPEN_FILES'
    }

    def __init__(self, message, error_code):
        Exception.__init__(self, message)

        self._message = message
        self._error_code = error_code

    def __str__(self):
        return '{0}: {1} ({2})'.format(self._message,
                                       REDError._error_code_names.get(self._error_code, '<unknown>'),
                                       self._error_code)

    @property
    def message(self):    return self._message
    @property
    def error_code(self): return self._error_code


class MethodRef:
    def __init__(self, method):
        self.target_ref   = weakref.ref(method.__self__)
        self.function_ref = weakref.ref(method.__func__)

    def get(self):
        return self.target_ref(), self.function_ref()


class REDBrick(BrickRED):
    def __init__(self, *args):
        BrickRED.__init__(self, *args)

        self._active_callbacks      = {}
        self._active_callbacks_lock = threading.Lock()
        self._next_cookie           = 1

    def _dispatch_callback(self, callback_id, *args, **kwargs):
        active_callbacks = self._active_callbacks[callback_id]
        dead_callbacks   = []

        for cookie in list(active_callbacks.keys()):
            try:
                callback_target, callback_function = active_callbacks[cookie].get()
            except KeyError:
                continue

            if callback_target != None and callback_function != None:
                try:
                    callback_function(callback_target, *args, **kwargs)
                except:
                    print 'REDBrick._dispatch_callback: callback_function failed'
                    traceback.print_exc()
            else:
                dead_callbacks.append(cookie)

        if len(dead_callbacks) > 0:
            with self._active_callbacks_lock:
                for cookie in dead_callbacks:
                    del active_callbacks[cookie]

    def add_callback(self, callback_id, callback_function):
        with self._active_callbacks_lock:
            cookie             = self._next_cookie
            self._next_cookie += 1

            if callback_id in self._active_callbacks:
                self._active_callbacks[callback_id][cookie] = MethodRef(callback_function)
            else:
                self._active_callbacks[callback_id] = {cookie: MethodRef(callback_function)}

                self.register_callback(callback_id, functools.partial(self._dispatch_callback, callback_id))

            return cookie

    def remove_callback(self, callback_id, cookie):
        with self._active_callbacks_lock:
            if callback_id not in self._active_callbacks or \
               cookie not in self._active_callbacks[callback_id]:
                return

            del self._active_callbacks[callback_id][cookie]

    def remove_all_callbacks(self):
        self.registered_callbacks = {}

        with self._active_callbacks_lock:
            self._active_callbacks = {}


class REDSession(QtCore.QObject):
    KEEP_ALIVE_INTERVAL = 5 # seconds
    LIFETIME            = 60 # seconds

    def __init__(self, brick):
        QtCore.QObject.__init__(self)

        self._brick            = brick
        self._session_id       = None
        self._keep_alive_timer = None

    def __del__(self):
        self.expire()

    def __repr__(self):
        return '<REDSession session_id: {0}>'.format(self._session_id)

    def _keep_session_alive(self):
        if self._session_id == None:
            # session is expired, don't keep it alive anymore longer
            return

        try:
            error_code = self._brick.keep_session_alive(self._session_id, REDSession.LIFETIME)
        except:
            # FIXME: error handling
            print 'REDSession._keep_session_alive: keep_session_alive failed'
            traceback.print_exc()

        if self._session_id == None:
            # session got expired during the keep-alive call, don't keep it alive any longer
            return

        self._keep_alive_timer = threading.Timer(REDSession.KEEP_ALIVE_INTERVAL,
                                                 self._keep_session_alive)
        self._keep_alive_timer.start()

    def create(self):
        self.expire()

        error_code, session_id = self._brick.create_session(REDSession.LIFETIME)

        if error_code != REDError.E_SUCCESS:
            raise REDError('Could not create session', error_code)

        self._session_id = session_id

        self._keep_alive_timer = threading.Timer(REDSession.KEEP_ALIVE_INTERVAL,
                                                 self._keep_session_alive)
        self._keep_alive_timer.start()

        return self

    # don't call this method with async_call, this is already non-blocking
    def expire(self):
        if self._session_id == None:
            # expiring an unattached session is allowed and does nothing
            return

        if self._keep_alive_timer != None:
            self._keep_alive_timer.cancel()

        # ensure to remove references to REDObject via their added callback methods
        self._brick.remove_all_callbacks()

        session_id       = self._session_id
        self._session_id = None

        try:
            self._brick.expire_session_unchecked(session_id)
        except:
            # ignoring IPConnection-level error
            print 'REDSession.expire: expire_session_unchecked failed'
            traceback.print_exc()

    @property
    def session_id(self): return self._session_id


def _attach_or_release(session, object_class, object_id, extra_object_ids_to_release_on_error=[]):
    try:
        object_class_instance = create_object_in_qt_main_thread(object_class, (session,))
        obj = object_class_instance.attach(object_id)
    except:
        try:
            session._brick.release_object_unchecked(object_id, session._session_id)
        except:
            # ignoring IPConnection-level error
            print '_attach_or_release: first release_object_unchecked failed'
            traceback.print_exc()

        for extra_object_id in extra_object_ids_to_release_on_error:
            try:
                session._brick.release_object_unchecked(extra_object_id, session._session_id)
            except:
                # ignoring IPConnection-level error
                print '_attach_or_release: second release_object_unchecked failed'
                traceback.print_exc()

        raise # just re-raise the original exception

    return obj


class REDObjectReleaser:
    def __init__(self, object, object_id, session):
        self._object_ref  = weakref.ref(object, self.release)
        self._object_id   = object_id
        self._session     = session
        self.armed        = True

    def release(self, ref):
        if not self.armed:
            return

        # only release object if the session was not already expired
        if self._session._session_id is not None:
            try:
                self._session._brick.release_object_unchecked(self._object_id, self._session._session_id)
            except:
                # ignoring IPConnection-level error
                print 'REDObjectReleaser.release: release_object_unchecked failed'
                traceback.print_exc()


class REDObject(QtCore.QObject):
    TYPE_STRING    = BrickRED.OBJECT_TYPE_STRING
    TYPE_LIST      = BrickRED.OBJECT_TYPE_LIST
    TYPE_FILE      = BrickRED.OBJECT_TYPE_FILE
    TYPE_DIRECTORY = BrickRED.OBJECT_TYPE_DIRECTORY
    TYPE_PROCESS   = BrickRED.OBJECT_TYPE_PROCESS
    TYPE_PROGRAM   = BrickRED.OBJECT_TYPE_PROGRAM

    _subclasses = {}

    def __init__(self, session):
        QtCore.QObject.__init__(self)

        self._session    = session
        self._releaser   = None
        self.__object_id = None # make object_id private, to ensure that it
                                # is only manipulated via attach/detach

        self._initialize()

    def __repr__(self):
        return '<REDObject object_id: {0}>'.format(self.__object_id)

    def _initialize(self):
        raise NotImplementedError()

    def _attach_callbacks(self):
        raise NotImplementedError()

    def _detach_callbacks(self):
        raise NotImplementedError()

    def update(self):
        raise NotImplementedError()

    def attach(self, object_id, update=True):
        self.release()

        self._releaser   = REDObjectReleaser(self, object_id, self._session)
        self.__object_id = object_id

        self._attach_callbacks()

        if update:
            self.update()

        return self

    def detach(self):
        if self.__object_id is None:
            raise RuntimeError('Cannot detach unattached object')

        self._detach_callbacks()

        self._releaser.armed = False
        self._releaser       = None
        object_id            = self.__object_id
        self.__object_id     = None

        self._initialize()

        return object_id

    # don't call this method with async_call, this is already non-blocking
    def release(self):
        if self.__object_id is None:
            # releasing an unattached object is allowed and does nothing
            return

        object_id = self.detach()

        # only release object if the session was not already expired
        if self._session._session_id is not None:
            try:
                self._session._brick.release_object_unchecked(object_id, self._session._session_id)
            except:
                # ignoring IPConnection-level error
                print 'REDObject.release: release_object_unchecked failed'
                traceback.print_exc()

    @property
    def session(self):   return self._session
    @property
    def object_id(self): return self.__object_id


class REDString(REDObject):
    MAX_ALLOCATE_BUFFER_LENGTH  = 58
    MAX_SET_CHUNK_BUFFER_LENGTH = 58
    MAX_GET_CHUNK_BUFFER_LENGTH = 63

    def __str__(self):
        return str(self._data)

    def __unicode__(self):
        return self._data

    def __repr__(self):
        return '<REDString object_id: {0}, data: {1}>'.format(self.object_id, repr(self._data))

    def _initialize(self):
        self._data = None # stored as unicode

    def _attach_callbacks(self):
        pass

    def _detach_callbacks(self):
        pass

    def update(self):
        if self.object_id is None:
            raise RuntimeError('Cannot update unattached string object')

        error_code, length = self._session._brick.get_string_length(self.object_id)

        if error_code != REDError.E_SUCCESS:
            raise REDError('Could not get length of string object {0}'.format(self.object_id), error_code)

        data_utf8 = ''

        while len(data_utf8) < length:
            error_code, chunk = self._session._brick.get_string_chunk(self.object_id, len(data_utf8))

            if error_code != REDError.E_SUCCESS:
                raise REDError('Could not get chunk of string object {0} at offset {1}'.format(self.object_id, len(data_utf8)), error_code)

            data_utf8 += chunk

        self._data = data_utf8.decode('utf-8')

    def allocate(self, data):
        self.release()

        data_unicode   = unicode(data)
        data_utf8      = data_unicode.encode('utf-8')
        chunk          = data_utf8[:REDString.MAX_ALLOCATE_BUFFER_LENGTH]
        remaining_data = data_utf8[REDString.MAX_ALLOCATE_BUFFER_LENGTH:]

        error_code, object_id = self._session._brick.allocate_string(len(data_utf8), chunk, self._session._session_id)

        if error_code != REDError.E_SUCCESS:
            raise REDError('Could not allocate string object', error_code)

        self.attach(object_id, False)

        offset = len(chunk)

        while len(remaining_data) > 0:
            chunk          = remaining_data[:REDString.MAX_SET_CHUNK_BUFFER_LENGTH]
            remaining_data = remaining_data[REDString.MAX_SET_CHUNK_BUFFER_LENGTH:]

            error_code = self._session._brick.set_string_chunk(self.object_id, offset, chunk)

            if error_code != REDError.E_SUCCESS:
                raise REDError('Could not set chunk of string object {0} at offset {1}'.format(self.object_id, offset), error_code)

            offset += len(chunk)

        self._data = data_unicode

        return self

    @property
    def data(self): return self._data


class REDList(REDObject):
    def __repr__(self):
        return '<REDList object_id: {0}>'.format(self.object_id)

    def _initialize(self):
        self._items = None

    def _attach_callbacks(self):
        pass

    def _detach_callbacks(self):
        pass

    def update(self):
        if self.object_id is None:
            raise RuntimeError('Cannot update unattached list object')

        error_code, length = self._session._brick.get_list_length(self.object_id)

        if error_code != REDError.E_SUCCESS:
            raise REDError('Could not get length of list object {0}'.format(self.object_id), error_code)

        items = []

        for i in range(length):
            error_code, item_object_id, type = self._session._brick.get_list_item(self.object_id, i, self._session._session_id)

            if error_code != REDError.E_SUCCESS:
                raise REDError('Could not get item at index {0} of list object {1}'.format(i, self.object_id), error_code)

            try:
                wrapper_class = REDObject._subclasses[type]
            except KeyError:
                raise TypeError('List object {0} contains item with unknown type {1} at index {2}'.format(self.object_id, type, i))

            items.append(_attach_or_release(self._session, wrapper_class, item_object_id))

        self._items = items

    def allocate(self, items):
        self.release()

        error_code, object_id = self._session._brick.allocate_list(len(items), self._session._session_id)

        if error_code != REDError.E_SUCCESS:
            raise REDError('Could not allocate list object', error_code)

        self.attach(object_id, False)

        for item in items:
            if isinstance(item, str) or isinstance(item, unicode):
                item = REDString(self._session).allocate(item)
            elif not isinstance(item, REDObject):
                raise TypeError('Cannot append {0} item to list object {1}'.format(type(item), self.object_id))

            error_code = self._session._brick.append_to_list(self.object_id, item.object_id)

            if error_code != REDError.E_SUCCESS:
                raise REDError('Could not append item {0} to list object {1}'.format(item.object_id, self.object_id), error_code)

        self._items = items

        return self

    @property
    def items(self): return self._items


def _get_zero_padded_chunk(data, max_chunk_length, start = 0):
    chunk        = data[start:start + max_chunk_length]
    chunk_length = len(chunk)
    chunk       += b'\0'*(max_chunk_length - chunk_length)

    return chunk, chunk_length


class REDFileBase(REDObject):
    class WriteAsyncData(QtCore.QObject):
        _qtcb_result = QtCore.pyqtSignal(object)
        _qtcb_status = QtCore.pyqtSignal(int, int)

        def __init__(self, data, result_callback, status_callback):
            QtCore.QObject.__init__(self)

            self.data    = data
            self.length  = len(data)
            self.written = 0
            self.abort   = False

            if result_callback != None:
                self._qtcb_result.connect(result_callback, QtCore.Qt.QueuedConnection)

            if status_callback != None:
                self._qtcb_status.connect(status_callback, QtCore.Qt.QueuedConnection)

    class ReadAsyncData(QtCore.QObject):
        _qtcb_result = QtCore.pyqtSignal(object)
        _qtcb_status = QtCore.pyqtSignal(int, int)

        def __init__(self, max_length, result_callback, status_callback):
            QtCore.QObject.__init__(self)

            self.max_length   = max_length
            self.burst_length = 0
            self.data_length  = 0
            self.data_chunks  = []
            self.abort        = False

            if result_callback != None:
                self._qtcb_result.connect(result_callback, QtCore.Qt.QueuedConnection)

            if status_callback != None:
                self._qtcb_status.connect(status_callback, QtCore.Qt.QueuedConnection)

    MAX_READ_BUFFER_LENGTH            = 62
    MAX_READ_ASYNC_BUFFER_LENGTH      = 60
    MAX_WRITE_BUFFER_LENGTH           = 61
    MAX_WRITE_UNCHECKED_BUFFER_LENGTH = 61
    MAX_WRITE_ASYNC_BUFFER_LENGTH     = 61

    TYPE_UNKNOWN   = BrickRED.FILE_TYPE_UNKNOWN
    TYPE_REGULAR   = BrickRED.FILE_TYPE_REGULAR
    TYPE_DIRECTORY = BrickRED.FILE_TYPE_DIRECTORY
    TYPE_CHARACTER = BrickRED.FILE_TYPE_CHARACTER
    TYPE_BLOCK     = BrickRED.FILE_TYPE_BLOCK
    TYPE_FIFO      = BrickRED.FILE_TYPE_FIFO
    TYPE_SYMLINK   = BrickRED.FILE_TYPE_SYMLINK
    TYPE_SOCKET    = BrickRED.FILE_TYPE_SOCKET
    TYPE_PIPE      = BrickRED.FILE_TYPE_PIPE

    EVENT_READABLE = BrickRED.FILE_EVENT_READABLE
    EVENT_WRITABLE = BrickRED.FILE_EVENT_WRITABLE

    AsyncReadResult = namedtuple('AsyncReadResult', 'data error')

    # Number of chunks written in one async read/write burst
    ASYNC_BURST_CHUNKS      = 50
    ASYNC_READ_BURST_LENGTH = ASYNC_BURST_CHUNKS * MAX_READ_ASYNC_BUFFER_LENGTH

    _qtcb_events_occurred = QtCore.pyqtSignal(int)

    def _initialize(self):
        self._type               = None
        self._name               = None
        self._flags              = None
        self._permissions        = None
        self._uid                = None
        self._gid                = None
        self._length             = None
        self._access_time        = None
        self._modification_time  = None
        self._status_change_time = None

        self.events_occurred_callback = None

        self._cb_async_write_cookie     = None
        self._cb_async_read_cookie      = None
        self._cb_events_occurred_cookie = None

        self._write_async_data = None
        self._read_async_data  = None

    def _attach_callbacks(self):
        self._qtcb_events_occurred.connect(self._cb_events_occurred, QtCore.Qt.QueuedConnection)

        self._cb_async_write_cookie     = self._session._brick.add_callback(REDBrick.CALLBACK_ASYNC_FILE_WRITE,
                                                                            self._cb_async_write)
        self._cb_async_read_cookie      = self._session._brick.add_callback(REDBrick.CALLBACK_ASYNC_FILE_READ,
                                                                            self._cb_async_read)
        self._cb_events_occurred_cookie = self._session._brick.add_callback(REDBrick.CALLBACK_FILE_EVENTS_OCCURRED,
                                                                            self._cb_events_occurred_emit)

    def _detach_callbacks(self):
        self._qtcb_events_occurred.disconnect(self._cb_events_occurred)

        self._session._brick.remove_callback(REDBrick.CALLBACK_ASYNC_FILE_WRITE,
                                             self._cb_async_write_cookie)
        self._session._brick.remove_callback(REDBrick.CALLBACK_ASYNC_FILE_READ,
                                             self._cb_async_read_cookie)
        self._session._brick.remove_callback(REDBrick.CALLBACK_FILE_EVENTS_OCCURRED,
                                             self._cb_events_occurred_cookie)

        self._cb_async_write_cookie     = None
        self._cb_async_read_cookie      = None
        self._cb_events_occurred_cookie = None

    def _report_write_async_status(self):
        self._write_async_data._qtcb_status.emit(self._write_async_data.written, self._write_async_data.length)

    def _report_write_async_result(self, error):
        self._write_async_data._qtcb_result.emit(error)
        self._write_async_data = None

    def _cb_async_write(self, file_id, error_code, length_written):
        if self.object_id != file_id:
            return

        if self._write_async_data == None:
            return

        if error_code != REDError.E_SUCCESS:
            # FIXME: recover seek position on error after successful call?
            self._report_write_async_result(REDError('Could not write to file object {0}'.format(self.object_id), error_code))
            return

        # Remove data of async call. Data of unchecked writes has been removed already.
        self._write_async_data.written += length_written
        self._report_write_async_status()

        # If there is no data remaining we are done.
        if self._write_async_data.written >= self._write_async_data.length:
            self._report_write_async_result(None)
            return

        self._next_write_async_burst()

    def _next_write_async_burst(self):
        if self._write_async_data.abort:
            self._report_write_async_result(REDError('Could not write to file object {0}'.format(self.object_id), REDError.E_OPERATION_ABORTED))
            return

        unchecked_writes = 0

        # do at most ASYNC_BURST_CHUNKS - 1 unchecked writes before the final async write per burst
        while unchecked_writes < REDFileBase.ASYNC_BURST_CHUNKS - 1 and \
              (self._write_async_data.length - self._write_async_data.written) > REDFileBase.MAX_WRITE_ASYNC_BUFFER_LENGTH:
            chunk, length_to_write = _get_zero_padded_chunk(self._write_async_data.data,
                                                            REDFileBase.MAX_WRITE_UNCHECKED_BUFFER_LENGTH,
                                                            self._write_async_data.written)

            try:
                self._session._brick.write_file_unchecked(self.object_id, chunk, length_to_write)
            except Exception as e:
                self._report_write_async_result(e)
                return

            self._write_async_data.written += length_to_write
            unchecked_writes               += 1

        chunk, length_to_write = _get_zero_padded_chunk(self._write_async_data.data,
                                                        REDFileBase.MAX_WRITE_ASYNC_BUFFER_LENGTH,
                                                        self._write_async_data.written)

        try:
            # FIXME: Do we need a timeout here for the case that no callback comes?
            self._session._brick.write_file_async(self.object_id, chunk, length_to_write)
        except Exception as e:
            self._report_write_async_result(e)

    def _report_read_async_status(self):
        self._read_async_data._qtcb_status.emit(self._read_async_data.data_length, self._read_async_data.max_length)

    def _report_read_async_result(self, error):
        data = bytearray().join(self._read_async_data.data_chunks)

        self._read_async_data._qtcb_result.emit(REDFileBase.AsyncReadResult(data, error))
        self._read_async_data = None

    def _cb_async_read(self, file_id, error_code, buf, length_read):
        if self.object_id != file_id:
            return

        if self._read_async_data == None:
            return

        if self._read_async_data.abort:
            error_code = REDError.E_SUCCESS

        if error_code != REDError.E_SUCCESS:
            self._report_read_async_result(REDError('Could not read from file object {0}'.format(self.object_id), error_code))
            return

        if length_read == 0:
            # no more data to read, report the result
            self._report_read_async_result(None)
            return

        self._read_async_data.burst_length += length_read
        self._read_async_data.data_length  += length_read

        self._read_async_data.data_chunks.append(bytearray(buf[:length_read]))

        if self._read_async_data.data_length >= self._read_async_data.max_length:
            # read max_length data, report the result
            self._report_read_async_status()
            self._report_read_async_result(None)
        elif self._read_async_data.burst_length == REDFileBase.ASYNC_READ_BURST_LENGTH:
            # burst finished, start next one
            self._report_read_async_status()
            self._next_read_async_burst()

    def _next_read_async_burst(self):
        remaining_length = self._read_async_data.max_length - self._read_async_data.data_length

        if remaining_length < 0:
            return

        length_to_read                     = min(remaining_length, REDFileBase.ASYNC_READ_BURST_LENGTH)
        self._read_async_data.burst_length = 0

        try:
            # FIXME: Do we need a timeout here for the case that no callback comes?
            self._session._brick.read_file_async(self.object_id, length_to_read)
        except Exception as e:
            self._report_read_async_result(e)

    def _cb_events_occurred_emit(self, file_id, events):
        if self.object_id != file_id:
            return

        # cannot directly use emit function as callback functions, because this
        # triggers a segfault on the second call for some unknown reason. adding
        # a method in between helps
        self._qtcb_events_occurred.emit(events)

    def _cb_events_occurred(self, events):
        events_occurred_callback = self.events_occurred_callback

        if events_occurred_callback != None:
            events_occurred_callback(events)

    def update(self):
        if self.object_id is None:
            raise RuntimeError('Cannot update unattached file object')

        error_code, type, name_string_id, flags, permissions, uid, gid, \
        length, access_time, modification_time, status_change_time = self._session._brick.get_file_info(self.object_id, self._session._session_id)

        if error_code != REDError.E_SUCCESS:
            raise REDError('Could not get information for file object {0}'.format(self.object_id), error_code)

        if type == REDFileBase.TYPE_PIPE:
            name = None
        else:
            name = _attach_or_release(self._session, REDString, name_string_id)

        self._type               = type
        self._name               = name
        self._flags              = flags
        self._permissions        = permissions
        self._uid                = uid
        self._gid                = gid
        self._length             = length
        self._access_time        = access_time
        self._modification_time  = modification_time
        self._status_change_time = status_change_time

    def write(self, data):
        if self.object_id is None:
            raise RuntimeError('Cannot write to unattached file object')

        remaining_data = bytearray(data)

        while len(remaining_data) > 0:
            chunk, length_to_write = _get_zero_padded_chunk(remaining_data,
                                                            REDFileBase.MAX_WRITE_BUFFER_LENGTH)

            error_code, length_written = self._session._brick.write_file(self.object_id, chunk, length_to_write)

            if error_code != REDError.E_SUCCESS:
                # FIXME: recover seek position on error after successful call?
                raise REDError('Could not write to file object {0}'.format(self.object_id), error_code)

            remaining_data = remaining_data[length_written:]

    def write_async(self, data, result_callback=None, status_callback=None):
        if self.object_id is None:
            raise RuntimeError('Cannot write to unattached file object')

        if self._write_async_data != None:
            raise RuntimeError('Another asynchronous write is already in progress')

        self._write_async_data = create_object_in_qt_main_thread(REDFileBase.WriteAsyncData,
                                                                 (bytearray(data), result_callback, status_callback))

        self._report_write_async_status()
        self._next_write_async_burst()

    def read(self, length):
        if self.object_id is None:
            raise RuntimeError('Cannot read from unattached file object')

        data = bytearray()

        while length > 0:
            length_to_read                 = min(length, REDFileBase.MAX_READ_BUFFER_LENGTH)
            error_code, chunk, length_read = self._session._brick.read_file(self.object_id, length_to_read)

            if error_code != REDError.E_SUCCESS:
                # FIXME: recover seek position on error after successful call?
                raise REDError('Could not read from file object {0}'.format(self.object_id), error_code)

            if length_read == 0:
                break

            data   += bytearray(chunk[:length_read])
            length -= length_read

        return data

    # calls "result_callback" with data of length min("max_length", "length_of_file")
    def read_async(self, max_length, result_callback, status_callback=None):
        if self.object_id is None:
            raise RuntimeError('Cannot read from unattached file object')

        if self._read_async_data != None:
            raise RuntimeError('Another asynchronous read is already in progress')

        self._read_async_data = create_object_in_qt_main_thread(REDFileBase.ReadAsyncData,
                                                                (max_length, result_callback, status_callback))

        self._report_read_async_status()
        self._next_read_async_burst()

    def abort_async_read(self):
        if self.object_id is None:
            raise RuntimeError('Cannot abort asynchronous read from unattached file object')

        if self._read_async_data != None:
            self._read_async_data.abort = True
            self._session._brick.abort_async_file_read(self.object_id)

    def abort_async_write(self):
        if self.object_id is None:
            raise RuntimeError('Cannot abort asynchronous read from unattached file object')

        if self._write_async_data != None:
            self._write_async_data.abort = True

    def set_events(self, events):
        if self.object_id is None:
            raise RuntimeError('Cannot set events of unattached file object')

        error_code = self._session._brick.set_file_events(self.object_id, events)

        if error_code != REDError.E_SUCCESS:
            raise REDError('Could not set events of file object {0}'.format(self.object_id), error_code)

    @property
    def type(self):               return self._type
    @property
    def name(self):               return self._name
    @property
    def flags(self):              return self._flags
    @property
    def permissions(self):        return self._permissions
    @property
    def uid(self):                return self._uid
    @property
    def gid(self):                return self._gid
    @property
    def length(self):             return self._length
    @property
    def access_time(self):        return self._access_time
    @property
    def modification_time(self):  return self._modification_time
    @property
    def status_change_time(self): return self._status_change_time


class REDFile(REDFileBase):
    FLAG_READ_ONLY    = BrickRED.FILE_FLAG_READ_ONLY
    FLAG_WRITE_ONLY   = BrickRED.FILE_FLAG_WRITE_ONLY
    FLAG_READ_WRITE   = BrickRED.FILE_FLAG_READ_WRITE
    FLAG_APPEND       = BrickRED.FILE_FLAG_APPEND
    FLAG_CREATE       = BrickRED.FILE_FLAG_CREATE
    FLAG_EXCLUSIVE    = BrickRED.FILE_FLAG_EXCLUSIVE
    FLAG_NON_BLOCKING = BrickRED.FILE_FLAG_NON_BLOCKING
    FLAG_TRUNCATE     = BrickRED.FILE_FLAG_TRUNCATE
    FLAG_TEMPORARY    = BrickRED.FILE_FLAG_TEMPORARY
    FLAG_REPLACE      = BrickRED.FILE_FLAG_REPLACE

    def __repr__(self):
        return '<REDFile object_id: {0}, name: {1}>'.format(self.object_id, repr(self._name))

    def open(self, name, flags, permissions, uid, gid):
        self.release()

        if not isinstance(name, REDString):
            name = REDString(self._session).allocate(name)

        error_code, object_id = self._session._brick.open_file(name.object_id, flags, permissions, uid, gid, self._session._session_id)

        if error_code != REDError.E_SUCCESS:
            raise REDError('Could not open file object', error_code)

        self.attach(object_id)

        return self


class REDPipe(REDFileBase):
    FLAG_NON_BLOCKING_READ  = BrickRED.PIPE_FLAG_NON_BLOCKING_READ
    FLAG_NON_BLOCKING_WRITE = BrickRED.PIPE_FLAG_NON_BLOCKING_WRITE

    def __repr__(self):
        return '<REDPipe object_id: {0}>'.format(self.object_id)

    def create(self, flags, length):
        self.release()

        error_code, object_id = self._session._brick.create_pipe(flags, length, self._session._session_id)

        if error_code != REDError.E_SUCCESS:
            raise REDError('Could not create pipe object', error_code)

        self.attach(object_id)

        return self


class REDFileOrPipeAttacher(REDObject):
    def __repr__(self):
        return '<REDFileOrPipeAttacher object_id: {0}>'.format(self.object_id)

    def _initialize(self):
        pass

    def _attach_callbacks(self):
        pass

    def _detach_callbacks(self):
        pass

    def attach(self, object_id):
        self.release()

        REDObject.attach(object_id, False)

        error_code, type, name_string_id, _, _, _, _, _, _, _, _ = self._session._brick.get_file_info(self.object_id, self._session._session_id)

        if error_code != REDError.E_SUCCESS:
            raise REDError('Could not get information for file object {0}'.format(self.object_id), error_code)

        if type == REDFileBase.TYPE_PIPE:
            obj = _attach_or_release(self._session, REDPipe, self.object_id)
        else:
            try:
                self._session._brick.release_object_unchecked(name_string_id, self._session._session_id)
            except:
                # ignoring IPConnection-level error
                print 'REDFileOrPipeAttacher.attach: release_object_unchecked failed'
                traceback.print_exc()

            obj = _attach_or_release(self._session, REDFile, self.object_id)

        self.detach()

        return obj


class REDDirectory(REDObject):
    ENTRY_TYPE_UNKNOWN   = BrickRED.DIRECTORY_ENTRY_TYPE_UNKNOWN
    ENTRY_TYPE_REGULAR   = BrickRED.DIRECTORY_ENTRY_TYPE_REGULAR
    ENTRY_TYPE_DIRECTORY = BrickRED.DIRECTORY_ENTRY_TYPE_DIRECTORY
    ENTRY_TYPE_CHARACTER = BrickRED.DIRECTORY_ENTRY_TYPE_CHARACTER
    ENTRY_TYPE_BLOCK     = BrickRED.DIRECTORY_ENTRY_TYPE_BLOCK
    ENTRY_TYPE_FIFO      = BrickRED.DIRECTORY_ENTRY_TYPE_FIFO
    ENTRY_TYPE_SYMLINK   = BrickRED.DIRECTORY_ENTRY_TYPE_SYMLINK
    ENTRY_TYPE_SOCKET    = BrickRED.DIRECTORY_ENTRY_TYPE_SOCKET

    def __repr__(self):
        return '<REDDirectory object_id: {0}, name: {1}>'.format(self.object_id, repr(self._name))

    def _initialize(self):
        self._name    = None
        self._entries = None

    def update(self):
        if self.object_id is None:
            raise RuntimeError('Cannot update unattached directory object')

        # get name
        error_code, name_string_id = self._session._brick.get_directory_name(self.object_id, self._session._session_id)

        if error_code != REDError.E_SUCCESS:
            raise REDError('Could not get name of directory object {0}'.format(self.object_id), error_code)

        self._name = _attach_or_release(self._session, REDString, name_string_id)

        # rewind
        error_code = self._session._brick.rewind_directory(self.object_id)

        if error_code != REDError.E_SUCCESS:
            raise REDError('Could not rewind directory object {0}'.format(self.object_id), error_code)

        # get entries
        entries = []

        while True:
            error_code, name_string_id, type = self._session._brick.get_next_directory_entry(self.object_id, self._session._session_id)

            if error_code == REDError.E_NO_MORE_DATA:
                break

            if error_code != REDError.E_SUCCESS:
                raise REDError('Could not get next entry of directory object {0}'.format(self.object_id), error_code)

            entries.append((_attach_or_release(self._session, REDString, name_string_id), type))

        self._entries = entries

    def open(self, name):
        self.release()

        if not isinstance(name, REDString):
            name = REDString(self._session).allocate(name)

        error_code, object_id = self._session._brick.open_directory(name.object_id, self._session._session_id)

        if error_code != REDError.E_SUCCESS:
            raise REDError('Could not open directory object', error_code)

        self.attach(object_id)

        return self

    @property
    def name(self):    return self._name
    @property
    def entries(self): return self._entries


DIRECTORY_FLAG_RECURSIVE = BrickRED.DIRECTORY_FLAG_RECURSIVE
DIRECTORY_FLAG_EXCLUSIVE = BrickRED.DIRECTORY_FLAG_EXCLUSIVE

def create_directory(session, name, flags, permissions, uid, gid):
    if not isinstance(name, REDString):
        name = REDString(session).allocate(name)

    error_code = session._brick.create_directory(name.object_id, flags, permissions, uid, gid)

    if error_code != REDError.E_SUCCESS:
        raise REDError('Could not create directory', error_code)


class REDProcess(REDObject):
    SIGNAL_INTERRUPT = BrickRED.PROCESS_SIGNAL_INTERRUPT
    SIGNAL_QUIT      = BrickRED.PROCESS_SIGNAL_QUIT
    SIGNAL_ABORT     = BrickRED.PROCESS_SIGNAL_ABORT
    SIGNAL_KILL      = BrickRED.PROCESS_SIGNAL_KILL
    SIGNAL_USER1     = BrickRED.PROCESS_SIGNAL_USER1
    SIGNAL_USER2     = BrickRED.PROCESS_SIGNAL_USER2
    SIGNAL_TERMINATE = BrickRED.PROCESS_SIGNAL_TERMINATE
    SIGNAL_CONTINUE  = BrickRED.PROCESS_SIGNAL_CONTINUE
    SIGNAL_STOP      = BrickRED.PROCESS_SIGNAL_STOP

    STATE_UNKNOWN = BrickRED.PROCESS_STATE_UNKNOWN
    STATE_RUNNING = BrickRED.PROCESS_STATE_RUNNING
    STATE_ERROR   = BrickRED.PROCESS_STATE_ERROR
    STATE_EXITED  = BrickRED.PROCESS_STATE_EXITED
    STATE_KILLED  = BrickRED.PROCESS_STATE_KILLED
    STATE_STOPPED = BrickRED.PROCESS_STATE_STOPPED

    # possible exit code values for error state
    E_INTERNAL_ERROR = 125
    E_CANNOT_EXECUTE = 126
    E_DOES_NOT_EXIST = 127

    _qtcb_state_changed = QtCore.pyqtSignal(int, int, int)

    def __repr__(self):
        return '<REDProcess object_id: {0}>'.format(self.object_id)

    def _initialize(self):
        self._executable        = None
        self._arguments         = None
        self._environment       = None
        self._working_directory = None
        self._pid               = None
        self._uid               = None
        self._gid               = None
        self._stdin             = None
        self._stdout            = None
        self._stderr            = None
        self._state             = None
        self._timestamp         = None
        self._exit_code         = None

        self.state_changed_callback = None

        self._cb_state_changed_emit_cookie = None

    def _attach_callbacks(self):
        self._qtcb_state_changed.connect(self._cb_state_changed, QtCore.Qt.QueuedConnection)
        self._cb_state_changed_emit_cookie = self._session._brick.add_callback(BrickRED.CALLBACK_PROCESS_STATE_CHANGED,
                                                                               self._cb_state_changed_emit)

    def _detach_callbacks(self):
        self._qtcb_state_changed.disconnect(self._cb_state_changed)
        self._session._brick.remove_callback(BrickRED.CALLBACK_PROCESS_STATE_CHANGED,
                                             self._cb_state_changed_emit_cookie)

        self._cb_state_changed_emit_cookie = None

    def _cb_state_changed_emit(self, process_id, state, timestamp, exit_code):
        if self.object_id != process_id:
            return

        # cannot directly use emit function as callback functions, because this
        # triggers a segfault on the second call for some unknown reason. adding
        # a method in between helps
        self._qtcb_state_changed.emit(state, timestamp, exit_code)

    def _cb_state_changed(self, state, timestamp, exit_code):
        self._state     = state
        self._timestamp = timestamp
        self._exit_code = exit_code

        if state != REDProcess.STATE_RUNNING and state != REDProcess.STATE_STOPPED:
            self._pid = None

        state_changed_callback = self.state_changed_callback

        if state_changed_callback is not None:
            state_changed_callback(self)

    def _fake_state_change_callback(self):
        self.update_state()
        self._cb_state_changed(self._state, self._timestamp, self._exit_code)

    def update(self):
        self.update_command()
        self.update_identity()
        self.update_stdio()
        self.update_state()

    def update_command(self):
        if self.object_id is None:
            raise RuntimeError('Cannot update unattached process object')

        error_code, executable_string_id, arguments_list_id, \
        environment_list_id, working_directory_string_id = self._session._brick.get_process_command(self.object_id, self._session._session_id)

        if error_code != REDError.E_SUCCESS:
            raise REDError('Could not get command of process object {0}'.format(self.object_id), error_code)

        executable        = _attach_or_release(self._session, REDString, executable_string_id, [arguments_list_id, environment_list_id, working_directory_string_id])
        arguments         = _attach_or_release(self._session, REDList, arguments_list_id, [environment_list_id, working_directory_string_id])
        environment       = _attach_or_release(self._session, REDList, environment_list_id, [working_directory_string_id])
        working_directory = _attach_or_release(self._session, REDString, working_directory_string_id)

        self._executable        = executable
        self._arguments         = arguments
        self._environment       = environment
        self._working_directory = working_directory

    def update_identity(self):
        if self.object_id is None:
            raise RuntimeError('Cannot update unattached process object')

        error_code, pid, uid, gid = self._session._brick.get_process_identity(self.object_id)

        if error_code != REDError.E_SUCCESS:
            raise REDError('Could not get identity of process object {0}'.format(self.object_id), error_code)

        self._pid = pid
        self._uid = uid
        self._gid = gid

    def update_stdio(self):
        if self.object_id is None:
            raise RuntimeError('Cannot update unattached process object')

        error_code, stdin_file_id, stdout_file_id, stderr_file_id = self._session._brick.get_process_stdio(self.object_id, self._session._session_id)

        if error_code != REDError.E_SUCCESS:
            raise REDError('Could not get stdio of process object {0}'.format(self.object_id), error_code)

        stdin  = _attach_or_release(self._session, REDFile, stdin_file_id, [stdout_file_id, stderr_file_id])
        stdout = _attach_or_release(self._session, REDFile, stdout_file_id, [stderr_file_id])
        stderr = _attach_or_release(self._session, REDFile, stderr_file_id)

        self._stdin  = stdin
        self._stdout = stdout
        self._stderr = stderr

    def update_state(self):
        if self.object_id is None:
            raise RuntimeError('Cannot update unattached process object')

        error_code, state, timestamp, exit_code = self._session._brick.get_process_state(self.object_id)

        if error_code != REDError.E_SUCCESS:
            raise REDError('Could not get state of process object {0}'.format(self.object_id), error_code)

        self._state     = state
        self._timestamp = timestamp
        self._exit_code = exit_code

    def spawn(self, executable, arguments, environment, working_directory,
              uid, gid, stdin, stdout, stderr):
        self.release()

        if not isinstance(executable, REDString):
            executable = REDString(self._session).allocate(executable)

        if not isinstance(arguments, REDList):
            arguments = REDList(self._session).allocate(arguments)

        if not isinstance(environment, REDList):
            environment = REDList(self._session).allocate(environment)

        if not isinstance(working_directory, REDString):
            working_directory = REDString(self._session).allocate(working_directory)

        error_code, object_id = self._session._brick.spawn_process(executable.object_id,
                                                                   arguments.object_id,
                                                                   environment.object_id,
                                                                   working_directory.object_id,
                                                                   uid, gid,
                                                                   stdin.object_id,
                                                                   stdout.object_id,
                                                                   stderr.object_id,
                                                                   self._session._session_id)

        if error_code != REDError.E_SUCCESS:
            raise REDError('Could not spawn process object', error_code)

        self.attach(object_id, False)

        self._executable        = executable
        self._arguments         = arguments
        self._environment       = environment
        self._working_directory = working_directory
        self._uid               = uid
        self._gid               = gid
        self._stdin             = stdin
        self._stdout            = stdout
        self._stderr            = stderr

        self.update_identity()
        self.update_state()

        return self

    def kill(self, signal):
        if self.object_id is None:
            raise RuntimeError('Cannot kill unattached process object')

        error_code = self._session._brick.kill_process(self.object_id, signal)

        if error_code != REDError.E_SUCCESS:
            raise REDError('Could not kill process object {0}'.format(self.object_id), error_code)

    @property
    def executable(self):        return self._executable
    @property
    def arguments(self):         return self._arguments
    @property
    def environment(self):       return self._environment
    @property
    def working_directory(self): return self._working_directory
    @property
    def pid(self):               return self._pid
    @property
    def uid(self):               return self._uid
    @property
    def gid(self):               return self._gid
    @property
    def stdin(self):             return self._stdin
    @property
    def stdout(self):            return self._stdout
    @property
    def stderr(self):            return self._stderr
    @property
    def state(self):             return self._state
    @property
    def timestamp(self):         return self._timestamp
    @property
    def exit_code(self):         return self._exit_code


def get_processes(session):
    error_code, processes_list_id = session._brick.get_processes(session._session_id)

    if error_code != REDError.E_SUCCESS:
        raise REDError('Could not get processes list object', error_code)

    return _attach_or_release(session, REDList, processes_list_id)


class REDProgram(REDObject):
    STDIO_REDIRECTION_DEV_NULL       = BrickRED.PROGRAM_STDIO_REDIRECTION_DEV_NULL
    STDIO_REDIRECTION_PIPE           = BrickRED.PROGRAM_STDIO_REDIRECTION_PIPE
    STDIO_REDIRECTION_FILE           = BrickRED.PROGRAM_STDIO_REDIRECTION_FILE
    STDIO_REDIRECTION_INDIVIDUAL_LOG = BrickRED.PROGRAM_STDIO_REDIRECTION_INDIVIDUAL_LOG
    STDIO_REDIRECTION_CONTINUOUS_LOG = BrickRED.PROGRAM_STDIO_REDIRECTION_CONTINUOUS_LOG
    STDIO_REDIRECTION_STDOUT         = BrickRED.PROGRAM_STDIO_REDIRECTION_STDOUT

    START_MODE_NEVER     = BrickRED.PROGRAM_START_MODE_NEVER
    START_MODE_ALWAYS    = BrickRED.PROGRAM_START_MODE_ALWAYS
    START_MODE_INTERVAL  = BrickRED.PROGRAM_START_MODE_INTERVAL
    START_MODE_CRON      = BrickRED.PROGRAM_START_MODE_CRON

    SCHEDULER_STATE_STOPPED = BrickRED.PROGRAM_SCHEDULER_STATE_STOPPED
    SCHEDULER_STATE_RUNNING = BrickRED.PROGRAM_SCHEDULER_STATE_RUNNING

    _qtcb_scheduler_state_changed = QtCore.pyqtSignal()
    _qtcb_process_spawned = QtCore.pyqtSignal()

    def __repr__(self):
        return '<REDProgram object_id: {0}, identifier: {1}>'.format(self.object_id, self._identifier)

    def _initialize(self):
        self._identifier             = None
        self._root_directory         = None
        self._executable             = None
        self._arguments              = None
        self._environment            = None
        self._working_directory      = None
        self._stdin_redirection      = None
        self._stdin_file_name        = None
        self._stdout_redirection     = None
        self._stdout_file_name       = None
        self._stderr_redirection     = None
        self._stderr_file_name       = None
        self._start_mode             = None
        self._continue_after_error   = None
        self._start_interval         = None
        self._start_fields           = None
        self._scheduler_state        = None
        self._scheduler_timestamp    = None
        self._scheduler_message      = None
        self._last_spawned_process   = None
        self._last_spawned_timestamp = None
        self._custom_options         = None

        self.enable_callbacks                 = False
        self.scheduler_state_changed_callback = None
        self.process_spawned_callback         = None

        self._cb_scheduler_state_changed_emit_cookie = None
        self._cb_process_spawned_emit_cookie         = None

    def _attach_callbacks(self):
        self._qtcb_scheduler_state_changed.connect(self._cb_scheduler_state_changed, QtCore.Qt.QueuedConnection)
        self._cb_scheduler_state_changed_emit_cookie = self._session._brick.add_callback(BrickRED.CALLBACK_PROGRAM_SCHEDULER_STATE_CHANGED,
                                                                                          self._cb_scheduler_state_changed_emit)

        self._qtcb_process_spawned.connect(self._cb_process_spawned, QtCore.Qt.QueuedConnection)
        self._cb_process_spawned_emit_cookie = self._session._brick.add_callback(BrickRED.CALLBACK_PROGRAM_PROCESS_SPAWNED,
                                                                                 self._cb_process_spawned_emit)

    def _detach_callbacks(self):
        self._qtcb_scheduler_state_changed.disconnect(self._cb_scheduler_state_changed)
        self._session._brick.remove_callback(BrickRED.CALLBACK_PROGRAM_SCHEDULER_STATE_CHANGED,
                                             self._cb_scheduler_state_changed_emit_cookie)

        self._qtcb_process_spawned.disconnect(self._cb_process_spawned)
        self._session._brick.remove_callback(BrickRED.CALLBACK_PROGRAM_PROCESS_SPAWNED,
                                             self._cb_process_spawned_emit_cookie)


        self._cb_scheduler_state_changed_emit_cookie = None
        self._cb_process_spawned_emit_cookie         = None

    def _cb_scheduler_state_changed_emit(self, program_id):
        if not self.enable_callbacks or self.object_id != program_id:
            return

        # cannot directly use emit function as callback functions, because this
        # triggers a segfault on the second call for some unknown reason. adding
        # a method in between helps
        self._qtcb_scheduler_state_changed.emit()

    def _cb_scheduler_state_changed(self):
        error_code, state, timestamp, message_string_id = self._session._brick.get_program_scheduler_state(self.object_id, self._session._session_id)

        if error_code != REDError.E_SUCCESS:
            return

        try:
            message = _attach_or_release(self._session, REDString, message_string_id)
        except:
            message = None

            print 'REDProgram._cb_scheduler_state_changed: _attach_or_release failed'
            traceback.print_exc() # FIXME: error handling

        self._scheduler_state     = state
        self._scheduler_timestamp = timestamp
        self._scheduler_message   = message

        if self._scheduler_message == None:
            return

        scheduler_state_changed_callback = self.scheduler_state_changed_callback

        if scheduler_state_changed_callback != None:
            scheduler_state_changed_callback(self)

    def _cb_process_spawned_emit(self, program_id):
        if not self.enable_callbacks or self.object_id != program_id:
            return

        # cannot directly use emit function as callback functions, because this
        # triggers a segfault on the second call for some unknown reason. adding
        # a method in between helps
        self._qtcb_process_spawned.emit()

    def _cb_process_spawned(self):
        error_code, process_id, timestamp = self._session._brick.get_last_spawned_program_process(self.object_id, self._session._session_id)

        if error_code != REDError.E_SUCCESS:
            return

        try:
            process = _attach_or_release(self._session, REDProcess, process_id)
        except:
            process = None

            print 'REDProgram._cb_process_spawned: _attach_or_release failed'
            traceback.print_exc() # FIXME: error handling

        self._last_spawned_process   = process
        self._last_spawned_timestamp = timestamp

        if self._last_spawned_process == None:
            return

        process_spawned_callback = self.process_spawned_callback

        if process_spawned_callback != None:
            process_spawned_callback(self)

        if self._last_spawned_process.state != REDProcess.STATE_RUNNING:
            try:
                self._last_spawned_process._fake_state_change_callback()
            except:
                print 'REDProgram._cb_process_spawned: _fake_state_change_callback failed'
                traceback.print_exc() # FIXME: error handling

    def update(self):
        self.update_identifier()
        self.update_root_directory()
        self.update_command()
        self.update_stdio_redirection()
        self.update_schedule()
        self.update_scheduler_state()
        self.update_last_spawned_process()
        self.update_custom_options()

    def update_identifier(self):
        if self.object_id is None:
            raise RuntimeError('Cannot update unattached program object')

        error_code, identifier_string_id = self._session._brick.get_program_identifier(self.object_id, self._session._session_id)

        if error_code != REDError.E_SUCCESS:
            raise REDError('Could not get identifier of program object {0}'.format(self.object_id), error_code)

        self._identifier = _attach_or_release(self._session, REDString, identifier_string_id)

    def update_root_directory(self):
        if self.object_id is None:
            raise RuntimeError('Cannot update unattached program object')

        error_code, root_directory_string_id = self._session._brick.get_program_root_directory(self.object_id, self._session._session_id)

        if error_code != REDError.E_SUCCESS:
            raise REDError('Could not get root directory of program object {0}'.format(self.object_id), error_code)

        self._root_directory = _attach_or_release(self._session, REDString, root_directory_string_id)

    def update_command(self):
        if self.object_id is None:
            raise RuntimeError('Cannot update unattached program object')

        error_code, executable_string_id, arguments_list_id, \
        environment_list_id, working_directory_string_id = self._session._brick.get_program_command(self.object_id, self._session._session_id)

        if error_code != REDError.E_SUCCESS:
            raise REDError('Could not get command of program object {0}'.format(self.object_id), error_code)

        executable        = _attach_or_release(self._session, REDString, executable_string_id, [arguments_list_id, environment_list_id, working_directory_string_id])
        arguments         = _attach_or_release(self._session, REDList, arguments_list_id, [environment_list_id, working_directory_string_id])
        environment       = _attach_or_release(self._session, REDList, environment_list_id, [working_directory_string_id])
        working_directory = _attach_or_release(self._session, REDString, working_directory_string_id)

        self._executable        = executable
        self._arguments         = arguments
        self._environment       = environment
        self._working_directory = working_directory

    def update_stdio_redirection(self):
        if self.object_id is None:
            raise RuntimeError('Cannot update unattached program object')

        error_code, stdin_redirection, stdin_file_name_string_id, stdout_redirection, stdout_file_name_string_id, \
        stderr_redirection, stderr_file_name_string_id = self._session._brick.get_program_stdio_redirection(self.object_id, self._session._session_id)

        if error_code != REDError.E_SUCCESS:
            raise REDError('Could not get stdio redirection of program object {0}'.format(self.object_id), error_code)

        # stdin
        if stdin_redirection == REDProgram.STDIO_REDIRECTION_FILE:
            extra_object_ids_to_release_on_error = []

            if stdout_redirection == REDProgram.STDIO_REDIRECTION_FILE:
                extra_object_ids_to_release_on_error.append(stdout_file_name_string_id)

            if stderr_redirection == REDProgram.STDIO_REDIRECTION_FILE:
                extra_object_ids_to_release_on_error.append(stderr_file_name_string_id)

            stdin_file_name = _attach_or_release(self._session, REDString, stdin_file_name_string_id, extra_object_ids_to_release_on_error)
        else:
            stdin_file_name = None

        # stdout
        if stdout_redirection == REDProgram.STDIO_REDIRECTION_FILE:
            extra_object_ids_to_release_on_error = []

            if stderr_redirection == REDProgram.STDIO_REDIRECTION_FILE:
                extra_object_ids_to_release_on_error.append(stderr_file_name_string_id)

            stdout_file_name = _attach_or_release(self._session, REDString, stdout_file_name_string_id, extra_object_ids_to_release_on_error)
        else:
            stdout_file_name = None

        # stderr
        if stderr_redirection == REDProgram.STDIO_REDIRECTION_FILE:
            stderr_file_name = _attach_or_release(self._session, REDString, stderr_file_name_string_id)
        else:
            stderr_file_name = None

        self._stdin_redirection  = stdin_redirection
        self._stdin_file_name    = stdin_file_name
        self._stdout_redirection = stdout_redirection
        self._stdout_file_name   = stdout_file_name
        self._stderr_redirection = stderr_redirection
        self._stderr_file_name   = stderr_file_name

    def update_schedule(self):
        if self.object_id is None:
            raise RuntimeError('Cannot update unattached program object')

        error_code, start_mode, continue_after_error, start_interval, \
        start_fields_string_id = self._session._brick.get_program_schedule(self.object_id, self._session._session_id)

        if error_code != REDError.E_SUCCESS:
            raise REDError('Could not get schedule of program object {0}'.format(self.object_id), error_code)

        if start_mode == REDProgram.START_MODE_CRON:
            start_fields = _attach_or_release(self._session, REDString, start_fields_string_id)
        else:
            start_fields = None

        self._start_mode           = start_mode
        self._continue_after_error = continue_after_error
        self._start_interval       = start_interval
        self._start_fields         = start_fields

    def update_scheduler_state(self):
        if self.object_id is None:
            raise RuntimeError('Cannot update unattached program object')

        error_code, state, timestamp, message_string_id = self._session._brick.get_program_scheduler_state(self.object_id, self._session._session_id)

        if error_code != REDError.E_SUCCESS:
            raise REDError('Could not get scheduler state of program object {0}'.format(self.object_id), error_code)

        message = _attach_or_release(self._session, REDString, message_string_id)

        self._scheduler_state     = state
        self._scheduler_timestamp = timestamp
        self._scheduler_message   = message

    def update_last_spawned_process(self):
        if self.object_id is None:
            raise RuntimeError('Cannot update unattached program object')

        if self._last_spawned_process != None:
            state_changed_callback = self._last_spawned_process.state_changed_callback
        else:
            state_changed_callback = None

        error_code, process_id, timestamp = self._session._brick.get_last_spawned_program_process(self.object_id, self._session._session_id)

        if error_code == REDError.E_DOES_NOT_EXIST:
            self._last_spawned_process   = None
            self._last_spawned_timestamp = None

            return

        if error_code != REDError.E_SUCCESS:
            raise REDError('Could not get last spawned process of program object {0}'.format(self.object_id), error_code)

        self._last_spawned_process   = _attach_or_release(self._session, REDProcess, process_id)
        self._last_spawned_timestamp = timestamp

        if self._last_spawned_process != None:
            self._last_spawned_process.state_changed_callback = state_changed_callback

    def update_custom_options(self):
        if self.object_id is None:
            raise RuntimeError('Cannot update unattached program object')

        error_code, custom_option_names_list_id = self._session._brick.get_custom_program_option_names(self.object_id, self._session._session_id)

        if error_code != REDError.E_SUCCESS:
            raise REDError('Could not get list of custom option names of program object {0}'.format(self.object_id), error_code)

        custom_option_names = _attach_or_release(self._session, REDList, custom_option_names_list_id)
        custom_options      = {}

        for name in custom_option_names.items:
            error_code, custom_option_value_string_id = \
            self._session._brick.get_custom_program_option_value(self.object_id, name.object_id, self._session._session_id)

            if error_code != REDError.E_SUCCESS:
                raise REDError('Could not get custom option value of program object {0}'.format(self.object_id), error_code)

            custom_options[unicode(name)] = _attach_or_release(self._session, REDString, custom_option_value_string_id)

        self._custom_options = custom_options

    def define(self, identifier):
        self.release()

        if not isinstance(identifier, REDString):
            identifier = REDString(self._session).allocate(identifier)

        error_code, object_id = self._session._brick.define_program(identifier.object_id,
                                                                    self._session._session_id)

        if error_code != REDError.E_SUCCESS:
            raise REDError('Could not define program object', error_code)

        self.attach(object_id)

        return self

    def purge(self):
        if self.object_id is None:
            raise RuntimeError('Cannot purge unattached program object')

        cookie = 0

        for c in str(self._identifier):
            cookie += ord(c)

        error_code = self._session._brick.purge_program(self.object_id, cookie)

        if error_code != REDError.E_SUCCESS:
            raise REDError('Could not purge program object {0}'.format(self.object_id), error_code)

    def set_command(self, executable, arguments, environment, working_directory):
        if self.object_id is None:
            raise RuntimeError('Cannot set command for unattached program object')

        if not isinstance(executable, REDString):
            executable = REDString(self._session).allocate(executable)

        if not isinstance(arguments, REDList):
            arguments = REDList(self._session).allocate(arguments)

        if not isinstance(environment, REDList):
            environment = REDList(self._session).allocate(environment)

        if not isinstance(working_directory, REDString):
            working_directory = REDString(self._session).allocate(working_directory)

        error_code = self._session._brick.set_program_command(self.object_id,
                                                              executable.object_id,
                                                              arguments.object_id,
                                                              environment.object_id,
                                                              working_directory.object_id)

        if error_code != REDError.E_SUCCESS:
            raise REDError('Could not set command for program object {0}'.format(self.object_id), error_code)

        self._executable        = executable
        self._arguments         = arguments
        self._environment       = environment
        self._working_directory = working_directory

    def set_stdio_redirection(self, stdin_redirection, stdin_file_name,
                              stdout_redirection, stdout_file_name,
                              stderr_redirection, stderr_file_name):
        if self.object_id is None:
            raise RuntimeError('Cannot set stdio redirection for unattached program object')

        # stdin
        if stdin_redirection == REDProgram.STDIO_REDIRECTION_FILE:
            if not isinstance(stdin_file_name, REDString):
                stdin_file_name = REDString(self._session).allocate(stdin_file_name)

            stdin_file_name_object_id = stdin_file_name.object_id
        else:
            stdin_file_name           = None
            stdin_file_name_object_id = 0

        # stdout
        if stdout_redirection == REDProgram.STDIO_REDIRECTION_FILE:
            if not isinstance(stdout_file_name, REDString):
                stdout_file_name = REDString(self._session).allocate(stdout_file_name)

            stdout_file_name_object_id = stdout_file_name.object_id
        else:
            stdout_file_name           = None
            stdout_file_name_object_id = 0

        # stderr
        if stderr_redirection == REDProgram.STDIO_REDIRECTION_FILE:
            if not isinstance(stderr_file_name, REDString):
                stderr_file_name = REDString(self._session).allocate(stderr_file_name)

            stderr_file_name_object_id = stderr_file_name.object_id
        else:
            stderr_file_name           = None
            stderr_file_name_object_id = 0

        error_code = self._session._brick.set_program_stdio_redirection(self.object_id,
                                                                        stdin_redirection,
                                                                        stdin_file_name_object_id,
                                                                        stdout_redirection,
                                                                        stdout_file_name_object_id,
                                                                        stderr_redirection,
                                                                        stderr_file_name_object_id)

        if error_code != REDError.E_SUCCESS:
            raise REDError('Could not set stdio redirection for program object {0}'.format(self.object_id), error_code)

        self._stdin_redirection  = stdin_redirection
        self._stdin_file_name    = stdin_file_name
        self._stdout_redirection = stdout_redirection
        self._stdout_file_name   = stdout_file_name
        self._stderr_redirection = stderr_redirection
        self._stderr_file_name   = stderr_file_name

    def set_schedule(self, start_mode, continue_after_error, start_interval, start_fields):
        if self.object_id is None:
            raise RuntimeError('Cannot set schedule for unattached program object')

        if start_mode == REDProgram.START_MODE_CRON:
            if not isinstance(start_fields, REDString):
                start_fields = REDString(self._session).allocate(start_fields)

            start_fields_object_id = start_fields.object_id
        else:
            start_fields           = None
            start_fields_object_id = 0

        error_code = self._session._brick.set_program_schedule(self.object_id,
                                                               start_mode,
                                                               continue_after_error,
                                                               start_interval,
                                                               start_fields_object_id)

        if error_code != REDError.E_SUCCESS:
            raise REDError('Could not set schedule for program object {0}'.format(self.object_id), error_code)

        self._start_mode           = start_mode
        self._continue_after_error = continue_after_error
        self._start_interval       = start_interval
        self._start_fields         = start_fields

    def continue_schedule(self):
        if self.object_id is None:
            raise RuntimeError('Cannot continue schedule of unattached program object now')

        error_code = self._session._brick.continue_program_schedule(self.object_id)

        if error_code != REDError.E_SUCCESS:
            raise REDError('Could not continue schedule of program object {0} now'.format(self.object_id), error_code)

    def start(self):
        if self.object_id is None:
            raise RuntimeError('Cannot start unattached program object now')

        error_code = self._session._brick.start_program(self.object_id)

        if error_code != REDError.E_SUCCESS:
            raise REDError('Could not start program object {0} now'.format(self.object_id), error_code)

    def set_custom_option_value(self, name, value):
        if self.object_id is None:
            raise RuntimeError('Cannot set custom option for unattached program object')

        if isinstance(value, list):
            self.set_custom_option_value_list(name, value)
        else:
            if not isinstance(name, REDString):
                name = REDString(self._session).allocate(name)

            if isinstance(value, bool):
                if value:
                    value = 'true'
                else:
                    value = 'false'

            if not isinstance(value, REDString):
                value = REDString(self._session).allocate(value)

            error_code = self._session._brick.set_custom_program_option_value(self.object_id, name.object_id, value.object_id)

            if error_code != REDError.E_SUCCESS:
                raise REDError('Could not set custom option for program object {0}'.format(self.object_id), error_code)

            self._custom_options[unicode(name)] = value

    def set_custom_option_value_list(self, name, values):
        if self.object_id is None:
            raise RuntimeError('Cannot set custom option for unattached program object')

        # FIXME: remove all custom options that start with <name>.item* to ensure that
        #        shrinking a list doesn't leaf old items behind
        for i, value in enumerate(values):
            self.set_custom_option_value(name + '.item' + str(i), unicode(value))

        self.set_custom_option_value(name + '.length', unicode(len(values)))

    def cast_custom_option_value(self, name, cast, default):
        try:
            string = self._custom_options[unicode(name)]
        except KeyError:
            return default

        if cast == bool:
            if unicode(string) == 'true':
                return True
            elif unicode(string) == 'false':
                return False
            else:
                return default
        else:
            try:
                return cast(unicode(string))
            except ValueError:
                return default

    def cast_custom_option_value_list(self, name, cast, default):
        length = self.cast_custom_option_value(name + '.length', int, None)

        if length == None:
            return default

        values = []

        for i in range(max(length, 0)):
            value = self.cast_custom_option_value(name + '.item' + str(i), cast, None)

            if value == None:
                return default

            values.append(value)

        return values

    @property
    def identifier(self):             return self._identifier
    @property
    def root_directory(self):         return self._root_directory
    @property
    def executable(self):             return self._executable
    @property
    def arguments(self):              return self._arguments
    @property
    def environment(self):            return self._environment
    @property
    def working_directory(self):      return self._working_directory
    @property
    def stdin_redirection(self):      return self._stdin_redirection
    @property
    def stdin_file_name(self):        return self._stdin_file_name
    @property
    def stdout_redirection(self):     return self._stdout_redirection
    @property
    def stdout_file_name(self):       return self._stdout_file_name
    @property
    def stderr_redirection(self):     return self._stderr_redirection
    @property
    def stderr_file_name(self):       return self._stderr_file_name
    @property
    def start_mode(self):             return self._start_mode
    @property
    def continue_after_error(self):   return self._continue_after_error
    @property
    def start_interval(self):         return self._start_interval
    @property
    def start_fields(self):           return self._start_fields
    @property
    def scheduler_state(self):        return self._scheduler_state
    @property
    def scheduler_timestamp(self):    return self._scheduler_timestamp
    @property
    def scheduler_message(self):      return self._scheduler_message
    @property
    def last_spawned_process(self):   return self._last_spawned_process
    @property
    def last_spawned_timestamp(self): return self._last_spawned_timestamp
    @property
    def custom_options(self):         return self._custom_options


def get_programs(session):
    error_code, programs_list_id = session._brick.get_programs(session._session_id)

    if error_code != REDError.E_SUCCESS:
        raise REDError('Could not get programs list object', error_code)

    return _attach_or_release(session, REDList, programs_list_id)


REDObject._subclasses = {
    REDObject.TYPE_STRING:    REDString,
    REDObject.TYPE_LIST:      REDList,
    REDObject.TYPE_FILE:      REDFileOrPipeAttacher,
    REDObject.TYPE_DIRECTORY: REDDirectory,
    REDObject.TYPE_PROCESS:   REDProcess,
    REDObject.TYPE_PROGRAM:   REDProgram
}
