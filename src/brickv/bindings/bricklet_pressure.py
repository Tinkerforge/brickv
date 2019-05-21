# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2019-05-21.      #
#                                                           #
# Python Bindings Version 2.1.22                            #
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

GetPressureCallbackThreshold = namedtuple('PressureCallbackThreshold', ['option', 'min', 'max'])
GetAnalogValueCallbackThreshold = namedtuple('AnalogValueCallbackThreshold', ['option', 'min', 'max'])
GetIdentity = namedtuple('Identity', ['uid', 'connected_uid', 'position', 'hardware_version', 'firmware_version', 'device_identifier'])

class BrickletPressure(Device):
    """
    Measures pressure with various pressure sensors
    """

    DEVICE_IDENTIFIER = 269
    DEVICE_DISPLAY_NAME = 'Pressure Bricklet'
    DEVICE_URL_PART = 'pressure' # internal

    CALLBACK_PRESSURE = 17
    CALLBACK_ANALOG_VALUE = 18
    CALLBACK_PRESSURE_REACHED = 19
    CALLBACK_ANALOG_VALUE_REACHED = 20


    FUNCTION_GET_PRESSURE = 1
    FUNCTION_GET_ANALOG_VALUE = 2
    FUNCTION_SET_PRESSURE_CALLBACK_PERIOD = 3
    FUNCTION_GET_PRESSURE_CALLBACK_PERIOD = 4
    FUNCTION_SET_ANALOG_VALUE_CALLBACK_PERIOD = 5
    FUNCTION_GET_ANALOG_VALUE_CALLBACK_PERIOD = 6
    FUNCTION_SET_PRESSURE_CALLBACK_THRESHOLD = 7
    FUNCTION_GET_PRESSURE_CALLBACK_THRESHOLD = 8
    FUNCTION_SET_ANALOG_VALUE_CALLBACK_THRESHOLD = 9
    FUNCTION_GET_ANALOG_VALUE_CALLBACK_THRESHOLD = 10
    FUNCTION_SET_DEBOUNCE_PERIOD = 11
    FUNCTION_GET_DEBOUNCE_PERIOD = 12
    FUNCTION_SET_SENSOR_TYPE = 13
    FUNCTION_GET_SENSOR_TYPE = 14
    FUNCTION_SET_MOVING_AVERAGE = 15
    FUNCTION_GET_MOVING_AVERAGE = 16
    FUNCTION_GET_IDENTITY = 255

    THRESHOLD_OPTION_OFF = 'x'
    THRESHOLD_OPTION_OUTSIDE = 'o'
    THRESHOLD_OPTION_INSIDE = 'i'
    THRESHOLD_OPTION_SMALLER = '<'
    THRESHOLD_OPTION_GREATER = '>'
    SENSOR_TYPE_MPX5500 = 0
    SENSOR_TYPE_MPXV5004 = 1
    SENSOR_TYPE_MPX4115A = 2

    def __init__(self, uid, ipcon):
        """
        Creates an object with the unique device ID *uid* and adds it to
        the IP Connection *ipcon*.
        """
        Device.__init__(self, uid, ipcon)

        self.api_version = (2, 0, 0)

        self.response_expected[BrickletPressure.FUNCTION_GET_PRESSURE] = BrickletPressure.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletPressure.FUNCTION_GET_ANALOG_VALUE] = BrickletPressure.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletPressure.FUNCTION_SET_PRESSURE_CALLBACK_PERIOD] = BrickletPressure.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletPressure.FUNCTION_GET_PRESSURE_CALLBACK_PERIOD] = BrickletPressure.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletPressure.FUNCTION_SET_ANALOG_VALUE_CALLBACK_PERIOD] = BrickletPressure.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletPressure.FUNCTION_GET_ANALOG_VALUE_CALLBACK_PERIOD] = BrickletPressure.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletPressure.FUNCTION_SET_PRESSURE_CALLBACK_THRESHOLD] = BrickletPressure.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletPressure.FUNCTION_GET_PRESSURE_CALLBACK_THRESHOLD] = BrickletPressure.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletPressure.FUNCTION_SET_ANALOG_VALUE_CALLBACK_THRESHOLD] = BrickletPressure.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletPressure.FUNCTION_GET_ANALOG_VALUE_CALLBACK_THRESHOLD] = BrickletPressure.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletPressure.FUNCTION_SET_DEBOUNCE_PERIOD] = BrickletPressure.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletPressure.FUNCTION_GET_DEBOUNCE_PERIOD] = BrickletPressure.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletPressure.FUNCTION_SET_SENSOR_TYPE] = BrickletPressure.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletPressure.FUNCTION_GET_SENSOR_TYPE] = BrickletPressure.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletPressure.FUNCTION_SET_MOVING_AVERAGE] = BrickletPressure.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletPressure.FUNCTION_GET_MOVING_AVERAGE] = BrickletPressure.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletPressure.FUNCTION_GET_IDENTITY] = BrickletPressure.RESPONSE_EXPECTED_ALWAYS_TRUE

        self.callback_formats[BrickletPressure.CALLBACK_PRESSURE] = 'i'
        self.callback_formats[BrickletPressure.CALLBACK_ANALOG_VALUE] = 'i'
        self.callback_formats[BrickletPressure.CALLBACK_PRESSURE_REACHED] = 'i'
        self.callback_formats[BrickletPressure.CALLBACK_ANALOG_VALUE_REACHED] = 'i'


    def get_pressure(self):
        """
        Returns the measured pressure in Pa.

        If you want to get the pressure periodically, it is recommended to use the
        :cb:`Pressure` callback and set the period with
        :func:`Set Pressure Callback Period`.
        """
        return self.ipcon.send_request(self, BrickletPressure.FUNCTION_GET_PRESSURE, (), '', 'i')

    def get_analog_value(self):
        """
        Returns the value as read by a 12-bit analog-to-digital converter.
        The value is between 0 and 4095.

        If you want the analog value periodically, it is recommended to use the
        :cb:`Analog Value` callback and set the period with
        :func:`Set Analog Value Callback Period`.
        """
        return self.ipcon.send_request(self, BrickletPressure.FUNCTION_GET_ANALOG_VALUE, (), '', 'i')

    def set_pressure_callback_period(self, period):
        """
        Sets the period in ms with which the :cb:`Pressure` callback is triggered
        periodically. A value of 0 turns the callback off.

        The :cb:`Pressure` callback is only triggered if the pressure has changed
        since the last triggering.

        The default value is 0.
        """
        period = int(period)

        self.ipcon.send_request(self, BrickletPressure.FUNCTION_SET_PRESSURE_CALLBACK_PERIOD, (period,), 'I', '')

    def get_pressure_callback_period(self):
        """
        Returns the period as set by :func:`Set Pressure Callback Period`.
        """
        return self.ipcon.send_request(self, BrickletPressure.FUNCTION_GET_PRESSURE_CALLBACK_PERIOD, (), '', 'I')

    def set_analog_value_callback_period(self, period):
        """
        Sets the period in ms with which the :cb:`Analog Value` callback is triggered
        periodically. A value of 0 turns the callback off.

        The :cb:`Analog Value` callback is only triggered if the analog value has
        changed since the last triggering.

        The default value is 0.
        """
        period = int(period)

        self.ipcon.send_request(self, BrickletPressure.FUNCTION_SET_ANALOG_VALUE_CALLBACK_PERIOD, (period,), 'I', '')

    def get_analog_value_callback_period(self):
        """
        Returns the period as set by :func:`Set Analog Value Callback Period`.
        """
        return self.ipcon.send_request(self, BrickletPressure.FUNCTION_GET_ANALOG_VALUE_CALLBACK_PERIOD, (), '', 'I')

    def set_pressure_callback_threshold(self, option, min, max):
        """
        Sets the thresholds for the :cb:`Pressure Reached` callback.

        The following options are possible:

        .. csv-table::
         :header: "Option", "Description"
         :widths: 10, 100

         "'x'",    "Callback is turned off"
         "'o'",    "Callback is triggered when the pressure is *outside* the min and max values"
         "'i'",    "Callback is triggered when the pressure is *inside* the min and max values"
         "'<'",    "Callback is triggered when the pressure is smaller than the min value (max is ignored)"
         "'>'",    "Callback is triggered when the pressure is greater than the min value (max is ignored)"

        The default value is ('x', 0, 0).
        """
        option = create_char(option)
        min = int(min)
        max = int(max)

        self.ipcon.send_request(self, BrickletPressure.FUNCTION_SET_PRESSURE_CALLBACK_THRESHOLD, (option, min, max), 'c i i', '')

    def get_pressure_callback_threshold(self):
        """
        Returns the threshold as set by :func:`Set Pressure Callback Threshold`.
        """
        return GetPressureCallbackThreshold(*self.ipcon.send_request(self, BrickletPressure.FUNCTION_GET_PRESSURE_CALLBACK_THRESHOLD, (), '', 'c i i'))

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

        self.ipcon.send_request(self, BrickletPressure.FUNCTION_SET_ANALOG_VALUE_CALLBACK_THRESHOLD, (option, min, max), 'c i i', '')

    def get_analog_value_callback_threshold(self):
        """
        Returns the threshold as set by :func:`Set Analog Value Callback Threshold`.
        """
        return GetAnalogValueCallbackThreshold(*self.ipcon.send_request(self, BrickletPressure.FUNCTION_GET_ANALOG_VALUE_CALLBACK_THRESHOLD, (), '', 'c i i'))

    def set_debounce_period(self, debounce):
        """
        Sets the period in ms with which the threshold callbacks

        * :cb:`Pressure Reached`,
        * :cb:`Analog Value Reached`

        are triggered, if the thresholds

        * :func:`Set Pressure Callback Threshold`,
        * :func:`Set Analog Value Callback Threshold`

        keep being reached.

        The default value is 100.
        """
        debounce = int(debounce)

        self.ipcon.send_request(self, BrickletPressure.FUNCTION_SET_DEBOUNCE_PERIOD, (debounce,), 'I', '')

    def get_debounce_period(self):
        """
        Returns the debounce period as set by :func:`Set Debounce Period`.
        """
        return self.ipcon.send_request(self, BrickletPressure.FUNCTION_GET_DEBOUNCE_PERIOD, (), '', 'I')

    def set_sensor_type(self, sensor):
        """
        Sets the sensor type. Possible values are:

        * 0 = MPX5500 (0 to 500 kPa)
        * 1 = MPXV5004, MPVZ5004 (0 to 3.92 kPa)
        * 2 = MPX4115A (15 to 115 kPa)

        The default value is 0.
        """
        sensor = int(sensor)

        self.ipcon.send_request(self, BrickletPressure.FUNCTION_SET_SENSOR_TYPE, (sensor,), 'B', '')

    def get_sensor_type(self):
        """
        Returns the sensor type as set by :func:`Set Sensor Type`.
        """
        return self.ipcon.send_request(self, BrickletPressure.FUNCTION_GET_SENSOR_TYPE, (), '', 'B')

    def set_moving_average(self, average):
        """
        Sets the length of a `moving averaging <https://en.wikipedia.org/wiki/Moving_average>`__
        for the pressure.

        Setting the length to 1 will turn the averaging off. With less
        averaging, there is more noise on the data.

        The range for the averaging is 1-50.

        The default value is 50.
        """
        average = int(average)

        self.ipcon.send_request(self, BrickletPressure.FUNCTION_SET_MOVING_AVERAGE, (average,), 'B', '')

    def get_moving_average(self):
        """
        Returns the length of the moving average as set by :func:`Set Moving Average`.
        """
        return self.ipcon.send_request(self, BrickletPressure.FUNCTION_GET_MOVING_AVERAGE, (), '', 'B')

    def get_identity(self):
        """
        Returns the UID, the UID where the Bricklet is connected to,
        the position, the hardware and firmware version as well as the
        device identifier.

        The position can be 'a', 'b', 'c' or 'd'.

        The device identifier numbers can be found :ref:`here <device_identifier>`.
        |device_identifier_constant|
        """
        return GetIdentity(*self.ipcon.send_request(self, BrickletPressure.FUNCTION_GET_IDENTITY, (), '', '8s 8s c 3B 3B H'))

    def register_callback(self, callback_id, function):
        """
        Registers the given *function* with the given *callback_id*.
        """
        if function is None:
            self.registered_callbacks.pop(callback_id, None)
        else:
            self.registered_callbacks[callback_id] = function

Pressure = BrickletPressure # for backward compatibility
