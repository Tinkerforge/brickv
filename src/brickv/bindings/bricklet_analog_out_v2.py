# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2018-06-08.      #
#                                                           #
# Python Bindings Version 2.1.17                            #
#                                                           #
# If you have a bugfix for this file and want to commit it, #
# please fix the bug in the generator. You can find a link  #
# to the generators git repository on tinkerforge.com       #
#############################################################

from collections import namedtuple

try:
    from .ip_connection import Device, IPConnection, Error, create_char, create_char_list, create_string, create_chunk_data
except ValueError:
    from ip_connection import Device, IPConnection, Error, create_char, create_char_list, create_string, create_chunk_data

GetIdentity = namedtuple('Identity', ['uid', 'connected_uid', 'position', 'hardware_version', 'firmware_version', 'device_identifier'])

class BrickletAnalogOutV2(Device):
    """
    Generates configurable DC voltage between 0V and 12V
    """

    DEVICE_IDENTIFIER = 256
    DEVICE_DISPLAY_NAME = 'Analog Out Bricklet 2.0'
    DEVICE_URL_PART = 'analog_out_v2' # internal



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

        self.response_expected[BrickletAnalogOutV2.FUNCTION_SET_OUTPUT_VOLTAGE] = BrickletAnalogOutV2.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletAnalogOutV2.FUNCTION_GET_OUTPUT_VOLTAGE] = BrickletAnalogOutV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletAnalogOutV2.FUNCTION_GET_INPUT_VOLTAGE] = BrickletAnalogOutV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletAnalogOutV2.FUNCTION_GET_IDENTITY] = BrickletAnalogOutV2.RESPONSE_EXPECTED_ALWAYS_TRUE



    def set_output_voltage(self, voltage):
        """
        Sets the voltage in mV. The possible range is 0V to 12V (0-12000).
        """
        voltage = int(voltage)

        self.ipcon.send_request(self, BrickletAnalogOutV2.FUNCTION_SET_OUTPUT_VOLTAGE, (voltage,), 'H', '')

    def get_output_voltage(self):
        """
        Returns the voltage as set by :func:`Set Output Voltage`.
        """
        return self.ipcon.send_request(self, BrickletAnalogOutV2.FUNCTION_GET_OUTPUT_VOLTAGE, (), '', 'H')

    def get_input_voltage(self):
        """
        Returns the input voltage in mV.
        """
        return self.ipcon.send_request(self, BrickletAnalogOutV2.FUNCTION_GET_INPUT_VOLTAGE, (), '', 'H')

    def get_identity(self):
        """
        Returns the UID, the UID where the Bricklet is connected to,
        the position, the hardware and firmware version as well as the
        device identifier.

        The position can be 'a', 'b', 'c' or 'd'.

        The device identifier numbers can be found :ref:`here <device_identifier>`.
        |device_identifier_constant|
        """
        return GetIdentity(*self.ipcon.send_request(self, BrickletAnalogOutV2.FUNCTION_GET_IDENTITY, (), '', '8s 8s c 3B 3B H'))

AnalogOutV2 = BrickletAnalogOutV2 # for backward compatibility
