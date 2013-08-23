# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2013-08-23.      #
#                                                           #
# Bindings Version 2.0.9                                    #
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

GetRGBValues = namedtuple('RGBValues', ['r', 'g', 'b'])
GetIdentity = namedtuple('Identity', ['uid', 'connected_uid', 'position', 'hardware_version', 'firmware_version', 'device_identifier'])

class BrickletLEDStrip(Device):
    """
    TODO
    """

    DEVICE_IDENTIFIER = 231

    CALLBACK_FRAME_RENDERED = 6

    FUNCTION_SET_RGB_VALUES = 1
    FUNCTION_GET_RGB_VALUES = 2
    FUNCTION_SET_CONFIG = 3
    FUNCTION_GET_CONFIG = 4
    FUNCTION_GET_SUPPLY_VOLTAGE = 5
    FUNCTION_GET_IDENTITY = 255


    def __init__(self, uid, ipcon):
        """
        Creates an object with the unique device ID *uid* and adds it to
        the IP Connection *ipcon*.
        """
        Device.__init__(self, uid, ipcon)

        self.api_version = (2, 0, 0)

        self.response_expected[BrickletLEDStrip.FUNCTION_SET_RGB_VALUES] = BrickletLEDStrip.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletLEDStrip.FUNCTION_GET_RGB_VALUES] = BrickletLEDStrip.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletLEDStrip.FUNCTION_SET_CONFIG] = BrickletLEDStrip.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletLEDStrip.FUNCTION_GET_CONFIG] = BrickletLEDStrip.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletLEDStrip.FUNCTION_GET_SUPPLY_VOLTAGE] = BrickletLEDStrip.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletLEDStrip.CALLBACK_FRAME_RENDERED] = BrickletLEDStrip.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletLEDStrip.FUNCTION_GET_IDENTITY] = BrickletLEDStrip.RESPONSE_EXPECTED_ALWAYS_TRUE

        self.callback_formats[BrickletLEDStrip.CALLBACK_FRAME_RENDERED] = 'H'

    def set_rgb_values(self, index, length, r, g, b):
        """
        
        """
        self.ipcon.send_request(self, BrickletLEDStrip.FUNCTION_SET_RGB_VALUES, (index, length, r, g, b), 'H B 16B 16B 16B', '')

    def get_rgb_values(self, index, length):
        """
        
        """
        return GetRGBValues(*self.ipcon.send_request(self, BrickletLEDStrip.FUNCTION_GET_RGB_VALUES, (index, length), 'H B', '16B 16B 16B'))

    def set_config(self, frame_duration):
        """
        
        """
        self.ipcon.send_request(self, BrickletLEDStrip.FUNCTION_SET_CONFIG, (frame_duration,), 'H', '')

    def get_config(self):
        """
        
        """
        return self.ipcon.send_request(self, BrickletLEDStrip.FUNCTION_GET_CONFIG, (), '', 'H')

    def get_supply_voltage(self):
        """
        
        """
        return self.ipcon.send_request(self, BrickletLEDStrip.FUNCTION_GET_SUPPLY_VOLTAGE, (), '', 'H')

    def get_identity(self):
        """
        Returns the UID, the UID where the Bricklet is connected to, 
        the position, the hardware and firmware version as well as the
        device identifier.
        
        The position can be 'a', 'b', 'c' or 'd'.
        
        The device identifiers can be found :ref:`here <device_identifier>`.
        
        .. versionadded:: 2.0.0~(Plugin)
        """
        return GetIdentity(*self.ipcon.send_request(self, BrickletLEDStrip.FUNCTION_GET_IDENTITY, (), '', '8s 8s c 3B 3B H'))

    def register_callback(self, id, callback):
        """
        Registers a callback with ID *id* to the function *callback*.
        """
        self.registered_callbacks[id] = callback

LEDStrip = BrickletLEDStrip # for backward compatibility
