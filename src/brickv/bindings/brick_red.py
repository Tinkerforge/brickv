# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2014-09-25.      #
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
GetFileInfo = namedtuple('FileInfo', ['error_code', 'type', 'name_string_id', 'flags', 'permissions', 'user_id', 'group_id', 'length', 'access_timestamp', 'modification_timestamp', 'status_change_timestamp'])
ReadFile = namedtuple('ReadFile', ['error_code', 'buffer', 'length_read'])
WriteFile = namedtuple('WriteFile', ['error_code', 'length_written'])
SetFilePosition = namedtuple('SetFilePosition', ['error_code', 'position'])
GetFilePosition = namedtuple('FilePosition', ['error_code', 'position'])
LookupFileInfo = namedtuple('LookupFileInfo', ['error_code', 'type', 'permissions', 'user_id', 'group_id', 'length', 'access_timestamp', 'modification_timestamp', 'status_change_timestamp'])
LookupSymlinkTarget = namedtuple('LookupSymlinkTarget', ['error_code', 'target_string_id'])
OpenDirectory = namedtuple('OpenDirectory', ['error_code', 'directory_id'])
GetDirectoryName = namedtuple('DirectoryName', ['error_code', 'name_string_id'])
GetNextDirectoryEntry = namedtuple('NextDirectoryEntry', ['error_code', 'name_string_id', 'type'])
SpawnProcess = namedtuple('SpawnProcess', ['error_code', 'process_id'])
GetProcessCommand = namedtuple('ProcessCommand', ['error_code', 'executable_string_id', 'arguments_list_id', 'environment_list_id', 'working_directory_string_id'])
GetProcessIdentity = namedtuple('ProcessIdentity', ['error_code', 'user_id', 'group_id'])
GetProcessStdio = namedtuple('ProcessStdio', ['error_code', 'stdin_file_id', 'stdout_file_id', 'stderr_file_id'])
GetProcessState = namedtuple('ProcessState', ['error_code', 'state', 'exit_code'])
DefineProgram = namedtuple('DefineProgram', ['error_code', 'program_id'])
GetProgramIdentifier = namedtuple('ProgramIdentifier', ['error_code', 'identifier_string_id'])
GetProgramDirectory = namedtuple('ProgramDirectory', ['error_code', 'directory_string_id'])
GetProgramCommand = namedtuple('ProgramCommand', ['error_code', 'executable_string_id', 'arguments_list_id', 'environment_list_id'])
GetProgramStdioRedirection = namedtuple('ProgramStdioRedirection', ['error_code', 'stdin_redirection', 'stdin_file_name_string_id', 'stdout_redirection', 'stdout_file_name_string_id', 'stderr_redirection', 'stderr_file_name_string_id'])
GetProgramSchedule = namedtuple('ProgramSchedule', ['error_code', 'start_condition', 'start_timestamp', 'start_delay', 'repeat_mode', 'repeat_interval', 'repeat_second_mask', 'repeat_minute_mask', 'repeat_hour_mask', 'repeat_day_mask', 'repeat_month_mask', 'repeat_weekday_mask'])
GetIdentity = namedtuple('Identity', ['uid', 'connected_uid', 'position', 'hardware_version', 'firmware_version', 'device_identifier'])

class BrickRED(Device):
    """
    Device for running user programs standalone on the stack
    """

    DEVICE_IDENTIFIER = 17

    CALLBACK_ASYNC_FILE_READ = 27
    CALLBACK_ASYNC_FILE_WRITE = 28
    CALLBACK_PROCESS_STATE_CHANGED = 42

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
    FUNCTION_GET_FILE_INFO = 18
    FUNCTION_READ_FILE = 19
    FUNCTION_READ_FILE_ASYNC = 20
    FUNCTION_ABORT_ASYNC_FILE_READ = 21
    FUNCTION_WRITE_FILE = 22
    FUNCTION_WRITE_FILE_UNCHECKED = 23
    FUNCTION_WRITE_FILE_ASYNC = 24
    FUNCTION_SET_FILE_POSITION = 25
    FUNCTION_GET_FILE_POSITION = 26
    FUNCTION_LOOKUP_FILE_INFO = 29
    FUNCTION_LOOKUP_SYMLINK_TARGET = 30
    FUNCTION_OPEN_DIRECTORY = 31
    FUNCTION_GET_DIRECTORY_NAME = 32
    FUNCTION_GET_NEXT_DIRECTORY_ENTRY = 33
    FUNCTION_REWIND_DIRECTORY = 34
    FUNCTION_CREATE_DIRECTORY = 35
    FUNCTION_SPAWN_PROCESS = 36
    FUNCTION_KILL_PROCESS = 37
    FUNCTION_GET_PROCESS_COMMAND = 38
    FUNCTION_GET_PROCESS_IDENTITY = 39
    FUNCTION_GET_PROCESS_STDIO = 40
    FUNCTION_GET_PROCESS_STATE = 41
    FUNCTION_DEFINE_PROGRAM = 43
    FUNCTION_UNDEFINE_PROGRAM = 44
    FUNCTION_GET_PROGRAM_IDENTIFIER = 45
    FUNCTION_GET_PROGRAM_DIRECTORY = 46
    FUNCTION_SET_PROGRAM_COMMAND = 47
    FUNCTION_GET_PROGRAM_COMMAND = 48
    FUNCTION_SET_PROGRAM_STDIO_REDIRECTION = 49
    FUNCTION_GET_PROGRAM_STDIO_REDIRECTION = 50
    FUNCTION_SET_PROGRAM_SCHEDULE = 51
    FUNCTION_GET_PROGRAM_SCHEDULE = 52
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
    FILE_FLAG_NON_BLOCKING = 64
    FILE_FLAG_TRUNCATE = 128
    FILE_FLAG_TEMPORARY = 256
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
    PIPE_FLAG_NON_BLOCKING_READ = 1
    PIPE_FLAG_NON_BLOCKING_WRITE = 2
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
    PROCESS_STATE_ERROR = 2
    PROCESS_STATE_EXITED = 3
    PROCESS_STATE_KILLED = 4
    PROCESS_STATE_STOPPED = 5
    PROGRAM_STDIO_REDIRECTION_DEV_NULL = 0
    PROGRAM_STDIO_REDIRECTION_PIPE = 1
    PROGRAM_STDIO_REDIRECTION_FILE = 2
    PROGRAM_STDIO_REDIRECTION_STDOUT = 3
    PROGRAM_STDIO_REDIRECTION_LOG = 4
    PROGRAM_START_CONDITION_NEVER = 0
    PROGRAM_START_CONDITION_NOW = 1
    PROGRAM_START_CONDITION_REBOOT = 2
    PROGRAM_START_CONDITION_TIMESTAMP = 3
    PROGRAM_REPEAT_MODE_NEVER = 0
    PROGRAM_REPEAT_MODE_INTERVAL = 1
    PROGRAM_REPEAT_MODE_SELECTION = 2

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
        self.response_expected[BrickRED.FUNCTION_GET_FILE_INFO] = BrickRED.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickRED.FUNCTION_READ_FILE] = BrickRED.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickRED.FUNCTION_READ_FILE_ASYNC] = BrickRED.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickRED.FUNCTION_ABORT_ASYNC_FILE_READ] = BrickRED.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickRED.FUNCTION_WRITE_FILE] = BrickRED.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickRED.FUNCTION_WRITE_FILE_UNCHECKED] = BrickRED.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickRED.FUNCTION_WRITE_FILE_ASYNC] = BrickRED.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickRED.FUNCTION_SET_FILE_POSITION] = BrickRED.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickRED.FUNCTION_GET_FILE_POSITION] = BrickRED.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickRED.CALLBACK_ASYNC_FILE_READ] = BrickRED.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickRED.CALLBACK_ASYNC_FILE_WRITE] = BrickRED.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickRED.FUNCTION_LOOKUP_FILE_INFO] = BrickRED.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickRED.FUNCTION_LOOKUP_SYMLINK_TARGET] = BrickRED.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickRED.FUNCTION_OPEN_DIRECTORY] = BrickRED.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickRED.FUNCTION_GET_DIRECTORY_NAME] = BrickRED.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickRED.FUNCTION_GET_NEXT_DIRECTORY_ENTRY] = BrickRED.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickRED.FUNCTION_REWIND_DIRECTORY] = BrickRED.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickRED.FUNCTION_CREATE_DIRECTORY] = BrickRED.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickRED.FUNCTION_SPAWN_PROCESS] = BrickRED.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickRED.FUNCTION_KILL_PROCESS] = BrickRED.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickRED.FUNCTION_GET_PROCESS_COMMAND] = BrickRED.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickRED.FUNCTION_GET_PROCESS_IDENTITY] = BrickRED.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickRED.FUNCTION_GET_PROCESS_STDIO] = BrickRED.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickRED.FUNCTION_GET_PROCESS_STATE] = BrickRED.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickRED.CALLBACK_PROCESS_STATE_CHANGED] = BrickRED.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickRED.FUNCTION_DEFINE_PROGRAM] = BrickRED.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickRED.FUNCTION_UNDEFINE_PROGRAM] = BrickRED.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickRED.FUNCTION_GET_PROGRAM_IDENTIFIER] = BrickRED.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickRED.FUNCTION_GET_PROGRAM_DIRECTORY] = BrickRED.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickRED.FUNCTION_SET_PROGRAM_COMMAND] = BrickRED.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickRED.FUNCTION_GET_PROGRAM_COMMAND] = BrickRED.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickRED.FUNCTION_SET_PROGRAM_STDIO_REDIRECTION] = BrickRED.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickRED.FUNCTION_GET_PROGRAM_STDIO_REDIRECTION] = BrickRED.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickRED.FUNCTION_SET_PROGRAM_SCHEDULE] = BrickRED.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickRED.FUNCTION_GET_PROGRAM_SCHEDULE] = BrickRED.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickRED.FUNCTION_GET_IDENTITY] = BrickRED.RESPONSE_EXPECTED_ALWAYS_TRUE

        self.callback_formats[BrickRED.CALLBACK_ASYNC_FILE_READ] = 'H B 60B B'
        self.callback_formats[BrickRED.CALLBACK_ASYNC_FILE_WRITE] = 'H B B'
        self.callback_formats[BrickRED.CALLBACK_PROCESS_STATE_CHANGED] = 'H B B'

    def release_object(self, object_id):
        """
        Decreases the reference count of an object by one and returns the resulting
        error code. If the reference count reaches zero the object gets destroyed.
        """
        return self.ipcon.send_request(self, BrickRED.FUNCTION_RELEASE_OBJECT, (object_id,), 'H', 'B')

    def open_inventory(self, type):
        """
        Opens the inventory for a specific object type and allocates a new inventory
        object for it.
        
        Possible object types are:
        
        * Inventory = 0
        * String = 1
        * List = 2
        * File = 3
        * Directory = 4
        * Process = 5
        * Program = 6
        
        Returns the object ID of the new directory object and the resulting error code.
        """
        return OpenInventory(*self.ipcon.send_request(self, BrickRED.FUNCTION_OPEN_INVENTORY, (type,), 'B', 'B H'))

    def get_inventory_type(self, inventory_id):
        """
        Returns the object type of a inventory object, as passed to
        :func:`OpenInventory`, and the resulting error code.
        
        See :func:`OpenInventory` for possible object types.
        """
        return GetInventoryType(*self.ipcon.send_request(self, BrickRED.FUNCTION_GET_INVENTORY_TYPE, (inventory_id,), 'H', 'B B'))

    def get_next_inventory_entry(self, inventory_id):
        """
        Returns the object ID of the next object in an inventory object and the
        resulting error code.
        
        If there is not next object then error code *NoMoreData* is returned. To rewind
        an inventory object call :func:`RewindInventory`.
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
        Allocates a new list object and reserves memory for ``length_to_reserve``
        items. Set ``length_to_reserve`` to the number of items that should be stored
        in the list object.
        
        Returns the object ID of the new list object and the resulting error code.
        
        When a list object gets destroyed then the reference count of each object in
        the list object is decreased by one.
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
        
        FIXME: name has to be absolute
        
        The reference count of the name string object is increased by one. When the
        file object gets destroyed then the reference count of the name string object is
        decreased by one. Also the name string object is locked and cannot be modified
        while the file object holds a reference to it.
        
        The ``flags`` parameter takes a ORed combination of the following possible file
        flags (in hexadecimal notation):
        
        * ReadOnly = 0x0001 (O_RDONLY)
        * WriteOnly = 0x0002 (O_WRONLY)
        * ReadWrite = 0x0004 (O_RDWR)
        * Append = 0x0008 (O_APPEND)
        * Create = 0x0010 (O_CREAT)
        * Exclusive = 0x0020 (O_EXCL)
        * NonBlocking = 0x0040 (O_NONBLOCK)
        * Truncate = 0x0080 (O_TRUNC)
        * Temporary = 0x0100
        
        FIXME: explain *Temporary* flag
        
        The ``permissions`` parameter takes a ORed combination of the following
        possible file permissions (in octal notation) that match the common UNIX
        permission bits:
        
        * UserRead = 00400
        * UserWrite = 00200
        * UserExecute = 00100
        * GroupRead = 00040
        * GroupWrite = 00020
        * GroupExecute = 00010
        * OthersRead = 00004
        * OthersWrite = 00002
        * OthersExecute = 00001
        
        Returns the object ID of the new file object and the resulting error code.
        """
        return OpenFile(*self.ipcon.send_request(self, BrickRED.FUNCTION_OPEN_FILE, (name_string_id, flags, permissions, user_id, group_id), 'H H H I I', 'B H'))

    def create_pipe(self, flags):
        """
        Creates a new pipe and allocates a new file object for it.
        
        The ``flags`` parameter takes a ORed combination of the following possible
        pipe flags (in hexadecimal notation):
        
        * NonBlockingRead = 0x0001
        * NonBlockingWrite = 0x0002
        
        Returns the object ID of the new file object and the resulting error code.
        """
        return CreatePipe(*self.ipcon.send_request(self, BrickRED.FUNCTION_CREATE_PIPE, (flags,), 'H', 'B H'))

    def get_file_info(self, file_id):
        """
        Returns various information about a file and the resulting error code.
        
        Possible file types are:
        
        * Unknown = 0
        * Regular = 1
        * Directory = 2
        * Character = 3
        * Block = 4
        * FIFO = 5
        * Symlink = 6
        * Socket = 7
        * Pipe = 8
        
        If the file type is *Pipe* then the returned name string object is invalid,
        because a pipe has no name. Otherwise the returned name string object was used
        to open or create the file object, as passed to :func:`OpenFile`.
        
        The returned flags were used to open or create the file object, as passed to
        :func:`OpenFile` or :func:`CreatePipe`. See the respective function for a list
        of possible file and pipe flags.
        
        FIXME: everything except flags is invalid if file type is *Pipe*
        """
        return GetFileInfo(*self.ipcon.send_request(self, BrickRED.FUNCTION_GET_FILE_INFO, (file_id,), 'H', 'B B H H H I I Q Q Q Q'))

    def read_file(self, file_id, length_to_read):
        """
        Reads up to 62 bytes from a file object.
        
        Returns the read bytes and the resulting error code.
        
        If the file object was created by :func:`OpenFile` without the *NonBlocking*
        flag or by :func:`CreatePipe` without the *NonBlockingRead* flag then the
        error code *NotSupported* is returned.
        """
        return ReadFile(*self.ipcon.send_request(self, BrickRED.FUNCTION_READ_FILE, (file_id, length_to_read), 'H B', 'B 62B B'))

    def read_file_async(self, file_id, length_to_read):
        """
        Reads up to 2\ :sup:`63`\  - 1 bytes from a file object asynchronously.
        
        Returns the resulting error code.
        
        The read bytes in 60 byte chunks and the resulting error codes of the read
        operations are reported via the :func:`AsyncFileRead` callback.
        
        If the file object was created by :func:`OpenFile` without the *NonBlocking*
        flag or by :func:`CreatePipe` without the *NonBlockingRead* flag then the error
        code *NotSupported* is reported via the :func:`AsyncFileRead` callback.
        """
        return self.ipcon.send_request(self, BrickRED.FUNCTION_READ_FILE_ASYNC, (file_id, length_to_read), 'H Q', 'B')

    def abort_async_file_read(self, file_id):
        """
        Aborts a :func:`ReadFileAsync` operation in progress.
        
        Returns the resulting error code.
        """
        return self.ipcon.send_request(self, BrickRED.FUNCTION_ABORT_ASYNC_FILE_READ, (file_id,), 'H', 'B')

    def write_file(self, file_id, buffer, length_to_write):
        """
        Writes up to 61 bytes to a file object.
        
        Returns the actual number of bytes written and the resulting error code.
        
        If the file object was created by :func:`OpenFile` without the *NonBlocking*
        flag or by :func:`CreatePipe` without the *NonBlockingWrite* flag then the
        error code *NotSupported* is returned.
        """
        return WriteFile(*self.ipcon.send_request(self, BrickRED.FUNCTION_WRITE_FILE, (file_id, buffer, length_to_write), 'H 61B B', 'B B'))

    def write_file_unchecked(self, file_id, buffer, length_to_write):
        """
        Writes up to 61 bytes to a file object.
        
        Does neither report the actual number of bytes written nor the resulting error
        code.
        
        If the file object was created by :func:`OpenFile` without the *NonBlocking*
        flag or by :func:`CreatePipe` without the *NonBlockingWrite* flag then the
        write operation will fail silently.
        """
        self.ipcon.send_request(self, BrickRED.FUNCTION_WRITE_FILE_UNCHECKED, (file_id, buffer, length_to_write), 'H 61B B', '')

    def write_file_async(self, file_id, buffer, length_to_write):
        """
        Writes up to 61 bytes to a file object.
        
        Reports the actual number of bytes written and the resulting error code via the
        :func:`AsyncFileWrite` callback.
        
        If the file object was created by :func:`OpenFile` without the *NonBlocking*
        flag or by :func:`CreatePipe` without the *NonBlockingWrite* flag then the
        error code *NotSupported* is reported via the :func:`AsyncFileWrite` callback.
        """
        self.ipcon.send_request(self, BrickRED.FUNCTION_WRITE_FILE_ASYNC, (file_id, buffer, length_to_write), 'H 61B B', '')

    def set_file_position(self, file_id, offset, origin):
        """
        Set the current seek position of a file object in bytes relative to ``origin``.
        
        Possible file origins are:
        
        * Beginning = 0
        * Current = 1
        * End = 2
        
        Returns the resulting absolute seek position and error code.
        
        If the file object was created by :func:`CreatePipe` then it has no seek
        position and the error code *InvalidSeek* is returned.
        """
        return SetFilePosition(*self.ipcon.send_request(self, BrickRED.FUNCTION_SET_FILE_POSITION, (file_id, offset, origin), 'H q B', 'B Q'))

    def get_file_position(self, file_id):
        """
        Returns the current seek position of a file object in bytes and returns the
        resulting error code.
        
        If the file object was created by :func:`CreatePipe` then it has no seek
        position and the error code *InvalidSeek* is returned.
        """
        return GetFilePosition(*self.ipcon.send_request(self, BrickRED.FUNCTION_GET_FILE_POSITION, (file_id,), 'H', 'B Q'))

    def lookup_file_info(self, name_string_id, follow_symlink):
        """
        Returns various information about a file and the resulting error code.
        
        FIXME: name has to be absolute
        
        The information is obtained via the
        `stat() <http://pubs.opengroup.org/onlinepubs/9699919799/functions/stat.html>`__
        function. If ``follow_symlink`` is *false* then the
        `lstat() <http://pubs.opengroup.org/onlinepubs/9699919799/functions/stat.html>`__
        function is used instead.
        
        See :func:`GetFileInfo` for a list of possible file types and see
        :func:`OpenFile` for a list of possible file permissions.
        """
        return LookupFileInfo(*self.ipcon.send_request(self, BrickRED.FUNCTION_LOOKUP_FILE_INFO, (name_string_id, follow_symlink), 'H ?', 'B B H I I Q Q Q Q'))

    def lookup_symlink_target(self, name_string_id, canonicalize):
        """
        Returns the target of a symbolic link and the resulting error code.
        
        FIXME: name has to be absolute
        
        If ``canonicalize`` is *false* then the target of the symbolic link is resolved
        one level via the
        `readlink() <http://pubs.opengroup.org/onlinepubs/9699919799/functions/readlink.html>`__
        function, otherwise it is fully resolved using the
        `realpath() <http://pubs.opengroup.org/onlinepubs/9699919799/functions/realpath.html>`__
        function.
        """
        return LookupSymlinkTarget(*self.ipcon.send_request(self, BrickRED.FUNCTION_LOOKUP_SYMLINK_TARGET, (name_string_id, canonicalize), 'H ?', 'B H'))

    def open_directory(self, name_string_id):
        """
        Opens an existing directory and allocates a new directory object for it.
        
        FIXME: name has to be absolute
        
        The reference count of the name string object is increased by one. When the
        directory object is destroyed then the reference count of the name string
        object is decreased by one. Also the name string object is locked and cannot be
        modified while the directory object holds a reference to it.
        
        Returns the object ID of the new directory object and the resulting error code.
        """
        return OpenDirectory(*self.ipcon.send_request(self, BrickRED.FUNCTION_OPEN_DIRECTORY, (name_string_id,), 'H', 'B H'))

    def get_directory_name(self, directory_id):
        """
        Returns the name of a directory object, as passed to :func:`OpenDirectory`, and
        the resulting error code.
        """
        return GetDirectoryName(*self.ipcon.send_request(self, BrickRED.FUNCTION_GET_DIRECTORY_NAME, (directory_id,), 'H', 'B H'))

    def get_next_directory_entry(self, directory_id):
        """
        Returns the next entry in a directory object and the resulting error code.
        
        If there is not next entry then error code *NoMoreData* is returned. To rewind
        a directory object call :func:`RewindDirectory`.
        
        See :func:`GetFileType` for a list of possible file types.
        """
        return GetNextDirectoryEntry(*self.ipcon.send_request(self, BrickRED.FUNCTION_GET_NEXT_DIRECTORY_ENTRY, (directory_id,), 'H', 'B H B'))

    def rewind_directory(self, directory_id):
        """
        Rewinds a directory object and returns the resulting error code.
        """
        return self.ipcon.send_request(self, BrickRED.FUNCTION_REWIND_DIRECTORY, (directory_id,), 'H', 'B')

    def create_directory(self, name_string_id, recursive, permissions, user_id, group_id):
        """
        FIXME: name has to be absolute
        """
        return self.ipcon.send_request(self, BrickRED.FUNCTION_CREATE_DIRECTORY, (name_string_id, recursive, permissions, user_id, group_id), 'H ? H I I', 'B')

    def spawn_process(self, executable_string_id, arguments_list_id, environment_list_id, working_directory_string_id, user_id, group_id, stdin_file_id, stdout_file_id, stderr_file_id):
        """
        
        """
        return SpawnProcess(*self.ipcon.send_request(self, BrickRED.FUNCTION_SPAWN_PROCESS, (executable_string_id, arguments_list_id, environment_list_id, working_directory_string_id, user_id, group_id, stdin_file_id, stdout_file_id, stderr_file_id), 'H H H H I I H H H', 'B H'))

    def kill_process(self, process_id, signal):
        """
        Sends a UNIX signal to a process object and returns the resulting error code.
        
        Possible UNIX signals are:
        
        * Interrupt = 2
        * Quit = 3
        * Abort = 6
        * Kill = 9
        * User1 = 10
        * User2 = 12
        * Terminate = 15
        * Continue =  18
        * Stop = 19
        """
        return self.ipcon.send_request(self, BrickRED.FUNCTION_KILL_PROCESS, (process_id, signal), 'H B', 'B')

    def get_process_command(self, process_id):
        """
        Returns the executable, arguments, environment and working directory used to
        spawn a process object, as passed to :func:`SpawnProcess`, and the resulting
        error code.
        """
        return GetProcessCommand(*self.ipcon.send_request(self, BrickRED.FUNCTION_GET_PROCESS_COMMAND, (process_id,), 'H', 'B H H H H'))

    def get_process_identity(self, process_id):
        """
        Returns the user and group ID used to spawn a process object, as passed to
        :func:`SpawnProcess`, and the resulting error code.
        """
        return GetProcessIdentity(*self.ipcon.send_request(self, BrickRED.FUNCTION_GET_PROCESS_IDENTITY, (process_id,), 'H', 'B I I'))

    def get_process_stdio(self, process_id):
        """
        Returns the stdin, stdout and stderr files used to spawn a process object, as
        passed to :func:`SpawnProcess`, and the resulting error code.
        """
        return GetProcessStdio(*self.ipcon.send_request(self, BrickRED.FUNCTION_GET_PROCESS_STDIO, (process_id,), 'H', 'B H H H'))

    def get_process_state(self, process_id):
        """
        Returns the current state and exit code of a process object, and the resulting
        error code.
        
        Possible process states are:
        
        * Unknown = 0
        * Running = 1
        * Error = 2
        * Exited = 3
        * Killed = 4
        * Stopped = 5
        
        The exit code is only valid if the state is *Error*, *Exited*, *Killed* or
        *Stopped* and has different meanings depending on the state:
        
        * Error: error code (see below)
        * Exited: exit status of the process
        * Killed: UNIX signal number used to kill the process
        * Stopped: UNIX signal number used to stop the process
        
        Possible exit/error codes in *Error* state are:
        
        * InternalError = 125
        * CannotExecute = 126
        * DoesNotExist = 127
        """
        return GetProcessState(*self.ipcon.send_request(self, BrickRED.FUNCTION_GET_PROCESS_STATE, (process_id,), 'H', 'B B B'))

    def define_program(self, identifier_string_id):
        """
        
        """
        return DefineProgram(*self.ipcon.send_request(self, BrickRED.FUNCTION_DEFINE_PROGRAM, (identifier_string_id,), 'H', 'B H'))

    def undefine_program(self, program_id):
        """
        
        """
        return self.ipcon.send_request(self, BrickRED.FUNCTION_UNDEFINE_PROGRAM, (program_id,), 'H', 'B')

    def get_program_identifier(self, program_id):
        """
        
        """
        return GetProgramIdentifier(*self.ipcon.send_request(self, BrickRED.FUNCTION_GET_PROGRAM_IDENTIFIER, (program_id,), 'H', 'B H'))

    def get_program_directory(self, program_id):
        """
        
        """
        return GetProgramDirectory(*self.ipcon.send_request(self, BrickRED.FUNCTION_GET_PROGRAM_DIRECTORY, (program_id,), 'H', 'B H'))

    def set_program_command(self, program_id, executable_string_id, arguments_list_id, environment_list_id):
        """
        
        """
        return self.ipcon.send_request(self, BrickRED.FUNCTION_SET_PROGRAM_COMMAND, (program_id, executable_string_id, arguments_list_id, environment_list_id), 'H H H H', 'B')

    def get_program_command(self, program_id):
        """
        
        """
        return GetProgramCommand(*self.ipcon.send_request(self, BrickRED.FUNCTION_GET_PROGRAM_COMMAND, (program_id,), 'H', 'B H H H'))

    def set_program_stdio_redirection(self, program_id, stdin_redirection, stdin_file_name_string_id, stdout_redirection, stdout_file_name_string_id, stderr_redirection, stderr_file_name_string_id):
        """
        
        """
        return self.ipcon.send_request(self, BrickRED.FUNCTION_SET_PROGRAM_STDIO_REDIRECTION, (program_id, stdin_redirection, stdin_file_name_string_id, stdout_redirection, stdout_file_name_string_id, stderr_redirection, stderr_file_name_string_id), 'H B H B H B H', 'B')

    def get_program_stdio_redirection(self, program_id):
        """
        
        """
        return GetProgramStdioRedirection(*self.ipcon.send_request(self, BrickRED.FUNCTION_GET_PROGRAM_STDIO_REDIRECTION, (program_id,), 'H', 'B B H B H B H'))

    def set_program_schedule(self, program_id, start_condition, start_timestamp, start_delay, repeat_mode, repeat_interval, repeat_second_mask, repeat_minute_mask, repeat_hour_mask, repeat_day_mask, repeat_month_mask, repeat_weekday_mask):
        """
        FIXME: week starts on monday
        """
        return self.ipcon.send_request(self, BrickRED.FUNCTION_SET_PROGRAM_SCHEDULE, (program_id, start_condition, start_timestamp, start_delay, repeat_mode, repeat_interval, repeat_second_mask, repeat_minute_mask, repeat_hour_mask, repeat_day_mask, repeat_month_mask, repeat_weekday_mask), 'H B Q I B I Q Q I I H B', 'B')

    def get_program_schedule(self, program_id):
        """
        FIXME: week starts on monday
        """
        return GetProgramSchedule(*self.ipcon.send_request(self, BrickRED.FUNCTION_GET_PROGRAM_SCHEDULE, (program_id,), 'H', 'B B Q I B I Q Q I I H B'))

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
