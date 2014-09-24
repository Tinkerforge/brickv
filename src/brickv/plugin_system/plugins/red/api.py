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

from PyQt4.QtCore import QObject, pyqtSignal
from brickv.bindings.brick_red import BrickRED

E_SUCCESS                  = 0
E_UNKNOWN_ERROR            = 1
E_INVALID_OPERATION        = 2
E_OPERATION_ABORTED        = 3
E_INTERNAL_ERROR           = 4
E_UNKNOWN_OBJECT_ID        = 5
E_NO_FREE_OBJECT_ID        = 6
E_OBJECT_IN_USE            = 7
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

error_code_names = {
    E_SUCCESS                  : 'E_SUCCESS',
    E_UNKNOWN_ERROR            : 'E_UNKNOWN_ERROR',
    E_INVALID_OPERATION        : 'E_INVALID_OPERATION',
    E_OPERATION_ABORTED        : 'E_OPERATION_ABORTED',
    E_INTERNAL_ERROR           : 'E_INTERNAL_ERROR',
    E_UNKNOWN_OBJECT_ID        : 'E_UNKNOWN_OBJECT_ID',
    E_NO_FREE_OBJECT_ID        : 'E_NO_FREE_OBJECT_ID',
    E_OBJECT_IN_USE            : 'E_OBJECT_IN_USE',
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


class REDError(Exception):
    def __init__(self, message, error_code):
        Exception.__init__(self, message)

        self.message = message
        self.error_code = error_code

    def __str__(self):
        return '{0}: {1} ({2})'.format(self.message,
                                       error_code_names[self.error_code],
                                       self.error_code)


def attach_or_release(red, object_class, object_id, extra_object_ids_to_release_on_error=[]):
    try:
        obj = object_class(red).attach(object_id)
    except Exception as e:
        try:
            red.release_object(object_id) # FIXME: error handling
        except:
            pass

        for extra_object_id in extra_object_ids_to_release_on_error:
            try:
                red.release_object(extra_object_id) # FIXME: error handling
            except:
                pass

        raise e

    return obj


class REDObject(QObject):
    def __init__(self, red):
        QObject.__init__(self)

        self._red = red
        self._object_id = None

        self._initialize()

    def __del__(self):
        self.release()

    def _initialize(self):
        raise NotImplementedError()

    def release(self):
        if self._object_id is None:
            return

        object_id = self._object_id
        self._object_id = None

        self._initialize()

        try:
            self._red.release_object(object_id) # FIXME: error handling
        except:
            pass

    @property
    def object_id(self):
        return self._object_id


class REDString(REDObject):
    MAX_ALLOCATE_BUFFER_LENGTH  = 60
    MAX_SET_CHUNK_BUFFER_LENGTH = 58
    MAX_GET_CHUNK_BUFFER_LENGTH = 63

    def _initialize(self):
        self._data = None

    def update(self):
        if self._object_id is None:
            raise RuntimeError('Cannot update unattached string object')

        error_code, length = self._red.get_string_length(self._object_id)

        if error_code != E_SUCCESS:
            raise REDError('Could not get length of string object {0}'.format(self._object_id), error_code)

        data = ''

        while len(data) < length:
            error_code, chunk = self._red.get_string_chunk(self._object_id, len(data))

            if error_code != E_SUCCESS:
                raise REDError('Could not get chunk of string object {0}'.format(self._object_id), error_code)

            data += chunk

        self._data = data

    def attach(self, object_id):
        self.release()

        self._object_id = object_id

        self.update()

        return self

    def allocate(self, data):
        self.release()

        error_code, object_id = self._red.allocate_string(len(data), '') # FIXME: don't waste first buffer

        if error_code != E_SUCCESS:
            raise REDError('Could not allocate string object', error_code)

        self._object_id = object_id

        remaining_data = data
        offset = 0

        while len(remaining_data) > 0:
            chunk = remaining_data[0:REDString.MAX_SET_CHUNK_BUFFER_LENGTH]
            remaining_data = remaining_data[REDString.MAX_SET_CHUNK_BUFFER_LENGTH:]
            error_code = self._red.set_string_chunk(self._object_id, offset, chunk)

            if error_code != E_SUCCESS:
                raise REDError('Could not set chunk of string object {0}'.format(self._object_id), error_code)

            offset += len(chunk)

        self._data = data

        return self

    @property
    def data(self):
        return self._data


class REDStringList(REDObject):
    def _initialize(self):
        self._items = None

    def update(self):
        if self._object_id is None:
            raise RuntimeError('Cannot update unattached list object')

        error_code, length = self._red.get_list_length(self._object_id)

        if error_code != E_SUCCESS:
            raise REDError('Could not get length of list object {0}'.format(self._object_id), error_code)

        items = []

        for i in range(length):
            error_code, item_id = self._red.get_list_item(self._object_id, i)

            if error_code != E_SUCCESS:
                raise REDError('Could not get item at index {0} of list object {0}'.format(i, self._object_id), error_code)

            items.append(attach_or_release(self._red, REDString, item_id))

        self._items = items

    def attach(self, object_id):
        self.release()

        self._object_id = object_id

        self.update()

        return self

    def allocate(self, items):
        self.release()

        error_code, object_id = self._red.allocate_list(len(items))

        if error_code != E_SUCCESS:
            raise REDError('Could not allocate list object', error_code)

        self._object_id = object_id

        for item in items:
            if not isinstance(item, REDString):
                item = REDString(self._red).allocate(item)

            error_code = self._red.append_to_list(self._object_id, item.object_id)

            if error_code != E_SUCCESS:
                raise REDError('Could not append item {0} to list object {0}'.format(item.object_id, self._object_id), error_code)

        self._items = items

        return self

    @property
    def items(self):
        return self._items


class REDFile(REDObject):
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

    def _initialize(self):
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

    def update(self):
        if self._object_id is None:
            raise RuntimeError('Cannot update unattached file object')

        error_code, type, name_string_id, flags, permissions, user_id, group_id, \
        length, access_time, modification_time, status_change_time = self._red.get_file_info(self._object_id)

        if error_code != E_SUCCESS:
            raise REDError('Could not get information for file object {0}'.format(self._object_id), error_code)

        self._type = type
        self._name = attach_or_release(self._red, REDString, name_string_id)
        self._flags = flags
        self._permissions = permissions
        self._user_id = user_id
        self._group_id = group_id
        self._length = length
        self._access_time = access_time
        self._modification_time = modification_time
        self._status_change_time = status_change_time

    def attach(self, object_id):
        self.release()

        self._object_id = object_id

        self.update()

        return self

    def open(self, name, flags, permissions, user_id, group_id):
        self.release()

        if not isinstance(name, REDString):
            name = REDString(self._red).allocate(name)

        error_code, object_id = self._red.open_file(name.object_id, flags, permissions, user_id, group_id)

        if error_code != E_SUCCESS:
            raise REDError('Could not open file object', error_code)

        self._object_id = object_id

        self.update()

        return self

    def write(self, data):
        if self._object_id is None:
            raise RuntimeError('Cannot write to unattached file object')

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
        if self._object_id is None:
            raise RuntimeError('Cannot read from unattached file object')

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
    STATE_EXITED  = BrickRED.PROCESS_STATE_EXITED
    STATE_KILLED  = BrickRED.PROCESS_STATE_KILLED
    STATE_STOPPED = BrickRED.PROCESS_STATE_STOPPED

    _qtcb_state_changed = pyqtSignal(int, int, int)

    def __init__(self, *args):
        REDObject.__init__(self, *args)

        self._qtcb_state_changed.connect(self._cb_state_changed)
        self._red.register_callback(BrickRED.CALLBACK_PROCESS_STATE_CHANGED,
                                    self._qtcb_state_changed.emit)

    def _initialize(self):
        self._executable = None
        self._arguments = None
        self._environment = None
        self._working_directory = None
        self._user_id = None
        self._group_id = None
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

        state_changed_callback = self.state_changed_callback

        if state_changed_callback is not None:
            state_changed_callback(self)

    def update(self):
        if self._object_id is None:
            raise RuntimeError('Cannot update unattached process object')

        # command
        error_code, executable_string_id, arguments_list_id, \
        environment_list_id, working_directory_string_id = self._red.get_process_command(self._object_id)

        if error_code != E_SUCCESS:
            raise REDError('Could not get command of process object {0}'.format(self._object_id), error_code)

        self._executable = attach_or_release(self._red, REDString, executable_string_id, [arguments_list_id, environment_list_id, working_directory_string_id])
        self._arguments = attach_or_release(self._red, REDStringList, arguments_list_id, [environment_list_id, working_directory_string_id])
        self._environment = attach_or_release(self._red, REDStringList, environment_list_id, [working_directory_string_id])
        self._working_directory = attach_or_release(self._red, REDString, working_directory_string_id)

        # identity
        error_code, user_id, group_id = self._red.get_process_identity(self._object_id)

        if error_code != E_SUCCESS:
            raise REDError('Could not get identity of process object {0}'.format(self._object_id), error_code)

        self._user_id = user_id
        self._group_id = group_id

        # stdio
        error_code, stdin_file_id, stdout_file_id, stderr_file_id = self._red.get_process_stdio(self._object_id)

        if error_code != E_SUCCESS:
            raise REDError('Could not get stdio of process object {0}'.format(self._object_id), error_code)

        self._stdin = attach_or_release(self._red, REDFile, stdin_file_id, [stdout_file_id, stderr_file_id])
        self._stdout = attach_or_release(self._red, REDFile, stdout_file_id, [stderr_file_id])
        self._stderr = attach_or_release(self._red, REDFile, stderr_file_id)

        # state
        error_code, state, exit_code = self._red.get_process_state(self._object_id)

        if error_code != E_SUCCESS:
            raise REDError('Could not get state of process object {0}'.format(self._object_id), error_code)

        self._state = state
        self._exit_code = exit_code

    def attach(self, object_id):
        self.release()

        self._object_id = object_id

        self.update()

        return self

    def spawn(self, executable, arguments, environment, working_directory,
              user_id, group_id, stdin_file, stdout_file, stderr_file):
        self.release()

        if not isinstance(executable, REDString):
            executable = REDString(self._red).allocate(executable)

        if not isinstance(arguments, REDStringList):
            arguments = REDStringList(self._red).allocate(arguments)

        if not isinstance(environment, REDStringList):
            environment = REDStringList(self._red).allocate(environment)

        if not isinstance(working_directory, REDString):
            working_directory = REDString(self._red).allocate(working_directory)

        error_code, object_id = self._red.spawn_process(executable.object_id,
                                                        arguments.object_id,
                                                        environment.object_id,
                                                        working_directory.object_id,
                                                        user_id,
                                                        group_id,
                                                        stdin_file.object_id,
                                                        stdout_file.object_id,
                                                        stderr_file.object_id)

        if error_code != E_SUCCESS:
            raise REDError('Could not spawn process object', error_code)

        self._object_id = object_id

        self.update()

        return self

    def kill(self, signal):
        if self._object_id is None:
            raise RuntimeError('Cannot kill unattached process object')

        error_code = self._red.kill_process(self._object_id, signal)

        if error_code != E_SUCCESS:
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
    def user_id(self):
        return self._user_id

    @property
    def group_id(self):
        return self._group_id

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
