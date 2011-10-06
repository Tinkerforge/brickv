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

class PiezoBuzzer(Device):
    CALLBACK_BEEP_FINISHED = 3
    CALLBACK_MORSE_CODE_FINISHED = 4

    TYPE_BEEP = 1
    TYPE_MORSE_CODE = 2
    TYPE_BEEP_FINISHED = 3
    TYPE_MORSE_CODE_FINISHED = 4

    def __init__(self, uid):
        Device.__init__(self, uid)

        self.binding_version = [1, 0, 0]

        self.callbacks_format[PiezoBuzzer.CALLBACK_BEEP_FINISHED] = ''
        self.callbacks_format[PiezoBuzzer.CALLBACK_MORSE_CODE_FINISHED] = ''

    def get_version(self):
        return GetVersion(self.name, self.firmware_version, self.binding_version)

    def beep(self, duration):
        self.ipcon.write(self, PiezoBuzzer.TYPE_BEEP, (duration,), 'I', '')

    def morse_code(self, morse):
        self.ipcon.write(self, PiezoBuzzer.TYPE_MORSE_CODE, (morse,), '60s', '')
