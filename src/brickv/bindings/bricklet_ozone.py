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

#### __DEVICE_IS_NOT_RELEASED__ ####

from collections import namedtuple

try:
    from .ip_connection import Device, IPConnection, Error, create_char, create_char_list, create_string, create_chunk_data
except ValueError:
    from ip_connection import Device, IPConnection, Error, create_char, create_char_list, create_string, create_chunk_data

GetOzoneConcentrationCallbackThreshold = namedtuple('OzoneConcentrationCallbackThreshold', ['option', 'min', 'max'])
GetAnalogValueCallbackThreshold = namedtuple('AnalogValueCallbackThreshold', ['option', 'min', 'max'])
GetIdentity = namedtuple('Identity', ['uid', 'connected_uid', 'position', 'hardware_version', 'firmware_version', 'device_identifier'])

class BrickletOzone(Device):
    """
    Measures ozone concentration in ppb
    """

    DEVICE_IDENTIFIER = 261
    DEVICE_DISPLAY_NAME = 'Ozone Bricklet'
    DEVICE_URL_PART = 'ozone' # internal

    CALLBACK_OZONE_CONCENTRATION = 15
    CALLBACK_ANALOG_VALUE = 16
    CALLBACK_OZONE_CONCENTRATION_REACHED = 17
    CALLBACK_ANALOG_VALUE_REACHED = 18


    FUNCTION_GET_OZONE_CONCENTRATION = 1
    FUNCTION_GET_ANALOG_VALUE = 2
    FUNCTION_SET_OZONE_CONCENTRATION_CALLBACK_PERIOD = 3
    FUNCTION_GET_OZONE_CONCENTRATION_CALLBACK_PERIOD = 4
    FUNCTION_SET_ANALOG_VALUE_CALLBACK_PERIOD = 5
    FUNCTION_GET_ANALOG_VALUE_CALLBACK_PERIOD = 6
    FUNCTION_SET_OZONE_CONCENTRATION_CALLBACK_THRESHOLD = 7
    FUNCTION_GET_OZONE_CONCENTRATION_CALLBACK_THRESHOLD = 8
    FUNCTION_SET_ANALOG_VALUE_CALLBACK_THRESHOLD = 9
    FUNCTION_GET_ANALOG_VALUE_CALLBACK_THRESHOLD = 10
    FUNCTION_SET_DEBOUNCE_PERIOD = 11
    FUNCTION_GET_DEBOUNCE_PERIOD = 12
    FUNCTION_SET_MOVING_AVERAGE = 13
    FUNCTION_GET_MOVING_AVERAGE = 14
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

        self.response_expected[BrickletOzone.FUNCTION_GET_OZONE_CONCENTRATION] = BrickletOzone.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletOzone.FUNCTION_GET_ANALOG_VALUE] = BrickletOzone.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletOzone.FUNCTION_SET_OZONE_CONCENTRATION_CALLBACK_PERIOD] = BrickletOzone.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletOzone.FUNCTION_GET_OZONE_CONCENTRATION_CALLBACK_PERIOD] = BrickletOzone.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletOzone.FUNCTION_SET_ANALOG_VALUE_CALLBACK_PERIOD] = BrickletOzone.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletOzone.FUNCTION_GET_ANALOG_VALUE_CALLBACK_PERIOD] = BrickletOzone.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletOzone.FUNCTION_SET_OZONE_CONCENTRATION_CALLBACK_THRESHOLD] = BrickletOzone.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletOzone.FUNCTION_GET_OZONE_CONCENTRATION_CALLBACK_THRESHOLD] = BrickletOzone.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletOzone.FUNCTION_SET_ANALOG_VALUE_CALLBACK_THRESHOLD] = BrickletOzone.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletOzone.FUNCTION_GET_ANALOG_VALUE_CALLBACK_THRESHOLD] = BrickletOzone.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletOzone.FUNCTION_SET_DEBOUNCE_PERIOD] = BrickletOzone.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletOzone.FUNCTION_GET_DEBOUNCE_PERIOD] = BrickletOzone.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletOzone.FUNCTION_SET_MOVING_AVERAGE] = BrickletOzone.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletOzone.FUNCTION_GET_MOVING_AVERAGE] = BrickletOzone.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletOzone.FUNCTION_GET_IDENTITY] = BrickletOzone.RESPONSE_EXPECTED_ALWAYS_TRUE

        self.callback_formats[BrickletOzone.CALLBACK_OZONE_CONCENTRATION] = 'H'
        self.callback_formats[BrickletOzone.CALLBACK_ANALOG_VALUE] = 'H'
        self.callback_formats[BrickletOzone.CALLBACK_OZONE_CONCENTRATION_REACHED] = 'H'
        self.callback_formats[BrickletOzone.CALLBACK_ANALOG_VALUE_REACHED] = 'H'


    def get_ozone_concentration(self):
        """
        Returns the measured ozone concentration. The value is in
        `ppb (parts per billion) <https://en.wikipedia.org/wiki/Parts-per_notation>`__
        and between 0 to 250.

        If you want to get the ozone concentration periodically, it is recommended to
        use the :cb:`Ozone Concentration` callback and set the period with
        :func:`Set Ozone Concentration Callback Period`.
        """
        return self.ipcon.send_request(self, BrickletOzone.FUNCTION_GET_OZONE_CONCENTRATION, (), '', 'H')

    def get_analog_value(self):
        """
        Returns the value as read by a 12-bit analog-to-digital converter.
        The value is between 0 and 4095.

        If you want the analog value periodically, it is recommended to use the
        :cb:`Analog Value` callback and set the period with
        :func:`Set Analog Value Callback Period`.
        """
        return self.ipcon.send_request(self, BrickletOzone.FUNCTION_GET_ANALOG_VALUE, (), '', 'H')

    def set_ozone_concentration_callback_period(self, period):
        """
        Sets the period in ms with which the :cb:`Ozone Concentration` callback is
        triggered periodically. A value of 0 turns the callback off.

        The :cb:`Ozone Concentration` callback is only triggered if the
        ozone concentration has changed since the last triggering.

        The default value is 0.
        """
        period = int(period)

        self.ipcon.send_request(self, BrickletOzone.FUNCTION_SET_OZONE_CONCENTRATION_CALLBACK_PERIOD, (period,), 'I', '')

    def get_ozone_concentration_callback_period(self):
        """
        Returns the period as set by :func:`Set Ozone Concentration Callback Period`.
        """
        return self.ipcon.send_request(self, BrickletOzone.FUNCTION_GET_OZONE_CONCENTRATION_CALLBACK_PERIOD, (), '', 'I')

    def set_analog_value_callback_period(self, period):
        """
        Sets the period in ms with which the :cb:`Analog Value` callback is triggered
        periodically. A value of 0 turns the callback off.

        The :cb:`Analog Value` callback is only triggered if the analog value has
        changed since the last triggering.

        The default value is 0.
        """
        period = int(period)

        self.ipcon.send_request(self, BrickletOzone.FUNCTION_SET_ANALOG_VALUE_CALLBACK_PERIOD, (period,), 'I', '')

    def get_analog_value_callback_period(self):
        """
        Returns the period as set by :func:`Set Analog Value Callback Period`.
        """
        return self.ipcon.send_request(self, BrickletOzone.FUNCTION_GET_ANALOG_VALUE_CALLBACK_PERIOD, (), '', 'I')

    def set_ozone_concentration_callback_threshold(self, option, min, max):
        """
        Sets the thresholds for the :cb:`Ozone Concentration Reached` callback.

        The following options are possible:

        .. csv-table::
         :header: "Option", "Description"
         :widths: 10, 100

         "'x'",    "Callback is turned off"
         "'o'",    "Callback is triggered when the ozone concentration is *outside* the min and max values"
         "'i'",    "Callback is triggered when the ozone concentration is *inside* the min and max values"
         "'<'",    "Callback is triggered when the ozone concentration is smaller than the min value (max is ignored)"
         "'>'",    "Callback is triggered when the ozone concentration is greater than the min value (max is ignored)"

        The default value is ('x', 0, 0).
        """
        option = create_char(option)
        min = int(min)
        max = int(max)

        self.ipcon.send_request(self, BrickletOzone.FUNCTION_SET_OZONE_CONCENTRATION_CALLBACK_THRESHOLD, (option, min, max), 'c H H', '')

    def get_ozone_concentration_callback_threshold(self):
        """
        Returns the threshold as set by :func:`Set Ozone Concentration Callback Threshold`.
        """
        return GetOzoneConcentrationCallbackThreshold(*self.ipcon.send_request(self, BrickletOzone.FUNCTION_GET_OZONE_CONCENTRATION_CALLBACK_THRESHOLD, (), '', 'c H H'))

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

        self.ipcon.send_request(self, BrickletOzone.FUNCTION_SET_ANALOG_VALUE_CALLBACK_THRESHOLD, (option, min, max), 'c H H', '')

    def get_analog_value_callback_threshold(self):
        """
        Returns the threshold as set by :func:`Set Analog Value Callback Threshold`.
        """
        return GetAnalogValueCallbackThreshold(*self.ipcon.send_request(self, BrickletOzone.FUNCTION_GET_ANALOG_VALUE_CALLBACK_THRESHOLD, (), '', 'c H H'))

    def set_debounce_period(self, debounce):
        """
        Sets the period in ms with which the threshold callbacks

        * :cb:`Ozone Concentration Reached`,
        * :cb:`Analog Value Reached`

        are triggered, if the thresholds

        * :func:`Set Ozone Concentration Callback Threshold`,
        * :func:`Set Analog Value Callback Threshold`

        keep being reached.

        The default value is 100.
        """
        debounce = int(debounce)

        self.ipcon.send_request(self, BrickletOzone.FUNCTION_SET_DEBOUNCE_PERIOD, (debounce,), 'I', '')

    def get_debounce_period(self):
        """
        Returns the debounce period as set by :func:`Set Debounce Period`.
        """
        return self.ipcon.send_request(self, BrickletOzone.FUNCTION_GET_DEBOUNCE_PERIOD, (), '', 'I')

    def set_moving_average(self, average):
        """
        Sets the length of a `moving averaging <https://en.wikipedia.org/wiki/Moving_average>`__
        for the ozone concentration.

        Setting the length to 1 will turn the averaging off. With less
        averaging, there is more noise on the data.

        The range for the averaging is 1-50.

        The default value is 50.
        """
        average = int(average)

        self.ipcon.send_request(self, BrickletOzone.FUNCTION_SET_MOVING_AVERAGE, (average,), 'B', '')

    def get_moving_average(self):
        """
        Returns the length of the moving average as set by :func:`Set Moving Average`.
        """
        return self.ipcon.send_request(self, BrickletOzone.FUNCTION_GET_MOVING_AVERAGE, (), '', 'B')

    def get_identity(self):
        """
        Returns the UID, the UID where the Bricklet is connected to,
        the position, the hardware and firmware version as well as the
        device identifier.

        The position can be 'a', 'b', 'c' or 'd'.

        The device identifier numbers can be found :ref:`here <device_identifier>`.
        |device_identifier_constant|
        """
        return GetIdentity(*self.ipcon.send_request(self, BrickletOzone.FUNCTION_GET_IDENTITY, (), '', '8s 8s c 3B 3B H'))

    def register_callback(self, callback_id, function):
        """
        Registers the given *function* with the given *callback_id*.
        """
        if function is None:
            self.registered_callbacks.pop(callback_id, None)
        else:
            self.registered_callbacks[callback_id] = function

Ozone = BrickletOzone # for backward compatibility
