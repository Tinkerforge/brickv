# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2013-01-14.      #
#                                                           #
# Bindings Version 2.0.0                                    #
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

class BrickletAnalogOut(Device):
    """
    Device for output of voltage between 0 and 5V
    """

    DEVICE_IDENTIFIER = 220


    FUNCTION_SET_VOLTAGE = 1
    FUNCTION_GET_VOLTAGE = 2
    FUNCTION_SET_MODE = 3
    FUNCTION_GET_MODE = 4
    FUNCTION_GET_IDENTITY = 255

    def __init__(self, uid, ipcon):
        """
        Creates an object with the unique device ID *uid* and adds it to
        the IP Connection *ipcon*.
        """
        Device.__init__(self, uid, ipcon)

        self.api_version = (2, 0, 0)

        self.response_expected[BrickletAnalogOut.FUNCTION_SET_VOLTAGE] = BrickletAnalogOut.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletAnalogOut.FUNCTION_GET_VOLTAGE] = BrickletAnalogOut.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletAnalogOut.FUNCTION_SET_MODE] = BrickletAnalogOut.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletAnalogOut.FUNCTION_GET_MODE] = BrickletAnalogOut.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletAnalogOut.FUNCTION_GET_IDENTITY] = BrickletAnalogOut.RESPONSE_EXPECTED_ALWAYS_TRUE


    def set_voltage(self, voltage):
        """
        Sets the voltage in mV. The possible range is 0V to 5V (0-5000).
        Calling this function will set the mode to 0 (see :func:`SetMode`).
        
        The default value is 0 (with mode 1).
        """
        self.ipcon.send_request(self, BrickletAnalogOut.FUNCTION_SET_VOLTAGE, (voltage,), 'H', '')

    def get_voltage(self):
        """
        Returns the voltage as set by :func:`SetVoltage`.
        """
        return self.ipcon.send_request(self, BrickletAnalogOut.FUNCTION_GET_VOLTAGE, (), '', 'H')

    def set_mode(self, mode):
        """
        Sets the mode of the analog value. Possible modes:
        
        * 0: Normal Mode (Analog value as set by :func:`SetVoltage` is applied
        * 1: 1k Ohm resistor to ground
        * 2: 100k Ohm resistor to ground
        * 3: 500k Ohm resistor to ground
        
        Setting the mode to 0 will result in an output voltage of 0. You can jump
        to a higher output voltage directly by calling :func:`SetVoltage`.
        
        The default mode is 1.
        """
        self.ipcon.send_request(self, BrickletAnalogOut.FUNCTION_SET_MODE, (mode,), 'B', '')

    def get_mode(self):
        """
        Returns the mode as set by :func:`SetMode`.
        """
        return self.ipcon.send_request(self, BrickletAnalogOut.FUNCTION_GET_MODE, (), '', 'B')

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
         "13", "Brick Master"
         "14", "Brick Servo"
         "15", "Brick Stepper"
         "16", "Brick IMU"
         "", ""
         "21", "Bricklet Ambient Light"
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
        return GetIdentity(*self.ipcon.send_request(self, BrickletAnalogOut.FUNCTION_GET_IDENTITY, (), '', '8s 8s c 3B 3B H'))

AnalogOut = BrickletAnalogOut # for backward compatibility
