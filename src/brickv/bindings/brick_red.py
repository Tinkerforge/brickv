# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2014-08-11.      #
#                                                           #
# Bindings Version 2.1.2                                    #
#                                                           #
# If you have a bugfix for this file and want to commit it, #
# please fix the bug in the generator. You can find a link  #
# to the generator git on tinkerforge.com                   #
#############################################################

try:
    from collections import namedtuple
except ImportError:
    try:
        from .ip_connection import namedtuple
    except ValueError:
        from ip_connection import namedtuple

try:
    from .ip_connection import Device, IPConnection, Error
except ValueError:
    from ip_connection import Device, IPConnection, Error

GetNextObjectTableEntry = namedtuple('NextObjectTableEntry', ['error_code', 'object_id'])
AllocateString = namedtuple('AllocateString', ['error_code', 'string_id'])
GetStringLength = namedtuple('StringLength', ['error_code', 'length'])
GetStringChunk = namedtuple('StringChunk', ['error_code', 'buffer'])
AllocateList = namedtuple('AllocateList', ['error_code', 'list_id'])
GetListLength = namedtuple('ListLength', ['error_code', 'length'])
GetListItem = namedtuple('ListItem', ['error_code', 'item_object_id'])
OpenFile = namedtuple('OpenFile', ['error_code', 'file_id'])
GetFileName = namedtuple('FileName', ['error_code', 'name_string_id'])
GetFileType = namedtuple('FileType', ['error_code', 'type'])
WriteFile = namedtuple('WriteFile', ['error_code', 'length_written'])
ReadFile = namedtuple('ReadFile', ['error_code', 'buffer', 'length_read'])
SetFilePosition = namedtuple('SetFilePosition', ['error_code', 'position'])
GetFilePosition = namedtuple('FilePosition', ['error_code', 'position'])
GetFileInfo = namedtuple('FileInfo', ['error_code', 'type', 'permissions', 'user_id', 'group_id', 'length', 'access_time', 'modification_time', 'status_change_time'])
GetSymlinkTarget = namedtuple('SymlinkTarget', ['error_code', 'target_string_id'])
OpenDirectory = namedtuple('OpenDirectory', ['error_code', 'directory_id'])
GetDirectoryName = namedtuple('DirectoryName', ['error_code', 'name_string_id'])
GetNextDirectoryEntry = namedtuple('NextDirectoryEntry', ['error_code', 'name_string_id', 'type'])
StartProcess = namedtuple('StartProcess', ['error_code', 'process_id'])
GetIdentity = namedtuple('Identity', ['uid', 'connected_uid', 'position', 'hardware_version', 'firmware_version', 'device_identifier'])

class BrickRED(Device):
    """
    Device for running user programs standalone on the stack
    """

    DEVICE_IDENTIFIER = 17

    CALLBACK_ASYNC_FILE_WRITE = 25
    CALLBACK_ASYNC_FILE_READ = 26

    FUNCTION_RELEASE_OBJECT = 1
    FUNCTION_GET_NEXT_OBJECT_TABLE_ENTRY = 2
    FUNCTION_REWIND_OBJECT_TABLE = 3
    FUNCTION_ALLOCATE_STRING = 4
    FUNCTION_TRUNCATE_STRING = 5
    FUNCTION_GET_STRING_LENGTH = 6
    FUNCTION_SET_STRING_CHUNK = 7
    FUNCTION_GET_STRING_CHUNK = 8
    FUNCTION_ALLOCATE_LIST = 9
    FUNCTION_GET_LIST_LENGTH = 10
    FUNCTION_GET_LIST_ITEM = 11
    FUNCTION_APPEND_TO_LIST = 12
    FUNCTION_REMOVE_FROM_LIST = 13
    FUNCTION_OPEN_FILE = 14
    FUNCTION_GET_FILE_NAME = 15
    FUNCTION_GET_FILE_TYPE = 16
    FUNCTION_WRITE_FILE = 17
    FUNCTION_WRITE_FILE_UNCHECKED = 18
    FUNCTION_WRITE_FILE_ASYNC = 19
    FUNCTION_READ_FILE = 20
    FUNCTION_READ_FILE_ASYNC = 21
    FUNCTION_ABORT_ASYNC_FILE_READ = 22
    FUNCTION_SET_FILE_POSITION = 23
    FUNCTION_GET_FILE_POSITION = 24
    FUNCTION_GET_FILE_INFO = 27
    FUNCTION_GET_SYMLINK_TARGET = 28
    FUNCTION_OPEN_DIRECTORY = 29
    FUNCTION_GET_DIRECTORY_NAME = 30
    FUNCTION_GET_NEXT_DIRECTORY_ENTRY = 31
    FUNCTION_REWIND_DIRECTORY = 32
    FUNCTION_START_PROCESS = 33
    FUNCTION_GET_IDENTITY = 255

    OBJECT_TYPE_STRING = 0
    OBJECT_TYPE_LIST = 1
    OBJECT_TYPE_FILE = 2
    OBJECT_TYPE_DIRECTORY = 3
    OBJECT_TYPE_PROCESS = 4
    OBJECT_TYPE_PROGRAM = 5
    FILE_FLAG_READ_ONLY = 1
    FILE_FLAG_WRITE_ONLY = 2
    FILE_FLAG_READ_WRITE = 4
    FILE_FLAG_APPEND = 8
    FILE_FLAG_CREATE = 16
    FILE_FLAG_EXCLUSIVE = 32
    FILE_FLAG_TRUNCATE = 64
    FILE_PERMISSION_USER_ALL = 448
    FILE_PERMISSION_USER_READ = 256
    FILE_PERMISSION_USER_WRITE = 128
    FILE_PERMISSION_USER_EXECUTE = 64
    FILE_PERMISSION_GROUP_ALL = 56
    FILE_PERMISSION_GROUP_READ = 32
    FILE_PERMISSION_GROUP_WRITE = 16
    FILE_PERMISSION_GROUP_EXECUTE = 8
    FILE_PERMISSION_OTHERS_ALL = 7
    FILE_PERMISSION_OTHERS_READ = 4
    FILE_PERMISSION_OTHERS_WRITE = 2
    FILE_PERMISSION_OTHERS_EXECUTE = 1
    FILE_TYPE_UNKNOWN = 0
    FILE_TYPE_REGULAR = 1
    FILE_TYPE_DIRECTORY = 2
    FILE_TYPE_CHARACTER = 3
    FILE_TYPE_BLOCK = 4
    FILE_TYPE_FIFO = 5
    FILE_TYPE_SYMLINK = 6
    FILE_TYPE_SOCKET = 7
    FILE_ORIGIN_SET = 0
    FILE_ORIGIN_CURRENT = 1
    FILE_ORIGIN_END = 2

    def __init__(self, uid, ipcon):
        """
        Creates an object with the unique device ID *uid* and adds it to
        the IP Connection *ipcon*.
        """
        Device.__init__(self, uid, ipcon)

        self.api_version = (2, 0, 0)

        self.response_expected[BrickRED.FUNCTION_RELEASE_OBJECT] = BrickRED.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickRED.FUNCTION_GET_NEXT_OBJECT_TABLE_ENTRY] = BrickRED.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickRED.FUNCTION_REWIND_OBJECT_TABLE] = BrickRED.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickRED.FUNCTION_ALLOCATE_STRING] = BrickRED.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickRED.FUNCTION_TRUNCATE_STRING] = BrickRED.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickRED.FUNCTION_GET_STRING_LENGTH] = BrickRED.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickRED.FUNCTION_SET_STRING_CHUNK] = BrickRED.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickRED.FUNCTION_GET_STRING_CHUNK] = BrickRED.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickRED.FUNCTION_ALLOCATE_LIST] = BrickRED.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickRED.FUNCTION_GET_LIST_LENGTH] = BrickRED.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickRED.FUNCTION_GET_LIST_ITEM] = BrickRED.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickRED.FUNCTION_APPEND_TO_LIST] = BrickRED.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickRED.FUNCTION_REMOVE_FROM_LIST] = BrickRED.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickRED.FUNCTION_OPEN_FILE] = BrickRED.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickRED.FUNCTION_GET_FILE_NAME] = BrickRED.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickRED.FUNCTION_GET_FILE_TYPE] = BrickRED.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickRED.FUNCTION_WRITE_FILE] = BrickRED.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickRED.FUNCTION_WRITE_FILE_UNCHECKED] = BrickRED.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickRED.FUNCTION_WRITE_FILE_ASYNC] = BrickRED.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickRED.FUNCTION_READ_FILE] = BrickRED.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickRED.FUNCTION_READ_FILE_ASYNC] = BrickRED.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickRED.FUNCTION_ABORT_ASYNC_FILE_READ] = BrickRED.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickRED.FUNCTION_SET_FILE_POSITION] = BrickRED.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickRED.FUNCTION_GET_FILE_POSITION] = BrickRED.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickRED.CALLBACK_ASYNC_FILE_WRITE] = BrickRED.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickRED.CALLBACK_ASYNC_FILE_READ] = BrickRED.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickRED.FUNCTION_GET_FILE_INFO] = BrickRED.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickRED.FUNCTION_GET_SYMLINK_TARGET] = BrickRED.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickRED.FUNCTION_OPEN_DIRECTORY] = BrickRED.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickRED.FUNCTION_GET_DIRECTORY_NAME] = BrickRED.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickRED.FUNCTION_GET_NEXT_DIRECTORY_ENTRY] = BrickRED.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickRED.FUNCTION_REWIND_DIRECTORY] = BrickRED.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickRED.FUNCTION_START_PROCESS] = BrickRED.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickRED.FUNCTION_GET_IDENTITY] = BrickRED.RESPONSE_EXPECTED_ALWAYS_TRUE

        self.callback_formats[BrickRED.CALLBACK_ASYNC_FILE_WRITE] = 'H B B'
        self.callback_formats[BrickRED.CALLBACK_ASYNC_FILE_READ] = 'H B 60B B'

    def release_object(self, object_id):
        """
        Decreases the reference count of an object by one and returns the resulting
        error code. If the reference count reaches zero the object is destroyed.
        """
        return self.ipcon.send_request(self, BrickRED.FUNCTION_RELEASE_OBJECT, (object_id,), 'H', 'B')

    def get_next_object_table_entry(self, type):
        """
        Returns the object ID of the next ``type`` object in the object table and the
        resulting error code. If there is not next ``type`` object then error code
        ``API_E_NO_MORE_DATA`` is returned. To rewind the table call
        :func:`RewindObjectTable`.
        """
        return GetNextObjectTableEntry(*self.ipcon.send_request(self, BrickRED.FUNCTION_GET_NEXT_OBJECT_TABLE_ENTRY, (type,), 'B', 'B H'))

    def rewind_object_table(self, type):
        """
        Rewinds the object table for ``type`` and returns the resulting error code.
        """
        return self.ipcon.send_request(self, BrickRED.FUNCTION_REWIND_OBJECT_TABLE, (type,), 'B', 'B')

    def allocate_string(self, length_to_reserve):
        """
        Allocates a new string object and reserves ``length_to_reserve`` bytes memory
        for it. Set ``length_to_reserve`` to the length of the string that should be
        stored in the string object.
        
        Returns the object ID of the new string object and the resulting error code.
        """
        return AllocateString(*self.ipcon.send_request(self, BrickRED.FUNCTION_ALLOCATE_STRING, (length_to_reserve,), 'I', 'B H'))

    def truncate_string(self, string_id, length):
        """
        Truncates a string object to ``length`` bytes and returns the resulting
        error code.
        """
        return self.ipcon.send_request(self, BrickRED.FUNCTION_TRUNCATE_STRING, (string_id, length), 'H I', 'B')

    def get_string_length(self, string_id):
        """
        Returns the length of a string object in bytes and the resulting error code.
        """
        return GetStringLength(*self.ipcon.send_request(self, BrickRED.FUNCTION_GET_STRING_LENGTH, (string_id,), 'H', 'B I'))

    def set_string_chunk(self, string_id, offset, buffer):
        """
        Sets a chunk of up to 58 bytes in a string object beginning at ``offset``.
        
        Returns the resulting error code.
        """
        return self.ipcon.send_request(self, BrickRED.FUNCTION_SET_STRING_CHUNK, (string_id, offset, buffer), 'H I 58s', 'B')

    def get_string_chunk(self, string_id, offset):
        """
        Returns a chunk up to 63 bytes from a string object beginning at ``offset`` and
        returns the resulting error code.
        """
        return GetStringChunk(*self.ipcon.send_request(self, BrickRED.FUNCTION_GET_STRING_CHUNK, (string_id, offset), 'H I', 'B 63s'))

    def allocate_list(self, length_to_reserve):
        """
        Allocates a new list object and reserves memory for ``length_to_reserve`` items.
        Set ``length_to_reserve`` to the number of items that should be stored in the
        list object.
        
        Returns the object ID of the new list object and the resulting error code.
        """
        return AllocateList(*self.ipcon.send_request(self, BrickRED.FUNCTION_ALLOCATE_LIST, (length_to_reserve,), 'H', 'B H'))

    def get_list_length(self, list_id):
        """
        Returns the length of a list object in items and the resulting error code.
        """
        return GetListLength(*self.ipcon.send_request(self, BrickRED.FUNCTION_GET_LIST_LENGTH, (list_id,), 'H', 'B H'))

    def get_list_item(self, list_id, index):
        """
        Returns the object ID of the object stored at ``index`` in a list object and
        returns the resulting error code.
        """
        return GetListItem(*self.ipcon.send_request(self, BrickRED.FUNCTION_GET_LIST_ITEM, (list_id, index), 'H H', 'B H'))

    def append_to_list(self, list_id, item_object_id):
        """
        Appends an object to a list object and increases the reference count of the
        appended object by one.
        
        Returns the resulting error code.
        """
        return self.ipcon.send_request(self, BrickRED.FUNCTION_APPEND_TO_LIST, (list_id, item_object_id), 'H H', 'B')

    def remove_from_list(self, list_id, index):
        """
        Removes the object stored at ``index`` from a list object and decreases the
        reference count of the removed object by one.
        
        Returns the resulting error code.
        """
        return self.ipcon.send_request(self, BrickRED.FUNCTION_REMOVE_FROM_LIST, (list_id, index), 'H H', 'B')

    def open_file(self, name_string_id, flags, permissions, user_id, group_id):
        """
        Opens an existing file or creates a new file and creates a file object for it.
        
        The reference count of the name string object is increased by one. When the
        file object is destroyed then the reference count of the name string object is
        decreased by one. Also the name string object is locked and cannot be modified
        while the file object holds a reference to it.
        
        Returns the object ID of the new file object and the resulting error code.
        """
        return OpenFile(*self.ipcon.send_request(self, BrickRED.FUNCTION_OPEN_FILE, (name_string_id, flags, permissions, user_id, group_id), 'H H H I I', 'B H'))

    def get_file_name(self, file_id):
        """
        Returns the name of a file object and the resulting error code.
        """
        return GetFileName(*self.ipcon.send_request(self, BrickRED.FUNCTION_GET_FILE_NAME, (file_id,), 'H', 'B H'))

    def get_file_type(self, file_id):
        """
        Returns the type of a file object and the resulting error code.
        """
        return GetFileType(*self.ipcon.send_request(self, BrickRED.FUNCTION_GET_FILE_TYPE, (file_id,), 'H', 'B B'))

    def write_file(self, file_id, buffer, length_to_write):
        """
        Writes up to 61 bytes to a file object.
        
        Returns the actual number of bytes written and the resulting error code.
        """
        return WriteFile(*self.ipcon.send_request(self, BrickRED.FUNCTION_WRITE_FILE, (file_id, buffer, length_to_write), 'H 61B B', 'B B'))

    def write_file_unchecked(self, file_id, buffer, length_to_write):
        """
        Writes up to 61 bytes to a file object.
        
        Does neither report the actual number of bytes written nor the resulting error
        code.
        """
        self.ipcon.send_request(self, BrickRED.FUNCTION_WRITE_FILE_UNCHECKED, (file_id, buffer, length_to_write), 'H 61B B', '')

    def write_file_async(self, file_id, buffer, length_to_write):
        """
        Writes up to 61 bytes to a file object.
        
        Reports the actual number of bytes written and the resulting error code via the
        :func:`AsyncFileWrite` callback.
        """
        self.ipcon.send_request(self, BrickRED.FUNCTION_WRITE_FILE_ASYNC, (file_id, buffer, length_to_write), 'H 61B B', '')

    def read_file(self, file_id, length_to_read):
        """
        Reads up to 62 bytes from a file object.
        
        Returns the read bytes and the resulting error code.
        """
        return ReadFile(*self.ipcon.send_request(self, BrickRED.FUNCTION_READ_FILE, (file_id, length_to_read), 'H B', 'B 62B B'))

    def read_file_async(self, file_id, length_to_read):
        """
        Reads up to 2\ :sup:`63`\  - 1 bytes from a file object.
        
        Returns the resulting error code.
        
        Reports the read bytes in 60 byte chunks and the resulting error code of the
        read operation via the :func:`AsyncFileRead` callback.
        """
        return self.ipcon.send_request(self, BrickRED.FUNCTION_READ_FILE_ASYNC, (file_id, length_to_read), 'H Q', 'B')

    def abort_async_file_read(self, file_id):
        """
        Aborts a :func:`ReadFileAsync` operation in progress.
        
        Returns the resulting error code.
        """
        return self.ipcon.send_request(self, BrickRED.FUNCTION_ABORT_ASYNC_FILE_READ, (file_id,), 'H', 'B')

    def set_file_position(self, file_id, offset, origin):
        """
        Set the current seek position of a file object in bytes.
        
        Returns the resulting seek position and error code.
        """
        return SetFilePosition(*self.ipcon.send_request(self, BrickRED.FUNCTION_SET_FILE_POSITION, (file_id, offset, origin), 'H q B', 'B Q'))

    def get_file_position(self, file_id):
        """
        Returns the current seek position of a file object in bytes and returns the
        resulting error code.
        """
        return GetFilePosition(*self.ipcon.send_request(self, BrickRED.FUNCTION_GET_FILE_POSITION, (file_id,), 'H', 'B Q'))

    def get_file_info(self, name_string_id, follow_symlink):
        """
        Returns various information about a file and the resulting error code.
        
        The information is obtained via the
        `stat() <http://pubs.opengroup.org/onlinepubs/9699919799/functions/stat.html>`__
        function. If ``follow_symlink`` is *false* then the
        `lstat() <http://pubs.opengroup.org/onlinepubs/9699919799/functions/stat.html>`__
        function is used instead.
        """
        return GetFileInfo(*self.ipcon.send_request(self, BrickRED.FUNCTION_GET_FILE_INFO, (name_string_id, follow_symlink), 'H ?', 'B B H I I Q Q Q Q'))

    def get_symlink_target(self, name_string_id, canonicalize):
        """
        Returns the target of a symlink and the resulting error code.
        
        If ``canonicalize`` is *false* then the target of the symlink is resolved one
        level via the
        `readlink() <http://pubs.opengroup.org/onlinepubs/9699919799/functions/readlink.html>`__
        function, otherwise it is fully resolved using the
        `realpath() <http://pubs.opengroup.org/onlinepubs/9699919799/functions/realpath.html>`__
        function.
        """
        return GetSymlinkTarget(*self.ipcon.send_request(self, BrickRED.FUNCTION_GET_SYMLINK_TARGET, (name_string_id, canonicalize), 'H ?', 'B H'))

    def open_directory(self, name_string_id):
        """
        Opens an existing directory and creates a directory object for it.
        
        The reference count of the name string object is increased by one. When the
        directory object is destroyed then the reference count of the name string
        object is decreased by one. Also the name string object is locked and cannot be
        modified while the directory object holds a reference to it.
        
        Returns the object ID of the new directory object and the resulting error code.
        """
        return OpenDirectory(*self.ipcon.send_request(self, BrickRED.FUNCTION_OPEN_DIRECTORY, (name_string_id,), 'H', 'B H'))

    def get_directory_name(self, directory_id):
        """
        Returns the name of a directory object and the resulting error code.
        """
        return GetDirectoryName(*self.ipcon.send_request(self, BrickRED.FUNCTION_GET_DIRECTORY_NAME, (directory_id,), 'H', 'B H'))

    def get_next_directory_entry(self, directory_id):
        """
        Returns the next entry in the directory object and the resulting error code.
        If there is not next entry then error code ``API_E_NO_MORE_DATA`` is returned.
        To rewind the directory object call :func:`RewindDirectory`.
        """
        return GetNextDirectoryEntry(*self.ipcon.send_request(self, BrickRED.FUNCTION_GET_NEXT_DIRECTORY_ENTRY, (directory_id,), 'H', 'B H B'))

    def rewind_directory(self, directory_id):
        """
        Rewinds the directory object and returns the resulting error code.
        """
        return self.ipcon.send_request(self, BrickRED.FUNCTION_REWIND_DIRECTORY, (directory_id,), 'H', 'B')

    def start_process(self, command_string_id, arguments_list_id, environment_list_id, working_directory_string_id, user_id, group_id, stdin_file_id, stdout_file_id, stderr_file_id):
        """
        
        """
        return StartProcess(*self.ipcon.send_request(self, BrickRED.FUNCTION_START_PROCESS, (command_string_id, arguments_list_id, environment_list_id, working_directory_string_id, user_id, group_id, stdin_file_id, stdout_file_id, stderr_file_id), 'H H H H I I H H H', 'B H'))

    def get_identity(self):
        """
        Returns the UID, the UID where the Brick is connected to, 
        the position, the hardware and firmware version as well as the
        device identifier.
        
        The position can be '0'-'8' (stack position).
        
        The device identifier numbers can be found :ref:`here <device_identifier>`.
        |device_identifier_constant|
        """
        return GetIdentity(*self.ipcon.send_request(self, BrickRED.FUNCTION_GET_IDENTITY, (), '', '8s 8s c 3B 3B H'))

    def register_callback(self, id, callback):
        """
        Registers a callback with ID *id* to the function *callback*.
        """
        self.registered_callbacks[id] = callback

RED = BrickRED # for backward compatibility
