# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2016-09-08.      #
#                                                           #
# Python Bindings Version 2.1.10                            #
#                                                           #
# If you have a bugfix for this file and want to commit it, #
# please fix the bug in the generator. You can find a link  #
# to the generators git repository on tinkerforge.com       #
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
    Generates configurable DC voltage between 0V and 5V
    """

    DEVICE_IDENTIFIER = 220
    DEVICE_DISPLAY_NAME = 'Analog Out Bricklet'


    FUNCTION_SET_VOLTAGE = 1
    FUNCTION_GET_VOLTAGE = 2
    FUNCTION_SET_MODE = 3
    FUNCTION_GET_MODE = 4
    FUNCTION_GET_IDENTITY = 255

    MODE_ANALOG_VALUE = 0
    MODE_1K_TO_GROUND = 1
    MODE_100K_TO_GROUND = 2
    MODE_500K_TO_GROUND = 3

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
        
        * 0: Normal Mode (Analog value as set by :func:`SetVoltage` is applied)
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
        
        The device identifier numbers can be found :ref:`here <device_identifier>`.
        |device_identifier_constant|
        """
        return GetIdentity(*self.ipcon.send_request(self, BrickletAnalogOut.FUNCTION_GET_IDENTITY, (), '', '8s 8s c 3B 3B H'))

AnalogOut = BrickletAnalogOut # for backward compatibility
