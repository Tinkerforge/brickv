# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2012-11-07.      #
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


class BrickletAnalogOut(Device):
    """
    Device for output of voltage between 0 and 5V
    """

    DEVICE_IDENTIFIER = 220


    FUNCTION_SET_VOLTAGE = 1
    FUNCTION_GET_VOLTAGE = 2
    FUNCTION_SET_MODE = 3
    FUNCTION_GET_MODE = 4

    def __init__(self, uid, ipcon):
        """
        Creates an object with the unique device ID *uid* and adds it to
        the IP Connection *ipcon*.
        """
        Device.__init__(self, uid, ipcon)

        self.api_version = (1, 0, 0)


    def set_voltage(self, voltage):
        """
        Sets the voltage in mV. The possible range is 0V to 5V (0-5000).
        Calling this function will set the mode to 0 (see `:func:SetMode`).
        
        The default value is 0 (with mode 1).
        """
        self.ipcon.send_request(self, AnalogOut.FUNCTION_SET_VOLTAGE, (voltage,), 'H', '')

    def get_voltage(self):
        """
        Returns the voltage as set by :func:`SetVoltage`.
        """
        return self.ipcon.send_request(self, AnalogOut.FUNCTION_GET_VOLTAGE, (), '', 'H')

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
        self.ipcon.send_request(self, AnalogOut.FUNCTION_SET_MODE, (mode,), 'B', '')

    def get_mode(self):
        """
        Returns the mode as set by :func:`SetMode`.
        """
        return self.ipcon.send_request(self, AnalogOut.FUNCTION_GET_MODE, (), '', 'B')

AnalogOut = BrickletAnalogOut # for backward compatibility
