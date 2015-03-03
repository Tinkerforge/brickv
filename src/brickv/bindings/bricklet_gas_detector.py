# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2015-03-03.      #
#                                                           #
# Bindings Version 2.1.4                                    #
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

GetValueCallbackThreshold = namedtuple('ValueCallbackThreshold', ['option', 'min', 'max'])
GetIdentity = namedtuple('Identity', ['uid', 'connected_uid', 'position', 'hardware_version', 'firmware_version', 'device_identifier'])

class BrickletGasDetector(Device):
    """
    Device for sensing different gases
    """

    DEVICE_IDENTIFIER = 252

    CALLBACK_VALUE = 15
    CALLBACK_VALUE_REACHED = 16

    FUNCTION_GET_VALUE = 1
    FUNCTION_SET_VALUE_CALLBACK_PERIOD = 2
    FUNCTION_GET_VALUE_CALLBACK_PERIOD = 3
    FUNCTION_SET_VALUE_CALLBACK_THRESHOLD = 4
    FUNCTION_GET_VALUE_CALLBACK_THRESHOLD = 5
    FUNCTION_SET_DEBOUNCE_PERIOD = 6
    FUNCTION_GET_DEBOUNCE_PERIOD = 7
    FUNCTION_SET_MOVING_AVERAGE = 8
    FUNCTION_GET_MOVING_AVERAGE = 9
    FUNCTION_SET_DETECTOR_TYPE = 10
    FUNCTION_GET_DETECTOR_TYPE = 11
    FUNCTION_HEATER_ON = 12
    FUNCTION_HEATER_OFF = 13
    FUNCTION_IS_HEATER_ON = 14
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

        self.response_expected[BrickletGasDetector.FUNCTION_GET_VALUE] = BrickletGasDetector.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletGasDetector.FUNCTION_SET_VALUE_CALLBACK_PERIOD] = BrickletGasDetector.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletGasDetector.FUNCTION_GET_VALUE_CALLBACK_PERIOD] = BrickletGasDetector.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletGasDetector.FUNCTION_SET_VALUE_CALLBACK_THRESHOLD] = BrickletGasDetector.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletGasDetector.FUNCTION_GET_VALUE_CALLBACK_THRESHOLD] = BrickletGasDetector.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletGasDetector.FUNCTION_SET_DEBOUNCE_PERIOD] = BrickletGasDetector.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletGasDetector.FUNCTION_GET_DEBOUNCE_PERIOD] = BrickletGasDetector.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletGasDetector.FUNCTION_SET_MOVING_AVERAGE] = BrickletGasDetector.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletGasDetector.FUNCTION_GET_MOVING_AVERAGE] = BrickletGasDetector.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletGasDetector.FUNCTION_SET_DETECTOR_TYPE] = BrickletGasDetector.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletGasDetector.FUNCTION_GET_DETECTOR_TYPE] = BrickletGasDetector.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletGasDetector.FUNCTION_HEATER_ON] = BrickletGasDetector.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletGasDetector.FUNCTION_HEATER_OFF] = BrickletGasDetector.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletGasDetector.FUNCTION_IS_HEATER_ON] = BrickletGasDetector.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletGasDetector.CALLBACK_VALUE] = BrickletGasDetector.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletGasDetector.CALLBACK_VALUE_REACHED] = BrickletGasDetector.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletGasDetector.FUNCTION_GET_IDENTITY] = BrickletGasDetector.RESPONSE_EXPECTED_ALWAYS_TRUE

        self.callback_formats[BrickletGasDetector.CALLBACK_VALUE] = 'H'
        self.callback_formats[BrickletGasDetector.CALLBACK_VALUE_REACHED] = 'H'

    def get_value(self):
        """
        TODO
        
        If you want to get the value periodically, it is recommended 
        to use the callback :func:`Value` and set the period with 
        :func:`SetValueCallbackPeriod`.
        """
        return self.ipcon.send_request(self, BrickletGasDetector.FUNCTION_GET_VALUE, (), '', 'H')

    def set_value_callback_period(self, period):
        """
        Sets the period in ms with which the :func:`Value` callback is triggered
        periodically. A value of 0 turns the callback off.
        
        :func:`Value` is only triggered if the value value has changed since the
        last triggering.
        
        The default value is 0.
        """
        self.ipcon.send_request(self, BrickletGasDetector.FUNCTION_SET_VALUE_CALLBACK_PERIOD, (period,), 'I', '')

    def get_value_callback_period(self):
        """
        Returns the period as set by :func:`SetValueCallbackPeriod`.
        """
        return self.ipcon.send_request(self, BrickletGasDetector.FUNCTION_GET_VALUE_CALLBACK_PERIOD, (), '', 'I')

    def set_value_callback_threshold(self, option, min, max):
        """
        Sets the thresholds for the :func:`ValueReached` callback. 
        
        The following options are possible:
        
        .. csv-table::
         :header: "Option", "Description"
         :widths: 10, 100
        
         "'x'",    "Callback is turned off"
         "'o'",    "Callback is triggered when the value value is *outside* the min and max values"
         "'i'",    "Callback is triggered when the value value is *inside* the min and max values"
         "'<'",    "Callback is triggered when the value value is smaller than the min value (max is ignored)"
         "'>'",    "Callback is triggered when the value value is greater than the min value (max is ignored)"
        
        The default value is ('x', 0, 0).
        """
        self.ipcon.send_request(self, BrickletGasDetector.FUNCTION_SET_VALUE_CALLBACK_THRESHOLD, (option, min, max), 'c H H', '')

    def get_value_callback_threshold(self):
        """
        Returns the threshold as set by :func:`SetValueCallbackThreshold`.
        """
        return GetValueCallbackThreshold(*self.ipcon.send_request(self, BrickletGasDetector.FUNCTION_GET_VALUE_CALLBACK_THRESHOLD, (), '', 'c H H'))

    def set_debounce_period(self, debounce):
        """
        Sets the period in ms with which the threshold callback
        
        * :func:`ValueReached`
        
        is triggered, if the threshold
        
        * :func:`SetValueCallbackThreshold`
        
        keeps being reached.
        
        The default value is 100.
        """
        self.ipcon.send_request(self, BrickletGasDetector.FUNCTION_SET_DEBOUNCE_PERIOD, (debounce,), 'I', '')

    def get_debounce_period(self):
        """
        Returns the debounce period as set by :func:`SetDebouncePeriod`.
        """
        return self.ipcon.send_request(self, BrickletGasDetector.FUNCTION_GET_DEBOUNCE_PERIOD, (), '', 'I')

    def set_moving_average(self, average):
        """
        Sets the length of a `moving averaging <http://en.wikipedia.org/wiki/Moving_average>`__ 
        for the value value.
        
        Setting the length to 1 will turn the averaging off. With less
        averaging, there is more noise on the data.
        
        The range for the averaging is 1-100.
        
        The default value is 100.
        """
        self.ipcon.send_request(self, BrickletGasDetector.FUNCTION_SET_MOVING_AVERAGE, (average,), 'B', '')

    def get_moving_average(self):
        """
        Returns the length moving average as set by :func:`SetMovingAverage`.
        """
        return self.ipcon.send_request(self, BrickletGasDetector.FUNCTION_GET_MOVING_AVERAGE, (), '', 'B')

    def set_detector_type(self, detector_type):
        """
        TODO
        """
        self.ipcon.send_request(self, BrickletGasDetector.FUNCTION_SET_DETECTOR_TYPE, (detector_type,), 'B', '')

    def get_detector_type(self):
        """
        TODO
        """
        return self.ipcon.send_request(self, BrickletGasDetector.FUNCTION_GET_DETECTOR_TYPE, (), '', 'B')

    def heater_on(self):
        """
        TODO
        """
        self.ipcon.send_request(self, BrickletGasDetector.FUNCTION_HEATER_ON, (), '', '')

    def heater_off(self):
        """
        TODO
        """
        self.ipcon.send_request(self, BrickletGasDetector.FUNCTION_HEATER_OFF, (), '', '')

    def is_heater_on(self):
        """
        TODO
        """
        return self.ipcon.send_request(self, BrickletGasDetector.FUNCTION_IS_HEATER_ON, (), '', '?')

    def get_identity(self):
        """
        Returns the UID, the UID where the Bricklet is connected to, 
        the position, the hardware and firmware version as well as the
        device identifier.
        
        The position can be 'a', 'b', 'c' or 'd'.
        
        The device identifier numbers can be found :ref:`here <device_identifier>`.
        |device_identifier_constant|
        """
        return GetIdentity(*self.ipcon.send_request(self, BrickletGasDetector.FUNCTION_GET_IDENTITY, (), '', '8s 8s c 3B 3B H'))

    def register_callback(self, id, callback):
        """
        Registers a callback with ID *id* to the function *callback*.
        """
        self.registered_callbacks[id] = callback

GasDetector = BrickletGasDetector # for backward compatibility
