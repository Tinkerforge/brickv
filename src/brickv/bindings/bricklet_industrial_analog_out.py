# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2019-12-03.      #
#                                                           #
# Python Bindings Version 2.1.24                            #
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

GetConfiguration = namedtuple('Configuration', ['voltage_range', 'current_range'])
GetIdentity = namedtuple('Identity', ['uid', 'connected_uid', 'position', 'hardware_version', 'firmware_version', 'device_identifier'])

class BrickletIndustrialAnalogOut(Device):
    """
    Generates configurable DC voltage and current, 0V to 10V and 4mA to 20mA
    """

    DEVICE_IDENTIFIER = 258
    DEVICE_DISPLAY_NAME = 'Industrial Analog Out Bricklet'
    DEVICE_URL_PART = 'industrial_analog_out' # internal



    FUNCTION_ENABLE = 1
    FUNCTION_DISABLE = 2
    FUNCTION_IS_ENABLED = 3
    FUNCTION_SET_VOLTAGE = 4
    FUNCTION_GET_VOLTAGE = 5
    FUNCTION_SET_CURRENT = 6
    FUNCTION_GET_CURRENT = 7
    FUNCTION_SET_CONFIGURATION = 8
    FUNCTION_GET_CONFIGURATION = 9
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

        self.response_expected[BrickletIndustrialAnalogOut.FUNCTION_ENABLE] = BrickletIndustrialAnalogOut.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletIndustrialAnalogOut.FUNCTION_DISABLE] = BrickletIndustrialAnalogOut.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletIndustrialAnalogOut.FUNCTION_IS_ENABLED] = BrickletIndustrialAnalogOut.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletIndustrialAnalogOut.FUNCTION_SET_VOLTAGE] = BrickletIndustrialAnalogOut.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletIndustrialAnalogOut.FUNCTION_GET_VOLTAGE] = BrickletIndustrialAnalogOut.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletIndustrialAnalogOut.FUNCTION_SET_CURRENT] = BrickletIndustrialAnalogOut.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletIndustrialAnalogOut.FUNCTION_GET_CURRENT] = BrickletIndustrialAnalogOut.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletIndustrialAnalogOut.FUNCTION_SET_CONFIGURATION] = BrickletIndustrialAnalogOut.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletIndustrialAnalogOut.FUNCTION_GET_CONFIGURATION] = BrickletIndustrialAnalogOut.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletIndustrialAnalogOut.FUNCTION_GET_IDENTITY] = BrickletIndustrialAnalogOut.RESPONSE_EXPECTED_ALWAYS_TRUE



    def enable(self):
        """
        Enables the output of voltage and current.

        The default is disabled.
        """
        self.ipcon.send_request(self, BrickletIndustrialAnalogOut.FUNCTION_ENABLE, (), '', '')

    def disable(self):
        """
        Disables the output of voltage and current.

        The default is disabled.
        """
        self.ipcon.send_request(self, BrickletIndustrialAnalogOut.FUNCTION_DISABLE, (), '', '')

    def is_enabled(self):
        """
        Returns *true* if output of voltage and current is enabled, *false* otherwise.
        """
        return self.ipcon.send_request(self, BrickletIndustrialAnalogOut.FUNCTION_IS_ENABLED, (), '', '!')

    def set_voltage(self, voltage):
        """
        Sets the output voltage.

        The output voltage and output current are linked. Changing the output voltage
        also changes the output current.
        """
        voltage = int(voltage)

        self.ipcon.send_request(self, BrickletIndustrialAnalogOut.FUNCTION_SET_VOLTAGE, (voltage,), 'H', '')

    def get_voltage(self):
        """
        Returns the voltage as set by :func:`Set Voltage`.
        """
        return self.ipcon.send_request(self, BrickletIndustrialAnalogOut.FUNCTION_GET_VOLTAGE, (), '', 'H')

    def set_current(self, current):
        """
        Sets the output current.

        The output current and output voltage are linked. Changing the output current
        also changes the output voltage.
        """
        current = int(current)

        self.ipcon.send_request(self, BrickletIndustrialAnalogOut.FUNCTION_SET_CURRENT, (current,), 'H', '')

    def get_current(self):
        """
        Returns the current as set by :func:`Set Current`.
        """
        return self.ipcon.send_request(self, BrickletIndustrialAnalogOut.FUNCTION_GET_CURRENT, (), '', 'H')

    def set_configuration(self, voltage_range, current_range):
        """
        Configures the voltage and current range.

        Possible voltage ranges are:

        * 0V to 5V
        * 0V to 10V

        Possible current ranges are:

        * 4mA to 20mA
        * 0mA to 20mA
        * 0mA to 24mA

        The resolution will always be 12 bit. This means, that the
        precision is higher with a smaller range.
        """
        voltage_range = int(voltage_range)
        current_range = int(current_range)

        self.ipcon.send_request(self, BrickletIndustrialAnalogOut.FUNCTION_SET_CONFIGURATION, (voltage_range, current_range), 'B B', '')

    def get_configuration(self):
        """
        Returns the configuration as set by :func:`Set Configuration`.
        """
        return GetConfiguration(*self.ipcon.send_request(self, BrickletIndustrialAnalogOut.FUNCTION_GET_CONFIGURATION, (), '', 'B B'))

    def get_identity(self):
        """
        Returns the UID, the UID where the Bricklet is connected to,
        the position, the hardware and firmware version as well as the
        device identifier.

        The position can be 'a', 'b', 'c', 'd', 'e', 'f', 'g' or 'h' (Bricklet Port).
        The Raspberry Pi HAT (Zero) Brick is always at position 'i' and the Bricklet
        connected to an :ref:`Isolator Bricklet <isolator_bricklet>` is always as
        position 'z'.

        The device identifier numbers can be found :ref:`here <device_identifier>`.
        |device_identifier_constant|
        """
        return GetIdentity(*self.ipcon.send_request(self, BrickletIndustrialAnalogOut.FUNCTION_GET_IDENTITY, (), '', '8s 8s c 3B 3B H'))

IndustrialAnalogOut = BrickletIndustrialAnalogOut # for backward compatibility
