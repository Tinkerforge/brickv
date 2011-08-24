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

GetIlluminanceCallbackThreshold = namedtuple('IlluminanceCallbackThreshold', ['option', 'min', 'max'])
GetAnalogValueCallbackThreshold = namedtuple('AnalogValueCallbackThreshold', ['option', 'min', 'max'])

class AmbientLight(Device):
    CALLBACK_ILLUMINANCE = 13
    CALLBACK_ANALOG_VALUE = 14
    CALLBACK_ILLUMINANCE_REACHED = 15
    CALLBACK_ANALOG_VALUE_REACHED = 16

    TYPE_GET_ILLUMINANCE = 1
    TYPE_GET_ANALOG_VALUE = 2
    TYPE_SET_ILLUMINANCE_CALLBACK_PERIOD = 3
    TYPE_GET_ILLUMINANCE_CALLBACK_PERIOD = 4
    TYPE_SET_ANALOG_VALUE_CALLBACK_PERIOD = 5
    TYPE_GET_ANALOG_VALUE_CALLBACK_PERIOD = 6
    TYPE_SET_ILLUMINANCE_CALLBACK_THRESHOLD = 7
    TYPE_GET_ILLUMINANCE_CALLBACK_THRESHOLD = 8
    TYPE_SET_ANALOG_VALUE_CALLBACK_THRESHOLD = 9
    TYPE_GET_ANALOG_VALUE_CALLBACK_THRESHOLD = 10
    TYPE_SET_DEBOUNCE_PERIOD = 11
    TYPE_GET_DEBOUNCE_PERIOD = 12
    TYPE_ILLUMINANCE = 13
    TYPE_ANALOG_VALUE = 14
    TYPE_ILLUMINANCE_REACHED = 15
    TYPE_ANALOG_VALUE_REACHED = 16

    def __init__(self, uid):
        Device.__init__(self, uid)

        self.callbacks_format[AmbientLight.CALLBACK_ILLUMINANCE] = 'H'
        self.callbacks_format[AmbientLight.CALLBACK_ANALOG_VALUE] = 'H'
        self.callbacks_format[AmbientLight.CALLBACK_ILLUMINANCE_REACHED] = 'H'
        self.callbacks_format[AmbientLight.CALLBACK_ANALOG_VALUE_REACHED] = 'H'

    def get_illuminance(self):
        return self.ipcon.write(self, AmbientLight.TYPE_GET_ILLUMINANCE, (), '', 'H')

    def get_analog_value(self):
        return self.ipcon.write(self, AmbientLight.TYPE_GET_ANALOG_VALUE, (), '', 'H')

    def set_illuminance_callback_period(self, period):
        self.ipcon.write(self, AmbientLight.TYPE_SET_ILLUMINANCE_CALLBACK_PERIOD, (period,), 'I', '')

    def get_illuminance_callback_period(self):
        return self.ipcon.write(self, AmbientLight.TYPE_GET_ILLUMINANCE_CALLBACK_PERIOD, (), '', 'I')

    def set_analog_value_callback_period(self, period):
        self.ipcon.write(self, AmbientLight.TYPE_SET_ANALOG_VALUE_CALLBACK_PERIOD, (period,), 'I', '')

    def get_analog_value_callback_period(self):
        return self.ipcon.write(self, AmbientLight.TYPE_GET_ANALOG_VALUE_CALLBACK_PERIOD, (), '', 'I')

    def set_illuminance_callback_threshold(self, option, min, max):
        self.ipcon.write(self, AmbientLight.TYPE_SET_ILLUMINANCE_CALLBACK_THRESHOLD, (option, min, max), 'c h h', '')

    def get_illuminance_callback_threshold(self):
        return GetIlluminanceCallbackThreshold(*self.ipcon.write(self, AmbientLight.TYPE_GET_ILLUMINANCE_CALLBACK_THRESHOLD, (), '', 'c h h'))

    def set_analog_value_callback_threshold(self, option, min, max):
        self.ipcon.write(self, AmbientLight.TYPE_SET_ANALOG_VALUE_CALLBACK_THRESHOLD, (option, min, max), 'c H H', '')

    def get_analog_value_callback_threshold(self):
        return GetAnalogValueCallbackThreshold(*self.ipcon.write(self, AmbientLight.TYPE_GET_ANALOG_VALUE_CALLBACK_THRESHOLD, (), '', 'c H H'))

    def set_debounce_period(self, debounce):
        self.ipcon.write(self, AmbientLight.TYPE_SET_DEBOUNCE_PERIOD, (debounce,), 'I', '')

    def get_debounce_period(self):
        return self.ipcon.write(self, AmbientLight.TYPE_GET_DEBOUNCE_PERIOD, (), '', 'I')
