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
from PyQt4.QtCore import QObject, pyqtSignal
from brickv.bindings.brick_red import BrickRED

# Number of chunks written in one async read/write burst
ASYNC_BURST_CHUNKS = 100

class REDError(Exception):
    E_SUCCESS                  = 0
    E_UNKNOWN_ERROR            = 1
    E_INVALID_OPERATION        = 2
    E_OPERATION_ABORTED        = 3
    E_INTERNAL_ERROR           = 4
    E_UNKNOWN_OBJECT_ID        = 5
    E_NO_FREE_OBJECT_ID        = 6
    E_OBJECT_IS_LOCKED         = 7
    E_NO_MORE_DATA             = 8
    E_WRONG_LIST_ITEM_TYPE     = 9
    E_MALFORMED_PROGRAM_CONFIG = 10
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

    _error_code_names = {
        E_SUCCESS                  : 'E_SUCCESS',
        E_UNKNOWN_ERROR            : 'E_UNKNOWN_ERROR',
        E_INVALID_OPERATION        : 'E_INVALID_OPERATION',
        E_OPERATION_ABORTED        : 'E_OPERATION_ABORTED',
        E_INTERNAL_ERROR           : 'E_INTERNAL_ERROR',
        E_UNKNOWN_OBJECT_ID        : 'E_UNKNOWN_OBJECT_ID',
        E_NO_FREE_OBJECT_ID        : 'E_NO_FREE_OBJECT_ID',
        E_OBJECT_IS_LOCKED         : 'E_OBJECT_IS_LOCKED',
        E_NO_MORE_DATA             : 'E_NO_MORE_DATA',
        E_WRONG_LIST_ITEM_TYPE     : 'E_WRONG_LIST_ITEM_TYPE',
        E_MALFORMED_PROGRAM_CONFIG : 'E_MALFORMED_PROGRAM_CONFIG',
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
        E_NOT_SUPPORTED            : 'E_NOT_SUPPORTED'
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
    def message(self):
        return self._message

    @property
    def error_code(self):
        return self._error_code


def _attach_or_release(red, object_class, object_id, extra_object_ids_to_release_on_error=[]):
    try:
        obj = object_class(red).attach(object_id)
    except Exception as e:
        try:
            red.release_object(object_id)
        except:
            # FIXME: error handling
            pass

        for extra_object_id in extra_object_ids_to_release_on_error:
            try:
                red.release_object(extra_object_id)
            except:
                # FIXME: error handling
                pass

        raise e

    return obj


class REDObject(QObject):
    TYPE_STRING    = BrickRED.OBJECT_TYPE_STRING
    TYPE_LIST      = BrickRED.OBJECT_TYPE_LIST
    TYPE_FILE      = BrickRED.OBJECT_TYPE_FILE
    TYPE_DIRECTORY = BrickRED.OBJECT_TYPE_DIRECTORY
    TYPE_PROCESS   = BrickRED.OBJECT_TYPE_PROCESS
    TYPE_PROGRAM   = BrickRED.OBJECT_TYPE_PROGRAM

    _subclasses = {}

    def __init__(self, red):
        QObject.__init__(self)

        self._red = red
        self._object_id = None

        self._initialize()

    def __del__(self):
        self.release()

    def _initialize(self):
        raise NotImplementedError()

    def update(self):
        raise NotImplementedError()

    def attach(self, object_id):
        self.release()

        self._object_id = object_id

        self.update()

        return self

    def detach(self):
        if self._object_id is None:
            raise RuntimeError('Cannot detach unattached object')

        object_id = self._object_id
        self._object_id = None

        self._initialize()

        return object_id

    def release(self):
        if self._object_id is None:
            # releasing an unattached object is allowed and does nothing
            return

        object_id = self.detach()

        try:
            self._red.release_object(object_id)
        except:
            # FIXME: error handling
            pass

    @property
    def object_id(self):
        return self._object_id


class REDString(REDObject):
    MAX_ALLOCATE_BUFFER_LENGTH  = 60
    MAX_SET_CHUNK_BUFFER_LENGTH = 58
    MAX_GET_CHUNK_BUFFER_LENGTH = 63

    def __str__(self):
        return self._data

    def __repr__(self):
        return '<REDString object_id: {0}, data: {1}>'.format(self._object_id, repr(self._data))

    def _initialize(self):
        self._data = None

    def update(self):
        if self._object_id is None:
            raise RuntimeError('Cannot update unattached string object')

        error_code, length = self._red.get_string_length(self._object_id)

        if error_code != REDError.E_SUCCESS:
            raise REDError('Could not get length of string object {0}'.format(self._object_id), error_code)

        data = ''

        while len(data) < length:
            error_code, chunk = self._red.get_string_chunk(self._object_id, len(data))

            if error_code != REDError.E_SUCCESS:
                raise REDError('Could not get chunk of string object {0} at offset {1}'.format(self._object_id, len(data)), error_code)

            data += chunk

        self._data = data

    def allocate(self, data):
        self.release()

        chunk = data[0:REDString.MAX_ALLOCATE_BUFFER_LENGTH]
        remaining_data = data[REDString.MAX_ALLOCATE_BUFFER_LENGTH:]

        error_code, object_id = self._red.allocate_string(len(data), chunk)

        if error_code != REDError.E_SUCCESS:
            raise REDError('Could not allocate string object', error_code)

        self._object_id = object_id

        offset = len(chunk)

        while len(remaining_data) > 0:
            chunk = remaining_data[0:REDString.MAX_SET_CHUNK_BUFFER_LENGTH]
            remaining_data = remaining_data[REDString.MAX_SET_CHUNK_BUFFER_LENGTH:]

            error_code = self._red.set_string_chunk(self._object_id, offset, chunk)

            if error_code != REDError.E_SUCCESS:
                raise REDError('Could not set chunk of string object {0} at offset {1}'.format(self._object_id, offset), error_code)

            offset += len(chunk)

        self._data = data

        return self

    @property
    def data(self):
        return self._data


class REDList(REDObject):
    def __repr__(self):
        return '<REDList object_id: {0}>'.format(self._object_id)

    def _initialize(self):
        self._items = None

    def update(self):
        if self._object_id is None:
            raise RuntimeError('Cannot update unattached list object')

        error_code, length = self._red.get_list_length(self._object_id)

        if error_code != REDError.E_SUCCESS:
            raise REDError('Could not get length of list object {0}'.format(self._object_id), error_code)

        items = []

        for i in range(length):
            error_code, item_object_id, type = self._red.get_list_item(self._object_id, i)

            if error_code != REDError.E_SUCCESS:
                raise REDError('Could not get item at index {0} of list object {1}'.format(i, self._object_id), error_code)

            try:
                wrapper_class = REDObject._subclasses[type]
            except KeyError:
                raise TypeError('List object {0} contains item with unknown type {1} at index {2}'.format(self._object_id, type, i))

            items.append(_attach_or_release(self._red, wrapper_class, item_object_id))

        self._items = items

    def allocate(self, items):
        self.release()

        error_code, object_id = self._red.allocate_list(len(items))

        if error_code != REDError.E_SUCCESS:
            raise REDError('Could not allocate list object', error_code)

        self._object_id = object_id

        for item in items:
            if isinstance(item, str):
                item = REDString(self._red).allocate(item)
            elif not isinstance(item, REDObject):
                raise TypeError('Cannot append {0} item to list object {0}'.format(type(item), self._object_id))

            error_code = self._red.append_to_list(self._object_id, item.object_id)

            if error_code != REDError.E_SUCCESS:
                raise REDError('Could not append item {0} to list object {0}'.format(item.object_id, self._object_id), error_code)

        self._items = items

        return self

    @property
    def items(self):
        return self._items


class REDFileBase(REDObject):
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

    def __init__(self, red):
        REDObject.__init__(self, red)
        self._red.register_callback(BrickRED.CALLBACK_ASYNC_FILE_WRITE, self._cb_async_file_write)

    def _initialize(self):
        self._type = None
        self._name = None
        self._flags = None
        self._permissions = None
        self._uid = None
        self._gid = None
        self._length = None
        self._access_time = None
        self._modification_time = None
        self._status_change_time = None

        self._write_async_remaining_data = None
        self._write_async_callback_status = None
        self._write_async_callback_error = None
        self._write_async_chunks = None

    # Unset all of the temporary async data in case of error.
    def _send_write_async_callback_error(self, error):
        if self._write_async_callback_error != None:
            self._write_async_callback_error(error)

        self._write_async_remaining_data = None
        self._write_async_callback_status = None
        self._write_async_callback_error = None
        self._write_async_length = None

    def _cb_async_file_write(self, file_id, error_code, length_written):
        if error_code != REDError.E_SUCCESS:
            # FIXME: recover seek position on error after successful call?
            self._send_write_async_callback_error(REDError('Could not write to file object {0}'.format(self._object_id), error_code))
            return

        # Remove data of async call.
        # Data of unchecked writes has been removed already.
        self._write_async_remaining_data = self._write_async_remaining_data[length_written:]

        if self._write_async_callback_status != None:
            self._write_async_callback_status(self._write_async_length - len(self._write_async_remaining_data), self._write_async_length)

        # If there is no data remaining we are done.
        if len(self._write_async_remaining_data) == 0:
            self._send_write_async_callback_error(None)
            return

        for i in range(ASYNC_BURST_CHUNKS):
            chunk = self._write_async_remaining_data[0:REDFile.MAX_WRITE_BUFFER_LENGTH]
            length_to_write = len(chunk)
            chunk += [0]*(REDFile.MAX_WRITE_BUFFER_LENGTH - length_to_write)

            if (len(self._write_async_remaining_data) - length_to_write <= 0) or i == (ASYNC_BURST_CHUNKS - 1):
                # FIXME: Do we need a timeout here for the case that no callback comes?
                self._red.write_file_async(self._object_id, chunk, length_to_write)
                break
            else:
                self._red.write_file_unchecked(self._object_id, chunk, length_to_write)
                self._write_async_remaining_data = self._write_async_remaining_data[length_to_write:]

    def update(self):
        if self._object_id is None:
            raise RuntimeError('Cannot update unattached file object')

        error_code, type, name_string_id, flags, permissions, uid, gid, \
        length, access_time, modification_time, status_change_time = self._red.get_file_info(self._object_id)

        if error_code != REDError.E_SUCCESS:
            raise REDError('Could not get information for file object {0}'.format(self._object_id), error_code)

        self._type = type

        if type == REDFileBase.TYPE_PIPE:
            self._name = None
        else:
            self._name = _attach_or_release(self._red, REDString, name_string_id)

        self._flags = flags
        self._permissions = permissions
        self._uid = uid
        self._gid = gid
        self._length = length
        self._access_time = access_time
        self._modification_time = modification_time
        self._status_change_time = status_change_time

    def write(self, data):
        if self._object_id is None:
            raise RuntimeError('Cannot write to unattached file object')

        remaining_data = [ord(x) for x in data]

        while len(remaining_data) > 0:
            chunk = remaining_data[0:REDFile.MAX_WRITE_BUFFER_LENGTH]
            length_to_write = len(chunk)
            chunk += [0]*(REDFile.MAX_WRITE_BUFFER_LENGTH - length_to_write)

            error_code, length_written = self._red.write_file(self._object_id, chunk, length_to_write)

            if error_code != REDError.E_SUCCESS:
                # FIXME: recover seek position on error after successful call?
                raise REDError('Could not write to file object {0}'.format(self._object_id), error_code)

            remaining_data = remaining_data[length_written:]

    def write_async(self, data, callback_error = None, callback_status = None):
        if self._object_id is None:
            raise RuntimeError('Cannot write to unattached file object')

        self._write_async_callback_error = callback_error
        self._write_async_callback_status = callback_status
        self._write_async_remaining_data = [ord(x) for x in data]
        self._write_async_length = len(self._write_async_remaining_data)

        for i in range(ASYNC_BURST_CHUNKS):
            chunk = self._write_async_remaining_data[0:REDFile.MAX_WRITE_BUFFER_LENGTH]
            length_to_write = len(chunk)
            chunk += [0]*(REDFile.MAX_WRITE_BUFFER_LENGTH - length_to_write)

            if (len(self._write_async_remaining_data) - length_to_write <= 0) or i == (ASYNC_BURST_CHUNKS - 1):
                # FIXME: Do we need a timeout here for the case that no callback comes?
                self._red.write_file_async(self._object_id, chunk, length_to_write)
                break
            else:
                self._red.write_file_unchecked(self._object_id, chunk, length_to_write)
                self._write_async_remaining_data = self._write_async_remaining_data[length_to_write:]

    def read(self, length):
        if self._object_id is None:
            raise RuntimeError('Cannot read from unattached file object')

        data = ''

        while length > 0:
            length_to_read = min(length, REDFile.MAX_READ_BUFFER_LENGTH)

            error_code, chunk, length_read = self._red.read_file(self._object_id, length_to_read)

            if error_code != REDError.E_SUCCESS:
                # FIXME: recover seek position on error after successful call?
                raise REDError('Could not read from file object {0}'.format(self._object_id), error_code)

            if length_read == 0:
                break

            data += ''.join([chr(x) for x in chunk[:length_read]])
            length -= length_read

        return data

    @property
    def type(self):
        return self._type

    @property
    def name(self):
        return self._name

    @property
    def flags(self):
        return self._flags

    @property
    def permissions(self):
        return self._permissions

    @property
    def uid(self):
        return self._uid

    @property
    def gid(self):
        return self._gid

    @property
    def length(self):
        return self._length

    @property
    def access_time(self):
        return self._access_time

    @property
    def modification_time(self):
        return self._modification_time

    @property
    def status_change_time(self):
        return self._status_change_time


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

    def __repr__(self):
        return '<REDFile object_id: {0}, name: {1}>'.format(self._object_id, repr(self._name))

    def open(self, name, flags, permissions, uid, gid):
        self.release()

        if not isinstance(name, REDString):
            name = REDString(self._red).allocate(name)

        error_code, object_id = self._red.open_file(name.object_id, flags, permissions, uid, gid)

        if error_code != REDError.E_SUCCESS:
            raise REDError('Could not open file object', error_code)

        self._object_id = object_id

        self.update()

        return self


class REDPipe(REDFileBase):
    FLAG_NON_BLOCKING_READ  = BrickRED.PIPE_FLAG_NON_BLOCKING_READ
    FLAG_NON_BLOCKING_WRITE = BrickRED.PIPE_FLAG_NON_BLOCKING_WRITE

    def __repr__(self):
        return '<REDPipe object_id: {0}>'.format(self._object_id)

    def create(self, flags):
        self.release()

        error_code, object_id = self._red.create_pipe(flags)

        if error_code != REDError.E_SUCCESS:
            raise REDError('Could not create pipe object', error_code)

        self._object_id = object_id

        self.update()

        return self


class REDFileOrPipeAttacher:
    def __repr__(self):
        return '<REDFileOrPipeAttacher object_id: {0}>'.format(self._object_id)

    def _initialize(self):
        pass

    def attach(self, object_id):
        self.release()

        self._object_id = object_id

        error_code, type, name_string_id, _, _, _, _, _, _, _, _ = self._red.get_file_info(self._object_id)

        if error_code != REDError.E_SUCCESS:
            raise REDError('Could not get information for file object {0}'.format(self._object_id), error_code)

        if type == REDFileBase.TYPE_PIPE:
            obj = _attach_or_release(self._red, REDPipe, self._object_id)
        else:
            try:
                self._red.release_object(name_string_id)
            except:
                # FIXME: error handling
                pass

            obj = _attach_or_release(self._red, REDFile, self._object_id)

        self.detach()

        return obj


REDFileInfo = namedtuple('REDFileInfo', ['type', 'permissions', 'uid', 'gid', 'length', 'access_timestamp', 'modification_timestamp', 'status_change_timestamp'])

def lookup_file_info(red, name, follow_symlink):
    if not isinstance(name, REDString):
        name = REDString(red).allocate(name)

    result = red.lookup_file_info(name, follow_symlink)
    error_code = result[0]

    if error_code != REDError.E_SUCCESS:
        raise REDError('Could not lookup file info', error_code)

    return REDFileInfo(result[1:])


def lookup_symlink_target(red, name, canonicalize):
    if not isinstance(name, REDString):
        name = REDString(red).allocate(name)

    error_code, target_string_id = red.lookup_symlink_target(name, canonicalize)

    if error_code != REDError.E_SUCCESS:
        raise REDError('Could not lookup symlink target', error_code)

    return _attach_or_release(red, REDString, target_string_id)


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
        return '<REDDirectory object_id: {0}, name: {1}>'.format(self._object_id, repr(self._name))

    def _initialize(self):
        self._name = None
        self._entries = None

    def update(self):
        if self._object_id is None:
            raise RuntimeError('Cannot update unattached directory object')

        # get name
        error_code, name_string_id = self._red.get_directory_name(self._object_id)

        if error_code != REDError.E_SUCCESS:
            raise REDError('Could not get name of directory object {0}'.format(self._object_id), error_code)

        self._name = _attach_or_release(self._red, REDString, name_string_id)

        # rewind
        error_code = self._red.rewind_directory(self._object_id)

        if error_code != REDError.E_SUCCESS:
            raise REDError('Could not rewind directory object {0}'.format(self._object_id), error_code)

        # get entries
        entries = []

        while True:
            error_code, name_string_id, type = self._red.get_next_directory_entry(self._object_id)

            if error_code == REDError.E_NO_MORE_DATA:
                break

            if error_code != REDError.E_SUCCESS:
                raise REDError('Could not get next entry of directory object {0}'.format(self._object_id), error_code)

            entries.append((_attach_or_release(self._red, REDString, name_string_id), type))

        self._entries = entries

    def open(self, name):
        self.release()

        if not isinstance(name, REDString):
            name = REDString(self._red).allocate(name)

        error_code, object_id = self._red.open_directory(name.object_id)

        if error_code != REDError.E_SUCCESS:
            raise REDError('Could not open directory object', error_code)

        self._object_id = object_id

        self.update()

        return self

    @property
    def name(self):
        return self._name

    @property
    def entries(self):
        return self._entries


DIRECTORY_FLAG_RECURSIVE = BrickRED.DIRECTORY_FLAG_RECURSIVE
DIRECTORY_FLAG_EXCLUSIVE = BrickRED.DIRECTORY_FLAG_EXCLUSIVE

def create_directory(red, name, flags, permissions, uid, gid):
    if not isinstance(name, REDString):
        name = REDString(red).allocate(name)

    error_code = red.create_directory(name, flags, permissions, uid, gid)

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

    _qtcb_state_changed = pyqtSignal(int, int, int)

    def __init__(self, *args):
        REDObject.__init__(self, *args)

        self._qtcb_state_changed.connect(self._cb_state_changed)
        self._red.register_callback(BrickRED.CALLBACK_PROCESS_STATE_CHANGED,
                                    self._qtcb_state_changed.emit)

    def __repr__(self):
        return '<REDProcess object_id: {0}>'.format(self._object_id)

    def _initialize(self):
        self._executable = None
        self._arguments = None
        self._environment = None
        self._working_directory = None
        self._pid = None
        self._uid = None
        self._gid = None
        self._stdin = None
        self._stdout = None
        self._stderr = None
        self._state = None
        self._exit_code = None
        self.state_changed_callback = None

    def _cb_state_changed(self, process_id, state, exit_code):
        if self._object_id != process_id:
            return

        self._state = state
        self._exit_code = exit_code

        if state != REDProcess.STATE_RUNNING and state != REDProcess.STATE_STOPPED:
            self._pid = None

        state_changed_callback = self.state_changed_callback

        if state_changed_callback is not None:
            state_changed_callback(self)

    def update(self):
        self.update_command()
        self.update_identity()
        self.update_stdio()
        self.update_state()

    def update_command(self):
        if self._object_id is None:
            raise RuntimeError('Cannot update unattached process object')

        error_code, executable_string_id, arguments_list_id, \
        environment_list_id, working_directory_string_id = self._red.get_process_command(self._object_id)

        if error_code != REDError.E_SUCCESS:
            raise REDError('Could not get command of process object {0}'.format(self._object_id), error_code)

        self._executable = _attach_or_release(self._red, REDString, executable_string_id, [arguments_list_id, environment_list_id, working_directory_string_id])
        self._arguments = _attach_or_release(self._red, REDList, arguments_list_id, [environment_list_id, working_directory_string_id])
        self._environment = _attach_or_release(self._red, REDList, environment_list_id, [working_directory_string_id])
        self._working_directory = _attach_or_release(self._red, REDString, working_directory_string_id)

    def update_identity(self):
        if self._object_id is None:
            raise RuntimeError('Cannot update unattached process object')

        error_code, pid, uid, gid = self._red.get_process_identity(self._object_id)

        if error_code != REDError.E_SUCCESS:
            raise REDError('Could not get identity of process object {0}'.format(self._object_id), error_code)

        self._pid = pid
        self._uid = uid
        self._gid = gid

    def update_stdio(self):
        if self._object_id is None:
            raise RuntimeError('Cannot update unattached process object')

        error_code, stdin_file_id, stdout_file_id, stderr_file_id = self._red.get_process_stdio(self._object_id)

        if error_code != REDError.E_SUCCESS:
            raise REDError('Could not get stdio of process object {0}'.format(self._object_id), error_code)

        self._stdin = _attach_or_release(self._red, REDFile, stdin_file_id, [stdout_file_id, stderr_file_id])
        self._stdout = _attach_or_release(self._red, REDFile, stdout_file_id, [stderr_file_id])
        self._stderr = _attach_or_release(self._red, REDFile, stderr_file_id)

    def update_state(self):
        if self._object_id is None:
            raise RuntimeError('Cannot update unattached process object')

        error_code, state, exit_code = self._red.get_process_state(self._object_id)

        if error_code != REDError.E_SUCCESS:
            raise REDError('Could not get state of process object {0}'.format(self._object_id), error_code)

        self._state = state
        self._exit_code = exit_code

    def spawn(self, executable, arguments, environment, working_directory,
              uid, gid, stdin, stdout, stderr):
        self.release()

        if not isinstance(executable, REDString):
            executable = REDString(self._red).allocate(executable)

        if not isinstance(arguments, REDList):
            arguments = REDList(self._red).allocate(arguments)

        if not isinstance(environment, REDList):
            environment = REDList(self._red).allocate(environment)

        if not isinstance(working_directory, REDString):
            working_directory = REDString(self._red).allocate(working_directory)

        error_code, object_id = self._red.spawn_process(executable.object_id,
                                                        arguments.object_id,
                                                        environment.object_id,
                                                        working_directory.object_id,
                                                        uid, gid,
                                                        stdin.object_id,
                                                        stdout.object_id,
                                                        stderr.object_id)

        if error_code != REDError.E_SUCCESS:
            raise REDError('Could not spawn process object', error_code)

        self._object_id = object_id
        self._executable = executable
        self._arguments = arguments
        self._environment = environment
        self._working_directory = working_directory
        self._uid = uid
        self._gid = gid
        self._stdin = stdin
        self._stdout = stdout
        self._stderr = stderr

        self.update_identity()
        self.update_state()

        return self

    def kill(self, signal):
        if self._object_id is None:
            raise RuntimeError('Cannot kill unattached process object')

        error_code = self._red.kill_process(self._object_id, signal)

        if error_code != REDError.E_SUCCESS:
            raise REDError('Could not kill process object {0}'.format(self._object_id), error_code)

    @property
    def executable(self):
        return self._executable

    @property
    def arguments(self):
        return self._arguments

    @property
    def environment(self):
        return self._environment

    @property
    def working_directory(self):
        return self._working_directory

    @property
    def pid(self):
        return self._pid

    @property
    def uid(self):
        return self._uid

    @property
    def gid(self):
        return self._gid

    @property
    def stdin(self):
        return self._stdin

    @property
    def stdout(self):
        return self._stdout

    @property
    def stderr(self):
        return self._stderr

    @property
    def state(self):
        return self._state

    @property
    def exit_code(self):
        return self._exit_code


def get_processes(red):
    error_code, processes_list_id = red.get_processes()

    if error_code != REDError.E_SUCCESS:
        raise REDError('Could not get processes list object', error_code)

    return _attach_or_release(red, REDList, processes_list_id)


REDObject._subclasses = {
    REDObject.TYPE_STRING:    REDString,
    REDObject.TYPE_LIST:      REDList,
    REDObject.TYPE_FILE:      REDFileOrPipeAttacher,
    REDObject.TYPE_DIRECTORY: REDDirectory,
    REDObject.TYPE_PROCESS:   REDProcess,
}
