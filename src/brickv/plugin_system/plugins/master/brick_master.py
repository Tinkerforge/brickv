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

GetVersion = namedtuple('Version', ['name', 'firmware_version', 'binding_version'])

class Master(Device):

    TYPE_GET_STACK_VOLTAGE = 1
    TYPE_GET_STACK_CURRENT = 2

    def __init__(self, uid):
        Device.__init__(self, uid)

        self.binding_version = [1, 0, 0]


    def get_version(self):
        return GetVersion(self.name, self.firmware_version, self.binding_version)

    def get_stack_voltage(self):
        return self.ipcon.write(self, Master.TYPE_GET_STACK_VOLTAGE, (), '', 'H')

    def get_stack_current(self):
        return self.ipcon.write(self, Master.TYPE_GET_STACK_CURRENT, (), '', 'H')
