# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2014-07-02.      #
#                                                           #
# Bindings Version 2.1.0                                    #
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
OpenFile = namedtuple('OpenFile', ['error_code', 'file_id'])
GetFileName = namedtuple('FileName', ['error_code', 'name_string_id'])
WriteFile = namedtuple('WriteFile', ['error_code', 'length_written'])
ReadFile = namedtuple('ReadFile', ['error_code', 'buffer', 'length_read'])
SetFilePosition = namedtuple('SetFilePosition', ['error_code', 'position'])
GetFilePosition = namedtuple('FilePosition', ['error_code', 'position'])
GetFileInfo = namedtuple('FileInfo', ['error_code', 'type', 'permissions', 'user_id', 'group_id', 'length', 'access_time', 'modification_time', 'status_change_time'])
OpenDirectory = namedtuple('OpenDirectory', ['error_code', 'directory_id'])
GetDirectoryName = namedtuple('DirectoryName', ['error_code', 'name_string_id'])
GetNextDirectoryEntry = namedtuple('NextDirectoryEntry', ['error_code', 'name_string_id'])
GetIdentity = namedtuple('Identity', ['uid', 'connected_uid', 'position', 'hardware_version', 'firmware_version', 'device_identifier'])

class BrickRED(Device):
    """
    Device for running user programs standalone on the stack
    """

    DEVICE_IDENTIFIER = 17

    CALLBACK_ASYNC_FILE_WRITE = 19
    CALLBACK_ASYNC_FILE_READ = 20

    FUNCTION_RELEASE_OBJECT = 1
    FUNCTION_GET_NEXT_OBJECT_TABLE_ENTRY = 2
    FUNCTION_REWIND_OBJECT_TABLE = 3
    FUNCTION_ALLOCATE_STRING = 4
    FUNCTION_TRUNCATE_STRING = 5
    FUNCTION_GET_STRING_LENGTH = 6
    FUNCTION_SET_STRING_CHUNK = 7
    FUNCTION_GET_STRING_CHUNK = 8
    FUNCTION_OPEN_FILE = 9
    FUNCTION_GET_FILE_NAME = 10
    FUNCTION_WRITE_FILE = 11
    FUNCTION_WRITE_FILE_UNCHECKED = 12
    FUNCTION_WRITE_FILE_ASYNC = 13
    FUNCTION_READ_FILE = 14
    FUNCTION_READ_FILE_ASYNC = 15
    FUNCTION_ABORT_ASYNC_FILE_READ = 16
    FUNCTION_SET_FILE_POSITION = 17
    FUNCTION_GET_FILE_POSITION = 18
    FUNCTION_GET_FILE_INFO = 21
    FUNCTION_OPEN_DIRECTORY = 22
    FUNCTION_GET_DIRECTORY_NAME = 23
    FUNCTION_GET_NEXT_DIRECTORY_ENTRY = 24
    FUNCTION_REWIND_DIRECTORY = 25
    FUNCTION_GET_IDENTITY = 255

    FILE_FLAG_READ_ONLY = 1
    FILE_FLAG_WRITE_ONLY = 2
    FILE_FLAG_READ_WRITE = 4
    FILE_FLAG_APPEND = 8
    FILE_FLAG_CREATE = 16
    FILE_FLAG_TRUNCATE = 32
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
    FILE_ORIGIN_SET = 0
    FILE_ORIGIN_CURRENT = 1
    FILE_ORIGIN_END = 2
    FILE_TYPE_UNKNOWN = 0
    FILE_TYPE_REGULAR = 1
    FILE_TYPE_DIRECTORY = 2
    FILE_TYPE_CHARACTER = 3
    FILE_TYPE_BLOCK = 4
    FILE_TYPE_FIFO = 5
    FILE_TYPE_SYMLINK = 6
    FILE_TYPE_SOCKET = 7

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
        self.response_expected[BrickRED.FUNCTION_OPEN_FILE] = BrickRED.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickRED.FUNCTION_GET_FILE_NAME] = BrickRED.RESPONSE_EXPECTED_ALWAYS_TRUE
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
        self.response_expected[BrickRED.FUNCTION_OPEN_DIRECTORY] = BrickRED.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickRED.FUNCTION_GET_DIRECTORY_NAME] = BrickRED.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickRED.FUNCTION_GET_NEXT_DIRECTORY_ENTRY] = BrickRED.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickRED.FUNCTION_REWIND_DIRECTORY] = BrickRED.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickRED.FUNCTION_GET_IDENTITY] = BrickRED.RESPONSE_EXPECTED_ALWAYS_TRUE

        self.callback_formats[BrickRED.CALLBACK_ASYNC_FILE_WRITE] = 'H B B'
        self.callback_formats[BrickRED.CALLBACK_ASYNC_FILE_READ] = 'H B 60B B'

    def release_object(self, object_id):
        """
        
        """
        return self.ipcon.send_request(self, BrickRED.FUNCTION_RELEASE_OBJECT, (object_id,), 'H', 'B')

    def get_next_object_table_entry(self, object_type):
        """
        
        """
        return GetNextObjectTableEntry(*self.ipcon.send_request(self, BrickRED.FUNCTION_GET_NEXT_OBJECT_TABLE_ENTRY, (object_type,), 'B', 'B H'))

    def rewind_object_table(self, object_type):
        """
        
        """
        return self.ipcon.send_request(self, BrickRED.FUNCTION_REWIND_OBJECT_TABLE, (object_type,), 'B', 'B')

    def allocate_string(self, length_to_reserve):
        """
        
        """
        return AllocateString(*self.ipcon.send_request(self, BrickRED.FUNCTION_ALLOCATE_STRING, (length_to_reserve,), 'I', 'B H'))

    def truncate_string(self, string_id, length):
        """
        
        """
        return self.ipcon.send_request(self, BrickRED.FUNCTION_TRUNCATE_STRING, (string_id, length), 'H I', 'B')

    def get_string_length(self, string_id):
        """
        
        """
        return GetStringLength(*self.ipcon.send_request(self, BrickRED.FUNCTION_GET_STRING_LENGTH, (string_id,), 'H', 'B I'))

    def set_string_chunk(self, string_id, offset, buffer):
        """
        
        """
        return self.ipcon.send_request(self, BrickRED.FUNCTION_SET_STRING_CHUNK, (string_id, offset, buffer), 'H I 58s', 'B')

    def get_string_chunk(self, string_id, offset):
        """
        
        """
        return GetStringChunk(*self.ipcon.send_request(self, BrickRED.FUNCTION_GET_STRING_CHUNK, (string_id, offset), 'H I', 'B 63s'))

    def open_file(self, name_string_id, flags, permissions):
        """
        
        """
        return OpenFile(*self.ipcon.send_request(self, BrickRED.FUNCTION_OPEN_FILE, (name_string_id, flags, permissions), 'H H H', 'B H'))

    def get_file_name(self, file_id):
        """
        
        """
        return GetFileName(*self.ipcon.send_request(self, BrickRED.FUNCTION_GET_FILE_NAME, (file_id,), 'H', 'B H'))

    def write_file(self, file_id, buffer, length_to_write):
        """
        
        """
        return WriteFile(*self.ipcon.send_request(self, BrickRED.FUNCTION_WRITE_FILE, (file_id, buffer, length_to_write), 'H 61B B', 'B B'))

    def write_file_unchecked(self, file_id, buffer, length_to_write):
        """
        
        """
        self.ipcon.send_request(self, BrickRED.FUNCTION_WRITE_FILE_UNCHECKED, (file_id, buffer, length_to_write), 'H 61B B', '')

    def write_file_async(self, file_id, buffer, length_to_write):
        """
        
        """
        self.ipcon.send_request(self, BrickRED.FUNCTION_WRITE_FILE_ASYNC, (file_id, buffer, length_to_write), 'H 61B B', '')

    def read_file(self, file_id, length_to_read):
        """
        
        """
        return ReadFile(*self.ipcon.send_request(self, BrickRED.FUNCTION_READ_FILE, (file_id, length_to_read), 'H B', 'B 62B b'))

    def read_file_async(self, file_id, length_to_read):
        """
        
        """
        return self.ipcon.send_request(self, BrickRED.FUNCTION_READ_FILE_ASYNC, (file_id, length_to_read), 'H Q', 'B')

    def abort_async_file_read(self, file_id):
        """
        
        """
        return self.ipcon.send_request(self, BrickRED.FUNCTION_ABORT_ASYNC_FILE_READ, (file_id,), 'H', 'B')

    def set_file_position(self, file_id, offset, origin):
        """
        
        """
        return SetFilePosition(*self.ipcon.send_request(self, BrickRED.FUNCTION_SET_FILE_POSITION, (file_id, offset, origin), 'H q B', 'B Q'))

    def get_file_position(self, file_id):
        """
        
        """
        return GetFilePosition(*self.ipcon.send_request(self, BrickRED.FUNCTION_GET_FILE_POSITION, (file_id,), 'H', 'B Q'))

    def get_file_info(self, name_string_id, follow_symlink):
        """
        
        """
        return GetFileInfo(*self.ipcon.send_request(self, BrickRED.FUNCTION_GET_FILE_INFO, (name_string_id, follow_symlink), 'H ?', 'B B H I I Q Q Q Q'))

    def open_directory(self, name_string_id):
        """
        
        """
        return OpenDirectory(*self.ipcon.send_request(self, BrickRED.FUNCTION_OPEN_DIRECTORY, (name_string_id,), 'H', 'B H'))

    def get_directory_name(self, directory_id):
        """
        
        """
        return GetDirectoryName(*self.ipcon.send_request(self, BrickRED.FUNCTION_GET_DIRECTORY_NAME, (directory_id,), 'H', 'B H'))

    def get_next_directory_entry(self, directory_id):
        """
        
        """
        return GetNextDirectoryEntry(*self.ipcon.send_request(self, BrickRED.FUNCTION_GET_NEXT_DIRECTORY_ENTRY, (directory_id,), 'H', 'B H'))

    def rewind_directory(self, directory_id):
        """
        
        """
        return self.ipcon.send_request(self, BrickRED.FUNCTION_REWIND_DIRECTORY, (directory_id,), 'H', 'B')

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
