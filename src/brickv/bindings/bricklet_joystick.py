# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2012-05-18.      #
#                                                           #
# If you have a bugfix for this file and want to commit it, #
# please fix the bug in the generator. You can find a link  #
# to the generator git on tinkerforge.com                   #
#############################################################

try:
    from collections import namedtuple
except ImportError:
    from .ip_connection import namedtuple
from .ip_connection import Device, IPConnection, Error

GetPosition = namedtuple('Position', ['x', 'y'])
GetAnalogValue = namedtuple('AnalogValue', ['x', 'y'])
GetPositionCallbackThreshold = namedtuple('PositionCallbackThreshold', ['option', 'min_x', 'max_x', 'min_y', 'max_y'])
GetAnalogValueCallbackThreshold = namedtuple('AnalogValueCallbackThreshold', ['option', 'min_x', 'max_x', 'min_y', 'max_y'])

class Joystick(Device):
    """
    Dual-Axis Joystick with Button
    """

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

    def __init__(self, uid):
        """
        Creates an object with the unique device ID *uid*. This object can
        then be added to the IP connection.
        """
        Device.__init__(self, uid)

        self.expected_name = 'Joystick Bricklet';

        self.binding_version = [1, 0, 0]

        self.callbacks_format[Joystick.CALLBACK_POSITION] = 'h h'
        self.callbacks_format[Joystick.CALLBACK_ANALOG_VALUE] = 'H H'
        self.callbacks_format[Joystick.CALLBACK_POSITION_REACHED] = 'h h'
        self.callbacks_format[Joystick.CALLBACK_ANALOG_VALUE_REACHED] = 'H H'
        self.callbacks_format[Joystick.CALLBACK_PRESSED] = ''
        self.callbacks_format[Joystick.CALLBACK_RELEASED] = ''

    def get_position(self):
        """
        Returns the position of the Joystick. The value ranges between -100 and
        100 for both axis. The middle position of the joystick is x=0, y=0. The
        returned values are averaged and calibrated (see :func:`Calibrate`).
        
        If you want to get the position periodically, it is recommended to use the
        callback :func:`Position` and set the period with 
        :func:`SetPositionCallbackPeriod`.
        """
        return GetPosition(*self.ipcon.write(self, Joystick.FUNCTION_GET_POSITION, (), '', 'h h'))

    def is_pressed(self):
        """
        Returns true if the button is pressed and false otherwise.
        
        It is recommended to use the :func:`Pressed` and :func:`Released` callbacks
        to handle the button.
        """
        return self.ipcon.write(self, Joystick.FUNCTION_IS_PRESSED, (), '', '?')

    def get_analog_value(self):
        """
        Returns the values as read by a 12 bit analog to digital converter.
        The values are between 0 and 4095 for both axis.
        
         .. note::
          The values returned by :func:`GetPosition` are averaged over several samples
          to yield less noise, while :func:`GetAnalogValue` gives back raw
          unfiltered analog values. The only reason to use :func:`GetAnalogValue` is,
          if you need the full resolution of the analog to digital converter.
        
        If you want the analog values periodically, it is recommended to use the 
        callback :func:`AnalogValue` and set the period with 
        :func:`SetAnalogValueCallbackPeriod`.
        """
        return GetAnalogValue(*self.ipcon.write(self, Joystick.FUNCTION_GET_ANALOG_VALUE, (), '', 'H H'))

    def calibrate(self):
        """
        Calibrates the middle position of the Joystick. If your Joystick Bricklet
        does not return x=0 and y=0 in the middle position, call this function
        while the Joystick is standing still in the middle position.
        
        The resulting calibration will be saved on the EEPROM of the Joystick
        Bricklet, thus you only have to calibrate it once.
        """
        self.ipcon.write(self, Joystick.FUNCTION_CALIBRATE, (), '', '')

    def set_position_callback_period(self, period):
        """
        Sets the period in ms with which the :func:`Position` callback is triggered
        periodically. A value of 0 turns the callback off.
        
        :func:`Position` is only triggered if the position has changed since the
        last triggering.
        
        The default value is 0.
        """
        self.ipcon.write(self, Joystick.FUNCTION_SET_POSITION_CALLBACK_PERIOD, (period,), 'I', '')

    def get_position_callback_period(self):
        """
        Returns the period as set by :func:`SetPositionCallbackPeriod`.
        """
        return self.ipcon.write(self, Joystick.FUNCTION_GET_POSITION_CALLBACK_PERIOD, (), '', 'I')

    def set_analog_value_callback_period(self, period):
        """
        Sets the period in ms with which the :func:`AnalogValue` callback is triggered
        periodically. A value of 0 turns the callback off.
        
        :func:`AnalogValue` is only triggered if the analog value has changed since the
        last triggering.
        
        The default value is 0.
        """
        self.ipcon.write(self, Joystick.FUNCTION_SET_ANALOG_VALUE_CALLBACK_PERIOD, (period,), 'I', '')

    def get_analog_value_callback_period(self):
        """
        Returns the period as set by :func:`SetAnalogValueCallbackPeriod`.
        """
        return self.ipcon.write(self, Joystick.FUNCTION_GET_ANALOG_VALUE_CALLBACK_PERIOD, (), '', 'I')

    def set_position_callback_threshold(self, option, min_x, max_x, min_y, max_y):
        """
        Sets the thresholds for the :func:`PositionReached` callback. 
        
        The following options are possible:
        
        .. csv-table::
         :header: "Option", "Description"
         :widths: 10, 100
        
         "'x'", "Callback is turned off."
         "'o'", "Callback is triggered when the position is *outside* the min and max values"
         "'i'", "Callback is triggered when the position is *inside* the min and max values"
         "'<'", "Callback is triggered when the position is smaller than the min value (max is ignored)"
         "'>'", "Callback is triggered when the position is greater than the min value (max is ignored)"
        
        The default value is ('x', 0, 0, 0, 0).
        """
        self.ipcon.write(self, Joystick.FUNCTION_SET_POSITION_CALLBACK_THRESHOLD, (option, min_x, max_x, min_y, max_y), 'c h h h h', '')

    def get_position_callback_threshold(self):
        """
        Returns the threshold as set by :func:`SetPositionCallbackThreshold`.
        """
        return GetPositionCallbackThreshold(*self.ipcon.write(self, Joystick.FUNCTION_GET_POSITION_CALLBACK_THRESHOLD, (), '', 'c h h h h'))

    def set_analog_value_callback_threshold(self, option, min_x, max_x, min_y, max_y):
        """
        Sets the thresholds for the :func:`AnalogValueReached` callback. 
        
        The following options are possible:
        
        .. csv-table::
         :header: "Option", "Description"
         :widths: 10, 100
        
         "'x'", "Callback is turned off."
         "'o'", "Callback is triggered when the position is *outside* the min and max values"
         "'i'", "Callback is triggered when the position is *inside* the min and max values"
         "'<'", "Callback is triggered when the position is smaller than the min value (max is ignored)"
         "'>'", "Callback is triggered when the position is greater than the min value (max is ignored)"
        
        The default value is ('x', 0, 0, 0, 0).
        """
        self.ipcon.write(self, Joystick.FUNCTION_SET_ANALOG_VALUE_CALLBACK_THRESHOLD, (option, min_x, max_x, min_y, max_y), 'c H H H H', '')

    def get_analog_value_callback_threshold(self):
        """
        Returns the threshold as set by :func:`SetAnalogValueCallbackThreshold`.
        """
        return GetAnalogValueCallbackThreshold(*self.ipcon.write(self, Joystick.FUNCTION_GET_ANALOG_VALUE_CALLBACK_THRESHOLD, (), '', 'c H H H H'))

    def set_debounce_period(self, debounce):
        """
        Sets the period in ms with which the threshold callbacks
        
         :func:`PositionReached`, :func:`AnalogValueReached`
        
        are triggered, if the thresholds
        
         :func:`SetPositionCallbackThreshold`, :func:`SetAnalogValueCallbackThreshold`
        
        keep being reached.
        
        The default value is 100.
        """
        self.ipcon.write(self, Joystick.FUNCTION_SET_DEBOUNCE_PERIOD, (debounce,), 'I', '')

    def get_debounce_period(self):
        """
        Returns the debounce period as set by :func:`SetDebouncePeriod`.
        """
        return self.ipcon.write(self, Joystick.FUNCTION_GET_DEBOUNCE_PERIOD, (), '', 'I')

    def register_callback(self, cb, func):
        """
        Registers a callback with ID cb to the function func.
        """
        self.callbacks[cb] = func
