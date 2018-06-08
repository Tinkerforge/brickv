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

GetCurrentCallbackThreshold = namedtuple('CurrentCallbackThreshold', ['option', 'min', 'max'])
GetAnalogValueCallbackThreshold = namedtuple('AnalogValueCallbackThreshold', ['option', 'min', 'max'])
GetIdentity = namedtuple('Identity', ['uid', 'connected_uid', 'position', 'hardware_version', 'firmware_version', 'device_identifier'])

class BrickletCurrent12(Device):
    """
    Measures AC/DC current between -12.5A and +12.5A
    """

    DEVICE_IDENTIFIER = 23
    DEVICE_DISPLAY_NAME = 'Current12 Bricklet'
    DEVICE_URL_PART = 'current12' # internal

    CALLBACK_CURRENT = 15
    CALLBACK_ANALOG_VALUE = 16
    CALLBACK_CURRENT_REACHED = 17
    CALLBACK_ANALOG_VALUE_REACHED = 18
    CALLBACK_OVER_CURRENT = 19


    FUNCTION_GET_CURRENT = 1
    FUNCTION_CALIBRATE = 2
    FUNCTION_IS_OVER_CURRENT = 3
    FUNCTION_GET_ANALOG_VALUE = 4
    FUNCTION_SET_CURRENT_CALLBACK_PERIOD = 5
    FUNCTION_GET_CURRENT_CALLBACK_PERIOD = 6
    FUNCTION_SET_ANALOG_VALUE_CALLBACK_PERIOD = 7
    FUNCTION_GET_ANALOG_VALUE_CALLBACK_PERIOD = 8
    FUNCTION_SET_CURRENT_CALLBACK_THRESHOLD = 9
    FUNCTION_GET_CURRENT_CALLBACK_THRESHOLD = 10
    FUNCTION_SET_ANALOG_VALUE_CALLBACK_THRESHOLD = 11
    FUNCTION_GET_ANALOG_VALUE_CALLBACK_THRESHOLD = 12
    FUNCTION_SET_DEBOUNCE_PERIOD = 13
    FUNCTION_GET_DEBOUNCE_PERIOD = 14
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

        self.response_expected[BrickletCurrent12.FUNCTION_GET_CURRENT] = BrickletCurrent12.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletCurrent12.FUNCTION_CALIBRATE] = BrickletCurrent12.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletCurrent12.FUNCTION_IS_OVER_CURRENT] = BrickletCurrent12.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletCurrent12.FUNCTION_GET_ANALOG_VALUE] = BrickletCurrent12.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletCurrent12.FUNCTION_SET_CURRENT_CALLBACK_PERIOD] = BrickletCurrent12.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletCurrent12.FUNCTION_GET_CURRENT_CALLBACK_PERIOD] = BrickletCurrent12.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletCurrent12.FUNCTION_SET_ANALOG_VALUE_CALLBACK_PERIOD] = BrickletCurrent12.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletCurrent12.FUNCTION_GET_ANALOG_VALUE_CALLBACK_PERIOD] = BrickletCurrent12.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletCurrent12.FUNCTION_SET_CURRENT_CALLBACK_THRESHOLD] = BrickletCurrent12.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletCurrent12.FUNCTION_GET_CURRENT_CALLBACK_THRESHOLD] = BrickletCurrent12.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletCurrent12.FUNCTION_SET_ANALOG_VALUE_CALLBACK_THRESHOLD] = BrickletCurrent12.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletCurrent12.FUNCTION_GET_ANALOG_VALUE_CALLBACK_THRESHOLD] = BrickletCurrent12.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletCurrent12.FUNCTION_SET_DEBOUNCE_PERIOD] = BrickletCurrent12.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletCurrent12.FUNCTION_GET_DEBOUNCE_PERIOD] = BrickletCurrent12.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletCurrent12.FUNCTION_GET_IDENTITY] = BrickletCurrent12.RESPONSE_EXPECTED_ALWAYS_TRUE

        self.callback_formats[BrickletCurrent12.CALLBACK_CURRENT] = 'h'
        self.callback_formats[BrickletCurrent12.CALLBACK_ANALOG_VALUE] = 'H'
        self.callback_formats[BrickletCurrent12.CALLBACK_CURRENT_REACHED] = 'h'
        self.callback_formats[BrickletCurrent12.CALLBACK_ANALOG_VALUE_REACHED] = 'H'
        self.callback_formats[BrickletCurrent12.CALLBACK_OVER_CURRENT] = ''


    def get_current(self):
        """
        Returns the current of the sensor. The value is in mA
        and between -12500mA and 12500mA.

        If you want to get the current periodically, it is recommended to use the
        :cb:`Current` callback and set the period with
        :func:`Set Current Callback Period`.
        """
        return self.ipcon.send_request(self, BrickletCurrent12.FUNCTION_GET_CURRENT, (), '', 'h')

    def calibrate(self):
        """
        Calibrates the 0 value of the sensor. You have to call this function
        when there is no current present.

        The zero point of the current sensor
        is depending on the exact properties of the analog-to-digital converter,
        the length of the Bricklet cable and the temperature. Thus, if you change
        the Brick or the environment in which the Bricklet is used, you might
        have to recalibrate.

        The resulting calibration will be saved on the EEPROM of the Current
        Bricklet.
        """
        self.ipcon.send_request(self, BrickletCurrent12.FUNCTION_CALIBRATE, (), '', '')

    def is_over_current(self):
        """
        Returns *true* if more than 12.5A were measured.

        .. note::
         To reset this value you have to power cycle the Bricklet.
        """
        return self.ipcon.send_request(self, BrickletCurrent12.FUNCTION_IS_OVER_CURRENT, (), '', '!')

    def get_analog_value(self):
        """
        Returns the value as read by a 12-bit analog-to-digital converter.
        The value is between 0 and 4095.

        .. note::
         The value returned by :func:`Get Current` is averaged over several samples
         to yield less noise, while :func:`Get Analog Value` gives back raw
         unfiltered analog values. The only reason to use :func:`Get Analog Value` is,
         if you need the full resolution of the analog-to-digital converter.

        If you want the analog value periodically, it is recommended to use the
        :cb:`Analog Value` callback and set the period with
        :func:`Set Analog Value Callback Period`.
        """
        return self.ipcon.send_request(self, BrickletCurrent12.FUNCTION_GET_ANALOG_VALUE, (), '', 'H')

    def set_current_callback_period(self, period):
        """
        Sets the period in ms with which the :cb:`Current` callback is triggered
        periodically. A value of 0 turns the callback off.

        The :cb:`Current` callback is only triggered if the current has changed since
        the last triggering.

        The default value is 0.
        """
        period = int(period)

        self.ipcon.send_request(self, BrickletCurrent12.FUNCTION_SET_CURRENT_CALLBACK_PERIOD, (period,), 'I', '')

    def get_current_callback_period(self):
        """
        Returns the period as set by :func:`Set Current Callback Period`.
        """
        return self.ipcon.send_request(self, BrickletCurrent12.FUNCTION_GET_CURRENT_CALLBACK_PERIOD, (), '', 'I')

    def set_analog_value_callback_period(self, period):
        """
        Sets the period in ms with which the :cb:`Analog Value` callback is triggered
        periodically. A value of 0 turns the callback off.

        The :cb:`Analog Value` callback is only triggered if the analog value has
        changed since the last triggering.

        The default value is 0.
        """
        period = int(period)

        self.ipcon.send_request(self, BrickletCurrent12.FUNCTION_SET_ANALOG_VALUE_CALLBACK_PERIOD, (period,), 'I', '')

    def get_analog_value_callback_period(self):
        """
        Returns the period as set by :func:`Set Analog Value Callback Period`.
        """
        return self.ipcon.send_request(self, BrickletCurrent12.FUNCTION_GET_ANALOG_VALUE_CALLBACK_PERIOD, (), '', 'I')

    def set_current_callback_threshold(self, option, min, max):
        """
        Sets the thresholds for the :cb:`Current Reached` callback.

        The following options are possible:

        .. csv-table::
         :header: "Option", "Description"
         :widths: 10, 100

         "'x'",    "Callback is turned off"
         "'o'",    "Callback is triggered when the current is *outside* the min and max values"
         "'i'",    "Callback is triggered when the current is *inside* the min and max values"
         "'<'",    "Callback is triggered when the current is smaller than the min value (max is ignored)"
         "'>'",    "Callback is triggered when the current is greater than the min value (max is ignored)"

        The default value is ('x', 0, 0).
        """
        option = create_char(option)
        min = int(min)
        max = int(max)

        self.ipcon.send_request(self, BrickletCurrent12.FUNCTION_SET_CURRENT_CALLBACK_THRESHOLD, (option, min, max), 'c h h', '')

    def get_current_callback_threshold(self):
        """
        Returns the threshold as set by :func:`Set Current Callback Threshold`.
        """
        return GetCurrentCallbackThreshold(*self.ipcon.send_request(self, BrickletCurrent12.FUNCTION_GET_CURRENT_CALLBACK_THRESHOLD, (), '', 'c h h'))

    def set_analog_value_callback_threshold(self, option, min, max):
        """
        Sets the thresholds for the :cb:`Analog Value Reached` callback.

        The following options are possible:

        .. csv-table::
         :header: "Option", "Description"
         :widths: 10, 100

         "'x'",    "Callback is turned off"
         "'o'",    "Callback is triggered when the analog value is *outside* the min and max values"
         "'i'",    "Callback is triggered when the analog value is *inside* the min and max values"
         "'<'",    "Callback is triggered when the analog value is smaller than the min value (max is ignored)"
         "'>'",    "Callback is triggered when the analog value is greater than the min value (max is ignored)"

        The default value is ('x', 0, 0).
        """
        option = create_char(option)
        min = int(min)
        max = int(max)

        self.ipcon.send_request(self, BrickletCurrent12.FUNCTION_SET_ANALOG_VALUE_CALLBACK_THRESHOLD, (option, min, max), 'c H H', '')

    def get_analog_value_callback_threshold(self):
        """
        Returns the threshold as set by :func:`Set Analog Value Callback Threshold`.
        """
        return GetAnalogValueCallbackThreshold(*self.ipcon.send_request(self, BrickletCurrent12.FUNCTION_GET_ANALOG_VALUE_CALLBACK_THRESHOLD, (), '', 'c H H'))

    def set_debounce_period(self, debounce):
        """
        Sets the period in ms with which the threshold callbacks

        * :cb:`Current Reached`,
        * :cb:`Analog Value Reached`

        are triggered, if the thresholds

        * :func:`Set Current Callback Threshold`,
        * :func:`Set Analog Value Callback Threshold`

        keep being reached.

        The default value is 100.
        """
        debounce = int(debounce)

        self.ipcon.send_request(self, BrickletCurrent12.FUNCTION_SET_DEBOUNCE_PERIOD, (debounce,), 'I', '')

    def get_debounce_period(self):
        """
        Returns the debounce period as set by :func:`Set Debounce Period`.
        """
        return self.ipcon.send_request(self, BrickletCurrent12.FUNCTION_GET_DEBOUNCE_PERIOD, (), '', 'I')

    def get_identity(self):
        """
        Returns the UID, the UID where the Bricklet is connected to,
        the position, the hardware and firmware version as well as the
        device identifier.

        The position can be 'a', 'b', 'c' or 'd'.

        The device identifier numbers can be found :ref:`here <device_identifier>`.
        |device_identifier_constant|
        """
        return GetIdentity(*self.ipcon.send_request(self, BrickletCurrent12.FUNCTION_GET_IDENTITY, (), '', '8s 8s c 3B 3B H'))

    def register_callback(self, callback_id, function):
        """
        Registers the given *function* with the given *callback_id*.
        """
        if function is None:
            self.registered_callbacks.pop(callback_id, None)
        else:
            self.registered_callbacks[callback_id] = function

Current12 = BrickletCurrent12 # for backward compatibility
