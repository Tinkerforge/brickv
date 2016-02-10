# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2016-02-10.      #
#                                                           #
# Python Bindings Version 2.1.8                             #
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

GetAmbientTemperatureCallbackThreshold = namedtuple('AmbientTemperatureCallbackThreshold', ['option', 'min', 'max'])
GetObjectTemperatureCallbackThreshold = namedtuple('ObjectTemperatureCallbackThreshold', ['option', 'min', 'max'])
GetIdentity = namedtuple('Identity', ['uid', 'connected_uid', 'position', 'hardware_version', 'firmware_version', 'device_identifier'])

class BrickletTemperatureIR(Device):
    """
    Measures contactless object temperature between -70°C and +380°C
    """

    DEVICE_IDENTIFIER = 217
    DEVICE_DISPLAY_NAME = 'Temperature IR Bricklet'

    CALLBACK_AMBIENT_TEMPERATURE = 15
    CALLBACK_OBJECT_TEMPERATURE = 16
    CALLBACK_AMBIENT_TEMPERATURE_REACHED = 17
    CALLBACK_OBJECT_TEMPERATURE_REACHED = 18

    FUNCTION_GET_AMBIENT_TEMPERATURE = 1
    FUNCTION_GET_OBJECT_TEMPERATURE = 2
    FUNCTION_SET_EMISSIVITY = 3
    FUNCTION_GET_EMISSIVITY = 4
    FUNCTION_SET_AMBIENT_TEMPERATURE_CALLBACK_PERIOD = 5
    FUNCTION_GET_AMBIENT_TEMPERATURE_CALLBACK_PERIOD = 6
    FUNCTION_SET_OBJECT_TEMPERATURE_CALLBACK_PERIOD = 7
    FUNCTION_GET_OBJECT_TEMPERATURE_CALLBACK_PERIOD = 8
    FUNCTION_SET_AMBIENT_TEMPERATURE_CALLBACK_THRESHOLD = 9
    FUNCTION_GET_AMBIENT_TEMPERATURE_CALLBACK_THRESHOLD = 10
    FUNCTION_SET_OBJECT_TEMPERATURE_CALLBACK_THRESHOLD = 11
    FUNCTION_GET_OBJECT_TEMPERATURE_CALLBACK_THRESHOLD = 12
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

        self.response_expected[BrickletTemperatureIR.FUNCTION_GET_AMBIENT_TEMPERATURE] = BrickletTemperatureIR.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletTemperatureIR.FUNCTION_GET_OBJECT_TEMPERATURE] = BrickletTemperatureIR.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletTemperatureIR.FUNCTION_SET_EMISSIVITY] = BrickletTemperatureIR.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletTemperatureIR.FUNCTION_GET_EMISSIVITY] = BrickletTemperatureIR.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletTemperatureIR.FUNCTION_SET_AMBIENT_TEMPERATURE_CALLBACK_PERIOD] = BrickletTemperatureIR.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletTemperatureIR.FUNCTION_GET_AMBIENT_TEMPERATURE_CALLBACK_PERIOD] = BrickletTemperatureIR.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletTemperatureIR.FUNCTION_SET_OBJECT_TEMPERATURE_CALLBACK_PERIOD] = BrickletTemperatureIR.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletTemperatureIR.FUNCTION_GET_OBJECT_TEMPERATURE_CALLBACK_PERIOD] = BrickletTemperatureIR.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletTemperatureIR.FUNCTION_SET_AMBIENT_TEMPERATURE_CALLBACK_THRESHOLD] = BrickletTemperatureIR.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletTemperatureIR.FUNCTION_GET_AMBIENT_TEMPERATURE_CALLBACK_THRESHOLD] = BrickletTemperatureIR.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletTemperatureIR.FUNCTION_SET_OBJECT_TEMPERATURE_CALLBACK_THRESHOLD] = BrickletTemperatureIR.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletTemperatureIR.FUNCTION_GET_OBJECT_TEMPERATURE_CALLBACK_THRESHOLD] = BrickletTemperatureIR.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletTemperatureIR.FUNCTION_SET_DEBOUNCE_PERIOD] = BrickletTemperatureIR.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletTemperatureIR.FUNCTION_GET_DEBOUNCE_PERIOD] = BrickletTemperatureIR.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletTemperatureIR.CALLBACK_AMBIENT_TEMPERATURE] = BrickletTemperatureIR.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletTemperatureIR.CALLBACK_OBJECT_TEMPERATURE] = BrickletTemperatureIR.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletTemperatureIR.CALLBACK_AMBIENT_TEMPERATURE_REACHED] = BrickletTemperatureIR.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletTemperatureIR.CALLBACK_OBJECT_TEMPERATURE_REACHED] = BrickletTemperatureIR.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletTemperatureIR.FUNCTION_GET_IDENTITY] = BrickletTemperatureIR.RESPONSE_EXPECTED_ALWAYS_TRUE

        self.callback_formats[BrickletTemperatureIR.CALLBACK_AMBIENT_TEMPERATURE] = 'h'
        self.callback_formats[BrickletTemperatureIR.CALLBACK_OBJECT_TEMPERATURE] = 'h'
        self.callback_formats[BrickletTemperatureIR.CALLBACK_AMBIENT_TEMPERATURE_REACHED] = 'h'
        self.callback_formats[BrickletTemperatureIR.CALLBACK_OBJECT_TEMPERATURE_REACHED] = 'h'

    def get_ambient_temperature(self):
        """
        Returns the ambient temperature of the sensor. The value
        has a range of -400 to 1250 and is given in °C/10,
        e.g. a value of 423 means that an ambient temperature of 42.3 °C is 
        measured.
        
        If you want to get the ambient temperature periodically, it is recommended 
        to use the callback :func:`AmbientTemperature` and set the period with 
        :func:`SetAmbientTemperatureCallbackPeriod`.
        """
        return self.ipcon.send_request(self, BrickletTemperatureIR.FUNCTION_GET_AMBIENT_TEMPERATURE, (), '', 'h')

    def get_object_temperature(self):
        """
        Returns the object temperature of the sensor, i.e. the temperature
        of the surface of the object the sensor is aimed at. The value
        has a range of -700 to 3800 and is given in °C/10,
        e.g. a value of 3001 means that a temperature of 300.1 °C is measured
        on the surface of the object.
        
        The temperature of different materials is dependent on their `emissivity 
        <https://en.wikipedia.org/wiki/Emissivity>`__. The emissivity of the material
        can be set with :func:`SetEmissivity`.
        
        If you want to get the object temperature periodically, it is recommended 
        to use the callback :func:`ObjectTemperature` and set the period with 
        :func:`SetObjectTemperatureCallbackPeriod`.
        """
        return self.ipcon.send_request(self, BrickletTemperatureIR.FUNCTION_GET_OBJECT_TEMPERATURE, (), '', 'h')

    def set_emissivity(self, emissivity):
        """
        Sets the `emissivity <https://en.wikipedia.org/wiki/Emissivity>`__ that is
        used to calculate the surface temperature as returned by 
        :func:`GetObjectTemperature`. 
        
        The emissivity is usually given as a value between 0.0 and 1.0. A list of
        emissivities of different materials can be found 
        `here <http://www.infrared-thermography.com/material.htm>`__.
        
        The parameter of :func:`SetEmissivity` has to be given with a factor of
        65535 (16-bit). For example: An emissivity of 0.1 can be set with the
        value 6553, an emissivity of 0.5 with the value 32767 and so on.
        
        .. note::
         If you need a precise measurement for the object temperature, it is
         absolutely crucial that you also provide a precise emissivity.
        
        The default emissivity is 1.0 (value of 65535) and the minimum emissivity the
        sensor can handle is 0.1 (value of 6553).
        """
        self.ipcon.send_request(self, BrickletTemperatureIR.FUNCTION_SET_EMISSIVITY, (emissivity,), 'H', '')

    def get_emissivity(self):
        """
        Returns the emissivity as set by :func:`SetEmissivity`.
        """
        return self.ipcon.send_request(self, BrickletTemperatureIR.FUNCTION_GET_EMISSIVITY, (), '', 'H')

    def set_ambient_temperature_callback_period(self, period):
        """
        Sets the period in ms with which the :func:`AmbientTemperature` callback is triggered
        periodically. A value of 0 turns the callback off.
        
        :func:`AmbientTemperature` is only triggered if the temperature has changed since the
        last triggering.
        
        The default value is 0.
        """
        self.ipcon.send_request(self, BrickletTemperatureIR.FUNCTION_SET_AMBIENT_TEMPERATURE_CALLBACK_PERIOD, (period,), 'I', '')

    def get_ambient_temperature_callback_period(self):
        """
        Returns the period as set by :func:`SetAmbientTemperatureCallbackPeriod`.
        """
        return self.ipcon.send_request(self, BrickletTemperatureIR.FUNCTION_GET_AMBIENT_TEMPERATURE_CALLBACK_PERIOD, (), '', 'I')

    def set_object_temperature_callback_period(self, period):
        """
        Sets the period in ms with which the :func:`ObjectTemperature` callback is triggered
        periodically. A value of 0 turns the callback off.
        
        :func:`ObjectTemperature` is only triggered if the temperature has changed since the
        last triggering.
        
        The default value is 0.
        """
        self.ipcon.send_request(self, BrickletTemperatureIR.FUNCTION_SET_OBJECT_TEMPERATURE_CALLBACK_PERIOD, (period,), 'I', '')

    def get_object_temperature_callback_period(self):
        """
        Returns the period as set by :func:`SetObjectTemperatureCallbackPeriod`.
        """
        return self.ipcon.send_request(self, BrickletTemperatureIR.FUNCTION_GET_OBJECT_TEMPERATURE_CALLBACK_PERIOD, (), '', 'I')

    def set_ambient_temperature_callback_threshold(self, option, min, max):
        """
        Sets the thresholds for the :func:`AmbientTemperatureReached` callback. 
        
        The following options are possible:
        
        .. csv-table::
         :header: "Option", "Description"
         :widths: 10, 100
        
         "'x'",    "Callback is turned off"
         "'o'",    "Callback is triggered when the ambient temperature is *outside* the min and max values"
         "'i'",    "Callback is triggered when the ambient temperature is *inside* the min and max values"
         "'<'",    "Callback is triggered when the ambient temperature is smaller than the min value (max is ignored)"
         "'>'",    "Callback is triggered when the ambient temperature is greater than the min value (max is ignored)"
        
        The default value is ('x', 0, 0).
        """
        self.ipcon.send_request(self, BrickletTemperatureIR.FUNCTION_SET_AMBIENT_TEMPERATURE_CALLBACK_THRESHOLD, (option, min, max), 'c h h', '')

    def get_ambient_temperature_callback_threshold(self):
        """
        Returns the threshold as set by :func:`SetAmbientTemperatureCallbackThreshold`.
        """
        return GetAmbientTemperatureCallbackThreshold(*self.ipcon.send_request(self, BrickletTemperatureIR.FUNCTION_GET_AMBIENT_TEMPERATURE_CALLBACK_THRESHOLD, (), '', 'c h h'))

    def set_object_temperature_callback_threshold(self, option, min, max):
        """
        Sets the thresholds for the :func:`ObjectTemperatureReached` callback. 
        
        The following options are possible:
        
        .. csv-table::
         :header: "Option", "Description"
         :widths: 10, 100
        
         "'x'",    "Callback is turned off"
         "'o'",    "Callback is triggered when the object temperature is *outside* the min and max values"
         "'i'",    "Callback is triggered when the object temperature is *inside* the min and max values"
         "'<'",    "Callback is triggered when the object temperature is smaller than the min value (max is ignored)"
         "'>'",    "Callback is triggered when the object temperature is greater than the min value (max is ignored)"
        
        The default value is ('x', 0, 0).
        """
        self.ipcon.send_request(self, BrickletTemperatureIR.FUNCTION_SET_OBJECT_TEMPERATURE_CALLBACK_THRESHOLD, (option, min, max), 'c h h', '')

    def get_object_temperature_callback_threshold(self):
        """
        Returns the threshold as set by :func:`SetObjectTemperatureCallbackThreshold`.
        """
        return GetObjectTemperatureCallbackThreshold(*self.ipcon.send_request(self, BrickletTemperatureIR.FUNCTION_GET_OBJECT_TEMPERATURE_CALLBACK_THRESHOLD, (), '', 'c h h'))

    def set_debounce_period(self, debounce):
        """
        Sets the period in ms with which the threshold callbacks
        
        * :func:`AmbientTemperatureReached`,
        * :func:`ObjectTemperatureReached`
        
        are triggered, if the thresholds
        
        * :func:`SetAmbientTemperatureCallbackThreshold`,
        * :func:`SetObjectTemperatureCallbackThreshold`
        
        keep being reached.
        
        The default value is 100.
        """
        self.ipcon.send_request(self, BrickletTemperatureIR.FUNCTION_SET_DEBOUNCE_PERIOD, (debounce,), 'I', '')

    def get_debounce_period(self):
        """
        Returns the debounce period as set by :func:`SetDebouncePeriod`.
        """
        return self.ipcon.send_request(self, BrickletTemperatureIR.FUNCTION_GET_DEBOUNCE_PERIOD, (), '', 'I')

    def get_identity(self):
        """
        Returns the UID, the UID where the Bricklet is connected to, 
        the position, the hardware and firmware version as well as the
        device identifier.
        
        The position can be 'a', 'b', 'c' or 'd'.
        
        The device identifier numbers can be found :ref:`here <device_identifier>`.
        |device_identifier_constant|
        """
        return GetIdentity(*self.ipcon.send_request(self, BrickletTemperatureIR.FUNCTION_GET_IDENTITY, (), '', '8s 8s c 3B 3B H'))

    def register_callback(self, id, callback):
        """
        Registers a callback with ID *id* to the function *callback*.
        """
        self.registered_callbacks[id] = callback

TemperatureIR = BrickletTemperatureIR # for backward compatibility
