# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2014-08-21.      #
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

OpenInventory = namedtuple('OpenInventory', ['error_code', 'inventory_id'])
GetInventoryType = namedtuple('InventoryType', ['error_code', 'type'])
GetNextInventoryEntry = namedtuple('NextInventoryEntry', ['error_code', 'object_id'])
AllocateString = namedtuple('AllocateString', ['error_code', 'string_id'])
GetStringLength = namedtuple('StringLength', ['error_code', 'length'])
GetStringChunk = namedtuple('StringChunk', ['error_code', 'buffer'])
AllocateList = namedtuple('AllocateList', ['error_code', 'list_id'])
GetListLength = namedtuple('ListLength', ['error_code', 'length'])
GetListItem = namedtuple('ListItem', ['error_code', 'item_object_id'])
OpenFile = namedtuple('OpenFile', ['error_code', 'file_id'])
CreatePipe = namedtuple('CreatePipe', ['error_code', 'file_id'])
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
SpawnProcess = namedtuple('SpawnProcess', ['error_code', 'process_id'])
GetProcessCommand = namedtuple('ProcessCommand', ['error_code', 'command_string_id'])
GetProcessArguments = namedtuple('ProcessArguments', ['error_code', 'arguments_list_id'])
GetProcessEnvironment = namedtuple('ProcessEnvironment', ['error_code', 'environment_list_id'])
GetProcessWorkingDirectory = namedtuple('ProcessWorkingDirectory', ['error_code', 'working_directory_string_id'])
GetProcessUserID = namedtuple('ProcessUserID', ['error_code', 'user_id'])
GetProcessGroupID = namedtuple('ProcessGroupID', ['error_code', 'group_id'])
GetProcessStdin = namedtuple('ProcessStdin', ['error_code', 'stdin_file_id'])
GetProcessStdout = namedtuple('ProcessStdout', ['error_code', 'stdout_file_id'])
GetProcessStderr = namedtuple('ProcessStderr', ['error_code', 'stderr_file_id'])
GetProcessState = namedtuple('ProcessState', ['error_code', 'state', 'exit_code'])
GetIdentity = namedtuple('Identity', ['uid', 'connected_uid', 'position', 'hardware_version', 'firmware_version', 'device_identifier'])

class BrickRED(Device):
    """
    Device for running user programs standalone on the stack
    """

    DEVICE_IDENTIFIER = 17

    CALLBACK_ASYNC_FILE_WRITE = 28
    CALLBACK_ASYNC_FILE_READ = 29
    CALLBACK_PROCESS_STATE_CHANGED = 48

    FUNCTION_RELEASE_OBJECT = 1
    FUNCTION_OPEN_INVENTORY = 2
    FUNCTION_GET_INVENTORY_TYPE = 3
    FUNCTION_GET_NEXT_INVENTORY_ENTRY = 4
    FUNCTION_REWIND_INVENTORY = 5
    FUNCTION_ALLOCATE_STRING = 6
    FUNCTION_TRUNCATE_STRING = 7
    FUNCTION_GET_STRING_LENGTH = 8
    FUNCTION_SET_STRING_CHUNK = 9
    FUNCTION_GET_STRING_CHUNK = 10
    FUNCTION_ALLOCATE_LIST = 11
    FUNCTION_GET_LIST_LENGTH = 12
    FUNCTION_GET_LIST_ITEM = 13
    FUNCTION_APPEND_TO_LIST = 14
    FUNCTION_REMOVE_FROM_LIST = 15
    FUNCTION_OPEN_FILE = 16
    FUNCTION_CREATE_PIPE = 17
    FUNCTION_GET_FILE_NAME = 18
    FUNCTION_GET_FILE_TYPE = 19
    FUNCTION_WRITE_FILE = 20
    FUNCTION_WRITE_FILE_UNCHECKED = 21
    FUNCTION_WRITE_FILE_ASYNC = 22
    FUNCTION_READ_FILE = 23
    FUNCTION_READ_FILE_ASYNC = 24
    FUNCTION_ABORT_ASYNC_FILE_READ = 25
    FUNCTION_SET_FILE_POSITION = 26
    FUNCTION_GET_FILE_POSITION = 27
    FUNCTION_GET_FILE_INFO = 30
    FUNCTION_GET_SYMLINK_TARGET = 31
    FUNCTION_OPEN_DIRECTORY = 32
    FUNCTION_GET_DIRECTORY_NAME = 33
    FUNCTION_GET_NEXT_DIRECTORY_ENTRY = 34
    FUNCTION_REWIND_DIRECTORY = 35
    FUNCTION_SPAWN_PROCESS = 36
    FUNCTION_KILL_PROCESS = 37
    FUNCTION_GET_PROCESS_COMMAND = 38
    FUNCTION_GET_PROCESS_ARGUMENTS = 39
    FUNCTION_GET_PROCESS_ENVIRONMENT = 40
    FUNCTION_GET_PROCESS_WORKING_DIRECTORY = 41
    FUNCTION_GET_PROCESS_USER_ID = 42
    FUNCTION_GET_PROCESS_GROUP_ID = 43
    FUNCTION_GET_PROCESS_STDIN = 44
    FUNCTION_GET_PROCESS_STDOUT = 45
    FUNCTION_GET_PROCESS_STDERR = 46
    FUNCTION_GET_PROCESS_STATE = 47
    FUNCTION_GET_IDENTITY = 255

    OBJECT_TYPE_INVENTORY = 0
    OBJECT_TYPE_STRING = 1
    OBJECT_TYPE_LIST = 2
    OBJECT_TYPE_FILE = 3
    OBJECT_TYPE_DIRECTORY = 4
    OBJECT_TYPE_PROCESS = 5
    OBJECT_TYPE_PROGRAM = 6
    FILE_FLAG_READ_ONLY = 1
    FILE_FLAG_WRITE_ONLY = 2
    FILE_FLAG_READ_WRITE = 4
    FILE_FLAG_APPEND = 8
    FILE_FLAG_CREATE = 16
    FILE_FLAG_EXCLUSIVE = 32
    FILE_FLAG_NO_ACCESS_TIME = 64
    FILE_FLAG_NO_FOLLOW = 128
    FILE_FLAG_TRUNCATE = 256
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
    FILE_TYPE_PIPE = 8
    FILE_ORIGIN_BEGINNING = 0
    FILE_ORIGIN_CURRENT = 1
    FILE_ORIGIN_END = 2
    PROCESS_SIGNAL_INTERRUPT = 2
    PROCESS_SIGNAL_QUIT = 3
    PROCESS_SIGNAL_ABORT = 6
    PROCESS_SIGNAL_KILL = 9
    PROCESS_SIGNAL_USER1 = 10
    PROCESS_SIGNAL_USER2 = 12
    PROCESS_SIGNAL_TERMINATE = 15
    PROCESS_SIGNAL_CONTINUE = 18
    PROCESS_SIGNAL_STOP = 19
    PROCESS_STATE_UNKNOWN = 0
    PROCESS_STATE_RUNNING = 1
    PROCESS_STATE_EXITED = 2
    PROCESS_STATE_KILLED = 3
    PROCESS_STATE_STOPPED = 4

    def __init__(self, uid, ipcon):
        """
        Creates an object with the unique device ID *uid* and adds it to
        the IP Connection *ipcon*.
        """
        Device.__init__(self, uid, ipcon)

        self.api_version = (2, 0, 0)

        self.response_expected[BrickRED.FUNCTION_RELEASE_OBJECT] = BrickRED.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickRED.FUNCTION_OPEN_INVENTORY] = BrickRED.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickRED.FUNCTION_GET_INVENTORY_TYPE] = BrickRED.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickRED.FUNCTION_GET_NEXT_INVENTORY_ENTRY] = BrickRED.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickRED.FUNCTION_REWIND_INVENTORY] = BrickRED.RESPONSE_EXPECTED_ALWAYS_TRUE
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
        self.response_expected[BrickRED.FUNCTION_CREATE_PIPE] = BrickRED.RESPONSE_EXPECTED_ALWAYS_TRUE
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
        self.response_expected[BrickRED.FUNCTION_SPAWN_PROCESS] = BrickRED.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickRED.FUNCTION_KILL_PROCESS] = BrickRED.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickRED.FUNCTION_GET_PROCESS_COMMAND] = BrickRED.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickRED.FUNCTION_GET_PROCESS_ARGUMENTS] = BrickRED.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickRED.FUNCTION_GET_PROCESS_ENVIRONMENT] = BrickRED.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickRED.FUNCTION_GET_PROCESS_WORKING_DIRECTORY] = BrickRED.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickRED.FUNCTION_GET_PROCESS_USER_ID] = BrickRED.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickRED.FUNCTION_GET_PROCESS_GROUP_ID] = BrickRED.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickRED.FUNCTION_GET_PROCESS_STDIN] = BrickRED.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickRED.FUNCTION_GET_PROCESS_STDOUT] = BrickRED.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickRED.FUNCTION_GET_PROCESS_STDERR] = BrickRED.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickRED.FUNCTION_GET_PROCESS_STATE] = BrickRED.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickRED.CALLBACK_PROCESS_STATE_CHANGED] = BrickRED.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickRED.FUNCTION_GET_IDENTITY] = BrickRED.RESPONSE_EXPECTED_ALWAYS_TRUE

        self.callback_formats[BrickRED.CALLBACK_ASYNC_FILE_WRITE] = 'H B B'
        self.callback_formats[BrickRED.CALLBACK_ASYNC_FILE_READ] = 'H B 60B B'
        self.callback_formats[BrickRED.CALLBACK_PROCESS_STATE_CHANGED] = 'H B B'

    def release_object(self, object_id):
        """
        Decreases the reference count of an object by one and returns the resulting
        error code. If the reference count reaches zero the object is destroyed.
        """
        return self.ipcon.send_request(self, BrickRED.FUNCTION_RELEASE_OBJECT, (object_id,), 'H', 'B')

    def open_inventory(self, type):
        """
        Opens the inventory for a specific object type and allocates a new inventory
        object for it.
        
        Returns the object ID of the new directory object and the resulting error code.
        """
        return OpenInventory(*self.ipcon.send_request(self, BrickRED.FUNCTION_OPEN_INVENTORY, (type,), 'B', 'B H'))

    def get_inventory_type(self, inventory_id):
        """
        Returns the object type of a inventory object and the resulting error code.
        """
        return GetInventoryType(*self.ipcon.send_request(self, BrickRED.FUNCTION_GET_INVENTORY_TYPE, (inventory_id,), 'H', 'B B'))

    def get_next_inventory_entry(self, inventory_id):
        """
        Returns the object ID of the next object in an inventory object and the
        resulting error code. If there is not next object then error code
        ``API_E_NO_MORE_DATA`` is returned. To rewind an inventory object call
        :func:`RewindInventory`.
        """
        return GetNextInventoryEntry(*self.ipcon.send_request(self, BrickRED.FUNCTION_GET_NEXT_INVENTORY_ENTRY, (inventory_id,), 'H', 'B H'))

    def rewind_inventory(self, inventory_id):
        """
        Rewinds an inventory object and returns the resulting error code.
        """
        return self.ipcon.send_request(self, BrickRED.FUNCTION_REWIND_INVENTORY, (inventory_id,), 'H', 'B')

    def allocate_string(self, length_to_reserve, buffer):
        """
        Allocates a new string object, reserves ``length_to_reserve`` bytes memory
        for it and sets up to the first 60 bytes. Set ``length_to_reserve`` to the
        length of the string that should be stored in the string object.
        
        Returns the object ID of the new string object and the resulting error code.
        """
        return AllocateString(*self.ipcon.send_request(self, BrickRED.FUNCTION_ALLOCATE_STRING, (length_to_reserve, buffer), 'I 60s', 'B H'))

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
        Opens an existing file or creates a new file and allocates a new file object
        for it.
        
        The reference count of the name string object is increased by one. When the
        file object is destroyed then the reference count of the name string object is
        decreased by one. Also the name string object is locked and cannot be modified
        while the file object holds a reference to it.
        
        Returns the object ID of the new file object and the resulting error code.
        """
        return OpenFile(*self.ipcon.send_request(self, BrickRED.FUNCTION_OPEN_FILE, (name_string_id, flags, permissions, user_id, group_id), 'H H H I I', 'B H'))

    def create_pipe(self):
        """
        Creates a new pipe and allocates a new file object for it.
        
        Returns the object ID of the new file object and the resulting error code.
        """
        return CreatePipe(*self.ipcon.send_request(self, BrickRED.FUNCTION_CREATE_PIPE, (), '', 'B H'))

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
        Set the current seek position of a file object in bytes relative to ``origin``.
        
        Returns the resulting absolute seek position and error code.
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
        Opens an existing directory and allocates a new directory object for it.
        
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
        Returns the next entry in a directory object and the resulting error code.
        If there is not next entry then error code ``API_E_NO_MORE_DATA`` is returned.
        To rewind a directory object call :func:`RewindDirectory`.
        """
        return GetNextDirectoryEntry(*self.ipcon.send_request(self, BrickRED.FUNCTION_GET_NEXT_DIRECTORY_ENTRY, (directory_id,), 'H', 'B H B'))

    def rewind_directory(self, directory_id):
        """
        Rewinds a directory object and returns the resulting error code.
        """
        return self.ipcon.send_request(self, BrickRED.FUNCTION_REWIND_DIRECTORY, (directory_id,), 'H', 'B')

    def spawn_process(self, command_string_id, arguments_list_id, environment_list_id, working_directory_string_id, user_id, group_id, stdin_file_id, stdout_file_id, stderr_file_id):
        """
        
        """
        return SpawnProcess(*self.ipcon.send_request(self, BrickRED.FUNCTION_SPAWN_PROCESS, (command_string_id, arguments_list_id, environment_list_id, working_directory_string_id, user_id, group_id, stdin_file_id, stdout_file_id, stderr_file_id), 'H H H H I I H H H', 'B H'))

    def kill_process(self, process_id, signal):
        """
        
        """
        self.ipcon.send_request(self, BrickRED.FUNCTION_KILL_PROCESS, (process_id, signal), 'H B', '')

    def get_process_command(self, process_id):
        """
        
        """
        return GetProcessCommand(*self.ipcon.send_request(self, BrickRED.FUNCTION_GET_PROCESS_COMMAND, (process_id,), 'H', 'B H'))

    def get_process_arguments(self, process_id):
        """
        
        """
        return GetProcessArguments(*self.ipcon.send_request(self, BrickRED.FUNCTION_GET_PROCESS_ARGUMENTS, (process_id,), 'H', 'B H'))

    def get_process_environment(self, process_id):
        """
        
        """
        return GetProcessEnvironment(*self.ipcon.send_request(self, BrickRED.FUNCTION_GET_PROCESS_ENVIRONMENT, (process_id,), 'H', 'B H'))

    def get_process_working_directory(self, process_id):
        """
        
        """
        return GetProcessWorkingDirectory(*self.ipcon.send_request(self, BrickRED.FUNCTION_GET_PROCESS_WORKING_DIRECTORY, (process_id,), 'H', 'B H'))

    def get_process_user_id(self, process_id):
        """
        
        """
        return GetProcessUserID(*self.ipcon.send_request(self, BrickRED.FUNCTION_GET_PROCESS_USER_ID, (process_id,), 'H', 'B I'))

    def get_process_group_id(self, process_id):
        """
        
        """
        return GetProcessGroupID(*self.ipcon.send_request(self, BrickRED.FUNCTION_GET_PROCESS_GROUP_ID, (process_id,), 'H', 'B I'))

    def get_process_stdin(self, process_id):
        """
        
        """
        return GetProcessStdin(*self.ipcon.send_request(self, BrickRED.FUNCTION_GET_PROCESS_STDIN, (process_id,), 'H', 'B H'))

    def get_process_stdout(self, process_id):
        """
        
        """
        return GetProcessStdout(*self.ipcon.send_request(self, BrickRED.FUNCTION_GET_PROCESS_STDOUT, (process_id,), 'H', 'B H'))

    def get_process_stderr(self, process_id):
        """
        
        """
        return GetProcessStderr(*self.ipcon.send_request(self, BrickRED.FUNCTION_GET_PROCESS_STDERR, (process_id,), 'H', 'B H'))

    def get_process_state(self, process_id):
        """
        
        """
        return GetProcessState(*self.ipcon.send_request(self, BrickRED.FUNCTION_GET_PROCESS_STATE, (process_id,), 'H', 'B B B'))

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
