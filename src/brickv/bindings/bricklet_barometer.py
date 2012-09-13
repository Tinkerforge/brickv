# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2012-08-24.      #
#                                                           #
# If you have a bugfix for this file and want to commit it, #
# please fix the bug in the generator. You can find a link  #
# to the generator git on tinkerforge.com                   #
#############################################################

try:
    from collections import namedtuple
except ImportError:
    from .ip_connection import namedtuple
from .ip_connection import Device, IPConnection, Error

GetAirPressureCallbackThreshold = namedtuple('AirPressureCallbackThreshold', ['option', 'min', 'max'])
GetAltitudeCallbackThreshold = namedtuple('AltitudeCallbackThreshold', ['option', 'min', 'max'])

class Barometer(Device):
    """
    Device for sensing air pressure and altitude changes
    """

    CALLBACK_AIR_PRESSURE = 15
    CALLBACK_ALTITUDE = 16
    CALLBACK_AIR_PRESSURE_REACHED = 17
    CALLBACK_ALTITUDE_REACHED = 18

    FUNCTION_GET_AIR_PRESSURE = 1
    FUNCTION_GET_ALTITUDE = 2
    FUNCTION_GET_TEMPERATURE = 3
    FUNCTION_SET_AIR_PRESSURE_CALLBACK_PERIOD = 4
    FUNCTION_GET_AIR_PRESSURE_CALLBACK_PERIOD = 5
    FUNCTION_SET_ALTITUDE_CALLBACK_PERIOD = 6
    FUNCTION_GET_ALTITUDE_CALLBACK_PERIOD = 7
    FUNCTION_SET_AIR_PRESSURE_CALLBACK_THRESHOLD = 8
    FUNCTION_GET_AIR_PRESSURE_CALLBACK_THRESHOLD = 9
    FUNCTION_SET_ALTITUDE_CALLBACK_THRESHOLD = 10
    FUNCTION_GET_ALTITUDE_CALLBACK_THRESHOLD = 11
    FUNCTION_SET_DEBOUNCE_PERIOD = 12
    FUNCTION_GET_DEBOUNCE_PERIOD = 13
    FUNCTION_CALIBRATE_ALTITUDE = 14

    def __init__(self, uid):
        """
        Creates an object with the unique device ID *uid*. This object can
        then be added to the IP connection.
        """
        Device.__init__(self, uid)

        self.expected_name = 'Barometer Bricklet'

        self.binding_version = [1, 0, 0]

        self.callback_formats[Barometer.CALLBACK_AIR_PRESSURE] = 'i'
        self.callback_formats[Barometer.CALLBACK_ALTITUDE] = 'i'
        self.callback_formats[Barometer.CALLBACK_AIR_PRESSURE_REACHED] = 'i'
        self.callback_formats[Barometer.CALLBACK_ALTITUDE_REACHED] = 'i'

    def get_air_pressure(self):
        """
        Returns the air pressure of the air pressure sensor. The value
        has a range of 1000 to 120000 and is given in mbar/100, i.e. a value
        of 100009 means that an air pressure of 1000.09 mbar is measured.
        
        If you want to get the air pressure periodically, it is recommended to use the
        callback :func:`AirPressure` and set the period with
        :func:`SetAirPressureCallbackPeriod`.
        """
        return self.ipcon.send_request(self, Barometer.FUNCTION_GET_AIR_PRESSURE, (), '', 'i')

    def get_altitude(self):
        """
        Returns the relative altitude of the air pressure sensor. The value is given in
        cm and represents the difference between the current altitude and the reference
        altitude that can be set with :func:`CalibrateAltitude`.
        
        If you want to get the altitude periodically, it is recommended to use the
        callback :func:`Altitude` and set the period with
        :func:`SetAltitudeCallbackPeriod`.
        """
        return self.ipcon.send_request(self, Barometer.FUNCTION_GET_ALTITUDE, (), '', 'i')

    def get_temperature(self):
        """
        Returns the temperature of the air pressure sensor. The value
        has a range of -4000 to 8500 and is given in °C/100, i.e. a value
        of 2007 means that a temperature of 20.07 °C is measured.
        
        This temperature is used internally for temperature compensation of the air
        pressure measurement. It is not as accurate as the temperature measured by the
        :ref:`temperature_bricklet` or the :ref:`temperature_ir_bricklet`.
        """
        return self.ipcon.send_request(self, Barometer.FUNCTION_GET_TEMPERATURE, (), '', 'h')

    def set_air_pressure_callback_period(self, period):
        """
        Sets the period in ms with which the :func:`AirPressure` callback is triggered
        periodically. A value of 0 turns the callback off.
        
        :func:`AirPressure` is only triggered if the air pressure has changed since the
        last triggering.
        
        The default value is 0.
        """
        self.ipcon.send_request(self, Barometer.FUNCTION_SET_AIR_PRESSURE_CALLBACK_PERIOD, (period,), 'I', '')

    def get_air_pressure_callback_period(self):
        """
        Returns the period as set by :func:`SetAirPressureCallbackPeriod`.
        """
        return self.ipcon.send_request(self, Barometer.FUNCTION_GET_AIR_PRESSURE_CALLBACK_PERIOD, (), '', 'I')

    def set_altitude_callback_period(self, period):
        """
        Sets the period in ms with which the :func:`Altitude` callback is triggered
        periodically. A value of 0 turns the callback off.
        
        :func:`Altitude` is only triggered if the altitude has changed since the
        last triggering.
        
        The default value is 0.
        """
        self.ipcon.send_request(self, Barometer.FUNCTION_SET_ALTITUDE_CALLBACK_PERIOD, (period,), 'I', '')

    def get_altitude_callback_period(self):
        """
        Returns the period as set by :func:`SetAltitudeCallbackPeriod`.
        """
        return self.ipcon.send_request(self, Barometer.FUNCTION_GET_ALTITUDE_CALLBACK_PERIOD, (), '', 'I')

    def set_air_pressure_callback_threshold(self, option, min, max):
        """
        Sets the thresholds for the :func:`AirPressureReached` callback.
        
        The following options are possible:
        
        .. csv-table::
         :header: "Option", "Description"
         :widths: 10, 100
        
         "'x'",    "Callback is turned off"
         "'o'",    "Callback is triggered when the air pressure is *outside* the min and max values"
         "'i'",    "Callback is triggered when the air pressure is *inside* the min and max values"
         "'<'",    "Callback is triggered when the air pressure is smaller than the min value (max is ignored)"
         "'>'",    "Callback is triggered when the air pressure is greater than the min value (max is ignored)"
        
        The default value is ('x', 0, 0).
        """
        self.ipcon.send_request(self, Barometer.FUNCTION_SET_AIR_PRESSURE_CALLBACK_THRESHOLD, (option, min, max), 'c i i', '')

    def get_air_pressure_callback_threshold(self):
        """
        Returns the threshold as set by :func:`SetAirPressureCallbackThreshold`.
        """
        return GetAirPressureCallbackThreshold(*self.ipcon.send_request(self, Barometer.FUNCTION_GET_AIR_PRESSURE_CALLBACK_THRESHOLD, (), '', 'c i i'))

    def set_altitude_callback_threshold(self, option, min, max):
        """
        Sets the thresholds for the :func:`AltitudeReached` callback.
        
        The following options are possible:
        
        .. csv-table::
         :header: "Option", "Description"
         :widths: 10, 100
        
         "'x'",    "Callback is turned off"
         "'o'",    "Callback is triggered when the altitude is *outside* the min and max values"
         "'i'",    "Callback is triggered when the altitude is *inside* the min and max values"
         "'<'",    "Callback is triggered when the altitude is smaller than the min value (max is ignored)"
         "'>'",    "Callback is triggered when the altitude is greater than the min value (max is ignored)"
        
        The default value is ('x', 0, 0).
        """
        self.ipcon.send_request(self, Barometer.FUNCTION_SET_ALTITUDE_CALLBACK_THRESHOLD, (option, min, max), 'c i i', '')

    def get_altitude_callback_threshold(self):
        """
        Returns the threshold as set by :func:`SetAltitudeCallbackThreshold`.
        """
        return GetAltitudeCallbackThreshold(*self.ipcon.send_request(self, Barometer.FUNCTION_GET_ALTITUDE_CALLBACK_THRESHOLD, (), '', 'c i i'))

    def set_debounce_period(self, debounce):
        """
        Sets the period in ms with which the threshold callbacks
        
         :func:`AirPressureReached`, :func:`AltitudeReached`
        
        are triggered, if the thresholds
        
         :func:`SetAirPressureCallbackThreshold`, :func:`SetAltitudeCallbackThreshold`
        
        keep being reached.
        
        The default value is 100.
        """
        self.ipcon.send_request(self, Barometer.FUNCTION_SET_DEBOUNCE_PERIOD, (debounce,), 'I', '')

    def get_debounce_period(self):
        """
        Returns the debounce period as set by :func:`SetDebouncePeriod`.
        """
        return self.ipcon.send_request(self, Barometer.FUNCTION_GET_DEBOUNCE_PERIOD, (), '', 'I')

    def calibrate_altitude(self):
        """
        Calibrates the altitude by setting the reference altitude to the current
        altitude.
        """
        self.ipcon.send_request(self, Barometer.FUNCTION_CALIBRATE_ALTITUDE, (), '', '')

    def register_callback(self, id, callback):
        """
        Registers a callback with ID id to the function callback.
        """
        self.registered_callbacks[id] = callback
