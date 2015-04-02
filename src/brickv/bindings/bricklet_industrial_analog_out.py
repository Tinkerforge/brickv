# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2015-04-02.      #
#                                                           #
# Bindings Version 2.1.4                                    #
#                                                           #
# If you have a bugfix for this file and want to commit it, #
# please fix the bug in the generator. You can find a link  #
# to the generator git on tinkerforge.com                   #
#############################################################

#### __DEVICE_IS_NOT_RELEASED__ ####

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

GetConfiguration = namedtuple('Configuration', ['voltage_range', 'current_range'])
GetIdentity = namedtuple('Identity', ['uid', 'connected_uid', 'position', 'hardware_version', 'firmware_version', 'device_identifier'])

class BrickletIndustrialAnalogOut(Device):
    """
    Device for output of voltage between 0 and 10V and current between 4 an 20mA
    """

    DEVICE_IDENTIFIER = 258
    DEVICE_DISPLAY_NAME = 'Industrial Analog Out Bricklet'


    FUNCTION_SET_VOLTAGE = 1
    FUNCTION_GET_VOLTAGE = 2
    FUNCTION_SET_CURRENT = 3
    FUNCTION_GET_CURRENT = 4
    FUNCTION_SET_CONFIGURATION = 5
    FUNCTION_GET_CONFIGURATION = 6
    FUNCTION_GET_IDENTITY = 255

    VOLTAGE_RANGE_0_TO_5V = 0
    VOLTAGE_RANGE_0_TO_10V = 1
    CURRENT_RANGE_4_TO_20MA = 0
    CURRENT_RANGE_0_TO_20MA = 1
    CURRENT_RANGE_0_TO_24MA = 2

    def __init__(self, uid, ipcon):
        """
        Creates an object with the unique device ID *uid* and adds it to
        the IP Connection *ipcon*.
        """
        Device.__init__(self, uid, ipcon)

        self.api_version = (2, 0, 0)

        self.response_expected[BrickletIndustrialAnalogOut.FUNCTION_SET_VOLTAGE] = BrickletIndustrialAnalogOut.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletIndustrialAnalogOut.FUNCTION_GET_VOLTAGE] = BrickletIndustrialAnalogOut.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletIndustrialAnalogOut.FUNCTION_SET_CURRENT] = BrickletIndustrialAnalogOut.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletIndustrialAnalogOut.FUNCTION_GET_CURRENT] = BrickletIndustrialAnalogOut.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletIndustrialAnalogOut.FUNCTION_SET_CONFIGURATION] = BrickletIndustrialAnalogOut.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletIndustrialAnalogOut.FUNCTION_GET_CONFIGURATION] = BrickletIndustrialAnalogOut.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletIndustrialAnalogOut.FUNCTION_GET_IDENTITY] = BrickletIndustrialAnalogOut.RESPONSE_EXPECTED_ALWAYS_TRUE


    def set_voltage(self, voltage):
        """
        Sets the voltage in mV.
        """
        self.ipcon.send_request(self, BrickletIndustrialAnalogOut.FUNCTION_SET_VOLTAGE, (voltage,), 'H', '')

    def get_voltage(self):
        """
        Returns the voltage as set by :func:`SetVoltage`.
        """
        return self.ipcon.send_request(self, BrickletIndustrialAnalogOut.FUNCTION_GET_VOLTAGE, (), '', 'H')

    def set_current(self, current):
        """
        Sets the current in µA.
        """
        self.ipcon.send_request(self, BrickletIndustrialAnalogOut.FUNCTION_SET_CURRENT, (current,), 'H', '')

    def get_current(self):
        """
        Returns the current as set by :func:`SetCurrent`.
        """
        return self.ipcon.send_request(self, BrickletIndustrialAnalogOut.FUNCTION_GET_CURRENT, (), '', 'H')

    def set_configuration(self, voltage_range, current_range):
        """
        TODO
        """
        self.ipcon.send_request(self, BrickletIndustrialAnalogOut.FUNCTION_SET_CONFIGURATION, (voltage_range, current_range), 'B B', '')

    def get_configuration(self):
        """
        Returns the configuration as set by :func:`SetConfiguration`.
        """
        return GetConfiguration(*self.ipcon.send_request(self, BrickletIndustrialAnalogOut.FUNCTION_GET_CONFIGURATION, (), '', 'B B'))

    def get_identity(self):
        """
        Returns the UID, the UID where the Bricklet is connected to, 
        the position, the hardware and firmware version as well as the
        device identifier.
        
        The position can be 'a', 'b', 'c' or 'd'.
        
        The device identifier numbers can be found :ref:`here <device_identifier>`.
        |device_identifier_constant|
        """
        return GetIdentity(*self.ipcon.send_request(self, BrickletIndustrialAnalogOut.FUNCTION_GET_IDENTITY, (), '', '8s 8s c 3B 3B H'))

IndustrialAnalogOut = BrickletIndustrialAnalogOut # for backward compatibility
