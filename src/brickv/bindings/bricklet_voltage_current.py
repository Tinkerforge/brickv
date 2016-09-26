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

GetConfiguration = namedtuple('Configuration', ['averaging', 'voltage_conversion_time', 'current_conversion_time'])
GetCalibration = namedtuple('Calibration', ['gain_multiplier', 'gain_divisor'])
GetCurrentCallbackThreshold = namedtuple('CurrentCallbackThreshold', ['option', 'min', 'max'])
GetVoltageCallbackThreshold = namedtuple('VoltageCallbackThreshold', ['option', 'min', 'max'])
GetPowerCallbackThreshold = namedtuple('PowerCallbackThreshold', ['option', 'min', 'max'])
GetIdentity = namedtuple('Identity', ['uid', 'connected_uid', 'position', 'hardware_version', 'firmware_version', 'device_identifier'])

class BrickletVoltageCurrent(Device):
    """
    Measures power, DC voltage and DC current up to 720W/36V/20A
    """

    DEVICE_IDENTIFIER = 227
    DEVICE_DISPLAY_NAME = 'Voltage/Current Bricklet'

    CALLBACK_CURRENT = 22
    CALLBACK_VOLTAGE = 23
    CALLBACK_POWER = 24
    CALLBACK_CURRENT_REACHED = 25
    CALLBACK_VOLTAGE_REACHED = 26
    CALLBACK_POWER_REACHED = 27

    FUNCTION_GET_CURRENT = 1
    FUNCTION_GET_VOLTAGE = 2
    FUNCTION_GET_POWER = 3
    FUNCTION_SET_CONFIGURATION = 4
    FUNCTION_GET_CONFIGURATION = 5
    FUNCTION_SET_CALIBRATION = 6
    FUNCTION_GET_CALIBRATION = 7
    FUNCTION_SET_CURRENT_CALLBACK_PERIOD = 8
    FUNCTION_GET_CURRENT_CALLBACK_PERIOD = 9
    FUNCTION_SET_VOLTAGE_CALLBACK_PERIOD = 10
    FUNCTION_GET_VOLTAGE_CALLBACK_PERIOD = 11
    FUNCTION_SET_POWER_CALLBACK_PERIOD = 12
    FUNCTION_GET_POWER_CALLBACK_PERIOD = 13
    FUNCTION_SET_CURRENT_CALLBACK_THRESHOLD = 14
    FUNCTION_GET_CURRENT_CALLBACK_THRESHOLD = 15
    FUNCTION_SET_VOLTAGE_CALLBACK_THRESHOLD = 16
    FUNCTION_GET_VOLTAGE_CALLBACK_THRESHOLD = 17
    FUNCTION_SET_POWER_CALLBACK_THRESHOLD = 18
    FUNCTION_GET_POWER_CALLBACK_THRESHOLD = 19
    FUNCTION_SET_DEBOUNCE_PERIOD = 20
    FUNCTION_GET_DEBOUNCE_PERIOD = 21
    FUNCTION_GET_IDENTITY = 255

    AVERAGING_1 = 0
    AVERAGING_4 = 1
    AVERAGING_16 = 2
    AVERAGING_64 = 3
    AVERAGING_128 = 4
    AVERAGING_256 = 5
    AVERAGING_512 = 6
    AVERAGING_1024 = 7
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

        self.response_expected[BrickletVoltageCurrent.FUNCTION_GET_CURRENT] = BrickletVoltageCurrent.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletVoltageCurrent.FUNCTION_GET_VOLTAGE] = BrickletVoltageCurrent.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletVoltageCurrent.FUNCTION_GET_POWER] = BrickletVoltageCurrent.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletVoltageCurrent.FUNCTION_SET_CONFIGURATION] = BrickletVoltageCurrent.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletVoltageCurrent.FUNCTION_GET_CONFIGURATION] = BrickletVoltageCurrent.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletVoltageCurrent.FUNCTION_SET_CALIBRATION] = BrickletVoltageCurrent.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletVoltageCurrent.FUNCTION_GET_CALIBRATION] = BrickletVoltageCurrent.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletVoltageCurrent.FUNCTION_SET_CURRENT_CALLBACK_PERIOD] = BrickletVoltageCurrent.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletVoltageCurrent.FUNCTION_GET_CURRENT_CALLBACK_PERIOD] = BrickletVoltageCurrent.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletVoltageCurrent.FUNCTION_SET_VOLTAGE_CALLBACK_PERIOD] = BrickletVoltageCurrent.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletVoltageCurrent.FUNCTION_GET_VOLTAGE_CALLBACK_PERIOD] = BrickletVoltageCurrent.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletVoltageCurrent.FUNCTION_SET_POWER_CALLBACK_PERIOD] = BrickletVoltageCurrent.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletVoltageCurrent.FUNCTION_GET_POWER_CALLBACK_PERIOD] = BrickletVoltageCurrent.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletVoltageCurrent.FUNCTION_SET_CURRENT_CALLBACK_THRESHOLD] = BrickletVoltageCurrent.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletVoltageCurrent.FUNCTION_GET_CURRENT_CALLBACK_THRESHOLD] = BrickletVoltageCurrent.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletVoltageCurrent.FUNCTION_SET_VOLTAGE_CALLBACK_THRESHOLD] = BrickletVoltageCurrent.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletVoltageCurrent.FUNCTION_GET_VOLTAGE_CALLBACK_THRESHOLD] = BrickletVoltageCurrent.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletVoltageCurrent.FUNCTION_SET_POWER_CALLBACK_THRESHOLD] = BrickletVoltageCurrent.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletVoltageCurrent.FUNCTION_GET_POWER_CALLBACK_THRESHOLD] = BrickletVoltageCurrent.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletVoltageCurrent.FUNCTION_SET_DEBOUNCE_PERIOD] = BrickletVoltageCurrent.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletVoltageCurrent.FUNCTION_GET_DEBOUNCE_PERIOD] = BrickletVoltageCurrent.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletVoltageCurrent.CALLBACK_CURRENT] = BrickletVoltageCurrent.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletVoltageCurrent.CALLBACK_VOLTAGE] = BrickletVoltageCurrent.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletVoltageCurrent.CALLBACK_POWER] = BrickletVoltageCurrent.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletVoltageCurrent.CALLBACK_CURRENT_REACHED] = BrickletVoltageCurrent.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletVoltageCurrent.CALLBACK_VOLTAGE_REACHED] = BrickletVoltageCurrent.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletVoltageCurrent.CALLBACK_POWER_REACHED] = BrickletVoltageCurrent.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletVoltageCurrent.FUNCTION_GET_IDENTITY] = BrickletVoltageCurrent.RESPONSE_EXPECTED_ALWAYS_TRUE

        self.callback_formats[BrickletVoltageCurrent.CALLBACK_CURRENT] = 'i'
        self.callback_formats[BrickletVoltageCurrent.CALLBACK_VOLTAGE] = 'i'
        self.callback_formats[BrickletVoltageCurrent.CALLBACK_POWER] = 'i'
        self.callback_formats[BrickletVoltageCurrent.CALLBACK_CURRENT_REACHED] = 'i'
        self.callback_formats[BrickletVoltageCurrent.CALLBACK_VOLTAGE_REACHED] = 'i'
        self.callback_formats[BrickletVoltageCurrent.CALLBACK_POWER_REACHED] = 'i'

    def get_current(self):
        """
        Returns the current. The value is in mA
        and between -20000mA and 20000mA.
        
        If you want to get the current periodically, it is recommended to use the
        callback :func:`Current` and set the period with 
        :func:`SetCurrentCallbackPeriod`.
        """
        return self.ipcon.send_request(self, BrickletVoltageCurrent.FUNCTION_GET_CURRENT, (), '', 'i')

    def get_voltage(self):
        """
        Returns the voltage. The value is in mV
        and between 0mV and 36000mV.
        
        If you want to get the voltage periodically, it is recommended to use the
        callback :func:`Voltage` and set the period with 
        :func:`SetVoltageCallbackPeriod`.
        """
        return self.ipcon.send_request(self, BrickletVoltageCurrent.FUNCTION_GET_VOLTAGE, (), '', 'i')

    def get_power(self):
        """
        Returns the power. The value is in mW
        and between 0mV and 720000mW.
        
        If you want to get the power periodically, it is recommended to use the
        callback :func:`Power` and set the period with 
        :func:`SetPowerCallbackPeriod`.
        """
        return self.ipcon.send_request(self, BrickletVoltageCurrent.FUNCTION_GET_POWER, (), '', 'i')

    def set_configuration(self, averaging, voltage_conversion_time, current_conversion_time):
        """
        Sets the configuration of the Voltage/Current Bricklet. It is
        possible to configure number of averages as well as
        voltage and current conversion time.
        
        Averaging:
        
        .. csv-table::
         :header: "Value", "Number of Averages"
         :widths: 20, 20
        
         "0",    "1"
         "1",    "4"
         "2",    "16"
         "3",    "64"
         "4",    "128"
         "5",    "256"
         "6",    "512"
         ">=7",  "1024"
        
        Voltage/Current conversion:
        
        .. csv-table::
         :header: "Value", "Conversion time"
         :widths: 20, 20
        
         "0",    "140µs"
         "1",    "204µs"
         "2",    "332µs"
         "3",    "588µs"
         "4",    "1.1ms"
         "5",    "2.116ms"
         "6",    "4.156ms"
         ">=7",  "8.244ms"
        
        The default values are 3, 4 and 4 (64, 1.1ms, 1.1ms) for averaging, voltage 
        conversion and current conversion.
        """
        self.ipcon.send_request(self, BrickletVoltageCurrent.FUNCTION_SET_CONFIGURATION, (averaging, voltage_conversion_time, current_conversion_time), 'B B B', '')

    def get_configuration(self):
        """
        Returns the configuration as set by :func:`SetConfiguration`.
        """
        return GetConfiguration(*self.ipcon.send_request(self, BrickletVoltageCurrent.FUNCTION_GET_CONFIGURATION, (), '', 'B B B'))

    def set_calibration(self, gain_multiplier, gain_divisor):
        """
        Since the shunt resistor that is used to measure the current is not
        perfectly precise, it needs to be calibrated by a multiplier and
        divisor if a very precise reading is needed.
        
        For example, if you are expecting a measurement of 1000mA and you
        are measuring 1023mA, you can calibrate the Voltage/Current Bricklet 
        by setting the multiplier to 1000 and the divisor to 1023.
        """
        self.ipcon.send_request(self, BrickletVoltageCurrent.FUNCTION_SET_CALIBRATION, (gain_multiplier, gain_divisor), 'H H', '')

    def get_calibration(self):
        """
        Returns the calibration as set by :func:`SetCalibration`.
        """
        return GetCalibration(*self.ipcon.send_request(self, BrickletVoltageCurrent.FUNCTION_GET_CALIBRATION, (), '', 'H H'))

    def set_current_callback_period(self, period):
        """
        Sets the period in ms with which the :func:`Current` callback is triggered
        periodically. A value of 0 turns the callback off.
        
        :func:`Current` is only triggered if the current has changed since the
        last triggering.
        
        The default value is 0.
        """
        self.ipcon.send_request(self, BrickletVoltageCurrent.FUNCTION_SET_CURRENT_CALLBACK_PERIOD, (period,), 'I', '')

    def get_current_callback_period(self):
        """
        Returns the period as set by :func:`SetCurrentCallbackPeriod`.
        """
        return self.ipcon.send_request(self, BrickletVoltageCurrent.FUNCTION_GET_CURRENT_CALLBACK_PERIOD, (), '', 'I')

    def set_voltage_callback_period(self, period):
        """
        Sets the period in ms with which the :func:`Voltage` callback is triggered
        periodically. A value of 0 turns the callback off.
        
        :func:`Voltage` is only triggered if the voltage has changed since the
        last triggering.
        
        The default value is 0.
        """
        self.ipcon.send_request(self, BrickletVoltageCurrent.FUNCTION_SET_VOLTAGE_CALLBACK_PERIOD, (period,), 'I', '')

    def get_voltage_callback_period(self):
        """
        Returns the period as set by :func:`SetVoltageCallbackPeriod`.
        """
        return self.ipcon.send_request(self, BrickletVoltageCurrent.FUNCTION_GET_VOLTAGE_CALLBACK_PERIOD, (), '', 'I')

    def set_power_callback_period(self, period):
        """
        Sets the period in ms with which the :func:`Power` callback is triggered
        periodically. A value of 0 turns the callback off.
        
        :func:`Power` is only triggered if the power has changed since the
        last triggering.
        
        The default value is 0.
        """
        self.ipcon.send_request(self, BrickletVoltageCurrent.FUNCTION_SET_POWER_CALLBACK_PERIOD, (period,), 'I', '')

    def get_power_callback_period(self):
        """
        Returns the period as set by :func:`GetPowerCallbackPeriod`.
        """
        return self.ipcon.send_request(self, BrickletVoltageCurrent.FUNCTION_GET_POWER_CALLBACK_PERIOD, (), '', 'I')

    def set_current_callback_threshold(self, option, min, max):
        """
        Sets the thresholds for the :func:`CurrentReached` callback. 
        
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
        self.ipcon.send_request(self, BrickletVoltageCurrent.FUNCTION_SET_CURRENT_CALLBACK_THRESHOLD, (option, min, max), 'c i i', '')

    def get_current_callback_threshold(self):
        """
        Returns the threshold as set by :func:`SetCurrentCallbackThreshold`.
        """
        return GetCurrentCallbackThreshold(*self.ipcon.send_request(self, BrickletVoltageCurrent.FUNCTION_GET_CURRENT_CALLBACK_THRESHOLD, (), '', 'c i i'))

    def set_voltage_callback_threshold(self, option, min, max):
        """
        Sets the thresholds for the :func:`VoltageReached` callback. 
        
        The following options are possible:
        
        .. csv-table::
         :header: "Option", "Description"
         :widths: 10, 100
        
         "'x'",    "Callback is turned off"
         "'o'",    "Callback is triggered when the voltage is *outside* the min and max values"
         "'i'",    "Callback is triggered when the voltage is *inside* the min and max values"
         "'<'",    "Callback is triggered when the voltage is smaller than the min value (max is ignored)"
         "'>'",    "Callback is triggered when the voltage is greater than the min value (max is ignored)"
        
        The default value is ('x', 0, 0).
        """
        self.ipcon.send_request(self, BrickletVoltageCurrent.FUNCTION_SET_VOLTAGE_CALLBACK_THRESHOLD, (option, min, max), 'c i i', '')

    def get_voltage_callback_threshold(self):
        """
        Returns the threshold as set by :func:`SetVoltageCallbackThreshold`.
        """
        return GetVoltageCallbackThreshold(*self.ipcon.send_request(self, BrickletVoltageCurrent.FUNCTION_GET_VOLTAGE_CALLBACK_THRESHOLD, (), '', 'c i i'))

    def set_power_callback_threshold(self, option, min, max):
        """
        Sets the thresholds for the :func:`PowerReached` callback. 
        
        The following options are possible:
        
        .. csv-table::
         :header: "Option", "Description"
         :widths: 10, 100
        
         "'x'",    "Callback is turned off"
         "'o'",    "Callback is triggered when the power is *outside* the min and max values"
         "'i'",    "Callback is triggered when the power is *inside* the min and max values"
         "'<'",    "Callback is triggered when the power is smaller than the min value (max is ignored)"
         "'>'",    "Callback is triggered when the power is greater than the min value (max is ignored)"
        
        The default value is ('x', 0, 0).
        """
        self.ipcon.send_request(self, BrickletVoltageCurrent.FUNCTION_SET_POWER_CALLBACK_THRESHOLD, (option, min, max), 'c i i', '')

    def get_power_callback_threshold(self):
        """
        Returns the threshold as set by :func:`SetPowerCallbackThreshold`.
        """
        return GetPowerCallbackThreshold(*self.ipcon.send_request(self, BrickletVoltageCurrent.FUNCTION_GET_POWER_CALLBACK_THRESHOLD, (), '', 'c i i'))

    def set_debounce_period(self, debounce):
        """
        Sets the period in ms with which the threshold callbacks
        
        * :func:`CurrentReached`,
        * :func:`VoltageReached`,
        * :func:`PowerReached`
        
        are triggered, if the thresholds
        
        * :func:`SetCurrentCallbackThreshold`,
        * :func:`SetVoltageCallbackThreshold`,
        * :func:`SetPowerCallbackThreshold`
        
        keep being reached.
        
        The default value is 100.
        """
        self.ipcon.send_request(self, BrickletVoltageCurrent.FUNCTION_SET_DEBOUNCE_PERIOD, (debounce,), 'I', '')

    def get_debounce_period(self):
        """
        Returns the debounce period as set by :func:`SetDebouncePeriod`.
        """
        return self.ipcon.send_request(self, BrickletVoltageCurrent.FUNCTION_GET_DEBOUNCE_PERIOD, (), '', 'I')

    def get_identity(self):
        """
        Returns the UID, the UID where the Bricklet is connected to, 
        the position, the hardware and firmware version as well as the
        device identifier.
        
        The position can be 'a', 'b', 'c' or 'd'.
        
        The device identifier numbers can be found :ref:`here <device_identifier>`.
        |device_identifier_constant|
        """
        return GetIdentity(*self.ipcon.send_request(self, BrickletVoltageCurrent.FUNCTION_GET_IDENTITY, (), '', '8s 8s c 3B 3B H'))

    def register_callback(self, id, callback):
        """
        Registers a callback with ID *id* to the function *callback*.
        """
        self.registered_callbacks[id] = callback

VoltageCurrent = BrickletVoltageCurrent # for backward compatibility
