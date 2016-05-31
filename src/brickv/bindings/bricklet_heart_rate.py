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

GetHeartRateCallbackThreshold = namedtuple('HeartRateCallbackThreshold', ['option', 'min', 'max'])
GetIdentity = namedtuple('Identity', ['uid', 'connected_uid', 'position', 'hardware_version', 'firmware_version', 'device_identifier'])

class BrickletHeartRate(Device):
    """
    Measures heart rate
    """

    DEVICE_IDENTIFIER = 245
    DEVICE_DISPLAY_NAME = 'Heart Rate Bricklet'

    CALLBACK_HEART_RATE = 8
    CALLBACK_HEART_RATE_REACHED = 9
    CALLBACK_BEAT_STATE_CHANGED = 10

    FUNCTION_GET_HEART_RATE = 1
    FUNCTION_SET_HEART_RATE_CALLBACK_PERIOD = 2
    FUNCTION_GET_HEART_RATE_CALLBACK_PERIOD = 3
    FUNCTION_SET_HEART_RATE_CALLBACK_THRESHOLD = 4
    FUNCTION_GET_HEART_RATE_CALLBACK_THRESHOLD = 5
    FUNCTION_SET_DEBOUNCE_PERIOD = 6
    FUNCTION_GET_DEBOUNCE_PERIOD = 7
    FUNCTION_ENABLE_BEAT_STATE_CHANGED_CALLBACK = 11
    FUNCTION_DISABLE_BEAT_STATE_CHANGED_CALLBACK = 12
    FUNCTION_IS_BEAT_STATE_CHANGED_CALLBACK_ENABLED = 13
    FUNCTION_GET_IDENTITY = 255

    THRESHOLD_OPTION_OFF = 'x'
    THRESHOLD_OPTION_OUTSIDE = 'o'
    THRESHOLD_OPTION_INSIDE = 'i'
    THRESHOLD_OPTION_SMALLER = '<'
    THRESHOLD_OPTION_GREATER = '>'
    BEAT_STATE_FALLING = 0
    BEAT_STATE_RISING = 1

    def __init__(self, uid, ipcon):
        """
        Creates an object with the unique device ID *uid* and adds it to
        the IP Connection *ipcon*.
        """
        Device.__init__(self, uid, ipcon)

        self.api_version = (2, 0, 0)

        self.response_expected[BrickletHeartRate.FUNCTION_GET_HEART_RATE] = BrickletHeartRate.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletHeartRate.FUNCTION_SET_HEART_RATE_CALLBACK_PERIOD] = BrickletHeartRate.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletHeartRate.FUNCTION_GET_HEART_RATE_CALLBACK_PERIOD] = BrickletHeartRate.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletHeartRate.FUNCTION_SET_HEART_RATE_CALLBACK_THRESHOLD] = BrickletHeartRate.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletHeartRate.FUNCTION_GET_HEART_RATE_CALLBACK_THRESHOLD] = BrickletHeartRate.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletHeartRate.FUNCTION_SET_DEBOUNCE_PERIOD] = BrickletHeartRate.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletHeartRate.FUNCTION_GET_DEBOUNCE_PERIOD] = BrickletHeartRate.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletHeartRate.CALLBACK_HEART_RATE] = BrickletHeartRate.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletHeartRate.CALLBACK_HEART_RATE_REACHED] = BrickletHeartRate.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletHeartRate.CALLBACK_BEAT_STATE_CHANGED] = BrickletHeartRate.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletHeartRate.FUNCTION_ENABLE_BEAT_STATE_CHANGED_CALLBACK] = BrickletHeartRate.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletHeartRate.FUNCTION_DISABLE_BEAT_STATE_CHANGED_CALLBACK] = BrickletHeartRate.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletHeartRate.FUNCTION_IS_BEAT_STATE_CHANGED_CALLBACK_ENABLED] = BrickletHeartRate.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletHeartRate.FUNCTION_GET_IDENTITY] = BrickletHeartRate.RESPONSE_EXPECTED_ALWAYS_TRUE

        self.callback_formats[BrickletHeartRate.CALLBACK_HEART_RATE] = 'H'
        self.callback_formats[BrickletHeartRate.CALLBACK_HEART_RATE_REACHED] = 'H'
        self.callback_formats[BrickletHeartRate.CALLBACK_BEAT_STATE_CHANGED] = 'B'

    def get_heart_rate(self):
        """
        Returns the current heart rate measured.
        
        If you want to get the heart rate periodically, it is recommended 
        to use the callback :func:`HeartRate` and set the period with 
        :func:`SetHeartRateCallbackPeriod`.
        """
        return self.ipcon.send_request(self, BrickletHeartRate.FUNCTION_GET_HEART_RATE, (), '', 'H')

    def set_heart_rate_callback_period(self, period):
        """
        Sets the period in ms with which the :func:`HeartRate` callback is triggered
        periodically. A value of 0 turns the callback off.
        
        :func:`HeartRate` is only triggered if the heart rate has changed since the
        last triggering.
        
        The default value is 0.
        """
        self.ipcon.send_request(self, BrickletHeartRate.FUNCTION_SET_HEART_RATE_CALLBACK_PERIOD, (period,), 'I', '')

    def get_heart_rate_callback_period(self):
        """
        Returns the period as set by :func:`SetHeartRateCallbackPeriod`.
        """
        return self.ipcon.send_request(self, BrickletHeartRate.FUNCTION_GET_HEART_RATE_CALLBACK_PERIOD, (), '', 'I')

    def set_heart_rate_callback_threshold(self, option, min, max):
        """
        Sets the thresholds for the :func:`HeartRateReached` callback. 
        
        The following options are possible:
        
        .. csv-table::
         :header: "Option", "Description"
         :widths: 10, 100
        
         "'x'",    "Callback is turned off"
         "'o'",    "Callback is triggered when the heart rate is *outside* the min and max values"
         "'i'",    "Callback is triggered when the heart rate is *inside* the min and max values"
         "'<'",    "Callback is triggered when the heart rate is smaller than the min value (max is ignored)"
         "'>'",    "Callback is triggered when the heart rate is greater than the min value (max is ignored)"
        
        The default value is ('x', 0, 0).
        """
        self.ipcon.send_request(self, BrickletHeartRate.FUNCTION_SET_HEART_RATE_CALLBACK_THRESHOLD, (option, min, max), 'c H H', '')

    def get_heart_rate_callback_threshold(self):
        """
        Returns the threshold as set by :func:`SetHeartRateCallbackThreshold`.
        """
        return GetHeartRateCallbackThreshold(*self.ipcon.send_request(self, BrickletHeartRate.FUNCTION_GET_HEART_RATE_CALLBACK_THRESHOLD, (), '', 'c H H'))

    def set_debounce_period(self, debounce):
        """
        Sets the period in ms with which the threshold callback
        
        * :func:`HeartRateReached`
        
        is triggered, if the threshold
        
        * :func:`SetHeartRateCallbackThreshold`
        
        keeps being reached.
        
        The default value is 100.
        """
        self.ipcon.send_request(self, BrickletHeartRate.FUNCTION_SET_DEBOUNCE_PERIOD, (debounce,), 'I', '')

    def get_debounce_period(self):
        """
        Returns the debounce period as set by :func:`SetDebouncePeriod`.
        """
        return self.ipcon.send_request(self, BrickletHeartRate.FUNCTION_GET_DEBOUNCE_PERIOD, (), '', 'I')

    def enable_beat_state_changed_callback(self):
        """
        Enables the :func:`BeatStateChanged` callback.
        """
        self.ipcon.send_request(self, BrickletHeartRate.FUNCTION_ENABLE_BEAT_STATE_CHANGED_CALLBACK, (), '', '')

    def disable_beat_state_changed_callback(self):
        """
        Disables the :func:`BeatStateChanged` callback.
        """
        self.ipcon.send_request(self, BrickletHeartRate.FUNCTION_DISABLE_BEAT_STATE_CHANGED_CALLBACK, (), '', '')

    def is_beat_state_changed_callback_enabled(self):
        """
        Returns *true* if the :func:`BeatStateChanged` callback is enabled.
        """
        return self.ipcon.send_request(self, BrickletHeartRate.FUNCTION_IS_BEAT_STATE_CHANGED_CALLBACK_ENABLED, (), '', '?')

    def get_identity(self):
        """
        Returns the UID, the UID where the Bricklet is connected to, 
        the position, the hardware and firmware version as well as the
        device identifier.
        
        The position can be 'a', 'b', 'c' or 'd'.
        
        The device identifier numbers can be found :ref:`here <device_identifier>`.
        |device_identifier_constant|
        """
        return GetIdentity(*self.ipcon.send_request(self, BrickletHeartRate.FUNCTION_GET_IDENTITY, (), '', '8s 8s c 3B 3B H'))

    def register_callback(self, id, callback):
        """
        Registers a callback with ID *id* to the function *callback*.
        """
        self.registered_callbacks[id] = callback

HeartRate = BrickletHeartRate # for backward compatibility
