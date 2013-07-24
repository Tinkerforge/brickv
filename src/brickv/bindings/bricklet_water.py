# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2013-07-24.      #
#                                                           #
# Bindings Version 2.0.8                                    #
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

GetWaterCallbackThreshold = namedtuple('WaterCallbackThreshold', ['option', 'min', 'max'])
GetIdentity = namedtuple('Identity', ['uid', 'connected_uid', 'position', 'hardware_version', 'firmware_version', 'device_identifier'])

class BrickletWater(Device):
    """
    Device for sensing water amount (rainfall etc)
    """

    DEVICE_IDENTIFIER = 240

    CALLBACK_WATER = 8
    CALLBACK_WATER_REACHED = 9

    FUNCTION_GET_WATER_VALUE = 1
    FUNCTION_SET_WATER_CALLBACK_PERIOD = 2
    FUNCTION_GET_WATER_CALLBACK_PERIOD = 3
    FUNCTION_SET_WATER_CALLBACK_THRESHOLD = 4
    FUNCTION_GET_WATER_CALLBACK_THRESHOLD = 5
    FUNCTION_SET_DEBOUNCE_PERIOD = 6
    FUNCTION_GET_DEBOUNCE_PERIOD = 7
    FUNCTION_SET_MOVING_AVERAGE = 10
    FUNCTION_GET_MOVING_AVERAGE = 11
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

        self.response_expected[BrickletWater.FUNCTION_GET_WATER_VALUE] = BrickletWater.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletWater.FUNCTION_SET_WATER_CALLBACK_PERIOD] = BrickletWater.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletWater.FUNCTION_GET_WATER_CALLBACK_PERIOD] = BrickletWater.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletWater.FUNCTION_SET_WATER_CALLBACK_THRESHOLD] = BrickletWater.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletWater.FUNCTION_GET_WATER_CALLBACK_THRESHOLD] = BrickletWater.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletWater.FUNCTION_SET_DEBOUNCE_PERIOD] = BrickletWater.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletWater.FUNCTION_GET_DEBOUNCE_PERIOD] = BrickletWater.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletWater.CALLBACK_WATER] = BrickletWater.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletWater.CALLBACK_WATER_REACHED] = BrickletWater.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletWater.FUNCTION_SET_MOVING_AVERAGE] = BrickletWater.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletWater.FUNCTION_GET_MOVING_AVERAGE] = BrickletWater.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletWater.FUNCTION_GET_IDENTITY] = BrickletWater.RESPONSE_EXPECTED_ALWAYS_TRUE

        self.callback_formats[BrickletWater.CALLBACK_WATER] = 'H'
        self.callback_formats[BrickletWater.CALLBACK_WATER_REACHED] = 'H'

    def get_water_value(self):
        """
        If you want to get the water amount value periodically, it is recommended 
        to use the callback :func:`Water` and set the period with 
        :func:`SetWaterCallbackPeriod`.
        """
        return self.ipcon.send_request(self, BrickletWater.FUNCTION_GET_WATER_VALUE, (), '', 'H')

    def set_water_callback_period(self, period):
        """
        Sets the period in ms with which the :func:`Water` callback is triggered
        periodically. A value of 0 turns the callback off.
        
        :func:`Water` is only triggered if the water amount value has changed since the
        last triggering.
        
        The default value is 0.
        """
        self.ipcon.send_request(self, BrickletWater.FUNCTION_SET_WATER_CALLBACK_PERIOD, (period,), 'I', '')

    def get_water_callback_period(self):
        """
        Returns the period as set by :func:`SetWaterCallbackPeriod`.
        """
        return self.ipcon.send_request(self, BrickletWater.FUNCTION_GET_WATER_CALLBACK_PERIOD, (), '', 'I')

    def set_water_callback_threshold(self, option, min, max):
        """
        Sets the thresholds for the :func:`WaterReached` callback. 
        
        The following options are possible:
        
        .. csv-table::
         :header: "Option", "Description"
         :widths: 10, 100
        
         "'x'",    "Callback is turned off"
         "'o'",    "Callback is triggered when the water amount value is *outside* the min and max values"
         "'i'",    "Callback is triggered when the water amount value is *inside* the min and max values"
         "'<'",    "Callback is triggered when the water amount value is smaller than the min value (max is ignored)"
         "'>'",    "Callback is triggered when the water amount value is greater than the min value (max is ignored)"
        
        The default value is ('x', 0, 0).
        """
        self.ipcon.send_request(self, BrickletWater.FUNCTION_SET_WATER_CALLBACK_THRESHOLD, (option, min, max), 'c H H', '')

    def get_water_callback_threshold(self):
        """
        Returns the threshold as set by :func:`SetWaterCallbackThreshold`.
        """
        return GetWaterCallbackThreshold(*self.ipcon.send_request(self, BrickletWater.FUNCTION_GET_WATER_CALLBACK_THRESHOLD, (), '', 'c H H'))

    def set_debounce_period(self, debounce):
        """
        Sets the period in ms with which the threshold callback
        
        * :func:`WaterReached`
        
        is triggered, if the threshold
        
        * :func:`SetWaterCallbackThreshold`
        
        keeps being reached.
        
        The default value is 100.
        """
        self.ipcon.send_request(self, BrickletWater.FUNCTION_SET_DEBOUNCE_PERIOD, (debounce,), 'I', '')

    def get_debounce_period(self):
        """
        Returns the debounce period as set by :func:`SetDebouncePeriod`.
        """
        return self.ipcon.send_request(self, BrickletWater.FUNCTION_GET_DEBOUNCE_PERIOD, (), '', 'I')

    def set_moving_average(self, average):
        """
        TODO
        
        Max value: 100
        """
        self.ipcon.send_request(self, BrickletWater.FUNCTION_SET_MOVING_AVERAGE, (average,), 'B', '')

    def get_moving_average(self):
        """
        
        """
        return self.ipcon.send_request(self, BrickletWater.FUNCTION_GET_MOVING_AVERAGE, (), '', 'B')

    def get_identity(self):
        """
        Returns the UID, the UID where the Bricklet is connected to, 
        the position, the hardware and firmware version as well as the
        device identifier.
        
        The position can be 'a', 'b', 'c' or 'd'.
        
        The device identifiers can be found :ref:`here <device_identifier>`.
        
        .. versionadded:: 2.0.0~(Plugin)
        """
        return GetIdentity(*self.ipcon.send_request(self, BrickletWater.FUNCTION_GET_IDENTITY, (), '', '8s 8s c 3B 3B H'))

    def register_callback(self, id, callback):
        """
        Registers a callback with ID *id* to the function *callback*.
        """
        self.registered_callbacks[id] = callback

Water = BrickletWater # for backward compatibility
