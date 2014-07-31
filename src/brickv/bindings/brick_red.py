# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2014-07-31.      #
#                                                           #
# Bindings Version 2.1.1                                    #
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
        
        """
        return self.ipcon.send_request(self, BrickRED.FUNCTION_RELEASE_OBJECT, (object_id,), 'H', 'B')

    def get_next_object_table_entry(self, type):
        """
        
        """
        return GetNextObjectTableEntry(*self.ipcon.send_request(self, BrickRED.FUNCTION_GET_NEXT_OBJECT_TABLE_ENTRY, (type,), 'B', 'B H'))

    def rewind_object_table(self, type):
        """
        
        """
        return self.ipcon.send_request(self, BrickRED.FUNCTION_REWIND_OBJECT_TABLE, (type,), 'B', 'B')

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

    def allocate_list(self, length_to_reserve):
        """
        
        """
        return AllocateList(*self.ipcon.send_request(self, BrickRED.FUNCTION_ALLOCATE_LIST, (length_to_reserve,), 'H', 'B H'))

    def get_list_length(self, list_id):
        """
        
        """
        return GetListLength(*self.ipcon.send_request(self, BrickRED.FUNCTION_GET_LIST_LENGTH, (list_id,), 'H', 'B H'))

    def get_list_item(self, list_id, index):
        """
        
        """
        return GetListItem(*self.ipcon.send_request(self, BrickRED.FUNCTION_GET_LIST_ITEM, (list_id, index), 'H H', 'B H'))

    def append_to_list(self, list_id, item_object_id):
        """
        
        """
        return self.ipcon.send_request(self, BrickRED.FUNCTION_APPEND_TO_LIST, (list_id, item_object_id), 'H H', 'B')

    def remove_from_list(self, list_id, index):
        """
        
        """
        return self.ipcon.send_request(self, BrickRED.FUNCTION_REMOVE_FROM_LIST, (list_id, index), 'H H', 'B')

    def open_file(self, name_string_id, flags, permissions, user_id, group_id):
        """
        
        """
        return OpenFile(*self.ipcon.send_request(self, BrickRED.FUNCTION_OPEN_FILE, (name_string_id, flags, permissions, user_id, group_id), 'H H H I I', 'B H'))

    def get_file_name(self, file_id):
        """
        
        """
        return GetFileName(*self.ipcon.send_request(self, BrickRED.FUNCTION_GET_FILE_NAME, (file_id,), 'H', 'B H'))

    def get_file_type(self, file_id):
        """
        
        """
        return GetFileType(*self.ipcon.send_request(self, BrickRED.FUNCTION_GET_FILE_TYPE, (file_id,), 'H', 'B B'))

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

    def get_symlink_target(self, name_string_id, canonicalize):
        """
        
        """
        return GetSymlinkTarget(*self.ipcon.send_request(self, BrickRED.FUNCTION_GET_SYMLINK_TARGET, (name_string_id, canonicalize), 'H ?', 'B H'))

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
        return GetNextDirectoryEntry(*self.ipcon.send_request(self, BrickRED.FUNCTION_GET_NEXT_DIRECTORY_ENTRY, (directory_id,), 'H', 'B H B'))

    def rewind_directory(self, directory_id):
        """
        
        """
        return self.ipcon.send_request(self, BrickRED.FUNCTION_REWIND_DIRECTORY, (directory_id,), 'H', 'B')

    def start_process(self, command_string_id, argument_string_ids, argument_count, environment_string_ids, environment_count, merge_stdout_and_stderr):
        """
        
        """
        return StartProcess(*self.ipcon.send_request(self, BrickRED.FUNCTION_START_PROCESS, (command_string_id, argument_string_ids, argument_count, environment_string_ids, environment_count, merge_stdout_and_stderr), 'H 20H B 8H B ?', 'B H'))

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
