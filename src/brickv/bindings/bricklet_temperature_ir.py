# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2012-05-18.      #
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

GetAmbientTemperatureCallbackThreshold = namedtuple('AmbientTemperatureCallbackThreshold', ['option', 'min', 'max'])
GetObjectTemperatureCallbackThreshold = namedtuple('ObjectTemperatureCallbackThreshold', ['option', 'min', 'max'])

class TemperatureIR(Device):
    """
    Device for non-contact temperature sensing
    """

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

    def __init__(self, uid):
        """
        Creates an object with the unique device ID *uid*. This object can
        then be added to the IP connection.
        """
        Device.__init__(self, uid)

        self.expected_name = 'Temperature IR Bricklet';

        self.binding_version = [1, 0, 0]

        self.callbacks_format[TemperatureIR.CALLBACK_AMBIENT_TEMPERATURE] = 'h'
        self.callbacks_format[TemperatureIR.CALLBACK_OBJECT_TEMPERATURE] = 'h'
        self.callbacks_format[TemperatureIR.CALLBACK_AMBIENT_TEMPERATURE_REACHED] = 'h'
        self.callbacks_format[TemperatureIR.CALLBACK_OBJECT_TEMPERATURE_REACHED] = 'h'

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
        return self.ipcon.write(self, TemperatureIR.FUNCTION_GET_AMBIENT_TEMPERATURE, (), '', 'h')

    def get_object_temperature(self):
        """
        Returns the object temperature of the sensor, i.e. the temperature
        of the surface of the object the sensor is aimed at. The value
        has a range of -700 to 3800 and is given in °C/10,
        e.g. a value of 30001 means that a temperature of 300.01 °C is measured
        on the surface of the object.
        
        The temperature of different materials is dependent on their `emissivity 
        <http://en.wikipedia.org/wiki/Emissivity>`_. The emissivity of the material
        can be set with :func:`SetEmissivity`.
        
        If you want to get the object temperature periodically, it is recommended 
        to use the callback :func:`ObjectTemperature` and set the period with 
        :func:`SetObjectTemperatureCallbackPeriod`.
        """
        return self.ipcon.write(self, TemperatureIR.FUNCTION_GET_OBJECT_TEMPERATURE, (), '', 'h')

    def set_emissivity(self, emissivity):
        """
        Sets the `emissivity <http://en.wikipedia.org/wiki/Emissivity>`_ that is 
        used to calculate the surface temperature as returned by 
        :func:`GetObjectTemperature`. 
        
        The emissivity is usually given as a value between 0.0 and 1.0. A list of
        emissivities of different materials can be found 
        `here <http://www.infrared-thermography.com/material.htm>`_.
        
        The parameter of :func:`SetEmissivity` has to be given with a factor of
        65535 (16 bit). For example: An emissivity of 0.1 can be set with the 
        value 6553, an emissivity of 0.5 with the value 32767 and so on.
        
         .. note::
          If you need a precise measurement for the object temperature, it is
          absolutely crucial that you also provide a precise emissivity.
        
        The default emissivity is 1.0 (value of 65535) and the minimum emissivity the
        sensor can handle is 0.1 (value of 6553).
        """
        self.ipcon.write(self, TemperatureIR.FUNCTION_SET_EMISSIVITY, (emissivity,), 'H', '')

    def get_emissivity(self):
        """
        Returns the emissivity as set by :func:`SetEmissivity`.
        """
        return self.ipcon.write(self, TemperatureIR.FUNCTION_GET_EMISSIVITY, (), '', 'H')

    def set_ambient_temperature_callback_period(self, period):
        """
        Sets the period in ms with which the :func:`AmbientTemperature` callback is triggered
        periodically. A value of 0 turns the callback off.
        
        :func:`AmbientTemperature` is only triggered if the temperature has changed since the
        last triggering.
        
        The default value is 0.
        """
        self.ipcon.write(self, TemperatureIR.FUNCTION_SET_AMBIENT_TEMPERATURE_CALLBACK_PERIOD, (period,), 'I', '')

    def get_ambient_temperature_callback_period(self):
        """
        Returns the period as set by :func:`SetAmbientTemperatureCallbackPeriod`.
        """
        return self.ipcon.write(self, TemperatureIR.FUNCTION_GET_AMBIENT_TEMPERATURE_CALLBACK_PERIOD, (), '', 'I')

    def set_object_temperature_callback_period(self, period):
        """
        Sets the period in ms with which the :func:`ObjectTemperature` callback is triggered
        periodically. A value of 0 turns the callback off.
        
        :func:`ObjectTemperature` is only triggered if the temperature has changed since the
        last triggering.
        
        The default value is 0.
        """
        self.ipcon.write(self, TemperatureIR.FUNCTION_SET_OBJECT_TEMPERATURE_CALLBACK_PERIOD, (period,), 'I', '')

    def get_object_temperature_callback_period(self):
        """
        Returns the period as set by :func:`SetObjectTemperatureCallbackPeriod`.
        """
        return self.ipcon.write(self, TemperatureIR.FUNCTION_GET_OBJECT_TEMPERATURE_CALLBACK_PERIOD, (), '', 'I')

    def set_ambient_temperature_callback_threshold(self, option, min, max):
        """
        Sets the thresholds for the :func:`AmbientTemperatureReached` callback. 
        
        The following options are possible:
        
        .. csv-table::
         :header: "Option", "Description"
         :widths: 10, 100
        
         "'x'", "Callback is turned off."
         "'o'", "Callback is triggered when the temperature is *outside* the min and max values"
         "'i'", "Callback is triggered when the temperature is *inside* the min and max values"
         "'<'", "Callback is triggered when the temperature is smaller than the min value (max is ignored)"
         "'>'", "Callback is triggered when the temperature is greater than the min value (max is ignored)"
        
        The default value is ('x', 0, 0).
        """
        self.ipcon.write(self, TemperatureIR.FUNCTION_SET_AMBIENT_TEMPERATURE_CALLBACK_THRESHOLD, (option, min, max), 'c h h', '')

    def get_ambient_temperature_callback_threshold(self):
        """
        Returns the threshold as set by :func:`SetAmbientTemperatureCallbackThreshold`.
        """
        return GetAmbientTemperatureCallbackThreshold(*self.ipcon.write(self, TemperatureIR.FUNCTION_GET_AMBIENT_TEMPERATURE_CALLBACK_THRESHOLD, (), '', 'c h h'))

    def set_object_temperature_callback_threshold(self, option, min, max):
        """
        Sets the thresholds for the :func:`ObjectTemperatureReached` callback. 
        
        The following options are possible:
        
        .. csv-table::
         :header: "Option", "Description"
         :widths: 10, 100
        
         "'x'", "Callback is turned off."
         "'o'", "Callback is triggered when the temperature is *outside* the min and max values"
         "'i'", "Callback is triggered when the temperature is *inside* the min and max values"
         "'<'", "Callback is triggered when the temperature is smaller than the min value (max is ignored)"
         "'>'", "Callback is triggered when the temperature is greater than the min value (max is ignored)"
        
        The default value is ('x', 0, 0).
        """
        self.ipcon.write(self, TemperatureIR.FUNCTION_SET_OBJECT_TEMPERATURE_CALLBACK_THRESHOLD, (option, min, max), 'c h h', '')

    def get_object_temperature_callback_threshold(self):
        """
        Returns the threshold as set by :func:`SetAmbientTemperatureCallbackThreshold`.
        """
        return GetObjectTemperatureCallbackThreshold(*self.ipcon.write(self, TemperatureIR.FUNCTION_GET_OBJECT_TEMPERATURE_CALLBACK_THRESHOLD, (), '', 'c h h'))

    def set_debounce_period(self, debounce):
        """
        Sets the period in ms with which the threshold callbacks
        
         :func:`AmbientTemperatureReached`, :func:`ObjectTemperatureReached`
        
        are triggered, if the thresholds
        
         :func:`SetAmbientTemperatureCallbackThreshold`, :func:`SetObjectTemperatureCallbackThreshold`
        
        keep being reached.
        
        The default value is 100.
        """
        self.ipcon.write(self, TemperatureIR.FUNCTION_SET_DEBOUNCE_PERIOD, (debounce,), 'I', '')

    def get_debounce_period(self):
        """
        Returns the debounce period as set by :func:`SetDebouncePeriod`.
        """
        return self.ipcon.write(self, TemperatureIR.FUNCTION_GET_DEBOUNCE_PERIOD, (), '', 'I')

    def register_callback(self, cb, func):
        """
        Registers a callback with ID cb to the function func.
        """
        self.callbacks[cb] = func
