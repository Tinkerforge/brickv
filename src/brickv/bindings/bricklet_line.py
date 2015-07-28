# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2015-07-28.      #
#                                                           #
# Bindings Version 2.1.5                                    #
#                                                           #
# If you have a bugfix for this file and want to commit it, #
# please fix the bug in the generator. You can find a link  #
# to the generators git repository on tinkerforge.com       #
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

GetReflectivityCallbackThreshold = namedtuple('ReflectivityCallbackThreshold', ['option', 'min', 'max'])
GetIdentity = namedtuple('Identity', ['uid', 'connected_uid', 'position', 'hardware_version', 'firmware_version', 'device_identifier'])

class BrickletLine(Device):
    """
    Measures reflectivity of a surface
    """

    DEVICE_IDENTIFIER = 241
    DEVICE_DISPLAY_NAME = 'Line Bricklet'

    CALLBACK_REFLECTIVITY = 8
    CALLBACK_REFLECTIVITY_REACHED = 9

    FUNCTION_GET_REFLECTIVITY = 1
    FUNCTION_SET_REFLECTIVITY_CALLBACK_PERIOD = 2
    FUNCTION_GET_REFLECTIVITY_CALLBACK_PERIOD = 3
    FUNCTION_SET_REFLECTIVITY_CALLBACK_THRESHOLD = 4
    FUNCTION_GET_REFLECTIVITY_CALLBACK_THRESHOLD = 5
    FUNCTION_SET_DEBOUNCE_PERIOD = 6
    FUNCTION_GET_DEBOUNCE_PERIOD = 7
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

        self.response_expected[BrickletLine.FUNCTION_GET_REFLECTIVITY] = BrickletLine.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletLine.FUNCTION_SET_REFLECTIVITY_CALLBACK_PERIOD] = BrickletLine.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletLine.FUNCTION_GET_REFLECTIVITY_CALLBACK_PERIOD] = BrickletLine.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletLine.FUNCTION_SET_REFLECTIVITY_CALLBACK_THRESHOLD] = BrickletLine.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletLine.FUNCTION_GET_REFLECTIVITY_CALLBACK_THRESHOLD] = BrickletLine.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletLine.FUNCTION_SET_DEBOUNCE_PERIOD] = BrickletLine.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletLine.FUNCTION_GET_DEBOUNCE_PERIOD] = BrickletLine.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletLine.CALLBACK_REFLECTIVITY] = BrickletLine.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletLine.CALLBACK_REFLECTIVITY_REACHED] = BrickletLine.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletLine.FUNCTION_GET_IDENTITY] = BrickletLine.RESPONSE_EXPECTED_ALWAYS_TRUE

        self.callback_formats[BrickletLine.CALLBACK_REFLECTIVITY] = 'H'
        self.callback_formats[BrickletLine.CALLBACK_REFLECTIVITY_REACHED] = 'H'

    def get_reflectivity(self):
        """
        Returns the currently measured reflectivity. The reflectivity is
        a value between 0 (not reflective) and 4095 (very reflective).
        
        Usually black has a low reflectivity while white has a high
        reflectivity.
        
        If you want to get the reflectivity periodically, it is recommended 
        to use the callback :func:`Reflectivity` and set the period with 
        :func:`SetReflectivityCallbackPeriod`.
        """
        return self.ipcon.send_request(self, BrickletLine.FUNCTION_GET_REFLECTIVITY, (), '', 'H')

    def set_reflectivity_callback_period(self, period):
        """
        Sets the period in ms with which the :func:`Reflectivity` callback is triggered
        periodically. A value of 0 turns the callback off.
        
        :func:`Reflectivity` is only triggered if the reflectivity has changed since the
        last triggering.
        
        The default value is 0.
        """
        self.ipcon.send_request(self, BrickletLine.FUNCTION_SET_REFLECTIVITY_CALLBACK_PERIOD, (period,), 'I', '')

    def get_reflectivity_callback_period(self):
        """
        Returns the period as set by :func:`SetReflectivityCallbackPeriod`.
        """
        return self.ipcon.send_request(self, BrickletLine.FUNCTION_GET_REFLECTIVITY_CALLBACK_PERIOD, (), '', 'I')

    def set_reflectivity_callback_threshold(self, option, min, max):
        """
        Sets the thresholds for the :func:`ReflectivityReached` callback. 
        
        The following options are possible:
        
        .. csv-table::
         :header: "Option", "Description"
         :widths: 10, 100
        
         "'x'",    "Callback is turned off"
         "'o'",    "Callback is triggered when the reflectivity is *outside* the min and max values"
         "'i'",    "Callback is triggered when the reflectivity is *inside* the min and max values"
         "'<'",    "Callback is triggered when the reflectivity is smaller than the min value (max is ignored)"
         "'>'",    "Callback is triggered when the reflectivity is greater than the min value (max is ignored)"
        
        The default value is ('x', 0, 0).
        """
        self.ipcon.send_request(self, BrickletLine.FUNCTION_SET_REFLECTIVITY_CALLBACK_THRESHOLD, (option, min, max), 'c H H', '')

    def get_reflectivity_callback_threshold(self):
        """
        Returns the threshold as set by :func:`SetReflectivityCallbackThreshold`.
        """
        return GetReflectivityCallbackThreshold(*self.ipcon.send_request(self, BrickletLine.FUNCTION_GET_REFLECTIVITY_CALLBACK_THRESHOLD, (), '', 'c H H'))

    def set_debounce_period(self, debounce):
        """
        Sets the period in ms with which the threshold callback
        
        * :func:`ReflectivityReached`
        
        is triggered, if the threshold
        
        * :func:`SetReflectivityCallbackThreshold`
        
        keeps being reached.
        
        The default value is 100.
        """
        self.ipcon.send_request(self, BrickletLine.FUNCTION_SET_DEBOUNCE_PERIOD, (debounce,), 'I', '')

    def get_debounce_period(self):
        """
        Returns the debounce period as set by :func:`SetDebouncePeriod`.
        """
        return self.ipcon.send_request(self, BrickletLine.FUNCTION_GET_DEBOUNCE_PERIOD, (), '', 'I')

    def get_identity(self):
        """
        Returns the UID, the UID where the Bricklet is connected to, 
        the position, the hardware and firmware version as well as the
        device identifier.
        
        The position can be 'a', 'b', 'c' or 'd'.
        
        The device identifier numbers can be found :ref:`here <device_identifier>`.
        |device_identifier_constant|
        """
        return GetIdentity(*self.ipcon.send_request(self, BrickletLine.FUNCTION_GET_IDENTITY, (), '', '8s 8s c 3B 3B H'))

    def register_callback(self, id, callback):
        """
        Registers a callback with ID *id* to the function *callback*.
        """
        self.registered_callbacks[id] = callback

Line = BrickletLine # for backward compatibility
