# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2015-04-10.      #
#                                                           #
# Bindings Version 2.1.4                                    #
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

Read = namedtuple('Read', ['message', 'length'])
GetConfiguration = namedtuple('Configuration', ['baudrate', 'parity', 'stopbits', 'wordlength', 'hardware_flowcontrol', 'software_flowcontrol'])
GetIdentity = namedtuple('Identity', ['uid', 'connected_uid', 'position', 'hardware_version', 'firmware_version', 'device_identifier'])

class BrickletRS232(Device):
    """
    Device for RS232 communication
    """

    DEVICE_IDENTIFIER = 254
    DEVICE_DISPLAY_NAME = 'RS232 Bricklet'

    CALLBACK_READ_CALLBACK = 8

    FUNCTION_WRITE = 1
    FUNCTION_READ = 2
    FUNCTION_ENABLE_CALLBACK = 3
    FUNCTION_DISABLE_CALLBACK = 4
    FUNCTION_IS_CALLBACK_ENABLED = 5
    FUNCTION_SET_CONFIGURATION = 6
    FUNCTION_GET_CONFIGURATION = 7
    FUNCTION_GET_IDENTITY = 255

    BAUDRATE_300 = 0
    BAUDRATE_600 = 1
    BAUDRATE_1200 = 2
    BAUDRATE_2400 = 3
    BAUDRATE_4800 = 4
    BAUDRATE_9600 = 5
    BAUDRATE_14400 = 6
    BAUDRATE_28800 = 7
    BAUDRATE_38400 = 8
    BAUDRATE_57600 = 9
    BAUDRATE_115200 = 10
    BAUDRATE_230400 = 11
    PARITY_NONE = 0
    PARITY_ODD = 1
    PARITY_EVEN = 2
    PARITY_FORCED_PARITY_1 = 3
    PARITY_FORCED_PARITY_0 = 4
    STOPBITS_1 = 1
    STOPBITS_2 = 2
    WORDLENGTH_5 = 5
    WORDLENGTH_6 = 6
    WORDLENGTH_7 = 7
    WORDLENGTH_8 = 8
    HARDWARE_FLOWCONTROL_OFF = 0
    HARDWARE_FLOWCONTROL_ON = 1
    SOFTWARE_FLOWCONTROL_OFF = 0
    SOFTWARE_FLOWCONTROL_ON = 1

    def __init__(self, uid, ipcon):
        """
        Creates an object with the unique device ID *uid* and adds it to
        the IP Connection *ipcon*.
        """
        Device.__init__(self, uid, ipcon)

        self.api_version = (2, 0, 0)

        self.response_expected[BrickletRS232.FUNCTION_WRITE] = BrickletRS232.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletRS232.FUNCTION_READ] = BrickletRS232.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletRS232.FUNCTION_ENABLE_CALLBACK] = BrickletRS232.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletRS232.FUNCTION_DISABLE_CALLBACK] = BrickletRS232.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletRS232.FUNCTION_IS_CALLBACK_ENABLED] = BrickletRS232.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletRS232.FUNCTION_SET_CONFIGURATION] = BrickletRS232.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletRS232.FUNCTION_GET_CONFIGURATION] = BrickletRS232.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletRS232.CALLBACK_READ_CALLBACK] = BrickletRS232.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletRS232.FUNCTION_GET_IDENTITY] = BrickletRS232.RESPONSE_EXPECTED_ALWAYS_TRUE

        self.callback_formats[BrickletRS232.CALLBACK_READ_CALLBACK] = '60c B'

    def write(self, message, length):
        """
        TODO
        """
        self.ipcon.send_request(self, BrickletRS232.FUNCTION_WRITE, (message, length), '60c B', '')

    def read(self):
        """
        TODO
        """
        return Read(*self.ipcon.send_request(self, BrickletRS232.FUNCTION_READ, (), '', '60c B'))

    def enable_callback(self):
        """
        TODO
        """
        self.ipcon.send_request(self, BrickletRS232.FUNCTION_ENABLE_CALLBACK, (), '', '')

    def disable_callback(self):
        """
        TODO
        """
        self.ipcon.send_request(self, BrickletRS232.FUNCTION_DISABLE_CALLBACK, (), '', '')

    def is_callback_enabled(self):
        """
        TODO
        """
        return self.ipcon.send_request(self, BrickletRS232.FUNCTION_IS_CALLBACK_ENABLED, (), '', '?')

    def set_configuration(self, baudrate, parity, stopbits, wordlength, hardware_flowcontrol, software_flowcontrol):
        """
        TODO
        """
        self.ipcon.send_request(self, BrickletRS232.FUNCTION_SET_CONFIGURATION, (baudrate, parity, stopbits, wordlength, hardware_flowcontrol, software_flowcontrol), 'B B B B B B', '')

    def get_configuration(self):
        """
        TODO
        """
        return GetConfiguration(*self.ipcon.send_request(self, BrickletRS232.FUNCTION_GET_CONFIGURATION, (), '', 'B B B B B B'))

    def get_identity(self):
        """
        Returns the UID, the UID where the Bricklet is connected to, 
        the position, the hardware and firmware version as well as the
        device identifier.
        
        The position can be 'a', 'b', 'c' or 'd'.
        
        The device identifier numbers can be found :ref:`here <device_identifier>`.
        |device_identifier_constant|
        """
        return GetIdentity(*self.ipcon.send_request(self, BrickletRS232.FUNCTION_GET_IDENTITY, (), '', '8s 8s c 3B 3B H'))

    def register_callback(self, id, callback):
        """
        Registers a callback with ID *id* to the function *callback*.
        """
        self.registered_callbacks[id] = callback

RS232 = BrickletRS232 # for backward compatibility
