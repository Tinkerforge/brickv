# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2017-05-11.      #
#                                                           #
# Python Bindings Version 2.1.13                            #
#                                                           #
# If you have a bugfix for this file and want to commit it, #
# please fix the bug in the generator. You can find a link  #
# to the generators git repository on tinkerforge.com       #
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

GetPositionCallbackThreshold = namedtuple('PositionCallbackThreshold', ['option', 'min', 'max'])
GetAnalogValueCallbackThreshold = namedtuple('AnalogValueCallbackThreshold', ['option', 'min', 'max'])
GetMotorPosition = namedtuple('MotorPosition', ['position', 'disable_after_reach'])
GetIdentity = namedtuple('Identity', ['uid', 'connected_uid', 'position', 'hardware_version', 'firmware_version', 'device_identifier'])

class BrickletMotorizedPoti(Device):
    """
    TODO
    """

    DEVICE_IDENTIFIER = 267
    DEVICE_DISPLAY_NAME = 'Motorized Poti Bricklet'

    CALLBACK_POSITION = 13
    CALLBACK_ANALOG_VALUE = 14
    CALLBACK_POSITION_REACHED = 15
    CALLBACK_ANALOG_VALUE_REACHED = 16


    FUNCTION_GET_POSITION = 1
    FUNCTION_GET_ANALOG_VALUE = 2
    FUNCTION_SET_POSITION_CALLBACK_PERIOD = 3
    FUNCTION_GET_POSITION_CALLBACK_PERIOD = 4
    FUNCTION_SET_ANALOG_VALUE_CALLBACK_PERIOD = 5
    FUNCTION_GET_ANALOG_VALUE_CALLBACK_PERIOD = 6
    FUNCTION_SET_POSITION_CALLBACK_THRESHOLD = 7
    FUNCTION_GET_POSITION_CALLBACK_THRESHOLD = 8
    FUNCTION_SET_ANALOG_VALUE_CALLBACK_THRESHOLD = 9
    FUNCTION_GET_ANALOG_VALUE_CALLBACK_THRESHOLD = 10
    FUNCTION_SET_DEBOUNCE_PERIOD = 11
    FUNCTION_GET_DEBOUNCE_PERIOD = 12
    FUNCTION_SET_MOTOR_POSITION = 17
    FUNCTION_GET_MOTOR_POSITION = 18
    FUNCTION_ENABLE_MOTOR = 19
    FUNCTION_DISABLE_MOTOR = 20
    FUNCTION_IS_MOTOR_ENABLED = 21
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

        self.response_expected[BrickletMotorizedPoti.FUNCTION_GET_POSITION] = BrickletMotorizedPoti.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletMotorizedPoti.FUNCTION_GET_ANALOG_VALUE] = BrickletMotorizedPoti.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletMotorizedPoti.FUNCTION_SET_POSITION_CALLBACK_PERIOD] = BrickletMotorizedPoti.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletMotorizedPoti.FUNCTION_GET_POSITION_CALLBACK_PERIOD] = BrickletMotorizedPoti.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletMotorizedPoti.FUNCTION_SET_ANALOG_VALUE_CALLBACK_PERIOD] = BrickletMotorizedPoti.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletMotorizedPoti.FUNCTION_GET_ANALOG_VALUE_CALLBACK_PERIOD] = BrickletMotorizedPoti.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletMotorizedPoti.FUNCTION_SET_POSITION_CALLBACK_THRESHOLD] = BrickletMotorizedPoti.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletMotorizedPoti.FUNCTION_GET_POSITION_CALLBACK_THRESHOLD] = BrickletMotorizedPoti.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletMotorizedPoti.FUNCTION_SET_ANALOG_VALUE_CALLBACK_THRESHOLD] = BrickletMotorizedPoti.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletMotorizedPoti.FUNCTION_GET_ANALOG_VALUE_CALLBACK_THRESHOLD] = BrickletMotorizedPoti.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletMotorizedPoti.FUNCTION_SET_DEBOUNCE_PERIOD] = BrickletMotorizedPoti.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletMotorizedPoti.FUNCTION_GET_DEBOUNCE_PERIOD] = BrickletMotorizedPoti.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletMotorizedPoti.CALLBACK_POSITION] = BrickletMotorizedPoti.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletMotorizedPoti.CALLBACK_ANALOG_VALUE] = BrickletMotorizedPoti.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletMotorizedPoti.CALLBACK_POSITION_REACHED] = BrickletMotorizedPoti.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletMotorizedPoti.CALLBACK_ANALOG_VALUE_REACHED] = BrickletMotorizedPoti.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletMotorizedPoti.FUNCTION_SET_MOTOR_POSITION] = BrickletMotorizedPoti.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletMotorizedPoti.FUNCTION_GET_MOTOR_POSITION] = BrickletMotorizedPoti.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletMotorizedPoti.FUNCTION_ENABLE_MOTOR] = BrickletMotorizedPoti.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletMotorizedPoti.FUNCTION_DISABLE_MOTOR] = BrickletMotorizedPoti.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletMotorizedPoti.FUNCTION_IS_MOTOR_ENABLED] = BrickletMotorizedPoti.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletMotorizedPoti.FUNCTION_GET_IDENTITY] = BrickletMotorizedPoti.RESPONSE_EXPECTED_ALWAYS_TRUE

        self.callback_formats[BrickletMotorizedPoti.CALLBACK_POSITION] = 'H'
        self.callback_formats[BrickletMotorizedPoti.CALLBACK_ANALOG_VALUE] = 'H'
        self.callback_formats[BrickletMotorizedPoti.CALLBACK_POSITION_REACHED] = 'H'
        self.callback_formats[BrickletMotorizedPoti.CALLBACK_ANALOG_VALUE_REACHED] = 'H'


    def get_position(self):
        """
        Returns the position of the linear potentiometer. The value is
        between 0 (slider down) and 100 (slider up).

        If you want to get the position periodically, it is recommended to use the
        :cb:`Position` callback and set the period with
        :func:`Set Position Callback Period`.
        """
        return self.ipcon.send_request(self, BrickletMotorizedPoti.FUNCTION_GET_POSITION, (), '', 'H')

    def get_analog_value(self):
        """
        Returns the value as read by a 12-bit analog-to-digital converter.
        The value is between 0 and 4095.

        .. note::
         The value returned by :func:`Get Position` is averaged over several samples
         to yield less noise, while :func:`Get Analog Value` gives back raw
         unfiltered analog values. The only reason to use :func:`Get Analog Value` is,
         if you need the full resolution of the analog-to-digital converter.

        If you want the analog value periodically, it is recommended to use the
        :cb:`Analog Value` callback and set the period with
        :func:`Set Analog Value Callback Period`.
        """
        return self.ipcon.send_request(self, BrickletMotorizedPoti.FUNCTION_GET_ANALOG_VALUE, (), '', 'H')

    def set_position_callback_period(self, period):
        """
        Sets the period in ms with which the :cb:`Position` callback is triggered
        periodically. A value of 0 turns the callback off.

        The :cb:`Position` callback is only triggered if the position has changed
        since the last triggering.

        The default value is 0.
        """
        self.ipcon.send_request(self, BrickletMotorizedPoti.FUNCTION_SET_POSITION_CALLBACK_PERIOD, (period,), 'I', '')

    def get_position_callback_period(self):
        """
        Returns the period as set by :func:`Set Position Callback Period`.
        """
        return self.ipcon.send_request(self, BrickletMotorizedPoti.FUNCTION_GET_POSITION_CALLBACK_PERIOD, (), '', 'I')

    def set_analog_value_callback_period(self, period):
        """
        Sets the period in ms with which the :cb:`Analog Value` callback is triggered
        periodically. A value of 0 turns the callback off.

        The :cb:`Analog Value` callback is only triggered if the analog value has
        changed since the last triggering.

        The default value is 0.
        """
        self.ipcon.send_request(self, BrickletMotorizedPoti.FUNCTION_SET_ANALOG_VALUE_CALLBACK_PERIOD, (period,), 'I', '')

    def get_analog_value_callback_period(self):
        """
        Returns the period as set by :func:`Set Analog Value Callback Period`.
        """
        return self.ipcon.send_request(self, BrickletMotorizedPoti.FUNCTION_GET_ANALOG_VALUE_CALLBACK_PERIOD, (), '', 'I')

    def set_position_callback_threshold(self, option, min, max):
        """
        Sets the thresholds for the :cb:`Position Reached` callback.

        The following options are possible:

        .. csv-table::
         :header: "Option", "Description"
         :widths: 10, 100

         "'x'",    "Callback is turned off"
         "'o'",    "Callback is triggered when the position is *outside* the min and max values"
         "'i'",    "Callback is triggered when the position is *inside* the min and max values"
         "'<'",    "Callback is triggered when the position is smaller than the min value (max is ignored)"
         "'>'",    "Callback is triggered when the position is greater than the min value (max is ignored)"

        The default value is ('x', 0, 0).
        """
        self.ipcon.send_request(self, BrickletMotorizedPoti.FUNCTION_SET_POSITION_CALLBACK_THRESHOLD, (option, min, max), 'c H H', '')

    def get_position_callback_threshold(self):
        """
        Returns the threshold as set by :func:`Set Position Callback Threshold`.
        """
        return GetPositionCallbackThreshold(*self.ipcon.send_request(self, BrickletMotorizedPoti.FUNCTION_GET_POSITION_CALLBACK_THRESHOLD, (), '', 'c H H'))

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
        self.ipcon.send_request(self, BrickletMotorizedPoti.FUNCTION_SET_ANALOG_VALUE_CALLBACK_THRESHOLD, (option, min, max), 'c H H', '')

    def get_analog_value_callback_threshold(self):
        """
        Returns the threshold as set by :func:`Set Analog Value Callback Threshold`.
        """
        return GetAnalogValueCallbackThreshold(*self.ipcon.send_request(self, BrickletMotorizedPoti.FUNCTION_GET_ANALOG_VALUE_CALLBACK_THRESHOLD, (), '', 'c H H'))

    def set_debounce_period(self, debounce):
        """
        Sets the period in ms with which the threshold callbacks

        * :cb:`Position Reached`,
        * :cb:`Analog Value Reached`

        are triggered, if the thresholds

        * :func:`Set Position Callback Threshold`,
        * :func:`Set Analog Value Callback Threshold`

        keep being reached.

        The default value is 100.
        """
        self.ipcon.send_request(self, BrickletMotorizedPoti.FUNCTION_SET_DEBOUNCE_PERIOD, (debounce,), 'I', '')

    def get_debounce_period(self):
        """
        Returns the debounce period as set by :func:`Set Debounce Period`.
        """
        return self.ipcon.send_request(self, BrickletMotorizedPoti.FUNCTION_GET_DEBOUNCE_PERIOD, (), '', 'I')

    def set_motor_position(self, position, disable_after_reach):
        """
        TODO
        """
        self.ipcon.send_request(self, BrickletMotorizedPoti.FUNCTION_SET_MOTOR_POSITION, (position, disable_after_reach), 'H !', '')

    def get_motor_position(self):
        """
        TODO
        """
        return GetMotorPosition(*self.ipcon.send_request(self, BrickletMotorizedPoti.FUNCTION_GET_MOTOR_POSITION, (), '', 'H !'))

    def enable_motor(self):
        """
        TODO
        """
        self.ipcon.send_request(self, BrickletMotorizedPoti.FUNCTION_ENABLE_MOTOR, (), '', '')

    def disable_motor(self):
        """
        TODO
        """
        self.ipcon.send_request(self, BrickletMotorizedPoti.FUNCTION_DISABLE_MOTOR, (), '', '')

    def is_motor_enabled(self):
        """
        TODO
        """
        return self.ipcon.send_request(self, BrickletMotorizedPoti.FUNCTION_IS_MOTOR_ENABLED, (), '', '!')

    def get_identity(self):
        """
        Returns the UID, the UID where the Bricklet is connected to,
        the position, the hardware and firmware version as well as the
        device identifier.

        The position can be 'a', 'b', 'c' or 'd'.

        The device identifier numbers can be found :ref:`here <device_identifier>`.
        |device_identifier_constant|
        """
        return GetIdentity(*self.ipcon.send_request(self, BrickletMotorizedPoti.FUNCTION_GET_IDENTITY, (), '', '8s 8s c 3B 3B H'))

    def register_callback(self, id_, callback):
        """
        Registers a callback with ID *id* to the function *callback*.
        """
        if callback is None:
            self.registered_callbacks.pop(id_, None)
        else:
            self.registered_callbacks[id_] = callback

MotorizedPoti = BrickletMotorizedPoti # for backward compatibility
