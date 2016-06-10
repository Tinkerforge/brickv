# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2016-06-10.      #
#                                                           #
# Python Bindings Version 2.1.9                             #
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

GetRGBValue = namedtuple('RGBValue', ['r', 'g', 'b'])
GetIdentity = namedtuple('Identity', ['uid', 'connected_uid', 'position', 'hardware_version', 'firmware_version', 'device_identifier'])

class BrickletRGBLED(Device):
    """
    Controls one RGB LED
    """

    DEVICE_IDENTIFIER = 271
    DEVICE_DISPLAY_NAME = 'RGB LED Bricklet'


    FUNCTION_SET_RGB_VALUE = 1
    FUNCTION_GET_RGB_VALUE = 2
    FUNCTION_GET_IDENTITY = 255


    def __init__(self, uid, ipcon):
        """
        Creates an object with the unique device ID *uid* and adds it to
        the IP Connection *ipcon*.
        """
        Device.__init__(self, uid, ipcon)

        self.api_version = (2, 0, 0)

        self.response_expected[BrickletRGBLED.FUNCTION_SET_RGB_VALUE] = BrickletRGBLED.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletRGBLED.FUNCTION_GET_RGB_VALUE] = BrickletRGBLED.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletRGBLED.FUNCTION_GET_IDENTITY] = BrickletRGBLED.RESPONSE_EXPECTED_ALWAYS_TRUE


    def set_rgb_value(self, r, g, b):
        """
        TODO
        """
        self.ipcon.send_request(self, BrickletRGBLED.FUNCTION_SET_RGB_VALUE, (r, g, b), 'B B B', '')

    def get_rgb_value(self):
        """
        TODO
        """
        return GetRGBValue(*self.ipcon.send_request(self, BrickletRGBLED.FUNCTION_GET_RGB_VALUE, (), '', 'B B B'))

    def get_identity(self):
        """
        Returns the UID, the UID where the Bricklet is connected to, 
        the position, the hardware and firmware version as well as the
        device identifier.
        
        The position can be 'a', 'b', 'c' or 'd'.
        
        The device identifier numbers can be found :ref:`here <device_identifier>`.
        |device_identifier_constant|
        """
        return GetIdentity(*self.ipcon.send_request(self, BrickletRGBLED.FUNCTION_GET_IDENTITY, (), '', '8s 8s c 3B 3B H'))

RGBLED = BrickletRGBLED # for backward compatibility
