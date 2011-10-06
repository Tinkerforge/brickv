# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2011-10-06.      #
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

GetDistanceCallbackThreshold = namedtuple('DistanceCallbackThreshold', ['option', 'min', 'max'])
GetAnalogValueCallbackThreshold = namedtuple('AnalogValueCallbackThreshold', ['option', 'min', 'max'])
GetVersion = namedtuple('Version', ['name', 'firmware_version', 'binding_version'])

class DistanceIR(Device):
    CALLBACK_DISTANCE = 15
    CALLBACK_ANALOG_VALUE = 16
    CALLBACK_DISTANCE_REACHED = 17
    CALLBACK_ANALOG_VALUE_REACHED = 18

    TYPE_GET_DISTANCE = 1
    TYPE_GET_ANALOG_VALUE = 2
    TYPE_SET_SAMPLING_POINT = 3
    TYPE_GET_SAMPLING_POINT = 4
    TYPE_SET_DISTANCE_CALLBACK_PERIOD = 5
    TYPE_GET_DISTANCE_CALLBACK_PERIOD = 6
    TYPE_SET_ANALOG_VALUE_CALLBACK_PERIOD = 7
    TYPE_GET_ANALOG_VALUE_CALLBACK_PERIOD = 8
    TYPE_SET_DISTANCE_CALLBACK_THRESHOLD = 9
    TYPE_GET_DISTANCE_CALLBACK_THRESHOLD = 10
    TYPE_SET_ANALOG_VALUE_CALLBACK_THRESHOLD = 11
    TYPE_GET_ANALOG_VALUE_CALLBACK_THRESHOLD = 12
    TYPE_SET_DEBOUNCE_PERIOD = 13
    TYPE_GET_DEBOUNCE_PERIOD = 14
    TYPE_DISTANCE = 15
    TYPE_ANALOG_VALUE = 16
    TYPE_DISTANCE_REACHED = 17
    TYPE_ANALOG_VALUE_REACHED = 18

    def __init__(self, uid):
        Device.__init__(self, uid)

        self.binding_version = [1, 0, 0]

        self.callbacks_format[DistanceIR.CALLBACK_DISTANCE] = 'H'
        self.callbacks_format[DistanceIR.CALLBACK_ANALOG_VALUE] = 'H'
        self.callbacks_format[DistanceIR.CALLBACK_DISTANCE_REACHED] = 'H'
        self.callbacks_format[DistanceIR.CALLBACK_ANALOG_VALUE_REACHED] = 'H'

    def get_version(self):
        return GetVersion(self.name, self.firmware_version, self.binding_version)

    def get_distance(self):
        return self.ipcon.write(self, DistanceIR.TYPE_GET_DISTANCE, (), '', 'H')

    def get_analog_value(self):
        return self.ipcon.write(self, DistanceIR.TYPE_GET_ANALOG_VALUE, (), '', 'H')

    def set_sampling_point(self, position, distance):
        self.ipcon.write(self, DistanceIR.TYPE_SET_SAMPLING_POINT, (position, distance), 'B H', '')

    def get_sampling_point(self, position):
        return self.ipcon.write(self, DistanceIR.TYPE_GET_SAMPLING_POINT, (position,), 'B', 'H')

    def set_distance_callback_period(self, period):
        self.ipcon.write(self, DistanceIR.TYPE_SET_DISTANCE_CALLBACK_PERIOD, (period,), 'I', '')

    def get_distance_callback_period(self):
        return self.ipcon.write(self, DistanceIR.TYPE_GET_DISTANCE_CALLBACK_PERIOD, (), '', 'I')

    def set_analog_value_callback_period(self, period):
        self.ipcon.write(self, DistanceIR.TYPE_SET_ANALOG_VALUE_CALLBACK_PERIOD, (period,), 'I', '')

    def get_analog_value_callback_period(self):
        return self.ipcon.write(self, DistanceIR.TYPE_GET_ANALOG_VALUE_CALLBACK_PERIOD, (), '', 'I')

    def set_distance_callback_threshold(self, option, min, max):
        self.ipcon.write(self, DistanceIR.TYPE_SET_DISTANCE_CALLBACK_THRESHOLD, (option, min, max), 'c h h', '')

    def get_distance_callback_threshold(self):
        return GetDistanceCallbackThreshold(*self.ipcon.write(self, DistanceIR.TYPE_GET_DISTANCE_CALLBACK_THRESHOLD, (), '', 'c h h'))

    def set_analog_value_callback_threshold(self, option, min, max):
        self.ipcon.write(self, DistanceIR.TYPE_SET_ANALOG_VALUE_CALLBACK_THRESHOLD, (option, min, max), 'c H H', '')

    def get_analog_value_callback_threshold(self):
        return GetAnalogValueCallbackThreshold(*self.ipcon.write(self, DistanceIR.TYPE_GET_ANALOG_VALUE_CALLBACK_THRESHOLD, (), '', 'c H H'))

    def set_debounce_period(self, debounce):
        self.ipcon.write(self, DistanceIR.TYPE_SET_DEBOUNCE_PERIOD, (debounce,), 'I', '')

    def get_debounce_period(self):
        return self.ipcon.write(self, DistanceIR.TYPE_GET_DEBOUNCE_PERIOD, (), '', 'I')
