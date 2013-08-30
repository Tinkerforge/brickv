# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2013-08-30.      #
#                                                           #
# Bindings Version 2.0.10                                    #
#                                                           #
# If you have a bugfix for this file and want to commit it, #
# please fix the bug in the generator. You can find a link  #
# to the generator git on tinkerforge.com                   #
#############################################################

try:
    from collections import namedtuple
except ImportError:
    try:
        from .ip_connection import namedtuple
    except ValueError:
        from ip_connection import namedtuple

try:
    from .ip_connection import Device, IPConnection, Error
except ValueError:
    from ip_connection import Device, IPConnection, Error

GetIdentity = namedtuple('Identity', ['uid', 'connected_uid', 'position', 'hardware_version', 'firmware_version', 'device_identifier'])

class BrickletPiezoSpeaker(Device):
    """
    Device for controlling a piezo buzzer with configurable frequencies
    """

    DEVICE_IDENTIFIER = 242

    CALLBACK_BEEP_FINISHED = 3
    CALLBACK_MORSE_CODE_FINISHED = 4

    FUNCTION_BEEP = 1
    FUNCTION_MORSE_CODE = 2
    FUNCTION_GET_IDENTITY = 255


    def __init__(self, uid, ipcon):
        """
        Creates an object with the unique device ID *uid* and adds it to
        the IP Connection *ipcon*.
        """
        Device.__init__(self, uid, ipcon)

        self.api_version = (2, 0, 0)

        self.response_expected[BrickletPiezoSpeaker.FUNCTION_BEEP] = BrickletPiezoSpeaker.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletPiezoSpeaker.FUNCTION_MORSE_CODE] = BrickletPiezoSpeaker.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletPiezoSpeaker.CALLBACK_BEEP_FINISHED] = BrickletPiezoSpeaker.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletPiezoSpeaker.CALLBACK_MORSE_CODE_FINISHED] = BrickletPiezoSpeaker.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletPiezoSpeaker.FUNCTION_GET_IDENTITY] = BrickletPiezoSpeaker.RESPONSE_EXPECTED_ALWAYS_TRUE

        self.callback_formats[BrickletPiezoSpeaker.CALLBACK_BEEP_FINISHED] = ''
        self.callback_formats[BrickletPiezoSpeaker.CALLBACK_MORSE_CODE_FINISHED] = ''

    def beep(self, duration, frequency):
        """
        Beeps with the given frequency value for the duration in ms. For example: 
        If you set a duration of 1000, with a frequency value of 220
        the piezo buzzer will beep for one second with a frequency of
        approximately 2 kHz.
        
        *frequency* can be set between 0 and 512.
        
        Below you can find a graph that shows the relation between the frequency
        value parameter and a frequency in Hz of the played tone:
        
        .. image:: /Images/Bricklets/bricklet_piezo_speaker_value_to_frequency_graph.png
           :scale: 100 %
           :alt: Relation between value and frequency 
           :align: center
        """
        self.ipcon.send_request(self, BrickletPiezoSpeaker.FUNCTION_BEEP, (duration, frequency), 'I H', '')

    def morse_code(self, morse, frequency):
        """
        Sets morse code that will be played by the piezo buzzer. The morse code
        is given as a string consisting of "." (dot), "-" (minus) and " " (space)
        for *dits*, *dahs* and *pauses*. Every other character is ignored.
        The second parameter is the frequency value (see :func:`Beep`).
        
        For example: If you set the string "...---...", the piezo buzzer will beep
        nine times with the durations "short short short long long long short 
        short short".
        
        The maximum string size is 60.
        """
        self.ipcon.send_request(self, BrickletPiezoSpeaker.FUNCTION_MORSE_CODE, (morse, frequency), '60s H', '')

    def get_identity(self):
        """
        Returns the UID, the UID where the Bricklet is connected to, 
        the position, the hardware and firmware version as well as the
        device identifier.
        
        The position can be 'a', 'b', 'c' or 'd'.
        
        The device identifiers can be found :ref:`here <device_identifier>`.
        
        .. versionadded:: 2.0.0~(Plugin)
        """
        return GetIdentity(*self.ipcon.send_request(self, BrickletPiezoSpeaker.FUNCTION_GET_IDENTITY, (), '', '8s 8s c 3B 3B H'))

    def register_callback(self, id, callback):
        """
        Registers a callback with ID *id* to the function *callback*.
        """
        self.registered_callbacks[id] = callback

PiezoSpeaker = BrickletPiezoSpeaker # for backward compatibility
