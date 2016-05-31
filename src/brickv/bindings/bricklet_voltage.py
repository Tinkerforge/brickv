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

GetVoltageCallbackThreshold = namedtuple('VoltageCallbackThreshold', ['option', 'min', 'max'])
GetAnalogValueCallbackThreshold = namedtuple('AnalogValueCallbackThreshold', ['option', 'min', 'max'])
GetIdentity = namedtuple('Identity', ['uid', 'connected_uid', 'position', 'hardware_version', 'firmware_version', 'device_identifier'])

class BrickletVoltage(Device):
    """
    Measures DC voltage between 0V and 50V
    """

    DEVICE_IDENTIFIER = 218
    DEVICE_DISPLAY_NAME = 'Voltage Bricklet'

    CALLBACK_VOLTAGE = 13
    CALLBACK_ANALOG_VALUE = 14
    CALLBACK_VOLTAGE_REACHED = 15
    CALLBACK_ANALOG_VALUE_REACHED = 16

    FUNCTION_GET_VOLTAGE = 1
    FUNCTION_GET_ANALOG_VALUE = 2
    FUNCTION_SET_VOLTAGE_CALLBACK_PERIOD = 3
    FUNCTION_GET_VOLTAGE_CALLBACK_PERIOD = 4
    FUNCTION_SET_ANALOG_VALUE_CALLBACK_PERIOD = 5
    FUNCTION_GET_ANALOG_VALUE_CALLBACK_PERIOD = 6
    FUNCTION_SET_VOLTAGE_CALLBACK_THRESHOLD = 7
    FUNCTION_GET_VOLTAGE_CALLBACK_THRESHOLD = 8
    FUNCTION_SET_ANALOG_VALUE_CALLBACK_THRESHOLD = 9
    FUNCTION_GET_ANALOG_VALUE_CALLBACK_THRESHOLD = 10
    FUNCTION_SET_DEBOUNCE_PERIOD = 11
    FUNCTION_GET_DEBOUNCE_PERIOD = 12
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

        self.api_version = (2, 0, 1)

        self.response_expected[BrickletVoltage.FUNCTION_GET_VOLTAGE] = BrickletVoltage.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletVoltage.FUNCTION_GET_ANALOG_VALUE] = BrickletVoltage.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletVoltage.FUNCTION_SET_VOLTAGE_CALLBACK_PERIOD] = BrickletVoltage.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletVoltage.FUNCTION_GET_VOLTAGE_CALLBACK_PERIOD] = BrickletVoltage.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletVoltage.FUNCTION_SET_ANALOG_VALUE_CALLBACK_PERIOD] = BrickletVoltage.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletVoltage.FUNCTION_GET_ANALOG_VALUE_CALLBACK_PERIOD] = BrickletVoltage.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletVoltage.FUNCTION_SET_VOLTAGE_CALLBACK_THRESHOLD] = BrickletVoltage.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletVoltage.FUNCTION_GET_VOLTAGE_CALLBACK_THRESHOLD] = BrickletVoltage.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletVoltage.FUNCTION_SET_ANALOG_VALUE_CALLBACK_THRESHOLD] = BrickletVoltage.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletVoltage.FUNCTION_GET_ANALOG_VALUE_CALLBACK_THRESHOLD] = BrickletVoltage.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletVoltage.FUNCTION_SET_DEBOUNCE_PERIOD] = BrickletVoltage.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletVoltage.FUNCTION_GET_DEBOUNCE_PERIOD] = BrickletVoltage.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletVoltage.CALLBACK_VOLTAGE] = BrickletVoltage.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletVoltage.CALLBACK_ANALOG_VALUE] = BrickletVoltage.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletVoltage.CALLBACK_VOLTAGE_REACHED] = BrickletVoltage.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletVoltage.CALLBACK_ANALOG_VALUE_REACHED] = BrickletVoltage.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletVoltage.FUNCTION_GET_IDENTITY] = BrickletVoltage.RESPONSE_EXPECTED_ALWAYS_TRUE

        self.callback_formats[BrickletVoltage.CALLBACK_VOLTAGE] = 'H'
        self.callback_formats[BrickletVoltage.CALLBACK_ANALOG_VALUE] = 'H'
        self.callback_formats[BrickletVoltage.CALLBACK_VOLTAGE_REACHED] = 'H'
        self.callback_formats[BrickletVoltage.CALLBACK_ANALOG_VALUE_REACHED] = 'H'

    def get_voltage(self):
        """
        Returns the voltage of the sensor. The value is in mV and
        between 0mV and 50000mV.
        
        If you want to get the voltage periodically, it is recommended to use the
        callback :func:`Voltage` and set the period with 
        :func:`SetVoltageCallbackPeriod`.
        """
        return self.ipcon.send_request(self, BrickletVoltage.FUNCTION_GET_VOLTAGE, (), '', 'H')

    def get_analog_value(self):
        """
        Returns the value as read by a 12-bit analog-to-digital converter.
        The value is between 0 and 4095.
        
        .. note::
         The value returned by :func:`GetVoltage` is averaged over several samples
         to yield less noise, while :func:`GetAnalogValue` gives back raw
         unfiltered analog values. The only reason to use :func:`GetAnalogValue` is,
         if you need the full resolution of the analog-to-digital converter.
        
        If you want the analog value periodically, it is recommended to use the 
        callback :func:`AnalogValue` and set the period with 
        :func:`SetAnalogValueCallbackPeriod`.
        """
        return self.ipcon.send_request(self, BrickletVoltage.FUNCTION_GET_ANALOG_VALUE, (), '', 'H')

    def set_voltage_callback_period(self, period):
        """
        Sets the period in ms with which the :func:`Voltage` callback is triggered
        periodically. A value of 0 turns the callback off.
        
        :func:`Voltage` is only triggered if the voltage has changed since the
        last triggering.
        
        The default value is 0.
        """
        self.ipcon.send_request(self, BrickletVoltage.FUNCTION_SET_VOLTAGE_CALLBACK_PERIOD, (period,), 'I', '')

    def get_voltage_callback_period(self):
        """
        Returns the period as set by :func:`SetVoltageCallbackPeriod`.
        """
        return self.ipcon.send_request(self, BrickletVoltage.FUNCTION_GET_VOLTAGE_CALLBACK_PERIOD, (), '', 'I')

    def set_analog_value_callback_period(self, period):
        """
        Sets the period in ms with which the :func:`AnalogValue` callback is triggered
        periodically. A value of 0 turns the callback off.
        
        :func:`AnalogValue` is only triggered if the analog value has changed since the
        last triggering.
        
        The default value is 0.
        """
        self.ipcon.send_request(self, BrickletVoltage.FUNCTION_SET_ANALOG_VALUE_CALLBACK_PERIOD, (period,), 'I', '')

    def get_analog_value_callback_period(self):
        """
        Returns the period as set by :func:`SetAnalogValueCallbackPeriod`.
        """
        return self.ipcon.send_request(self, BrickletVoltage.FUNCTION_GET_ANALOG_VALUE_CALLBACK_PERIOD, (), '', 'I')

    def set_voltage_callback_threshold(self, option, min, max):
        """
        Sets the thresholds for the :func:`VoltageReached` callback. 
        
        The following options are possible:
        
        .. csv-table::
         :header: "Option", "Description"
         :widths: 10, 100
        
         "'x'",    "Callback is turned off"
         "'o'",    "Callback is triggered when the voltage is *outside* the min and max values"
         "'i'",    "Callback is triggered when the voltage is *inside* the min and max values"
         "'<'",    "Callback is triggered when the voltage is smaller than the min value (max is ignored)"
         "'>'",    "Callback is triggered when the voltage is greater than the min value (max is ignored)"
        
        The default value is ('x', 0, 0).
        """
        self.ipcon.send_request(self, BrickletVoltage.FUNCTION_SET_VOLTAGE_CALLBACK_THRESHOLD, (option, min, max), 'c H H', '')

    def get_voltage_callback_threshold(self):
        """
        Returns the threshold as set by :func:`SetVoltageCallbackThreshold`.
        """
        return GetVoltageCallbackThreshold(*self.ipcon.send_request(self, BrickletVoltage.FUNCTION_GET_VOLTAGE_CALLBACK_THRESHOLD, (), '', 'c H H'))

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
        self.ipcon.send_request(self, BrickletVoltage.FUNCTION_SET_ANALOG_VALUE_CALLBACK_THRESHOLD, (option, min, max), 'c H H', '')

    def get_analog_value_callback_threshold(self):
        """
        Returns the threshold as set by :func:`SetAnalogValueCallbackThreshold`.
        """
        return GetAnalogValueCallbackThreshold(*self.ipcon.send_request(self, BrickletVoltage.FUNCTION_GET_ANALOG_VALUE_CALLBACK_THRESHOLD, (), '', 'c H H'))

    def set_debounce_period(self, debounce):
        """
        Sets the period in ms with which the threshold callbacks
        
        * :func:`VoltageReached`,
        * :func:`AnalogValueReached`
        
        are triggered, if the thresholds
        
        * :func:`SetVoltageCallbackThreshold`,
        * :func:`SetAnalogValueCallbackThreshold`
        
        keep being reached.
        
        The default value is 100.
        """
        self.ipcon.send_request(self, BrickletVoltage.FUNCTION_SET_DEBOUNCE_PERIOD, (debounce,), 'I', '')

    def get_debounce_period(self):
        """
        Returns the debounce period as set by :func:`SetDebouncePeriod`.
        """
        return self.ipcon.send_request(self, BrickletVoltage.FUNCTION_GET_DEBOUNCE_PERIOD, (), '', 'I')

    def get_identity(self):
        """
        Returns the UID, the UID where the Bricklet is connected to, 
        the position, the hardware and firmware version as well as the
        device identifier.
        
        The position can be 'a', 'b', 'c' or 'd'.
        
        The device identifier numbers can be found :ref:`here <device_identifier>`.
        |device_identifier_constant|
        """
        return GetIdentity(*self.ipcon.send_request(self, BrickletVoltage.FUNCTION_GET_IDENTITY, (), '', '8s 8s c 3B 3B H'))

    def register_callback(self, id, callback):
        """
        Registers a callback with ID *id* to the function *callback*.
        """
        self.registered_callbacks[id] = callback

Voltage = BrickletVoltage # for backward compatibility
