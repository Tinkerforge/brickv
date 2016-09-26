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

GetCO2ConcentrationCallbackThreshold = namedtuple('CO2ConcentrationCallbackThreshold', ['option', 'min', 'max'])
GetIdentity = namedtuple('Identity', ['uid', 'connected_uid', 'position', 'hardware_version', 'firmware_version', 'device_identifier'])

class BrickletCO2(Device):
    """
    Measures CO2 concentration in ppm
    """

    DEVICE_IDENTIFIER = 262
    DEVICE_DISPLAY_NAME = 'CO2 Bricklet'

    CALLBACK_CO2_CONCENTRATION = 8
    CALLBACK_CO2_CONCENTRATION_REACHED = 9

    FUNCTION_GET_CO2_CONCENTRATION = 1
    FUNCTION_SET_CO2_CONCENTRATION_CALLBACK_PERIOD = 2
    FUNCTION_GET_CO2_CONCENTRATION_CALLBACK_PERIOD = 3
    FUNCTION_SET_CO2_CONCENTRATION_CALLBACK_THRESHOLD = 4
    FUNCTION_GET_CO2_CONCENTRATION_CALLBACK_THRESHOLD = 5
    FUNCTION_SET_DEBOUNCE_PERIOD = 6
    FUNCTION_GET_DEBOUNCE_PERIOD = 7
    FUNCTION_GET_IDENTITY = 255

    THRESHOLD_OPTION_OFF = 'x'
    THRESHOLD_OPTION_OUTSIDE = 'o'
    THRESHOLD_OPTION_INSIDE = 'i'
    THRESHOLD_OPTION_SMALLER = '<'
    THRESHOLD_OPTION_GREATER = '>'

    def __init__(self, uid, ipcon):
        """
        Creates an object with the unique device ID *uid* and adds it to
        the IP Connection *ipcon*.
        """
        Device.__init__(self, uid, ipcon)

        self.api_version = (2, 0, 0)

        self.response_expected[BrickletCO2.FUNCTION_GET_CO2_CONCENTRATION] = BrickletCO2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletCO2.FUNCTION_SET_CO2_CONCENTRATION_CALLBACK_PERIOD] = BrickletCO2.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletCO2.FUNCTION_GET_CO2_CONCENTRATION_CALLBACK_PERIOD] = BrickletCO2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletCO2.FUNCTION_SET_CO2_CONCENTRATION_CALLBACK_THRESHOLD] = BrickletCO2.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletCO2.FUNCTION_GET_CO2_CONCENTRATION_CALLBACK_THRESHOLD] = BrickletCO2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletCO2.FUNCTION_SET_DEBOUNCE_PERIOD] = BrickletCO2.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletCO2.FUNCTION_GET_DEBOUNCE_PERIOD] = BrickletCO2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletCO2.CALLBACK_CO2_CONCENTRATION] = BrickletCO2.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletCO2.CALLBACK_CO2_CONCENTRATION_REACHED] = BrickletCO2.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletCO2.FUNCTION_GET_IDENTITY] = BrickletCO2.RESPONSE_EXPECTED_ALWAYS_TRUE

        self.callback_formats[BrickletCO2.CALLBACK_CO2_CONCENTRATION] = 'H'
        self.callback_formats[BrickletCO2.CALLBACK_CO2_CONCENTRATION_REACHED] = 'H'

    def get_co2_concentration(self):
        """
        Returns the measured CO2 concentration. The value is in 
        `ppm (parts per million) <https://en.wikipedia.org/wiki/Parts-per_notation>`__
        and between 0 to 10000.
        
        If you want to get the CO2 concentration periodically, it is recommended to use the
        callback :func:`CO2Concentration` and set the period with
        :func:`SetCO2ConcentrationCallbackPeriod`.
        """
        return self.ipcon.send_request(self, BrickletCO2.FUNCTION_GET_CO2_CONCENTRATION, (), '', 'H')

    def set_co2_concentration_callback_period(self, period):
        """
        Sets the period in ms with which the :func:`CO2Concentration` callback is triggered
        periodically. A value of 0 turns the callback off.
        
        :func:`CO2Concentration` is only triggered if the CO2 concentration has changed since the
        last triggering.
        
        The default value is 0.
        """
        self.ipcon.send_request(self, BrickletCO2.FUNCTION_SET_CO2_CONCENTRATION_CALLBACK_PERIOD, (period,), 'I', '')

    def get_co2_concentration_callback_period(self):
        """
        Returns the period as set by :func:`SetCO2ConcentrationCallbackPeriod`.
        """
        return self.ipcon.send_request(self, BrickletCO2.FUNCTION_GET_CO2_CONCENTRATION_CALLBACK_PERIOD, (), '', 'I')

    def set_co2_concentration_callback_threshold(self, option, min, max):
        """
        Sets the thresholds for the :func:`CO2ConcentrationReached` callback.
        
        The following options are possible:
        
        .. csv-table::
         :header: "Option", "Description"
         :widths: 10, 100
        
         "'x'",    "Callback is turned off"
         "'o'",    "Callback is triggered when the CO2 concentration is *outside* the min and max values"
         "'i'",    "Callback is triggered when the CO2 concentration is *inside* the min and max values"
         "'<'",    "Callback is triggered when the CO2 concentration is smaller than the min value (max is ignored)"
         "'>'",    "Callback is triggered when the CO2 concentration is greater than the min value (max is ignored)"
        
        The default value is ('x', 0, 0).
        """
        self.ipcon.send_request(self, BrickletCO2.FUNCTION_SET_CO2_CONCENTRATION_CALLBACK_THRESHOLD, (option, min, max), 'c H H', '')

    def get_co2_concentration_callback_threshold(self):
        """
        Returns the threshold as set by :func:`SetCO2ConcentrationCallbackThreshold`.
        """
        return GetCO2ConcentrationCallbackThreshold(*self.ipcon.send_request(self, BrickletCO2.FUNCTION_GET_CO2_CONCENTRATION_CALLBACK_THRESHOLD, (), '', 'c H H'))

    def set_debounce_period(self, debounce):
        """
        Sets the period in ms with which the threshold callbacks
        
        * :func:`CO2ConcentrationReached`,
        
        are triggered, if the thresholds
        
        * :func:`SetCO2ConcentrationCallbackThreshold`,
        
        keep being reached.
        
        The default value is 100.
        """
        self.ipcon.send_request(self, BrickletCO2.FUNCTION_SET_DEBOUNCE_PERIOD, (debounce,), 'I', '')

    def get_debounce_period(self):
        """
        Returns the debounce period as set by :func:`SetDebouncePeriod`.
        """
        return self.ipcon.send_request(self, BrickletCO2.FUNCTION_GET_DEBOUNCE_PERIOD, (), '', 'I')

    def get_identity(self):
        """
        Returns the UID, the UID where the Bricklet is connected to, 
        the position, the hardware and firmware version as well as the
        device identifier.
        
        The position can be 'a', 'b', 'c' or 'd'.
        
        The device identifier numbers can be found :ref:`here <device_identifier>`.
        |device_identifier_constant|
        """
        return GetIdentity(*self.ipcon.send_request(self, BrickletCO2.FUNCTION_GET_IDENTITY, (), '', '8s 8s c 3B 3B H'))

    def register_callback(self, id, callback):
        """
        Registers a callback with ID *id* to the function *callback*.
        """
        self.registered_callbacks[id] = callback

CO2 = BrickletCO2 # for backward compatibility
