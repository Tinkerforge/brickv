# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2015-08-25.      #
#                                                           #
# Bindings Version 2.1.5                                    #
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

GetUVIndexCallbackThreshold = namedtuple('UVIndexCallbackThreshold', ['option', 'min', 'max'])
GetIRValueCallbackThreshold = namedtuple('IRValueCallbackThreshold', ['option', 'min', 'max'])
GetIlluminanceCallbackThreshold = namedtuple('IlluminanceCallbackThreshold', ['option', 'min', 'max'])
GetIdentity = namedtuple('Identity', ['uid', 'connected_uid', 'position', 'hardware_version', 'firmware_version', 'device_identifier'])

class BrickletUVLight(Device):
    """
    Measures UV, IR and ambient light
    """

    DEVICE_IDENTIFIER = 265
    DEVICE_DISPLAY_NAME = 'UV Light Bricklet'

    CALLBACK_UV_INDEX = 18
    CALLBACK_IR_VALUE = 19
    CALLBACK_ILLUMINANCE = 20
    CALLBACK_UV_INDEX_REACHED = 21
    CALLBACK_IR_VALUE_REACHED = 22
    CALLBACK_ILLUMINANCE_REACHED = 23

    FUNCTION_GET_UV_INDEX = 1
    FUNCTION_GET_IR_VALUE = 2
    FUNCTION_GET_ILLUMINANCE = 3
    FUNCTION_SET_UV_INDEX_CALLBACK_PERIOD = 4
    FUNCTION_GET_UV_INDEX_CALLBACK_PERIOD = 5
    FUNCTION_SET_IR_VALUE_CALLBACK_PERIOD = 6
    FUNCTION_GET_IR_VALUE_CALLBACK_PERIOD = 7
    FUNCTION_SET_ILLUMINANCE_CALLBACK_PERIOD = 8
    FUNCTION_GET_ILLUMINANCE_CALLBACK_PERIOD = 9
    FUNCTION_SET_UV_INDEX_CALLBACK_THRESHOLD = 10
    FUNCTION_GET_UV_INDEX_CALLBACK_THRESHOLD = 11
    FUNCTION_SET_IR_VALUE_CALLBACK_THRESHOLD = 12
    FUNCTION_GET_IR_VALUE_CALLBACK_THRESHOLD = 13
    FUNCTION_SET_ILLUMINANCE_CALLBACK_THRESHOLD = 14
    FUNCTION_GET_ILLUMINANCE_CALLBACK_THRESHOLD = 15
    FUNCTION_SET_DEBOUNCE_PERIOD = 16
    FUNCTION_GET_DEBOUNCE_PERIOD = 17
    FUNCTION_GET_IDENTITY = 255

    THRESHOLD_OPTION_OFF = 'x'
    THRESHOLD_OPTION_OUTSIDE = 'o'
    THRESHOLD_OPTION_INSIDE = 'i'
    THRESHOLD_OPTION_SMALLER = '<'
    THRESHOLD_OPTION_GREATER = '>'

    def __init__(self, uid, ipcon):
        """
        Creates an object with the unique device ID *uid* and adds it to
        the IP Connection *ipcon*.
        """
        Device.__init__(self, uid, ipcon)

        self.api_version = (2, 0, 0)

        self.response_expected[BrickletUVLight.FUNCTION_GET_UV_INDEX] = BrickletUVLight.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletUVLight.FUNCTION_GET_IR_VALUE] = BrickletUVLight.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletUVLight.FUNCTION_GET_ILLUMINANCE] = BrickletUVLight.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletUVLight.FUNCTION_SET_UV_INDEX_CALLBACK_PERIOD] = BrickletUVLight.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletUVLight.FUNCTION_GET_UV_INDEX_CALLBACK_PERIOD] = BrickletUVLight.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletUVLight.FUNCTION_SET_IR_VALUE_CALLBACK_PERIOD] = BrickletUVLight.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletUVLight.FUNCTION_GET_IR_VALUE_CALLBACK_PERIOD] = BrickletUVLight.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletUVLight.FUNCTION_SET_ILLUMINANCE_CALLBACK_PERIOD] = BrickletUVLight.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletUVLight.FUNCTION_GET_ILLUMINANCE_CALLBACK_PERIOD] = BrickletUVLight.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletUVLight.FUNCTION_SET_UV_INDEX_CALLBACK_THRESHOLD] = BrickletUVLight.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletUVLight.FUNCTION_GET_UV_INDEX_CALLBACK_THRESHOLD] = BrickletUVLight.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletUVLight.FUNCTION_SET_IR_VALUE_CALLBACK_THRESHOLD] = BrickletUVLight.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletUVLight.FUNCTION_GET_IR_VALUE_CALLBACK_THRESHOLD] = BrickletUVLight.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletUVLight.FUNCTION_SET_ILLUMINANCE_CALLBACK_THRESHOLD] = BrickletUVLight.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletUVLight.FUNCTION_GET_ILLUMINANCE_CALLBACK_THRESHOLD] = BrickletUVLight.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletUVLight.FUNCTION_SET_DEBOUNCE_PERIOD] = BrickletUVLight.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletUVLight.FUNCTION_GET_DEBOUNCE_PERIOD] = BrickletUVLight.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletUVLight.CALLBACK_UV_INDEX] = BrickletUVLight.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletUVLight.CALLBACK_IR_VALUE] = BrickletUVLight.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletUVLight.CALLBACK_ILLUMINANCE] = BrickletUVLight.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletUVLight.CALLBACK_UV_INDEX_REACHED] = BrickletUVLight.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletUVLight.CALLBACK_IR_VALUE_REACHED] = BrickletUVLight.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletUVLight.CALLBACK_ILLUMINANCE_REACHED] = BrickletUVLight.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletUVLight.FUNCTION_GET_IDENTITY] = BrickletUVLight.RESPONSE_EXPECTED_ALWAYS_TRUE

        self.callback_formats[BrickletUVLight.CALLBACK_UV_INDEX] = 'I'
        self.callback_formats[BrickletUVLight.CALLBACK_IR_VALUE] = 'I'
        self.callback_formats[BrickletUVLight.CALLBACK_ILLUMINANCE] = 'I'
        self.callback_formats[BrickletUVLight.CALLBACK_UV_INDEX_REACHED] = 'I'
        self.callback_formats[BrickletUVLight.CALLBACK_IR_VALUE_REACHED] = 'I'
        self.callback_formats[BrickletUVLight.CALLBACK_ILLUMINANCE_REACHED] = 'I'

    def get_uv_index(self):
        """
        
        """
        return self.ipcon.send_request(self, BrickletUVLight.FUNCTION_GET_UV_INDEX, (), '', 'I')

    def get_ir_value(self):
        """
        
        """
        return self.ipcon.send_request(self, BrickletUVLight.FUNCTION_GET_IR_VALUE, (), '', 'I')

    def get_illuminance(self):
        """
        
        """
        return self.ipcon.send_request(self, BrickletUVLight.FUNCTION_GET_ILLUMINANCE, (), '', 'I')

    def set_uv_index_callback_period(self, period):
        """
        
        """
        self.ipcon.send_request(self, BrickletUVLight.FUNCTION_SET_UV_INDEX_CALLBACK_PERIOD, (period,), 'I', '')

    def get_uv_index_callback_period(self):
        """
        
        """
        return self.ipcon.send_request(self, BrickletUVLight.FUNCTION_GET_UV_INDEX_CALLBACK_PERIOD, (), '', 'I')

    def set_ir_value_callback_period(self, period):
        """
        
        """
        self.ipcon.send_request(self, BrickletUVLight.FUNCTION_SET_IR_VALUE_CALLBACK_PERIOD, (period,), 'I', '')

    def get_ir_value_callback_period(self):
        """
        
        """
        return self.ipcon.send_request(self, BrickletUVLight.FUNCTION_GET_IR_VALUE_CALLBACK_PERIOD, (), '', 'I')

    def set_illuminance_callback_period(self, period):
        """
        
        """
        self.ipcon.send_request(self, BrickletUVLight.FUNCTION_SET_ILLUMINANCE_CALLBACK_PERIOD, (period,), 'I', '')

    def get_illuminance_callback_period(self):
        """
        
        """
        return self.ipcon.send_request(self, BrickletUVLight.FUNCTION_GET_ILLUMINANCE_CALLBACK_PERIOD, (), '', 'I')

    def set_uv_index_callback_threshold(self, option, min, max):
        """
        
        """
        self.ipcon.send_request(self, BrickletUVLight.FUNCTION_SET_UV_INDEX_CALLBACK_THRESHOLD, (option, min, max), 'c I I', '')

    def get_uv_index_callback_threshold(self):
        """
        
        """
        return GetUVIndexCallbackThreshold(*self.ipcon.send_request(self, BrickletUVLight.FUNCTION_GET_UV_INDEX_CALLBACK_THRESHOLD, (), '', 'c I I'))

    def set_ir_value_callback_threshold(self, option, min, max):
        """
        
        """
        self.ipcon.send_request(self, BrickletUVLight.FUNCTION_SET_IR_VALUE_CALLBACK_THRESHOLD, (option, min, max), 'c I I', '')

    def get_ir_value_callback_threshold(self):
        """
        
        """
        return GetIRValueCallbackThreshold(*self.ipcon.send_request(self, BrickletUVLight.FUNCTION_GET_IR_VALUE_CALLBACK_THRESHOLD, (), '', 'c I I'))

    def set_illuminance_callback_threshold(self, option, min, max):
        """
        
        """
        self.ipcon.send_request(self, BrickletUVLight.FUNCTION_SET_ILLUMINANCE_CALLBACK_THRESHOLD, (option, min, max), 'c I I', '')

    def get_illuminance_callback_threshold(self):
        """
        
        """
        return GetIlluminanceCallbackThreshold(*self.ipcon.send_request(self, BrickletUVLight.FUNCTION_GET_ILLUMINANCE_CALLBACK_THRESHOLD, (), '', 'c I I'))

    def set_debounce_period(self, debounce):
        """
        Sets the period in ms with which the threshold callbacks
        
        * :func:`UVLightReached`,
        * :func:`IRValueReached`
        * :func:`IlluminanceReached`
        
        are triggered, if the thresholds
        
        * :func:`SetUVLightCallbackThreshold`,
        * :func:`SetIRValueCallbackThreshold`,
        * :func:`SetIlluminanceCallbackThreshold`,
        
        keep being reached.
        
        The default value is 100.
        """
        self.ipcon.send_request(self, BrickletUVLight.FUNCTION_SET_DEBOUNCE_PERIOD, (debounce,), 'I', '')

    def get_debounce_period(self):
        """
        Returns the debounce period as set by :func:`SetDebouncePeriod`.
        """
        return self.ipcon.send_request(self, BrickletUVLight.FUNCTION_GET_DEBOUNCE_PERIOD, (), '', 'I')

    def get_identity(self):
        """
        Returns the UID, the UID where the Bricklet is connected to, 
        the position, the hardware and firmware version as well as the
        device identifier.
        
        The position can be 'a', 'b', 'c' or 'd'.
        
        The device identifier numbers can be found :ref:`here <device_identifier>`.
        |device_identifier_constant|
        """
        return GetIdentity(*self.ipcon.send_request(self, BrickletUVLight.FUNCTION_GET_IDENTITY, (), '', '8s 8s c 3B 3B H'))

    def register_callback(self, id, callback):
        """
        Registers a callback with ID *id* to the function *callback*.
        """
        self.registered_callbacks[id] = callback

UVLight = BrickletUVLight # for backward compatibility
