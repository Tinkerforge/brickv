# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2011-08-23.      #
#                                                           #
# If you have a bugfix for this file and want to commit it, #
# please fix the bug in the generator. You can find a link  #
# to the generator git on tinkerforge.com                   #
#############################################################

try:
    from collections import namedtuple
except ImportError:
    from ip_connection import namedtuple
from ip_connection import Device, IPConnection, Error

GetPosition = namedtuple('Position', ['x', 'y'])
GetAnalogValue = namedtuple('AnalogValue', ['x', 'y'])
GetPositionCallbackThreshold = namedtuple('PositionCallbackThreshold', ['option', 'min_x', 'max_x', 'min_y', 'max_y'])
GetAnalogValueCallbackThreshold = namedtuple('AnalogValueCallbackThreshold', ['option', 'min_x', 'max_x', 'min_y', 'max_y'])

class Joystick(Device):
    CALLBACK_POSITION = 15
    CALLBACK_ANALOG_VALUE = 16
    CALLBACK_POSITION_REACHED = 17
    CALLBACK_ANALOG_VALUE_REACHED = 18
    CALLBACK_PRESSED = 19
    CALLBACK_RELEASED = 20

    TYPE_GET_POSITION = 1
    TYPE_IS_PRESSED = 2
    TYPE_GET_ANALOG_VALUE = 3
    TYPE_CALIBRATE = 4
    TYPE_SET_POSITION_CALLBACK_PERIOD = 5
    TYPE_GET_POSITION_CALLBACK_PERIOD = 6
    TYPE_SET_ANALOG_VALUE_CALLBACK_PERIOD = 7
    TYPE_GET_ANALOG_VALUE_CALLBACK_PERIOD = 8
    TYPE_SET_POSITION_CALLBACK_THRESHOLD = 9
    TYPE_GET_POSITION_CALLBACK_THRESHOLD = 10
    TYPE_SET_ANALOG_VALUE_CALLBACK_THRESHOLD = 11
    TYPE_GET_ANALOG_VALUE_CALLBACK_THRESHOLD = 12
    TYPE_SET_DEBOUNCE_PERIOD = 13
    TYPE_GET_DEBOUNCE_PERIOD = 14
    TYPE_POSITION = 15
    TYPE_ANALOG_VALUE = 16
    TYPE_POSITION_REACHED = 17
    TYPE_ANALOG_VALUE_REACHED = 18
    TYPE_PRESSED = 19
    TYPE_RELEASED = 20

    def __init__(self, uid):
        Device.__init__(self, uid)

        self.callbacks_format[Joystick.CALLBACK_POSITION] = 'h h'
        self.callbacks_format[Joystick.CALLBACK_ANALOG_VALUE] = 'H H'
        self.callbacks_format[Joystick.CALLBACK_POSITION_REACHED] = 'h h'
        self.callbacks_format[Joystick.CALLBACK_ANALOG_VALUE_REACHED] = 'H H'
        self.callbacks_format[Joystick.CALLBACK_PRESSED] = ''
        self.callbacks_format[Joystick.CALLBACK_RELEASED] = ''

    def get_position(self):
        return GetPosition(*self.ipcon.write(self, Joystick.TYPE_GET_POSITION, (), '', 'h h'))

    def is_pressed(self):
        return self.ipcon.write(self, Joystick.TYPE_IS_PRESSED, (), '', '?')

    def get_analog_value(self):
        return GetAnalogValue(*self.ipcon.write(self, Joystick.TYPE_GET_ANALOG_VALUE, (), '', 'H H'))

    def calibrate(self):
        self.ipcon.write(self, Joystick.TYPE_CALIBRATE, (), '', '')

    def set_position_callback_period(self, period):
        self.ipcon.write(self, Joystick.TYPE_SET_POSITION_CALLBACK_PERIOD, (period,), 'I', '')

    def get_position_callback_period(self):
        return self.ipcon.write(self, Joystick.TYPE_GET_POSITION_CALLBACK_PERIOD, (), '', 'I')

    def set_analog_value_callback_period(self, period):
        self.ipcon.write(self, Joystick.TYPE_SET_ANALOG_VALUE_CALLBACK_PERIOD, (period,), 'I', '')

    def get_analog_value_callback_period(self):
        return self.ipcon.write(self, Joystick.TYPE_GET_ANALOG_VALUE_CALLBACK_PERIOD, (), '', 'I')

    def set_position_callback_threshold(self, option, min_x, max_x, min_y, max_y):
        self.ipcon.write(self, Joystick.TYPE_SET_POSITION_CALLBACK_THRESHOLD, (option, min_x, max_x, min_y, max_y), 'c h h h h', '')

    def get_position_callback_threshold(self):
        return GetPositionCallbackThreshold(*self.ipcon.write(self, Joystick.TYPE_GET_POSITION_CALLBACK_THRESHOLD, (), '', 'c h h h h'))

    def set_analog_value_callback_threshold(self, option, min_x, max_x, min_y, max_y):
        self.ipcon.write(self, Joystick.TYPE_SET_ANALOG_VALUE_CALLBACK_THRESHOLD, (option, min_x, max_x, min_y, max_y), 'c H H H H', '')

    def get_analog_value_callback_threshold(self):
        return GetAnalogValueCallbackThreshold(*self.ipcon.write(self, Joystick.TYPE_GET_ANALOG_VALUE_CALLBACK_THRESHOLD, (), '', 'c H H H H'))

    def set_debounce_period(self, debounce):
        self.ipcon.write(self, Joystick.TYPE_SET_DEBOUNCE_PERIOD, (debounce,), 'I', '')

    def get_debounce_period(self):
        return self.ipcon.write(self, Joystick.TYPE_GET_DEBOUNCE_PERIOD, (), '', 'I')
