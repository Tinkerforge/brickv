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

from brickv.bindings.brick_red import BrickRED

E_SUCCESS              = 0
E_UNKNOWN_ERROR        = 1
E_INVALID_OPERATION    = 2
E_OPERATION_ABORTED    = 3
E_INTERNAL_ERROR       = 4
E_UNKNOWN_OBJECT_ID    = 5
E_NO_FREE_OBJECT_ID    = 6
E_OBJECT_IN_USE        = 7
E_NO_MORE_DATA         = 8
E_WRONG_LIST_ITEM_TYPE = 9
E_INVALID_PARAMETER    = 128
E_NO_FREE_MEMORY       = 129
E_NO_FREE_SPACE        = 130
E_ACCESS_DENIED        = 131
E_ALREADY_EXISTS       = 132
E_DOES_NOT_EXIST       = 133
E_INTERRUPTED          = 134
E_IS_DIRECTORY         = 135
E_NOT_A_DIRECTORY      = 136
E_WOULD_BLOCK          = 137
E_OVERFLOW             = 138
E_BAD_FILE_DESCRIPTOR  = 139
E_OUT_OF_RANGE         = 140
E_NAME_TOO_LONG        = 141
E_INVALID_SEEK         = 142
E_NOT_SUPPORTED        = 143

error_code_names = {
    E_SUCCESS              : 'E_SUCCESS',
    E_UNKNOWN_ERROR        : 'E_UNKNOWN_ERROR',
    E_INVALID_OPERATION    : 'E_INVALID_OPERATION',
    E_OPERATION_ABORTED    : 'E_OPERATION_ABORTED',
    E_INTERNAL_ERROR       : 'E_INTERNAL_ERROR',
    E_UNKNOWN_OBJECT_ID    : 'E_UNKNOWN_OBJECT_ID',
    E_NO_FREE_OBJECT_ID    : 'E_NO_FREE_OBJECT_ID',
    E_OBJECT_IN_USE        : 'E_OBJECT_IN_USE',
    E_NO_MORE_DATA         : 'E_NO_MORE_DATA',
    E_WRONG_LIST_ITEM_TYPE : 'E_WRONG_LIST_ITEM_TYPE',
    E_INVALID_PARAMETER    : 'E_INVALID_PARAMETER',
    E_NO_FREE_MEMORY       : 'E_NO_FREE_MEMORY',
    E_NO_FREE_SPACE        : 'E_NO_FREE_SPACE',
    E_ACCESS_DENIED        : 'E_ACCESS_DENIED',
    E_ALREADY_EXISTS       : 'E_ALREADY_EXISTS',
    E_DOES_NOT_EXIST       : 'E_DOES_NOT_EXIST',
    E_INTERRUPTED          : 'E_INTERRUPTED',
    E_IS_DIRECTORY         : 'E_IS_DIRECTORY',
    E_NOT_A_DIRECTORY      : 'E_NOT_A_DIRECTORY',
    E_WOULD_BLOCK          : 'E_WOULD_BLOCK',
    E_OVERFLOW             : 'E_OVERFLOW',
    E_BAD_FILE_DESCRIPTOR  : 'E_BAD_FILE_DESCRIPTOR',
    E_OUT_OF_RANGE         : 'E_OUT_OF_RANGE',
    E_NAME_TOO_LONG        : 'E_NAME_TOO_LONG',
    E_INVALID_SEEK         : 'E_INVALID_SEEK',
    E_NOT_SUPPORTED        : 'E_NOT_SUPPORTED'
}

class REDError(Exception):
    def __init__(self, message, error_code):
        Exception.__init__(self, message)

        self.message = message
        self.error_code = error_code

    def __str__(self):
        return '{0}: {1} ({2})'.format(self.message,
                                       error_code_names[self.error_code],
                                       self.error_code)

class REDString:
    MAX_ALLOCATE_BUFFER_LENGTH  = 60
    MAX_SET_CHUNK_BUFFER_LENGTH = 58
    MAX_GET_CHUNK_BUFFER_LENGTH = 63

    def __init__(self, red, object_id=None, data=None):
        if object_id is not None and data is not None:
            raise ValueError('Cannot create string object with object ID and with data')
        elif object_id is None and data is None:
            raise ValueError('Cannot create string object without object ID and without data')

        self._red = red
        self._object_id = object_id
        self._data = data

        if self._object_id is not None:
            self._download_data()
        else:
            self._allocate_object()

    def __del__(self):
        if self._object_id is not None:
            self.release()

    def _download_data(self):
        error_code, length = self._red.get_string_length(self._object_id)

        if error_code != E_SUCCESS:
            raise REDError('Could not get length of string object', error_code)

        data = ''

        while len(data) < length:
            error_code, chunk = self._red.get_string_chunk(self._object_id, len(data))

            if error_code != E_SUCCESS:
                raise REDError('Could not download from string object', error_code)

            data += chunk

        self._data = data

    def _allocate_object(self):
        if self._object_id is not None:
            raise RuntimeError('Cannot allocate string object twice')

        error_code, object_id = self._red.allocate_string(len(self._data), '')

        if error_code != E_SUCCESS:
            raise REDError('Could not allocate string object', error_code)

        self._object_id = object_id
        remaining_data = self._data
        offset = 0

        while len(remaining_data) > 0:
            chunk = remaining_data[0:REDString.MAX_SET_CHUNK_BUFFER_LENGTH]
            remaining_data = remaining_data[REDString.MAX_SET_CHUNK_BUFFER_LENGTH:]
            error_code = self._red.set_string_chunk(self._object_id, offset, chunk)

            if error_code != E_SUCCESS:
                raise REDError('Could not upload to string object', error_code)

            offset += len(chunk)

    @property
    def object_id(self):
        return self._object_id

    @property
    def data(self):
        return self._data

    def release(self):
        if self._object_id is None:
            raise RuntimeError('Cannot release string object without an object ID')

        self._red.release_object(self._object_id) # FIXME: error handling

        self._red = None
        self._object_id = None
        self._data = None


class REDFile:
    MAX_READ_BUFFER_LENGTH            = 62
    MAX_ASYNC_READ_BUFFER_LENGTH      = 60
    MAX_WRITE_BUFFER_LENGTH           = 61
    MAX_WRITE_UNCHECKED_BUFFER_LENGTH = 61
    MAX_WRITE_ASYNC_BUFFER_LENGTH     = 61

    FLAG_READ_ONLY    = BrickRED.FILE_FLAG_READ_ONLY
    FLAG_WRITE_ONLY   = BrickRED.FILE_FLAG_WRITE_ONLY
    FLAG_READ_WRITE   = BrickRED.FILE_FLAG_READ_WRITE
    FLAG_APPEND       = BrickRED.FILE_FLAG_APPEND
    FLAG_CREATE       = BrickRED.FILE_FLAG_CREATE
    FLAG_EXCLUSIVE    = BrickRED.FILE_FLAG_EXCLUSIVE
    FLAG_NON_BLOCKING = BrickRED.FILE_FLAG_NON_BLOCKING
    FLAG_TRUNCATE     = BrickRED.FILE_FLAG_TRUNCATE
    FLAG_TEMPORARY    = BrickRED.FILE_FLAG_TEMPORARY

    def __init__(self, red, object_id=None, name=None, flags=None, permissions=None, user_id=None, group_id=None):
        if object_id is not None and (name is not None or flags is not None or permissions is not None or user_id is not None or group_id is not None):
            raise ValueError('Cannot create file object with object ID and with name, flags, permissions, user ID and group ID')
        elif object_id is None and (name is None or flags is None or permissions is None or user_id is None or group_id is None):
            raise ValueError('Cannot create file object without object ID and without name, flags, permissions, user ID and group ID')

        self._red = red
        self._object_id = object_id
        self._type = None
        self._name = name
        self._flags = flags
        self._permissions = permissions
        self._user_id = user_id
        self._group_id = group_id
        self._length = None
        self._access_time = None
        self._modification_time = None
        self._status_change_time = None

        if self._object_id is not None:
            self.update_info()
        else:
            self._open_file()

    def __del__(self):
        if self._object_id is not None:
            self.release()

    def _open_file(self):
        if self._object_id is not None:
            raise RuntimeError('Cannot open file object twice')

        error_code, object_id = self._red.open_file(self._name.object_id, self._flags, \
                                                    self._permissions, self._user_id, self._group_id)

        if error_code != E_SUCCESS:
            raise REDError('Could not open file object', error_code)

        self._object_id = object_id

        self.update_info()

    def update_info(self):
        error_code, type, name_string_id, flags, permissions, user_id, group_id, \
        length, access_time, modification_time, status_change_time = self._red.get_file_info(self._object_id)

        if error_code != E_SUCCESS:
            raise REDError('Could not get information for file object', error_code)

        self._type = type
        self._name = REDString(self._red, object_id=name_string_id)
        self._flags = flags
        self._permissions = permissions
        self._user_id = user_id
        self._group_id = group_id
        self._length = length
        self._access_time = access_time
        self._modification_time = modification_time
        self._status_change_time = status_change_time

    def write(self, data):
        remaining_data = [ord(x) for x in data]

        while len(remaining_data) > 0:
            chunk = remaining_data[0:REDFile.MAX_WRITE_BUFFER_LENGTH]
            length_to_write = len(chunk)
            chunk += [0]*(REDFile.MAX_WRITE_BUFFER_LENGTH - length_to_write)

            error_code, length_written = self._red.write_file(self._object_id, chunk, length_to_write)

            if error_code != E_SUCCESS:
                # FIXME: recover seek position on error after successful call?
                raise REDError('Could not write to file object', error_code)

            remaining_data = remaining_data[length_written:]

    def read(self, length):
        data = ''

        while length > 0:
            length_to_read = min(length, REDFile.MAX_READ_BUFFER_LENGTH)

            error_code, chunk, length_read = self._red.read_file(self._object_id, length_to_read)

            if error_code != E_SUCCESS:
                # FIXME: recover seek position on error after successful call?
                raise REDError('Could not read from file object', error_code)

            if length_read == 0:
                break

            data += ''.join([chr(x) for x in chunk[:length_read]])
            length -= length_read

        return data

    @property
    def object_id(self):
        return self._object_id

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
    def user_id(self):
        return self._user_id

    @property
    def group_id(self):
        return self._group_id

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

    def release(self):
        if self._object_id is None:
            raise RuntimeError('Cannot release file object without an object ID')

        self._red.release_object(self._object_id) # FIXME: error handling

        self._red = None
        self._object_id = None
        self._type = None
        self._name = None
        self._flags = None
        self._permissions = None
        self._user_id = None
        self._group_id = None
        self._length = None
        self._access_time = None
        self._modification_time = None
        self._status_change_time = None
