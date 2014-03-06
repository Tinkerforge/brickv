# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2014-03-06.      #
#                                                           #
# Bindings Version 2.0.13                                    #
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

GetColor = namedtuple('Color', ['r', 'g', 'b', 'c'])
GetColorCallbackThreshold = namedtuple('ColorCallbackThreshold', ['option', 'min_r', 'max_r', 'min_g', 'max_g', 'min_b', 'max_b', 'min_c', 'max_c'])
GetConfig = namedtuple('Config', ['gain', 'integration_time'])
GetIdentity = namedtuple('Identity', ['uid', 'connected_uid', 'position', 'hardware_version', 'firmware_version', 'device_identifier'])

class BrickletColor(Device):
    """
    Device for measuring color(RGB value) of objects
    """

    DEVICE_IDENTIFIER = 243

    CALLBACK_COLOR = 8
    CALLBACK_COLOR_REACHED = 9

    FUNCTION_GET_COLOR = 1
    FUNCTION_SET_COLOR_CALLBACK_PERIOD = 2
    FUNCTION_GET_COLOR_CALLBACK_PERIOD = 3
    FUNCTION_SET_COLOR_CALLBACK_THRESHOLD = 4
    FUNCTION_GET_COLOR_CALLBACK_THRESHOLD = 5
    FUNCTION_SET_DEBOUNCE_PERIOD = 6
    FUNCTION_GET_DEBOUNCE_PERIOD = 7
    FUNCTION_LIGHT_ON = 10
    FUNCTION_LIGHT_OFF = 11
    FUNCTION_IS_LIGHT_ON = 12
    FUNCTION_SET_CONFIG = 13
    FUNCTION_GET_CONFIG = 14
    FUNCTION_GET_IDENTITY = 255

    THRESHOLD_OPTION_OFF = 'x'
    THRESHOLD_OPTION_OUTSIDE = 'o'
    THRESHOLD_OPTION_INSIDE = 'i'
    THRESHOLD_OPTION_SMALLER = '<'
    THRESHOLD_OPTION_GREATER = '>'
    LIGHT_ON = 0
    LIGHT_OFF = 1
    GAIN_1X = 0
    GAIN_4X = 1
    GAIN_16X = 2
    GAIN_60X = 3
    INTEGRATION_TIME_2MS = 255
    INTEGRATION_TIME_24MS = 246
    INTEGRATION_TIME_101MS = 213
    INTEGRATION_TIME_154MS = 192
    INTEGRATION_TIME_700MS = 0

    def __init__(self, uid, ipcon):
        """
        Creates an object with the unique device ID *uid* and adds it to
        the IP Connection *ipcon*.
        """
        Device.__init__(self, uid, ipcon)

        self.api_version = (2, 0, 0)

        self.response_expected[BrickletColor.FUNCTION_GET_COLOR] = BrickletColor.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletColor.FUNCTION_SET_COLOR_CALLBACK_PERIOD] = BrickletColor.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletColor.FUNCTION_GET_COLOR_CALLBACK_PERIOD] = BrickletColor.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletColor.FUNCTION_SET_COLOR_CALLBACK_THRESHOLD] = BrickletColor.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletColor.FUNCTION_GET_COLOR_CALLBACK_THRESHOLD] = BrickletColor.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletColor.FUNCTION_SET_DEBOUNCE_PERIOD] = BrickletColor.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletColor.FUNCTION_GET_DEBOUNCE_PERIOD] = BrickletColor.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletColor.CALLBACK_COLOR] = BrickletColor.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletColor.CALLBACK_COLOR_REACHED] = BrickletColor.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletColor.FUNCTION_LIGHT_ON] = BrickletColor.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletColor.FUNCTION_LIGHT_OFF] = BrickletColor.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletColor.FUNCTION_IS_LIGHT_ON] = BrickletColor.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletColor.FUNCTION_SET_CONFIG] = BrickletColor.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletColor.FUNCTION_GET_CONFIG] = BrickletColor.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletColor.FUNCTION_GET_IDENTITY] = BrickletColor.RESPONSE_EXPECTED_ALWAYS_TRUE

        self.callback_formats[BrickletColor.CALLBACK_COLOR] = 'H H H H'
        self.callback_formats[BrickletColor.CALLBACK_COLOR_REACHED] = 'H H H H'

    def get_color(self):
        """
        
        """
        return GetColor(*self.ipcon.send_request(self, BrickletColor.FUNCTION_GET_COLOR, (), '', 'H H H H'))

    def set_color_callback_period(self, period):
        """
        
        """
        self.ipcon.send_request(self, BrickletColor.FUNCTION_SET_COLOR_CALLBACK_PERIOD, (period,), 'I', '')

    def get_color_callback_period(self):
        """
        
        """
        return self.ipcon.send_request(self, BrickletColor.FUNCTION_GET_COLOR_CALLBACK_PERIOD, (), '', 'I')

    def set_color_callback_threshold(self, option, min_r, max_r, min_g, max_g, min_b, max_b, min_c, max_c):
        """
        
        """
        self.ipcon.send_request(self, BrickletColor.FUNCTION_SET_COLOR_CALLBACK_THRESHOLD, (option, min_r, max_r, min_g, max_g, min_b, max_b, min_c, max_c), 'c H H H H H H H H', '')

    def get_color_callback_threshold(self):
        """
        
        """
        return GetColorCallbackThreshold(*self.ipcon.send_request(self, BrickletColor.FUNCTION_GET_COLOR_CALLBACK_THRESHOLD, (), '', 'c H H H H H H H H'))

    def set_debounce_period(self, debounce):
        """
        
        """
        self.ipcon.send_request(self, BrickletColor.FUNCTION_SET_DEBOUNCE_PERIOD, (debounce,), 'I', '')

    def get_debounce_period(self):
        """
        
        """
        return self.ipcon.send_request(self, BrickletColor.FUNCTION_GET_DEBOUNCE_PERIOD, (), '', 'I')

    def light_on(self):
        """
        Turns the LED on.
        """
        self.ipcon.send_request(self, BrickletColor.FUNCTION_LIGHT_ON, (), '', '')

    def light_off(self):
        """
        Turns the LED off.
        """
        self.ipcon.send_request(self, BrickletColor.FUNCTION_LIGHT_OFF, (), '', '')

    def is_light_on(self):
        """
        Returns *true* if the backlight is on and *false* otherwise.
        """
        return self.ipcon.send_request(self, BrickletColor.FUNCTION_IS_LIGHT_ON, (), '', 'B')

    def set_config(self, gain, integration_time):
        """
        
        """
        self.ipcon.send_request(self, BrickletColor.FUNCTION_SET_CONFIG, (gain, integration_time), 'B B', '')

    def get_config(self):
        """
        
        """
        return GetConfig(*self.ipcon.send_request(self, BrickletColor.FUNCTION_GET_CONFIG, (), '', 'B B'))

    def get_identity(self):
        """
        Returns the UID, the UID where the Bricklet is connected to, 
        the position, the hardware and firmware version as well as the
        device identifier.
        
        The position can be 'a', 'b', 'c' or 'd'.
        
        The device identifier numbers can be found :ref:`here <device_identifier>`.
        |device_identifier_constant|
        
        .. versionadded:: 2.0.0~(Plugin)
        """
        return GetIdentity(*self.ipcon.send_request(self, BrickletColor.FUNCTION_GET_IDENTITY, (), '', '8s 8s c 3B 3B H'))

    def register_callback(self, id, callback):
        """
        Registers a callback with ID *id* to the function *callback*.
        """
        self.registered_callbacks[id] = callback

Color = BrickletColor # for backward compatibility
