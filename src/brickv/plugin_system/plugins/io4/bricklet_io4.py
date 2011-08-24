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

GetConfiguration = namedtuple('Configuration', ['direction_mask', 'value_mask'])

class IO4(Device):
    CALLBACK_INTERRUPT = 9

    TYPE_SET_VALUE = 1
    TYPE_GET_VALUE = 2
    TYPE_SET_CONFIGURATION = 3
    TYPE_GET_CONFIGURATION = 4
    TYPE_SET_DEBOUNCE_PERIOD = 5
    TYPE_GET_DEBOUNCE_PERIOD = 6
    TYPE_SET_INTERRUPT = 7
    TYPE_GET_INTERRUPT = 8
    TYPE_INTERRUPT = 9

    def __init__(self, uid):
        Device.__init__(self, uid)

        self.callbacks_format[IO4.CALLBACK_INTERRUPT] = 'B B'

    def set_value(self, value_mask):
        self.ipcon.write(self, IO4.TYPE_SET_VALUE, (value_mask,), 'B', '')

    def get_value(self):
        return self.ipcon.write(self, IO4.TYPE_GET_VALUE, (), '', 'B')

    def set_configuration(self, pin_mask, direction, value):
        self.ipcon.write(self, IO4.TYPE_SET_CONFIGURATION, (pin_mask, direction, value), 'B c ?', '')

    def get_configuration(self):
        return GetConfiguration(*self.ipcon.write(self, IO4.TYPE_GET_CONFIGURATION, (), '', 'B B'))

    def set_debounce_period(self, debounce):
        self.ipcon.write(self, IO4.TYPE_SET_DEBOUNCE_PERIOD, (debounce,), 'I', '')

    def get_debounce_period(self):
        return self.ipcon.write(self, IO4.TYPE_GET_DEBOUNCE_PERIOD, (), '', 'I')

    def set_interrupt(self, interrupt_mask):
        self.ipcon.write(self, IO4.TYPE_SET_INTERRUPT, (interrupt_mask,), 'B', '')

    def get_interrupt(self):
        return self.ipcon.write(self, IO4.TYPE_GET_INTERRUPT, (), '', 'B')
