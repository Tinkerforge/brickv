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

GetTemperatureCallbackThreshold = namedtuple('TemperatureCallbackThreshold', ['option', 'min', 'max'])

class Temperature(Device):
    CALLBACK_TEMPERATURE = 8
    CALLBACK_TEMPERATURE_REACHED = 9

    TYPE_GET_TEMPERATURE = 1
    TYPE_SET_TEMPERATURE_CALLBACK_PERIOD = 2
    TYPE_GET_TEMPERATURE_CALLBACK_PERIOD = 3
    TYPE_SET_TEMPERATURE_CALLBACK_THRESHOLD = 4
    TYPE_GET_TEMPERATURE_CALLBACK_THRESHOLD = 5
    TYPE_SET_DEBOUNCE_PERIOD = 6
    TYPE_GET_DEBOUNCE_PERIOD = 7
    TYPE_TEMPERATURE = 8
    TYPE_TEMPERATURE_REACHED = 9

    def __init__(self, uid):
        Device.__init__(self, uid)

        self.callbacks_format[Temperature.CALLBACK_TEMPERATURE] = 'h'
        self.callbacks_format[Temperature.CALLBACK_TEMPERATURE_REACHED] = 'h'

    def get_temperature(self):
        return self.ipcon.write(self, Temperature.TYPE_GET_TEMPERATURE, (), '', 'h')

    def set_temperature_callback_period(self, period):
        self.ipcon.write(self, Temperature.TYPE_SET_TEMPERATURE_CALLBACK_PERIOD, (period,), 'I', '')

    def get_temperature_callback_period(self):
        return self.ipcon.write(self, Temperature.TYPE_GET_TEMPERATURE_CALLBACK_PERIOD, (), '', 'I')

    def set_temperature_callback_threshold(self, option, min, max):
        self.ipcon.write(self, Temperature.TYPE_SET_TEMPERATURE_CALLBACK_THRESHOLD, (option, min, max), 'c h h', '')

    def get_temperature_callback_threshold(self):
        return GetTemperatureCallbackThreshold(*self.ipcon.write(self, Temperature.TYPE_GET_TEMPERATURE_CALLBACK_THRESHOLD, (), '', 'c h h'))

    def set_debounce_period(self, debounce):
        self.ipcon.write(self, Temperature.TYPE_SET_DEBOUNCE_PERIOD, (debounce,), 'I', '')

    def get_debounce_period(self):
        return self.ipcon.write(self, Temperature.TYPE_GET_DEBOUNCE_PERIOD, (), '', 'I')
