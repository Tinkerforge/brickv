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

GetAcceleration = namedtuple('Acceleration', ['x', 'y', 'z'])
GetAccelerationCallbackThreshold = namedtuple('AccelerationCallbackThreshold', ['option', 'min_x', 'max_x', 'min_y', 'max_y', 'min_z', 'max_z'])
GetConfiguration = namedtuple('Configuration', ['data_rate', 'full_scale', 'filter_bandwidth'])
GetIdentity = namedtuple('Identity', ['uid', 'connected_uid', 'position', 'hardware_version', 'firmware_version', 'device_identifier'])

class BrickletAccelerometer(Device):
    """
    Measures acceleration in three axis
    """

    DEVICE_IDENTIFIER = 250
    DEVICE_DISPLAY_NAME = 'Accelerometer Bricklet'

    CALLBACK_ACCELERATION = 14
    CALLBACK_ACCELERATION_REACHED = 15

    FUNCTION_GET_ACCELERATION = 1
    FUNCTION_SET_ACCELERATION_CALLBACK_PERIOD = 2
    FUNCTION_GET_ACCELERATION_CALLBACK_PERIOD = 3
    FUNCTION_SET_ACCELERATION_CALLBACK_THRESHOLD = 4
    FUNCTION_GET_ACCELERATION_CALLBACK_THRESHOLD = 5
    FUNCTION_SET_DEBOUNCE_PERIOD = 6
    FUNCTION_GET_DEBOUNCE_PERIOD = 7
    FUNCTION_GET_TEMPERATURE = 8
    FUNCTION_SET_CONFIGURATION = 9
    FUNCTION_GET_CONFIGURATION = 10
    FUNCTION_LED_ON = 11
    FUNCTION_LED_OFF = 12
    FUNCTION_IS_LED_ON = 13
    FUNCTION_GET_IDENTITY = 255

    THRESHOLD_OPTION_OFF = 'x'
    THRESHOLD_OPTION_OUTSIDE = 'o'
    THRESHOLD_OPTION_INSIDE = 'i'
    THRESHOLD_OPTION_SMALLER = '<'
    THRESHOLD_OPTION_GREATER = '>'
    DATA_RATE_OFF = 0
    DATA_RATE_3HZ = 1
    DATA_RATE_6HZ = 2
    DATA_RATE_12HZ = 3
    DATA_RATE_25HZ = 4
    DATA_RATE_50HZ = 5
    DATA_RATE_100HZ = 6
    DATA_RATE_400HZ = 7
    DATA_RATE_800HZ = 8
    DATA_RATE_1600HZ = 9
    FULL_SCALE_2G = 0
    FULL_SCALE_4G = 1
    FULL_SCALE_6G = 2
    FULL_SCALE_8G = 3
    FULL_SCALE_16G = 4
    FILTER_BANDWIDTH_800HZ = 0
    FILTER_BANDWIDTH_400HZ = 1
    FILTER_BANDWIDTH_200HZ = 2
    FILTER_BANDWIDTH_50HZ = 3

    def __init__(self, uid, ipcon):
        """
        Creates an object with the unique device ID *uid* and adds it to
        the IP Connection *ipcon*.
        """
        Device.__init__(self, uid, ipcon)

        self.api_version = (2, 0, 1)

        self.response_expected[BrickletAccelerometer.FUNCTION_GET_ACCELERATION] = BrickletAccelerometer.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletAccelerometer.FUNCTION_SET_ACCELERATION_CALLBACK_PERIOD] = BrickletAccelerometer.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletAccelerometer.FUNCTION_GET_ACCELERATION_CALLBACK_PERIOD] = BrickletAccelerometer.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletAccelerometer.FUNCTION_SET_ACCELERATION_CALLBACK_THRESHOLD] = BrickletAccelerometer.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletAccelerometer.FUNCTION_GET_ACCELERATION_CALLBACK_THRESHOLD] = BrickletAccelerometer.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletAccelerometer.FUNCTION_SET_DEBOUNCE_PERIOD] = BrickletAccelerometer.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletAccelerometer.FUNCTION_GET_DEBOUNCE_PERIOD] = BrickletAccelerometer.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletAccelerometer.FUNCTION_GET_TEMPERATURE] = BrickletAccelerometer.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletAccelerometer.FUNCTION_SET_CONFIGURATION] = BrickletAccelerometer.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletAccelerometer.FUNCTION_GET_CONFIGURATION] = BrickletAccelerometer.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletAccelerometer.FUNCTION_LED_ON] = BrickletAccelerometer.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletAccelerometer.FUNCTION_LED_OFF] = BrickletAccelerometer.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletAccelerometer.FUNCTION_IS_LED_ON] = BrickletAccelerometer.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletAccelerometer.CALLBACK_ACCELERATION] = BrickletAccelerometer.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletAccelerometer.CALLBACK_ACCELERATION_REACHED] = BrickletAccelerometer.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletAccelerometer.FUNCTION_GET_IDENTITY] = BrickletAccelerometer.RESPONSE_EXPECTED_ALWAYS_TRUE

        self.callback_formats[BrickletAccelerometer.CALLBACK_ACCELERATION] = 'h h h'
        self.callback_formats[BrickletAccelerometer.CALLBACK_ACCELERATION_REACHED] = 'h h h'

    def get_acceleration(self):
        """
        Returns the acceleration in x, y and z direction. The values
        are given in g/1000 (1g = 9.80665m/s²), not to be confused with grams.
        
        If you want to get the acceleration periodically, it is recommended 
        to use the callback :func:`Acceleration` and set the period with 
        :func:`SetAccelerationCallbackPeriod`.
        """
        return GetAcceleration(*self.ipcon.send_request(self, BrickletAccelerometer.FUNCTION_GET_ACCELERATION, (), '', 'h h h'))

    def set_acceleration_callback_period(self, period):
        """
        Sets the period in ms with which the :func:`Acceleration` callback is triggered
        periodically. A value of 0 turns the callback off.
        
        :func:`Acceleration` is only triggered if the acceleration has changed since the
        last triggering.
        
        The default value is 0.
        """
        self.ipcon.send_request(self, BrickletAccelerometer.FUNCTION_SET_ACCELERATION_CALLBACK_PERIOD, (period,), 'I', '')

    def get_acceleration_callback_period(self):
        """
        Returns the period as set by :func:`SetAccelerationCallbackPeriod`.
        """
        return self.ipcon.send_request(self, BrickletAccelerometer.FUNCTION_GET_ACCELERATION_CALLBACK_PERIOD, (), '', 'I')

    def set_acceleration_callback_threshold(self, option, min_x, max_x, min_y, max_y, min_z, max_z):
        """
        Sets the thresholds for the :func:`AccelerationReached` callback. 
        
        The following options are possible:
        
        .. csv-table::
         :header: "Option", "Description"
         :widths: 10, 100
        
         "'x'",    "Callback is turned off"
         "'o'",    "Callback is triggered when the acceleration is *outside* the min and max values"
         "'i'",    "Callback is triggered when the acceleration is *inside* the min and max values"
         "'<'",    "Callback is triggered when the acceleration is smaller than the min value (max is ignored)"
         "'>'",    "Callback is triggered when the acceleration is greater than the min value (max is ignored)"
        
        The default value is ('x', 0, 0, 0, 0, 0, 0).
        """
        self.ipcon.send_request(self, BrickletAccelerometer.FUNCTION_SET_ACCELERATION_CALLBACK_THRESHOLD, (option, min_x, max_x, min_y, max_y, min_z, max_z), 'c h h h h h h', '')

    def get_acceleration_callback_threshold(self):
        """
        Returns the threshold as set by :func:`SetAccelerationCallbackThreshold`.
        """
        return GetAccelerationCallbackThreshold(*self.ipcon.send_request(self, BrickletAccelerometer.FUNCTION_GET_ACCELERATION_CALLBACK_THRESHOLD, (), '', 'c h h h h h h'))

    def set_debounce_period(self, debounce):
        """
        Sets the period in ms with which the threshold callback
        
        * :func:`AccelerationReached`
        
        is triggered, if the threshold
        
        * :func:`SetAccelerationCallbackThreshold`
        
        keeps being reached.
        
        The default value is 100.
        """
        self.ipcon.send_request(self, BrickletAccelerometer.FUNCTION_SET_DEBOUNCE_PERIOD, (debounce,), 'I', '')

    def get_debounce_period(self):
        """
        Returns the debounce period as set by :func:`SetDebouncePeriod`.
        """
        return self.ipcon.send_request(self, BrickletAccelerometer.FUNCTION_GET_DEBOUNCE_PERIOD, (), '', 'I')

    def get_temperature(self):
        """
        Returns the temperature of the accelerometer in °C.
        """
        return self.ipcon.send_request(self, BrickletAccelerometer.FUNCTION_GET_TEMPERATURE, (), '', 'h')

    def set_configuration(self, data_rate, full_scale, filter_bandwidth):
        """
        Configures the data rate, full scale range and filter bandwidth.
        Possible values are:
        
        * Data rate of 0Hz to 1600Hz.
        * Full scale range of -2G to +2G up to -16G to +16G.
        * Filter bandwidth between 50Hz and 800Hz.
        
        Decreasing data rate or full scale range will also decrease the noise on 
        the data.
        
        The default values are 100Hz data rate, -4G to +4G range and 200Hz
        filter bandwidth.
        """
        self.ipcon.send_request(self, BrickletAccelerometer.FUNCTION_SET_CONFIGURATION, (data_rate, full_scale, filter_bandwidth), 'B B B', '')

    def get_configuration(self):
        """
        Returns the configuration as set by :func:`SetConfiguration`.
        """
        return GetConfiguration(*self.ipcon.send_request(self, BrickletAccelerometer.FUNCTION_GET_CONFIGURATION, (), '', 'B B B'))

    def led_on(self):
        """
        Enables the LED on the Bricklet.
        """
        self.ipcon.send_request(self, BrickletAccelerometer.FUNCTION_LED_ON, (), '', '')

    def led_off(self):
        """
        Disables the LED on the Bricklet.
        """
        self.ipcon.send_request(self, BrickletAccelerometer.FUNCTION_LED_OFF, (), '', '')

    def is_led_on(self):
        """
        Returns *true* if the LED is enabled, *false* otherwise.
        """
        return self.ipcon.send_request(self, BrickletAccelerometer.FUNCTION_IS_LED_ON, (), '', '?')

    def get_identity(self):
        """
        Returns the UID, the UID where the Bricklet is connected to, 
        the position, the hardware and firmware version as well as the
        device identifier.
        
        The position can be 'a', 'b', 'c' or 'd'.
        
        The device identifier numbers can be found :ref:`here <device_identifier>`.
        |device_identifier_constant|
        """
        return GetIdentity(*self.ipcon.send_request(self, BrickletAccelerometer.FUNCTION_GET_IDENTITY, (), '', '8s 8s c 3B 3B H'))

    def register_callback(self, id, callback):
        """
        Registers a callback with ID *id* to the function *callback*.
        """
        self.registered_callbacks[id] = callback

Accelerometer = BrickletAccelerometer # for backward compatibility
