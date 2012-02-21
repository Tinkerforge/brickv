# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2012-02-21.      #
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

GetChibiErrorLog = namedtuple('ChibiErrorLog', ['underrun', 'crc_error', 'no_ack', 'overflow'])
GetVersion = namedtuple('Version', ['name', 'firmware_version', 'binding_version'])

class Master(Device):

    TYPE_GET_STACK_VOLTAGE = 1
    TYPE_GET_STACK_CURRENT = 2
    TYPE_SET_EXTENSION_TYPE = 3
    TYPE_GET_EXTENSION_TYPE = 4
    TYPE_IS_CHIBI_PRESENT = 5
    TYPE_SET_CHIBI_ADDRESS = 6
    TYPE_GET_CHIBI_ADDRESS = 7
    TYPE_SET_CHIBI_MASTER_ADDRESS = 8
    TYPE_GET_CHIBI_MASTER_ADDRESS = 9
    TYPE_SET_CHIBI_SLAVE_ADDRESS = 10
    TYPE_GET_CHIBI_SLAVE_ADDRESS = 11
    TYPE_GET_CHIBI_SIGNAL_STRENGTH = 12
    TYPE_GET_CHIBI_ERROR_LOG = 13
    TYPE_SET_CHIBI_FREQUENCY = 14
    TYPE_GET_CHIBI_FREQUENCY = 15
    TYPE_SET_CHIBI_CHANNEL = 16
    TYPE_GET_CHIBI_CHANNEL = 17

    def __init__(self, uid):
        Device.__init__(self, uid)

        self.binding_version = [1, 1, 0]


    def get_version(self):
        return GetVersion(self.name, self.firmware_version, self.binding_version)

    def get_stack_voltage(self):
        return self.ipcon.write(self, Master.TYPE_GET_STACK_VOLTAGE, (), '', 'H')

    def get_stack_current(self):
        return self.ipcon.write(self, Master.TYPE_GET_STACK_CURRENT, (), '', 'H')

    def set_extension_type(self, extension, exttype):
        self.ipcon.write(self, Master.TYPE_SET_EXTENSION_TYPE, (extension, exttype), 'B I', '')

    def get_extension_type(self, extension):
        return self.ipcon.write(self, Master.TYPE_GET_EXTENSION_TYPE, (extension,), 'B', 'I')

    def is_chibi_present(self):
        return self.ipcon.write(self, Master.TYPE_IS_CHIBI_PRESENT, (), '', '?')

    def set_chibi_address(self, address):
        self.ipcon.write(self, Master.TYPE_SET_CHIBI_ADDRESS, (address,), 'B', '')

    def get_chibi_address(self):
        return self.ipcon.write(self, Master.TYPE_GET_CHIBI_ADDRESS, (), '', 'B')

    def set_chibi_master_address(self, address):
        self.ipcon.write(self, Master.TYPE_SET_CHIBI_MASTER_ADDRESS, (address,), 'B', '')

    def get_chibi_master_address(self):
        return self.ipcon.write(self, Master.TYPE_GET_CHIBI_MASTER_ADDRESS, (), '', 'B')

    def set_chibi_slave_address(self, num, address):
        self.ipcon.write(self, Master.TYPE_SET_CHIBI_SLAVE_ADDRESS, (num, address), 'B B', '')

    def get_chibi_slave_address(self, num):
        return self.ipcon.write(self, Master.TYPE_GET_CHIBI_SLAVE_ADDRESS, (num,), 'B', 'B')

    def get_chibi_signal_strength(self):
        return self.ipcon.write(self, Master.TYPE_GET_CHIBI_SIGNAL_STRENGTH, (), '', 'B')

    def get_chibi_error_log(self):
        return GetChibiErrorLog(*self.ipcon.write(self, Master.TYPE_GET_CHIBI_ERROR_LOG, (), '', 'H H H H'))

    def set_chibi_frequency(self, frequency):
        self.ipcon.write(self, Master.TYPE_SET_CHIBI_FREQUENCY, (frequency,), 'B', '')

    def get_chibi_frequency(self):
        return self.ipcon.write(self, Master.TYPE_GET_CHIBI_FREQUENCY, (), '', 'B')

    def set_chibi_channel(self, channel):
        self.ipcon.write(self, Master.TYPE_SET_CHIBI_CHANNEL, (channel,), 'B', '')

    def get_chibi_channel(self):
        return self.ipcon.write(self, Master.TYPE_GET_CHIBI_CHANNEL, (), '', 'B')
