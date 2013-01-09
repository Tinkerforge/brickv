# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2013-01-09.      #
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

class BrickletPiezoBuzzer(Device):
    """
    Device for controlling a piezo buzzer
    """

    DEVICE_IDENTIFIER = 214

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

        self.api_version = (1, 0, 0)

        self.response_expected[BrickletPiezoBuzzer.FUNCTION_BEEP] = BrickletPiezoBuzzer.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletPiezoBuzzer.FUNCTION_MORSE_CODE] = BrickletPiezoBuzzer.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletPiezoBuzzer.CALLBACK_BEEP_FINISHED] = BrickletPiezoBuzzer.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletPiezoBuzzer.CALLBACK_MORSE_CODE_FINISHED] = BrickletPiezoBuzzer.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletPiezoBuzzer.FUNCTION_GET_IDENTITY] = BrickletPiezoBuzzer.RESPONSE_EXPECTED_ALWAYS_TRUE

        self.callback_formats[BrickletPiezoBuzzer.CALLBACK_BEEP_FINISHED] = ''
        self.callback_formats[BrickletPiezoBuzzer.CALLBACK_MORSE_CODE_FINISHED] = ''

    def beep(self, duration):
        """
        Beeps with the duration in ms. For example: If you set a value of 1000,
        the piezo buzzer will beep for one second.
        """
        self.ipcon.send_request(self, BrickletPiezoBuzzer.FUNCTION_BEEP, (duration,), 'I', '')

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
        self.ipcon.send_request(self, BrickletPiezoBuzzer.FUNCTION_MORSE_CODE, (morse,), '60s', '')

    def get_identity(self):
        """
        Returns the UID, the UID where the Bricklet is connected to, 
        the position, the hardware and firmware version as well as the
        device identifier.
        
        The position can be 'a', 'b', 'c' or 'd'.
        
        The device identifiers are:
        
        .. csv-table::
         :header: "Device Identifier", "Device Name"
         :widths: 30, 100
        
         "11", "Brick DC"
         "12", "Brick Debug"
         "13", "Brick Master"
         "14", "Brick Servo"
         "15", "Brick Stepper"
         "16", "Brick IMU"
         "", ""
         "21", "Bricklet Ambient Light"
         "22", "Bricklet Breakout"
         "23", "Bricklet Current12"
         "24", "Bricklet Current25"
         "25", "Bricklet Distance IR"
         "26", "Bricklet Dual Relay"
         "27", "Bricklet Humidity"
         "28", "Bricklet IO-16"
         "29", "Bricklet IO-4"
         "210", "Bricklet Joystick"
         "211", "Bricklet LCD 16x2"
         "212", "Bricklet LCD 20x4"
         "213", "Bricklet Linear Poti"
         "214", "Bricklet Piezo Buzzer"
         "215", "Bricklet Rotary Poti"
         "216", "Bricklet Temperature"
         "217", "Bricklet Temperature IR"
         "218", "Bricklet Voltage"
         "219", "Bricklet Analog In"
         "220", "Bricklet Analog Out"
         "221", "Bricklet Barometer"
         "222", "Bricklet GPS"
         "223", "Bricklet Industrial Digital In 4"
         "224", "Bricklet Industrial Digital Out 4"
         "225", "Bricklet Industrial Quad Relay"
         "226", "Bricklet PTC"
         "227", "Bricklet Voltage/Current"
        
        .. versionadded:: 2.0.0~(Plugin)
        """
        return GetIdentity(*self.ipcon.send_request(self, BrickletPiezoBuzzer.FUNCTION_GET_IDENTITY, (), '', '8s 8s c 3B 3B H'))

    def register_callback(self, id, callback):
        """
        Registers a callback with ID *id* to the function *callback*.
        """
        self.registered_callbacks[id] = callback

PiezoBuzzer = BrickletPiezoBuzzer # for backward compatibility
