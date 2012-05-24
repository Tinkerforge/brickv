# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2012-05-23.      #
#                                                           #
# If you have a bugfix for this file and want to commit it, #
# please fix the bug in the generator. You can find a link  #
# to the generator git on tinkerforge.com                   #
#############################################################

try:
    from collections import namedtuple
except ImportError:
    from .ip_connection import namedtuple
from .ip_connection import Device, IPConnection, Error


class PiezoBuzzer(Device):
    """
    Device for controlling a piezo buzzer
    """

    CALLBACK_BEEP_FINISHED = 3
    CALLBACK_MORSE_CODE_FINISHED = 4

    FUNCTION_BEEP = 1
    FUNCTION_MORSE_CODE = 2

    def __init__(self, uid):
        """
        Creates an object with the unique device ID *uid*. This object can
        then be added to the IP connection.
        """
        Device.__init__(self, uid)

        self.expected_name = 'Piezo Buzzer Bricklet'

        self.binding_version = [1, 0, 0]

        self.callbacks_format[PiezoBuzzer.CALLBACK_BEEP_FINISHED] = ''
        self.callbacks_format[PiezoBuzzer.CALLBACK_MORSE_CODE_FINISHED] = ''

    def beep(self, duration):
        """
        Beeps with the duration in ms. For example: If you set a value of 1000,
        the piezo buzzer will beep for one second.
        """
        self.ipcon.write(self, PiezoBuzzer.FUNCTION_BEEP, (duration,), 'I', '')

    def morse_code(self, morse):
        """
        Sets morse code that will be played by the piezo buzzer. The morse code
        is given as a string consisting of "." (dot), "-" (minus) and " " (space)
        for *dits*, *dahs* and *pauses*. Every other character is ignored.
        
        For example: If you set the string "...---...", the piezo buzzer will beep
        nine times with the durations "short short short long long long short 
        short short".
        
        The maximum string size is 60.
        """
        self.ipcon.write(self, PiezoBuzzer.FUNCTION_MORSE_CODE, (morse,), '60s', '')

    def register_callback(self, cb, func):
        """
        Registers a callback with ID cb to the function func.
        """
        self.callbacks[cb] = func
