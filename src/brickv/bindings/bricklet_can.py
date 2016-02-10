# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2016-02-10.      #
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
GetIdentity = namedtuple('Identity', ['uid', 'connected_uid', 'position', 'hardware_version', 'firmware_version', 'device_identifier'])

class BrickletCAN(Device):
    """
    Communicates with CAN devices
    """

    DEVICE_IDENTIFIER = 270
    DEVICE_DISPLAY_NAME = 'CAN Bricklet'

    CALLBACK_ERROR = 5

    FUNCTION_WRITE_FRAME = 1
    FUNCTION_READ_FRAME = 2
    FUNCTION_SET_CONFIGURATION = 3
    FUNCTION_GET_CONFIGURATION = 4
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
    ERROR_READ_REGISTER_FULL = 1
    ERROR_READ_BUFFER_FULL = 2

    def __init__(self, uid, ipcon):
        """
        Creates an object with the unique device ID *uid* and adds it to
        the IP Connection *ipcon*.
        """
        Device.__init__(self, uid, ipcon)

        self.api_version = (2, 0, 0)

        self.response_expected[BrickletCAN.FUNCTION_WRITE_FRAME] = BrickletCAN.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletCAN.FUNCTION_READ_FRAME] = BrickletCAN.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletCAN.FUNCTION_SET_CONFIGURATION] = BrickletCAN.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletCAN.FUNCTION_GET_CONFIGURATION] = BrickletCAN.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletCAN.CALLBACK_ERROR] = BrickletCAN.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletCAN.FUNCTION_GET_IDENTITY] = BrickletCAN.RESPONSE_EXPECTED_ALWAYS_TRUE

        self.callback_formats[BrickletCAN.CALLBACK_ERROR] = 'I'

    def write_frame(self, frame_type, identifier, data, length):
        """
        
        """
        return self.ipcon.send_request(self, BrickletCAN.FUNCTION_WRITE_FRAME, (frame_type, identifier, data, length), 'B I 8B B', '?')

    def read_frame(self):
        """
        
        """
        return ReadFrame(*self.ipcon.send_request(self, BrickletCAN.FUNCTION_READ_FRAME, (), '', '? B I 8B B'))

    def set_configuration(self, baud_rate, transceiver, write_timeout):
        """
        
        """
        self.ipcon.send_request(self, BrickletCAN.FUNCTION_SET_CONFIGURATION, (baud_rate, transceiver, write_timeout), 'B B i', '')

    def get_configuration(self):
        """
        Returns the configuration as set by :func:`SetConfiguration`.
        """
        return GetConfiguration(*self.ipcon.send_request(self, BrickletCAN.FUNCTION_GET_CONFIGURATION, (), '', 'B B i'))

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
