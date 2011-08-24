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

GetAmbientTemperatureCallbackThreshold = namedtuple('AmbientTemperatureCallbackThreshold', ['option', 'min', 'max'])
GetObjectTemperatureCallbackThreshold = namedtuple('ObjectTemperatureCallbackThreshold', ['option', 'min', 'max'])

class TemperatureIR(Device):
    CALLBACK_AMBIENT_TEMPERATURE = 15
    CALLBACK_OBJECT_TEMPERATURE = 16
    CALLBACK_AMBIENT_TEMPERATURE_REACHED = 17
    CALLBACK_OBJECT_TEMPERATURE_REACHED = 18

    TYPE_GET_AMBIENT_TEMPERATURE = 1
    TYPE_GET_OBJECT_TEMPERATURE = 2
    TYPE_SET_EMISSIVITY = 3
    TYPE_GET_EMISSIVITY = 4
    TYPE_SET_AMBIENT_TEMPERATURE_CALLBACK_PERIOD = 5
    TYPE_GET_AMBIENT_TEMPERATURE_CALLBACK_PERIOD = 6
    TYPE_SET_OBJECT_TEMPERATURE_CALLBACK_PERIOD = 7
    TYPE_GET_OBJECT_TEMPERATURE_CALLBACK_PERIOD = 8
    TYPE_SET_AMBIENT_TEMPERATURE_CALLBACK_THRESHOLD = 9
    TYPE_GET_AMBIENT_TEMPERATURE_CALLBACK_THRESHOLD = 10
    TYPE_SET_OBJECT_TEMPERATURE_CALLBACK_THRESHOLD = 11
    TYPE_GET_OBJECT_TEMPERATURE_CALLBACK_THRESHOLD = 12
    TYPE_SET_DEBOUNCE_PERIOD = 13
    TYPE_GET_DEBOUNCE_PERIOD = 14
    TYPE_AMBIENT_TEMPERATURE = 15
    TYPE_OBJECT_TEMPERATURE = 16
    TYPE_AMBIENT_TEMPERATURE_REACHED = 17
    TYPE_OBJECT_TEMPERATURE_REACHED = 18

    def __init__(self, uid):
        Device.__init__(self, uid)

        self.callbacks_format[TemperatureIR.CALLBACK_AMBIENT_TEMPERATURE] = 'h'
        self.callbacks_format[TemperatureIR.CALLBACK_OBJECT_TEMPERATURE] = 'h'
        self.callbacks_format[TemperatureIR.CALLBACK_AMBIENT_TEMPERATURE_REACHED] = 'h'
        self.callbacks_format[TemperatureIR.CALLBACK_OBJECT_TEMPERATURE_REACHED] = 'h'

    def get_ambient_temperature(self):
        return self.ipcon.write(self, TemperatureIR.TYPE_GET_AMBIENT_TEMPERATURE, (), '', 'h')

    def get_object_temperature(self):
        return self.ipcon.write(self, TemperatureIR.TYPE_GET_OBJECT_TEMPERATURE, (), '', 'h')

    def set_emissivity(self, emissivity):
        self.ipcon.write(self, TemperatureIR.TYPE_SET_EMISSIVITY, (emissivity,), 'H', '')

    def get_emissivity(self):
        return self.ipcon.write(self, TemperatureIR.TYPE_GET_EMISSIVITY, (), '', 'H')

    def set_ambient_temperature_callback_period(self, period):
        self.ipcon.write(self, TemperatureIR.TYPE_SET_AMBIENT_TEMPERATURE_CALLBACK_PERIOD, (period,), 'I', '')

    def get_ambient_temperature_callback_period(self):
        return self.ipcon.write(self, TemperatureIR.TYPE_GET_AMBIENT_TEMPERATURE_CALLBACK_PERIOD, (), '', 'I')

    def set_object_temperature_callback_period(self, period):
        self.ipcon.write(self, TemperatureIR.TYPE_SET_OBJECT_TEMPERATURE_CALLBACK_PERIOD, (period,), 'I', '')

    def get_object_temperature_callback_period(self):
        return self.ipcon.write(self, TemperatureIR.TYPE_GET_OBJECT_TEMPERATURE_CALLBACK_PERIOD, (), '', 'I')

    def set_ambient_temperature_callback_threshold(self, option, min, max):
        self.ipcon.write(self, TemperatureIR.TYPE_SET_AMBIENT_TEMPERATURE_CALLBACK_THRESHOLD, (option, min, max), 'c h h', '')

    def get_ambient_temperature_callback_threshold(self):
        return GetAmbientTemperatureCallbackThreshold(*self.ipcon.write(self, TemperatureIR.TYPE_GET_AMBIENT_TEMPERATURE_CALLBACK_THRESHOLD, (), '', 'c h h'))

    def set_object_temperature_callback_threshold(self, option, min, max):
        self.ipcon.write(self, TemperatureIR.TYPE_SET_OBJECT_TEMPERATURE_CALLBACK_THRESHOLD, (option, min, max), 'c h h', '')

    def get_object_temperature_callback_threshold(self):
        return GetObjectTemperatureCallbackThreshold(*self.ipcon.write(self, TemperatureIR.TYPE_GET_OBJECT_TEMPERATURE_CALLBACK_THRESHOLD, (), '', 'c h h'))

    def set_debounce_period(self, debounce):
        self.ipcon.write(self, TemperatureIR.TYPE_SET_DEBOUNCE_PERIOD, (debounce,), 'I', '')

    def get_debounce_period(self):
        return self.ipcon.write(self, TemperatureIR.TYPE_GET_DEBOUNCE_PERIOD, (), '', 'I')
