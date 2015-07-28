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

GetPosition = namedtuple('Position', ['x', 'y'])
GetAnalogValue = namedtuple('AnalogValue', ['x', 'y'])
GetPositionCallbackThreshold = namedtuple('PositionCallbackThreshold', ['option', 'min_x', 'max_x', 'min_y', 'max_y'])
GetAnalogValueCallbackThreshold = namedtuple('AnalogValueCallbackThreshold', ['option', 'min_x', 'max_x', 'min_y', 'max_y'])
GetIdentity = namedtuple('Identity', ['uid', 'connected_uid', 'position', 'hardware_version', 'firmware_version', 'device_identifier'])

class BrickletJoystick(Device):
    """
    2-axis joystick with push-button
    """

    DEVICE_IDENTIFIER = 210
    DEVICE_DISPLAY_NAME = 'Joystick Bricklet'

    CALLBACK_POSITION = 15
    CALLBACK_ANALOG_VALUE = 16
    CALLBACK_POSITION_REACHED = 17
    CALLBACK_ANALOG_VALUE_REACHED = 18
    CALLBACK_PRESSED = 19
    CALLBACK_RELEASED = 20

    FUNCTION_GET_POSITION = 1
    FUNCTION_IS_PRESSED = 2
    FUNCTION_GET_ANALOG_VALUE = 3
    FUNCTION_CALIBRATE = 4
    FUNCTION_SET_POSITION_CALLBACK_PERIOD = 5
    FUNCTION_GET_POSITION_CALLBACK_PERIOD = 6
    FUNCTION_SET_ANALOG_VALUE_CALLBACK_PERIOD = 7
    FUNCTION_GET_ANALOG_VALUE_CALLBACK_PERIOD = 8
    FUNCTION_SET_POSITION_CALLBACK_THRESHOLD = 9
    FUNCTION_GET_POSITION_CALLBACK_THRESHOLD = 10
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

        self.response_expected[BrickletJoystick.FUNCTION_GET_POSITION] = BrickletJoystick.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletJoystick.FUNCTION_IS_PRESSED] = BrickletJoystick.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletJoystick.FUNCTION_GET_ANALOG_VALUE] = BrickletJoystick.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletJoystick.FUNCTION_CALIBRATE] = BrickletJoystick.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletJoystick.FUNCTION_SET_POSITION_CALLBACK_PERIOD] = BrickletJoystick.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletJoystick.FUNCTION_GET_POSITION_CALLBACK_PERIOD] = BrickletJoystick.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletJoystick.FUNCTION_SET_ANALOG_VALUE_CALLBACK_PERIOD] = BrickletJoystick.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletJoystick.FUNCTION_GET_ANALOG_VALUE_CALLBACK_PERIOD] = BrickletJoystick.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletJoystick.FUNCTION_SET_POSITION_CALLBACK_THRESHOLD] = BrickletJoystick.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletJoystick.FUNCTION_GET_POSITION_CALLBACK_THRESHOLD] = BrickletJoystick.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletJoystick.FUNCTION_SET_ANALOG_VALUE_CALLBACK_THRESHOLD] = BrickletJoystick.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletJoystick.FUNCTION_GET_ANALOG_VALUE_CALLBACK_THRESHOLD] = BrickletJoystick.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletJoystick.FUNCTION_SET_DEBOUNCE_PERIOD] = BrickletJoystick.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletJoystick.FUNCTION_GET_DEBOUNCE_PERIOD] = BrickletJoystick.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletJoystick.CALLBACK_POSITION] = BrickletJoystick.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletJoystick.CALLBACK_ANALOG_VALUE] = BrickletJoystick.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletJoystick.CALLBACK_POSITION_REACHED] = BrickletJoystick.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletJoystick.CALLBACK_ANALOG_VALUE_REACHED] = BrickletJoystick.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletJoystick.CALLBACK_PRESSED] = BrickletJoystick.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletJoystick.CALLBACK_RELEASED] = BrickletJoystick.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletJoystick.FUNCTION_GET_IDENTITY] = BrickletJoystick.RESPONSE_EXPECTED_ALWAYS_TRUE

        self.callback_formats[BrickletJoystick.CALLBACK_POSITION] = 'h h'
        self.callback_formats[BrickletJoystick.CALLBACK_ANALOG_VALUE] = 'H H'
        self.callback_formats[BrickletJoystick.CALLBACK_POSITION_REACHED] = 'h h'
        self.callback_formats[BrickletJoystick.CALLBACK_ANALOG_VALUE_REACHED] = 'H H'
        self.callback_formats[BrickletJoystick.CALLBACK_PRESSED] = ''
        self.callback_formats[BrickletJoystick.CALLBACK_RELEASED] = ''

    def get_position(self):
        """
        Returns the position of the Joystick. The value ranges between -100 and
        100 for both axis. The middle position of the joystick is x=0, y=0. The
        returned values are averaged and calibrated (see :func:`Calibrate`).
        
        If you want to get the position periodically, it is recommended to use the
        callback :func:`Position` and set the period with 
        :func:`SetPositionCallbackPeriod`.
        """
        return GetPosition(*self.ipcon.send_request(self, BrickletJoystick.FUNCTION_GET_POSITION, (), '', 'h h'))

    def is_pressed(self):
        """
        Returns *true* if the button is pressed and *false* otherwise.
        
        It is recommended to use the :func:`Pressed` and :func:`Released` callbacks
        to handle the button.
        """
        return self.ipcon.send_request(self, BrickletJoystick.FUNCTION_IS_PRESSED, (), '', '?')

    def get_analog_value(self):
        """
        Returns the values as read by a 12-bit analog-to-digital converter.
        The values are between 0 and 4095 for both axis.
        
        .. note::
         The values returned by :func:`GetPosition` are averaged over several samples
         to yield less noise, while :func:`GetAnalogValue` gives back raw
         unfiltered analog values. The only reason to use :func:`GetAnalogValue` is,
         if you need the full resolution of the analog-to-digital converter.
        
        If you want the analog values periodically, it is recommended to use the 
        callback :func:`AnalogValue` and set the period with 
        :func:`SetAnalogValueCallbackPeriod`.
        """
        return GetAnalogValue(*self.ipcon.send_request(self, BrickletJoystick.FUNCTION_GET_ANALOG_VALUE, (), '', 'H H'))

    def calibrate(self):
        """
        Calibrates the middle position of the Joystick. If your Joystick Bricklet
        does not return x=0 and y=0 in the middle position, call this function
        while the Joystick is standing still in the middle position.
        
        The resulting calibration will be saved on the EEPROM of the Joystick
        Bricklet, thus you only have to calibrate it once.
        """
        self.ipcon.send_request(self, BrickletJoystick.FUNCTION_CALIBRATE, (), '', '')

    def set_position_callback_period(self, period):
        """
        Sets the period in ms with which the :func:`Position` callback is triggered
        periodically. A value of 0 turns the callback off.
        
        :func:`Position` is only triggered if the position has changed since the
        last triggering.
        
        The default value is 0.
        """
        self.ipcon.send_request(self, BrickletJoystick.FUNCTION_SET_POSITION_CALLBACK_PERIOD, (period,), 'I', '')

    def get_position_callback_period(self):
        """
        Returns the period as set by :func:`SetPositionCallbackPeriod`.
        """
        return self.ipcon.send_request(self, BrickletJoystick.FUNCTION_GET_POSITION_CALLBACK_PERIOD, (), '', 'I')

    def set_analog_value_callback_period(self, period):
        """
        Sets the period in ms with which the :func:`AnalogValue` callback is triggered
        periodically. A value of 0 turns the callback off.
        
        :func:`AnalogValue` is only triggered if the analog values have changed since the
        last triggering.
        
        The default value is 0.
        """
        self.ipcon.send_request(self, BrickletJoystick.FUNCTION_SET_ANALOG_VALUE_CALLBACK_PERIOD, (period,), 'I', '')

    def get_analog_value_callback_period(self):
        """
        Returns the period as set by :func:`SetAnalogValueCallbackPeriod`.
        """
        return self.ipcon.send_request(self, BrickletJoystick.FUNCTION_GET_ANALOG_VALUE_CALLBACK_PERIOD, (), '', 'I')

    def set_position_callback_threshold(self, option, min_x, max_x, min_y, max_y):
        """
        Sets the thresholds for the :func:`PositionReached` callback. 
        
        The following options are possible:
        
        .. csv-table::
         :header: "Option", "Description"
         :widths: 10, 100
        
         "'x'",    "Callback is turned off"
         "'o'",    "Callback is triggered when the position is *outside* the min and max values"
         "'i'",    "Callback is triggered when the position is *inside* the min and max values"
         "'<'",    "Callback is triggered when the position is smaller than the min values (max is ignored)"
         "'>'",    "Callback is triggered when the position is greater than the min values (max is ignored)"
        
        The default value is ('x', 0, 0, 0, 0).
        """
        self.ipcon.send_request(self, BrickletJoystick.FUNCTION_SET_POSITION_CALLBACK_THRESHOLD, (option, min_x, max_x, min_y, max_y), 'c h h h h', '')

    def get_position_callback_threshold(self):
        """
        Returns the threshold as set by :func:`SetPositionCallbackThreshold`.
        """
        return GetPositionCallbackThreshold(*self.ipcon.send_request(self, BrickletJoystick.FUNCTION_GET_POSITION_CALLBACK_THRESHOLD, (), '', 'c h h h h'))

    def set_analog_value_callback_threshold(self, option, min_x, max_x, min_y, max_y):
        """
        Sets the thresholds for the :func:`AnalogValueReached` callback. 
        
        The following options are possible:
        
        .. csv-table::
         :header: "Option", "Description"
         :widths: 10, 100
        
         "'x'",    "Callback is turned off"
         "'o'",    "Callback is triggered when the analog values are *outside* the min and max values"
         "'i'",    "Callback is triggered when the analog values are *inside* the min and max values"
         "'<'",    "Callback is triggered when the analog values are smaller than the min values (max is ignored)"
         "'>'",    "Callback is triggered when the analog values are greater than the min values (max is ignored)"
        
        The default value is ('x', 0, 0, 0, 0).
        """
        self.ipcon.send_request(self, BrickletJoystick.FUNCTION_SET_ANALOG_VALUE_CALLBACK_THRESHOLD, (option, min_x, max_x, min_y, max_y), 'c H H H H', '')

    def get_analog_value_callback_threshold(self):
        """
        Returns the threshold as set by :func:`SetAnalogValueCallbackThreshold`.
        """
        return GetAnalogValueCallbackThreshold(*self.ipcon.send_request(self, BrickletJoystick.FUNCTION_GET_ANALOG_VALUE_CALLBACK_THRESHOLD, (), '', 'c H H H H'))

    def set_debounce_period(self, debounce):
        """
        Sets the period in ms with which the threshold callbacks
        
        * :func:`PositionReached`,
        * :func:`AnalogValueReached`
        
        are triggered, if the thresholds
        
        * :func:`SetPositionCallbackThreshold`,
        * :func:`SetAnalogValueCallbackThreshold`
        
        keep being reached.
        
        The default value is 100.
        """
        self.ipcon.send_request(self, BrickletJoystick.FUNCTION_SET_DEBOUNCE_PERIOD, (debounce,), 'I', '')

    def get_debounce_period(self):
        """
        Returns the debounce period as set by :func:`SetDebouncePeriod`.
        """
        return self.ipcon.send_request(self, BrickletJoystick.FUNCTION_GET_DEBOUNCE_PERIOD, (), '', 'I')

    def get_identity(self):
        """
        Returns the UID, the UID where the Bricklet is connected to, 
        the position, the hardware and firmware version as well as the
        device identifier.
        
        The position can be 'a', 'b', 'c' or 'd'.
        
        The device identifier numbers can be found :ref:`here <device_identifier>`.
        |device_identifier_constant|
        """
        return GetIdentity(*self.ipcon.send_request(self, BrickletJoystick.FUNCTION_GET_IDENTITY, (), '', '8s 8s c 3B 3B H'))

    def register_callback(self, id, callback):
        """
        Registers a callback with ID *id* to the function *callback*.
        """
        self.registered_callbacks[id] = callback

Joystick = BrickletJoystick # for backward compatibility
