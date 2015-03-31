# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2015-03-31.      #
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

GetIdentity = namedtuple('Identity', ['uid', 'connected_uid', 'position', 'hardware_version', 'firmware_version', 'device_identifier'])

class BrickletIndustrialAnalogOut(Device):
    """
    Device for output of voltage between 0 and 10V and current between 4 an 20mA
    """

    DEVICE_IDENTIFIER = 258
    DEVICE_DISPLAY_NAME = 'Industrial Analog Out Bricklet'


    FUNCTION_SET_OUTPUT_VOLTAGE = 1
    FUNCTION_GET_OUTPUT_VOLTAGE = 2
    FUNCTION_GET_INPUT_VOLTAGE = 3
    FUNCTION_GET_IDENTITY = 255


    def __init__(self, uid, ipcon):
        """
        Creates an object with the unique device ID *uid* and adds it to
        the IP Connection *ipcon*.
        """
        Device.__init__(self, uid, ipcon)

        self.api_version = (2, 0, 0)

        self.response_expected[BrickletIndustrialAnalogOut.FUNCTION_SET_OUTPUT_VOLTAGE] = BrickletIndustrialAnalogOut.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletIndustrialAnalogOut.FUNCTION_GET_OUTPUT_VOLTAGE] = BrickletIndustrialAnalogOut.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletIndustrialAnalogOut.FUNCTION_GET_INPUT_VOLTAGE] = BrickletIndustrialAnalogOut.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletIndustrialAnalogOut.FUNCTION_GET_IDENTITY] = BrickletIndustrialAnalogOut.RESPONSE_EXPECTED_ALWAYS_TRUE


    def set_output_voltage(self, voltage):
        """
        Sets the voltage in mV. The possible range is 0V to 10V (0-10000).
        """
        self.ipcon.send_request(self, BrickletIndustrialAnalogOut.FUNCTION_SET_OUTPUT_VOLTAGE, (voltage,), 'H', '')

    def get_output_voltage(self):
        """
        Returns the voltage as set by :func:`SetOutputVoltage`.
        """
        return self.ipcon.send_request(self, BrickletIndustrialAnalogOut.FUNCTION_GET_OUTPUT_VOLTAGE, (), '', 'H')

    def get_input_voltage(self):
        """
        
        """
        return self.ipcon.send_request(self, BrickletIndustrialAnalogOut.FUNCTION_GET_INPUT_VOLTAGE, (), '', 'H')

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
