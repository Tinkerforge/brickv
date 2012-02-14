# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2012-01-15.      #
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

GetVersion = namedtuple('Version', ['name', 'firmware_version', 'binding_version'])

class AnalogOut(Device):

    TYPE_SET_VOLTAGE = 1
    TYPE_GET_VOLTAGE = 2
    TYPE_SET_MODE = 3
    TYPE_GET_MODE = 4

    def __init__(self, uid):
        Device.__init__(self, uid)

        self.binding_version = [1, 0, 0]


    def get_version(self):
        return GetVersion(self.name, self.firmware_version, self.binding_version)

    def set_voltage(self, voltage):
        self.ipcon.write(self, AnalogOut.TYPE_SET_VOLTAGE, (voltage,), 'H', '')

    def get_voltage(self):
        return self.ipcon.write(self, AnalogOut.TYPE_GET_VOLTAGE, (), '', 'H')

    def set_mode(self, mode):
        self.ipcon.write(self, AnalogOut.TYPE_SET_MODE, (mode,), 'B', '')

    def get_mode(self):
        return self.ipcon.write(self, AnalogOut.TYPE_GET_MODE, (), '', 'B')
