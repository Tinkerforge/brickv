# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2016-02-10.      #
#                                                           #
# Python Bindings Version 2.1.8                             #
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

GetCurrentCallbackThreshold = namedtuple('CurrentCallbackThreshold', ['option', 'min', 'max'])
GetAnalogValueCallbackThreshold = namedtuple('AnalogValueCallbackThreshold', ['option', 'min', 'max'])
GetIdentity = namedtuple('Identity', ['uid', 'connected_uid', 'position', 'hardware_version', 'firmware_version', 'device_identifier'])

class BrickletCurrent25(Device):
    """
    Measures AC/DC current between -25A and +25A
    """

    DEVICE_IDENTIFIER = 24
    DEVICE_DISPLAY_NAME = 'Current25 Bricklet'

    CALLBACK_CURRENT = 15
    CALLBACK_ANALOG_VALUE = 16
    CALLBACK_CURRENT_REACHED = 17
    CALLBACK_ANALOG_VALUE_REACHED = 18
    CALLBACK_OVER_CURRENT = 19

    FUNCTION_GET_CURRENT = 1
    FUNCTION_CALIBRATE = 2
    FUNCTION_IS_OVER_CURRENT = 3
    FUNCTION_GET_ANALOG_VALUE = 4
    FUNCTION_SET_CURRENT_CALLBACK_PERIOD = 5
    FUNCTION_GET_CURRENT_CALLBACK_PERIOD = 6
    FUNCTION_SET_ANALOG_VALUE_CALLBACK_PERIOD = 7
    FUNCTION_GET_ANALOG_VALUE_CALLBACK_PERIOD = 8
    FUNCTION_SET_CURRENT_CALLBACK_THRESHOLD = 9
    FUNCTION_GET_CURRENT_CALLBACK_THRESHOLD = 10
    FUNCTION_SET_ANALOG_VALUE_CALLBACK_THRESHOLD = 11
    FUNCTION_GET_ANALOG_VALUE_CALLBACK_THRESHOLD = 12
    FUNCTION_SET_DEBOUNCE_PERIOD = 13
    FUNCTION_GET_DEBOUNCE_PERIOD = 14
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

        self.response_expected[BrickletCurrent25.FUNCTION_GET_CURRENT] = BrickletCurrent25.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletCurrent25.FUNCTION_CALIBRATE] = BrickletCurrent25.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletCurrent25.FUNCTION_IS_OVER_CURRENT] = BrickletCurrent25.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletCurrent25.FUNCTION_GET_ANALOG_VALUE] = BrickletCurrent25.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletCurrent25.FUNCTION_SET_CURRENT_CALLBACK_PERIOD] = BrickletCurrent25.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletCurrent25.FUNCTION_GET_CURRENT_CALLBACK_PERIOD] = BrickletCurrent25.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletCurrent25.FUNCTION_SET_ANALOG_VALUE_CALLBACK_PERIOD] = BrickletCurrent25.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletCurrent25.FUNCTION_GET_ANALOG_VALUE_CALLBACK_PERIOD] = BrickletCurrent25.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletCurrent25.FUNCTION_SET_CURRENT_CALLBACK_THRESHOLD] = BrickletCurrent25.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletCurrent25.FUNCTION_GET_CURRENT_CALLBACK_THRESHOLD] = BrickletCurrent25.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletCurrent25.FUNCTION_SET_ANALOG_VALUE_CALLBACK_THRESHOLD] = BrickletCurrent25.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletCurrent25.FUNCTION_GET_ANALOG_VALUE_CALLBACK_THRESHOLD] = BrickletCurrent25.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletCurrent25.FUNCTION_SET_DEBOUNCE_PERIOD] = BrickletCurrent25.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletCurrent25.FUNCTION_GET_DEBOUNCE_PERIOD] = BrickletCurrent25.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletCurrent25.CALLBACK_CURRENT] = BrickletCurrent25.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletCurrent25.CALLBACK_ANALOG_VALUE] = BrickletCurrent25.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletCurrent25.CALLBACK_CURRENT_REACHED] = BrickletCurrent25.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletCurrent25.CALLBACK_ANALOG_VALUE_REACHED] = BrickletCurrent25.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletCurrent25.CALLBACK_OVER_CURRENT] = BrickletCurrent25.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletCurrent25.FUNCTION_GET_IDENTITY] = BrickletCurrent25.RESPONSE_EXPECTED_ALWAYS_TRUE

        self.callback_formats[BrickletCurrent25.CALLBACK_CURRENT] = 'h'
        self.callback_formats[BrickletCurrent25.CALLBACK_ANALOG_VALUE] = 'H'
        self.callback_formats[BrickletCurrent25.CALLBACK_CURRENT_REACHED] = 'h'
        self.callback_formats[BrickletCurrent25.CALLBACK_ANALOG_VALUE_REACHED] = 'H'
        self.callback_formats[BrickletCurrent25.CALLBACK_OVER_CURRENT] = ''

    def get_current(self):
        """
        Returns the current of the sensor. The value is in mA
        and between -25000mA and 25000mA.
        
        If you want to get the current periodically, it is recommended to use the
        callback :func:`Current` and set the period with 
        :func:`SetCurrentCallbackPeriod`.
        """
        return self.ipcon.send_request(self, BrickletCurrent25.FUNCTION_GET_CURRENT, (), '', 'h')

    def calibrate(self):
        """
        Calibrates the 0 value of the sensor. You have to call this function
        when there is no current present. 
        
        The zero point of the current sensor
        is depending on the exact properties of the analog-to-digital converter,
        the length of the Bricklet cable and the temperature. Thus, if you change
        the Brick or the environment in which the Bricklet is used, you might
        have to recalibrate.
        
        The resulting calibration will be saved on the EEPROM of the Current
        Bricklet.
        """
        self.ipcon.send_request(self, BrickletCurrent25.FUNCTION_CALIBRATE, (), '', '')

    def is_over_current(self):
        """
        Returns *true* if more than 25A were measured.
        
        .. note::
         To reset this value you have to power cycle the Bricklet.
        """
        return self.ipcon.send_request(self, BrickletCurrent25.FUNCTION_IS_OVER_CURRENT, (), '', '?')

    def get_analog_value(self):
        """
        Returns the value as read by a 12-bit analog-to-digital converter.
        The value is between 0 and 4095.
        
        .. note::
         The value returned by :func:`GetCurrent` is averaged over several samples
         to yield less noise, while :func:`GetAnalogValue` gives back raw
         unfiltered analog values. The only reason to use :func:`GetAnalogValue` is,
         if you need the full resolution of the analog-to-digital converter.
        
        If you want the analog value periodically, it is recommended to use the 
        callback :func:`AnalogValue` and set the period with 
        :func:`SetAnalogValueCallbackPeriod`.
        """
        return self.ipcon.send_request(self, BrickletCurrent25.FUNCTION_GET_ANALOG_VALUE, (), '', 'H')

    def set_current_callback_period(self, period):
        """
        Sets the period in ms with which the :func:`Current` callback is triggered
        periodically. A value of 0 turns the callback off.
        
        :func:`Current` is only triggered if the current has changed since the
        last triggering.
        
        The default value is 0.
        """
        self.ipcon.send_request(self, BrickletCurrent25.FUNCTION_SET_CURRENT_CALLBACK_PERIOD, (period,), 'I', '')

    def get_current_callback_period(self):
        """
        Returns the period as set by :func:`SetCurrentCallbackPeriod`.
        """
        return self.ipcon.send_request(self, BrickletCurrent25.FUNCTION_GET_CURRENT_CALLBACK_PERIOD, (), '', 'I')

    def set_analog_value_callback_period(self, period):
        """
        Sets the period in ms with which the :func:`AnalogValue` callback is triggered
        periodically. A value of 0 turns the callback off.
        
        :func:`AnalogValue` is only triggered if the analog value has changed since the
        last triggering.
        
        The default value is 0.
        """
        self.ipcon.send_request(self, BrickletCurrent25.FUNCTION_SET_ANALOG_VALUE_CALLBACK_PERIOD, (period,), 'I', '')

    def get_analog_value_callback_period(self):
        """
        Returns the period as set by :func:`SetAnalogValueCallbackPeriod`.
        """
        return self.ipcon.send_request(self, BrickletCurrent25.FUNCTION_GET_ANALOG_VALUE_CALLBACK_PERIOD, (), '', 'I')

    def set_current_callback_threshold(self, option, min, max):
        """
        Sets the thresholds for the :func:`CurrentReached` callback. 
        
        The following options are possible:
        
        .. csv-table::
         :header: "Option", "Description"
         :widths: 10, 100
        
         "'x'",    "Callback is turned off"
         "'o'",    "Callback is triggered when the current is *outside* the min and max values"
         "'i'",    "Callback is triggered when the current is *inside* the min and max values"
         "'<'",    "Callback is triggered when the current is smaller than the min value (max is ignored)"
         "'>'",    "Callback is triggered when the current is greater than the min value (max is ignored)"
        
        The default value is ('x', 0, 0).
        """
        self.ipcon.send_request(self, BrickletCurrent25.FUNCTION_SET_CURRENT_CALLBACK_THRESHOLD, (option, min, max), 'c h h', '')

    def get_current_callback_threshold(self):
        """
        Returns the threshold as set by :func:`SetCurrentCallbackThreshold`.
        """
        return GetCurrentCallbackThreshold(*self.ipcon.send_request(self, BrickletCurrent25.FUNCTION_GET_CURRENT_CALLBACK_THRESHOLD, (), '', 'c h h'))

    def set_analog_value_callback_threshold(self, option, min, max):
        """
        Sets the thresholds for the :func:`AnalogValueReached` callback. 
        
        The following options are possible:
        
        .. csv-table::
         :header: "Option", "Description"
         :widths: 10, 100
        
         "'x'",    "Callback is turned off"
         "'o'",    "Callback is triggered when the analog value is *outside* the min and max values"
         "'i'",    "Callback is triggered when the analog value is *inside* the min and max values"
         "'<'",    "Callback is triggered when the analog value is smaller than the min value (max is ignored)"
         "'>'",    "Callback is triggered when the analog value is greater than the min value (max is ignored)"
        
        The default value is ('x', 0, 0).
        """
        self.ipcon.send_request(self, BrickletCurrent25.FUNCTION_SET_ANALOG_VALUE_CALLBACK_THRESHOLD, (option, min, max), 'c H H', '')

    def get_analog_value_callback_threshold(self):
        """
        Returns the threshold as set by :func:`SetAnalogValueCallbackThreshold`.
        """
        return GetAnalogValueCallbackThreshold(*self.ipcon.send_request(self, BrickletCurrent25.FUNCTION_GET_ANALOG_VALUE_CALLBACK_THRESHOLD, (), '', 'c H H'))

    def set_debounce_period(self, debounce):
        """
        Sets the period in ms with which the threshold callbacks
        
        * :func:`CurrentReached`,
        * :func:`AnalogValueReached`
        
        are triggered, if the thresholds
        
        * :func:`SetCurrentCallbackThreshold`,
        * :func:`SetAnalogValueCallbackThreshold`
        
        keep being reached.
        
        The default value is 100.
        """
        self.ipcon.send_request(self, BrickletCurrent25.FUNCTION_SET_DEBOUNCE_PERIOD, (debounce,), 'I', '')

    def get_debounce_period(self):
        """
        Returns the debounce period as set by :func:`SetDebouncePeriod`.
        """
        return self.ipcon.send_request(self, BrickletCurrent25.FUNCTION_GET_DEBOUNCE_PERIOD, (), '', 'I')

    def get_identity(self):
        """
        Returns the UID, the UID where the Bricklet is connected to, 
        the position, the hardware and firmware version as well as the
        device identifier.
        
        The position can be 'a', 'b', 'c' or 'd'.
        
        The device identifier numbers can be found :ref:`here <device_identifier>`.
        |device_identifier_constant|
        """
        return GetIdentity(*self.ipcon.send_request(self, BrickletCurrent25.FUNCTION_GET_IDENTITY, (), '', '8s 8s c 3B 3B H'))

    def register_callback(self, id, callback):
        """
        Registers a callback with ID *id* to the function *callback*.
        """
        self.registered_callbacks[id] = callback

Current25 = BrickletCurrent25 # for backward compatibility
