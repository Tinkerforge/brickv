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

GetPortConfiguration = namedtuple('PortConfiguration', ['direction_mask', 'value_mask'])

class IO16(Device):
    CALLBACK_INTERRUPT = 9

    TYPE_SET_PORT = 1
    TYPE_GET_PORT = 2
    TYPE_SET_PORT_CONFIGURATION = 3
    TYPE_GET_PORT_CONFIGURATION = 4
    TYPE_SET_DEBOUNCE_PERIOD = 5
    TYPE_GET_DEBOUNCE_PERIOD = 6
    TYPE_SET_PORT_INTERRUPT = 7
    TYPE_GET_PORT_INTERRUPT = 8
    TYPE_INTERRUPT = 9

    def __init__(self, uid):
        Device.__init__(self, uid)

        self.callbacks_format[IO16.CALLBACK_INTERRUPT] = 'c B B'

    def set_port(self, port, value_mask):
        self.ipcon.write(self, IO16.TYPE_SET_PORT, (port, value_mask), 'c B', '')

    def get_port(self, port):
        return self.ipcon.write(self, IO16.TYPE_GET_PORT, (port,), 'c', 'B')

    def set_port_configuration(self, port, port_mask, direction, value):
        self.ipcon.write(self, IO16.TYPE_SET_PORT_CONFIGURATION, (port, port_mask, direction, value), 'c B c ?', '')

    def get_port_configuration(self, port):
        return GetPortConfiguration(*self.ipcon.write(self, IO16.TYPE_GET_PORT_CONFIGURATION, (port,), 'c', 'B B'))

    def set_debounce_period(self, debounce):
        self.ipcon.write(self, IO16.TYPE_SET_DEBOUNCE_PERIOD, (debounce,), 'I', '')

    def get_debounce_period(self):
        return self.ipcon.write(self, IO16.TYPE_GET_DEBOUNCE_PERIOD, (), '', 'I')

    def set_port_interrupt(self, port, interrupt_mask):
        self.ipcon.write(self, IO16.TYPE_SET_PORT_INTERRUPT, (port, interrupt_mask), 'c B', '')

    def get_port_interrupt(self, port):
        return self.ipcon.write(self, IO16.TYPE_GET_PORT_INTERRUPT, (port,), 'c', 'B')
