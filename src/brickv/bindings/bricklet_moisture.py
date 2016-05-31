# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2016-05-31.      #
#                                                           #
# Python Bindings Version 2.1.9                             #
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

GetMoistureCallbackThreshold = namedtuple('MoistureCallbackThreshold', ['option', 'min', 'max'])
GetIdentity = namedtuple('Identity', ['uid', 'connected_uid', 'position', 'hardware_version', 'firmware_version', 'device_identifier'])

class BrickletMoisture(Device):
    """
    Measures soil moisture
    """

    DEVICE_IDENTIFIER = 232
    DEVICE_DISPLAY_NAME = 'Moisture Bricklet'

    CALLBACK_MOISTURE = 8
    CALLBACK_MOISTURE_REACHED = 9

    FUNCTION_GET_MOISTURE_VALUE = 1
    FUNCTION_SET_MOISTURE_CALLBACK_PERIOD = 2
    FUNCTION_GET_MOISTURE_CALLBACK_PERIOD = 3
    FUNCTION_SET_MOISTURE_CALLBACK_THRESHOLD = 4
    FUNCTION_GET_MOISTURE_CALLBACK_THRESHOLD = 5
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

        self.response_expected[BrickletMoisture.FUNCTION_GET_MOISTURE_VALUE] = BrickletMoisture.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletMoisture.FUNCTION_SET_MOISTURE_CALLBACK_PERIOD] = BrickletMoisture.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletMoisture.FUNCTION_GET_MOISTURE_CALLBACK_PERIOD] = BrickletMoisture.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletMoisture.FUNCTION_SET_MOISTURE_CALLBACK_THRESHOLD] = BrickletMoisture.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletMoisture.FUNCTION_GET_MOISTURE_CALLBACK_THRESHOLD] = BrickletMoisture.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletMoisture.FUNCTION_SET_DEBOUNCE_PERIOD] = BrickletMoisture.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletMoisture.FUNCTION_GET_DEBOUNCE_PERIOD] = BrickletMoisture.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletMoisture.CALLBACK_MOISTURE] = BrickletMoisture.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletMoisture.CALLBACK_MOISTURE_REACHED] = BrickletMoisture.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletMoisture.FUNCTION_SET_MOVING_AVERAGE] = BrickletMoisture.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletMoisture.FUNCTION_GET_MOVING_AVERAGE] = BrickletMoisture.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletMoisture.FUNCTION_GET_IDENTITY] = BrickletMoisture.RESPONSE_EXPECTED_ALWAYS_TRUE

        self.callback_formats[BrickletMoisture.CALLBACK_MOISTURE] = 'H'
        self.callback_formats[BrickletMoisture.CALLBACK_MOISTURE_REACHED] = 'H'

    def get_moisture_value(self):
        """
        Returns the current moisture value. The value has a range of
        0 to 4095. A small value corresponds to little moisture, a big
        value corresponds to much moisture.
        
        If you want to get the moisture value periodically, it is recommended 
        to use the callback :func:`Moisture` and set the period with 
        :func:`SetMoistureCallbackPeriod`.
        """
        return self.ipcon.send_request(self, BrickletMoisture.FUNCTION_GET_MOISTURE_VALUE, (), '', 'H')

    def set_moisture_callback_period(self, period):
        """
        Sets the period in ms with which the :func:`Moisture` callback is triggered
        periodically. A value of 0 turns the callback off.
        
        :func:`Moisture` is only triggered if the moisture value has changed since the
        last triggering.
        
        The default value is 0.
        """
        self.ipcon.send_request(self, BrickletMoisture.FUNCTION_SET_MOISTURE_CALLBACK_PERIOD, (period,), 'I', '')

    def get_moisture_callback_period(self):
        """
        Returns the period as set by :func:`SetMoistureCallbackPeriod`.
        """
        return self.ipcon.send_request(self, BrickletMoisture.FUNCTION_GET_MOISTURE_CALLBACK_PERIOD, (), '', 'I')

    def set_moisture_callback_threshold(self, option, min, max):
        """
        Sets the thresholds for the :func:`MoistureReached` callback. 
        
        The following options are possible:
        
        .. csv-table::
         :header: "Option", "Description"
         :widths: 10, 100
        
         "'x'",    "Callback is turned off"
         "'o'",    "Callback is triggered when the moisture value is *outside* the min and max values"
         "'i'",    "Callback is triggered when the moisture value is *inside* the min and max values"
         "'<'",    "Callback is triggered when the moisture value is smaller than the min value (max is ignored)"
         "'>'",    "Callback is triggered when the moisture value is greater than the min value (max is ignored)"
        
        The default value is ('x', 0, 0).
        """
        self.ipcon.send_request(self, BrickletMoisture.FUNCTION_SET_MOISTURE_CALLBACK_THRESHOLD, (option, min, max), 'c H H', '')

    def get_moisture_callback_threshold(self):
        """
        Returns the threshold as set by :func:`SetMoistureCallbackThreshold`.
        """
        return GetMoistureCallbackThreshold(*self.ipcon.send_request(self, BrickletMoisture.FUNCTION_GET_MOISTURE_CALLBACK_THRESHOLD, (), '', 'c H H'))

    def set_debounce_period(self, debounce):
        """
        Sets the period in ms with which the threshold callback
        
        * :func:`MoistureReached`
        
        is triggered, if the threshold
        
        * :func:`SetMoistureCallbackThreshold`
        
        keeps being reached.
        
        The default value is 100.
        """
        self.ipcon.send_request(self, BrickletMoisture.FUNCTION_SET_DEBOUNCE_PERIOD, (debounce,), 'I', '')

    def get_debounce_period(self):
        """
        Returns the debounce period as set by :func:`SetDebouncePeriod`.
        """
        return self.ipcon.send_request(self, BrickletMoisture.FUNCTION_GET_DEBOUNCE_PERIOD, (), '', 'I')

    def set_moving_average(self, average):
        """
        Sets the length of a `moving averaging <https://en.wikipedia.org/wiki/Moving_average>`__
        for the moisture value.
        
        Setting the length to 0 will turn the averaging completely off. With less
        averaging, there is more noise on the data.
        
        The range for the averaging is 0-100.
        
        The default value is 100.
        """
        self.ipcon.send_request(self, BrickletMoisture.FUNCTION_SET_MOVING_AVERAGE, (average,), 'B', '')

    def get_moving_average(self):
        """
        Returns the length moving average as set by :func:`SetMovingAverage`.
        """
        return self.ipcon.send_request(self, BrickletMoisture.FUNCTION_GET_MOVING_AVERAGE, (), '', 'B')

    def get_identity(self):
        """
        Returns the UID, the UID where the Bricklet is connected to, 
        the position, the hardware and firmware version as well as the
        device identifier.
        
        The position can be 'a', 'b', 'c' or 'd'.
        
        The device identifier numbers can be found :ref:`here <device_identifier>`.
        |device_identifier_constant|
        """
        return GetIdentity(*self.ipcon.send_request(self, BrickletMoisture.FUNCTION_GET_IDENTITY, (), '', '8s 8s c 3B 3B H'))

    def register_callback(self, id, callback):
        """
        Registers a callback with ID *id* to the function *callback*.
        """
        self.registered_callbacks[id] = callback

Moisture = BrickletMoisture # for backward compatibility
