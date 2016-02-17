# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2016-02-16.      #
#                                                           #
# Python Bindings Version 2.1.8                             #
#                                                           #
# If you have a bugfix for this file and want to commit it, #
# please fix the bug in the generator. You can find a link  #
# to the generators git repository on tinkerforge.com       #
#############################################################

#### __DEVICE_IS_NOT_RELEASED__ ####

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

ReadFrame = namedtuple('ReadFrame', ['success', 'frame_type', 'identifier', 'data', 'length'])
GetConfiguration = namedtuple('Configuration', ['baud_rate', 'transceiver_mode', 'write_timeout'])
GetReadFilter = namedtuple('ReadFilter', ['mode', 'mask', 'filter1', 'filter2'])
GetErrorLog = namedtuple('ErrorLog', ['transceiver_disabled', 'write_error_level', 'read_error_level', 'write_timeout_count', 'read_register_overflow_count', 'read_buffer_overflow_count'])
GetIdentity = namedtuple('Identity', ['uid', 'connected_uid', 'position', 'hardware_version', 'firmware_version', 'device_identifier'])

class BrickletCAN(Device):
    """
    Communicates with CAN devices
    """

    DEVICE_IDENTIFIER = 270
    DEVICE_DISPLAY_NAME = 'CAN Bricklet'

    CALLBACK_FRAME_READ = 11

    FUNCTION_WRITE_FRAME = 1
    FUNCTION_READ_FRAME = 2
    FUNCTION_ENABLE_FRAME_READ_CALLBACK = 3
    FUNCTION_DISABLE_FRAME_READ_CALLBACK = 4
    FUNCTION_IS_FRAME_READ_CALLBACK_ENABLED = 5
    FUNCTION_SET_CONFIGURATION = 6
    FUNCTION_GET_CONFIGURATION = 7
    FUNCTION_SET_READ_FILTER = 8
    FUNCTION_GET_READ_FILTER = 9
    FUNCTION_GET_ERROR_LOG = 10
    FUNCTION_GET_IDENTITY = 255

    FRAME_TYPE_STANDARD_DATA = 0
    FRAME_TYPE_STANDARD_REMOTE = 1
    FRAME_TYPE_EXTENDED_DATA = 2
    FRAME_TYPE_EXTENDED_REMOTE = 3
    BAUD_RATE_10000 = 0
    BAUD_RATE_20000 = 1
    BAUD_RATE_50000 = 2
    BAUD_RATE_125000 = 3
    BAUD_RATE_250000 = 4
    BAUD_RATE_500000 = 5
    BAUD_RATE_800000 = 6
    BAUD_RATE_1000000 = 7
    TRANSCEIVER_MODE_NORMAL = 0
    TRANSCEIVER_MODE_LOOPBACK = 1
    TRANSCEIVER_MODE_READ_ONLY = 2
    FILTER_MODE_DISABLED = 0
    FILTER_MODE_ACCEPT_ALL = 1
    FILTER_MODE_MATCH_STANDARD = 2
    FILTER_MODE_MATCH_STANDARD_AND_DATA = 3
    FILTER_MODE_MATCH_EXTENDED = 4

    def __init__(self, uid, ipcon):
        """
        Creates an object with the unique device ID *uid* and adds it to
        the IP Connection *ipcon*.
        """
        Device.__init__(self, uid, ipcon)

        self.api_version = (2, 0, 0)

        self.response_expected[BrickletCAN.FUNCTION_WRITE_FRAME] = BrickletCAN.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletCAN.FUNCTION_READ_FRAME] = BrickletCAN.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletCAN.FUNCTION_ENABLE_FRAME_READ_CALLBACK] = BrickletCAN.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletCAN.FUNCTION_DISABLE_FRAME_READ_CALLBACK] = BrickletCAN.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletCAN.FUNCTION_IS_FRAME_READ_CALLBACK_ENABLED] = BrickletCAN.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletCAN.FUNCTION_SET_CONFIGURATION] = BrickletCAN.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletCAN.FUNCTION_GET_CONFIGURATION] = BrickletCAN.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletCAN.FUNCTION_SET_READ_FILTER] = BrickletCAN.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletCAN.FUNCTION_GET_READ_FILTER] = BrickletCAN.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletCAN.FUNCTION_GET_ERROR_LOG] = BrickletCAN.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletCAN.CALLBACK_FRAME_READ] = BrickletCAN.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletCAN.FUNCTION_GET_IDENTITY] = BrickletCAN.RESPONSE_EXPECTED_ALWAYS_TRUE

        self.callback_formats[BrickletCAN.CALLBACK_FRAME_READ] = 'B I 8B B'

    def write_frame(self, frame_type, identifier, data, length):
        """
        
        """
        return self.ipcon.send_request(self, BrickletCAN.FUNCTION_WRITE_FRAME, (frame_type, identifier, data, length), 'B I 8B B', '?')

    def read_frame(self):
        """
        
        """
        return ReadFrame(*self.ipcon.send_request(self, BrickletCAN.FUNCTION_READ_FRAME, (), '', '? B I 8B B'))

    def enable_frame_read_callback(self):
        """
        Enables the :func:`FrameRead` callback.
        
        By default the callback is disabled.
        """
        self.ipcon.send_request(self, BrickletCAN.FUNCTION_ENABLE_FRAME_READ_CALLBACK, (), '', '')

    def disable_frame_read_callback(self):
        """
        Disables the :func:`FrameRead` callback.
        
        By default the callback is disabled.
        """
        self.ipcon.send_request(self, BrickletCAN.FUNCTION_DISABLE_FRAME_READ_CALLBACK, (), '', '')

    def is_frame_read_callback_enabled(self):
        """
        Returns *true* if the :func:`FrameRead` callback is enabled, *false* otherwise.
        """
        return self.ipcon.send_request(self, BrickletCAN.FUNCTION_IS_FRAME_READ_CALLBACK_ENABLED, (), '', '?')

    def set_configuration(self, baud_rate, transceiver_mode, write_timeout):
        """
        
        """
        self.ipcon.send_request(self, BrickletCAN.FUNCTION_SET_CONFIGURATION, (baud_rate, transceiver_mode, write_timeout), 'B B i', '')

    def get_configuration(self):
        """
        Returns the configuration as set by :func:`SetConfiguration`.
        """
        return GetConfiguration(*self.ipcon.send_request(self, BrickletCAN.FUNCTION_GET_CONFIGURATION, (), '', 'B B i'))

    def set_read_filter(self, mode, mask, filter1, filter2):
        """
        
        """
        self.ipcon.send_request(self, BrickletCAN.FUNCTION_SET_READ_FILTER, (mode, mask, filter1, filter2), 'B I I I', '')

    def get_read_filter(self):
        """
        Returns the read filter as set by :func:`SetReadFilter`.
        """
        return GetReadFilter(*self.ipcon.send_request(self, BrickletCAN.FUNCTION_GET_READ_FILTER, (), '', 'B I I I'))

    def get_error_log(self):
        """
        FIXME: in what modes are which values available and how are they reset if they are?
        """
        return GetErrorLog(*self.ipcon.send_request(self, BrickletCAN.FUNCTION_GET_ERROR_LOG, (), '', '? B B I I I'))

    def get_identity(self):
        """
        Returns the UID, the UID where the Bricklet is connected to, 
        the position, the hardware and firmware version as well as the
        device identifier.
        
        The position can be 'a', 'b', 'c' or 'd'.
        
        The device identifier numbers can be found :ref:`here <device_identifier>`.
        |device_identifier_constant|
        """
        return GetIdentity(*self.ipcon.send_request(self, BrickletCAN.FUNCTION_GET_IDENTITY, (), '', '8s 8s c 3B 3B H'))

    def register_callback(self, id, callback):
        """
        Registers a callback with ID *id* to the function *callback*.
        """
        self.registered_callbacks[id] = callback

CAN = BrickletCAN # for backward compatibility
