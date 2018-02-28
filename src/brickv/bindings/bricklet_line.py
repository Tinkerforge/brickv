# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2018-02-28.      #
#                                                           #
# Python Bindings Version 2.1.16                            #
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

GetReflectivityCallbackThreshold = namedtuple('ReflectivityCallbackThreshold', ['option', 'min', 'max'])
GetIdentity = namedtuple('Identity', ['uid', 'connected_uid', 'position', 'hardware_version', 'firmware_version', 'device_identifier'])

class BrickletLine(Device):
    """
    Measures reflectivity of a surface
    """

    DEVICE_IDENTIFIER = 241
    DEVICE_DISPLAY_NAME = 'Line Bricklet'
    DEVICE_URL_PART = 'line' # internal

    CALLBACK_REFLECTIVITY = 8
    CALLBACK_REFLECTIVITY_REACHED = 9


    FUNCTION_GET_REFLECTIVITY = 1
    FUNCTION_SET_REFLECTIVITY_CALLBACK_PERIOD = 2
    FUNCTION_GET_REFLECTIVITY_CALLBACK_PERIOD = 3
    FUNCTION_SET_REFLECTIVITY_CALLBACK_THRESHOLD = 4
    FUNCTION_GET_REFLECTIVITY_CALLBACK_THRESHOLD = 5
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

        self.response_expected[BrickletLine.FUNCTION_GET_REFLECTIVITY] = BrickletLine.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletLine.FUNCTION_SET_REFLECTIVITY_CALLBACK_PERIOD] = BrickletLine.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletLine.FUNCTION_GET_REFLECTIVITY_CALLBACK_PERIOD] = BrickletLine.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletLine.FUNCTION_SET_REFLECTIVITY_CALLBACK_THRESHOLD] = BrickletLine.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletLine.FUNCTION_GET_REFLECTIVITY_CALLBACK_THRESHOLD] = BrickletLine.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletLine.FUNCTION_SET_DEBOUNCE_PERIOD] = BrickletLine.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletLine.FUNCTION_GET_DEBOUNCE_PERIOD] = BrickletLine.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletLine.FUNCTION_GET_IDENTITY] = BrickletLine.RESPONSE_EXPECTED_ALWAYS_TRUE

        self.callback_formats[BrickletLine.CALLBACK_REFLECTIVITY] = 'H'
        self.callback_formats[BrickletLine.CALLBACK_REFLECTIVITY_REACHED] = 'H'


    def get_reflectivity(self):
        """
        Returns the currently measured reflectivity. The reflectivity is
        a value between 0 (not reflective) and 4095 (very reflective).

        Usually black has a low reflectivity while white has a high
        reflectivity.

        If you want to get the reflectivity periodically, it is recommended
        to use the :cb:`Reflectivity` callback and set the period with
        :func:`Set Reflectivity Callback Period`.
        """
        return self.ipcon.send_request(self, BrickletLine.FUNCTION_GET_REFLECTIVITY, (), '', 'H')

    def set_reflectivity_callback_period(self, period):
        """
        Sets the period in ms with which the :cb:`Reflectivity` callback is triggered
        periodically. A value of 0 turns the callback off.

        The :cb:`Reflectivity` callback is only triggered if the reflectivity has
        changed since the last triggering.

        The default value is 0.
        """
        period = int(period)

        self.ipcon.send_request(self, BrickletLine.FUNCTION_SET_REFLECTIVITY_CALLBACK_PERIOD, (period,), 'I', '')

    def get_reflectivity_callback_period(self):
        """
        Returns the period as set by :func:`Set Reflectivity Callback Period`.
        """
        return self.ipcon.send_request(self, BrickletLine.FUNCTION_GET_REFLECTIVITY_CALLBACK_PERIOD, (), '', 'I')

    def set_reflectivity_callback_threshold(self, option, min, max):
        """
        Sets the thresholds for the :cb:`Reflectivity Reached` callback.

        The following options are possible:

        .. csv-table::
         :header: "Option", "Description"
         :widths: 10, 100

         "'x'",    "Callback is turned off"
         "'o'",    "Callback is triggered when the reflectivity is *outside* the min and max values"
         "'i'",    "Callback is triggered when the reflectivity is *inside* the min and max values"
         "'<'",    "Callback is triggered when the reflectivity is smaller than the min value (max is ignored)"
         "'>'",    "Callback is triggered when the reflectivity is greater than the min value (max is ignored)"

        The default value is ('x', 0, 0).
        """
        option = create_char(option)
        min = int(min)
        max = int(max)

        self.ipcon.send_request(self, BrickletLine.FUNCTION_SET_REFLECTIVITY_CALLBACK_THRESHOLD, (option, min, max), 'c H H', '')

    def get_reflectivity_callback_threshold(self):
        """
        Returns the threshold as set by :func:`Set Reflectivity Callback Threshold`.
        """
        return GetReflectivityCallbackThreshold(*self.ipcon.send_request(self, BrickletLine.FUNCTION_GET_REFLECTIVITY_CALLBACK_THRESHOLD, (), '', 'c H H'))

    def set_debounce_period(self, debounce):
        """
        Sets the period in ms with which the threshold callback

        * :cb:`Reflectivity Reached`

        is triggered, if the threshold

        * :func:`Set Reflectivity Callback Threshold`

        keeps being reached.

        The default value is 100.
        """
        debounce = int(debounce)

        self.ipcon.send_request(self, BrickletLine.FUNCTION_SET_DEBOUNCE_PERIOD, (debounce,), 'I', '')

    def get_debounce_period(self):
        """
        Returns the debounce period as set by :func:`Set Debounce Period`.
        """
        return self.ipcon.send_request(self, BrickletLine.FUNCTION_GET_DEBOUNCE_PERIOD, (), '', 'I')

    def get_identity(self):
        """
        Returns the UID, the UID where the Bricklet is connected to,
        the position, the hardware and firmware version as well as the
        device identifier.

        The position can be 'a', 'b', 'c' or 'd'.

        The device identifier numbers can be found :ref:`here <device_identifier>`.
        |device_identifier_constant|
        """
        return GetIdentity(*self.ipcon.send_request(self, BrickletLine.FUNCTION_GET_IDENTITY, (), '', '8s 8s c 3B 3B H'))

    def register_callback(self, callback_id, function):
        """
        Registers the given *function* with the given *callback_id*.
        """
        if function is None:
            self.registered_callbacks.pop(callback_id, None)
        else:
            self.registered_callbacks[callback_id] = function

Line = BrickletLine # for backward compatibility
