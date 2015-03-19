# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2015-03-18.      #
#                                                           #
# Bindings Version 2.1.4                                    #
#                                                           #
# If you have a bugfix for this file and want to commit it, #
# please fix the bug in the generator. You can find a link  #
# to the generator git on tinkerforge.com                   #
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
GetIdentity = namedtuple('Identity', ['uid', 'connected_uid', 'position', 'hardware_version', 'firmware_version', 'device_identifier'])

class BrickletRS232(Device):
    """
    Device for RS232 communication
    """

    DEVICE_IDENTIFIER = 254
    DEVICE_DISPLAY_NAME = 'RS232 Bricklet'


    FUNCTION_WRITE = 1
    FUNCTION_READ = 2
    FUNCTION_ENABLE_CALLBACK = 3
    FUNCTION_IS_CALLBACK_ENABLED = 4
    FUNCTION_SET_CONFIGURATION = 5
    FUNCTION_GET_CONFIGURATION = 6
    FUNCTION_GET_IDENTITY = 255


    def __init__(self, uid, ipcon):
        """
        Creates an object with the unique device ID *uid* and adds it to
        the IP Connection *ipcon*.
        """
        Device.__init__(self, uid, ipcon)

        self.api_version = (2, 0, 0)

        self.response_expected[BrickletRS232.FUNCTION_WRITE] = BrickletRS232.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletRS232.FUNCTION_READ] = BrickletRS232.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletRS232.FUNCTION_ENABLE_CALLBACK] = BrickletRS232.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletRS232.FUNCTION_IS_CALLBACK_ENABLED] = BrickletRS232.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletRS232.FUNCTION_SET_CONFIGURATION] = BrickletRS232.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletRS232.FUNCTION_GET_CONFIGURATION] = BrickletRS232.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletRS232.FUNCTION_GET_IDENTITY] = BrickletRS232.RESPONSE_EXPECTED_ALWAYS_TRUE


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

    def enable_callback(self, enable):
        """
        TODO
        """
        self.ipcon.send_request(self, BrickletRS232.FUNCTION_ENABLE_CALLBACK, (enable,), '?', '')

    def is_callback_enabled(self):
        """
        TODO
        """
        return self.ipcon.send_request(self, BrickletRS232.FUNCTION_IS_CALLBACK_ENABLED, (), '', '?')

    def set_configuration(self, speed, parity, stopbits):
        """
        TODO
        """
        self.ipcon.send_request(self, BrickletRS232.FUNCTION_SET_CONFIGURATION, (speed, parity, stopbits), 'I c B', '')

    def get_configuration(self, speed, parity, stopbits):
        """
        TODO
        """
        self.ipcon.send_request(self, BrickletRS232.FUNCTION_GET_CONFIGURATION, (speed, parity, stopbits), 'I c B', '')

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

RS232 = BrickletRS232 # for backward compatibility
