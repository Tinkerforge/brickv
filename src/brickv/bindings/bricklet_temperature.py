# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2012-10-26.      #
#                                                           #
# If you have a bugfix for this file and want to commit it, #
# please fix the bug in the generator. You can find a link  #
# to the generator git on tinkerforge.com                   #
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

GetTemperatureCallbackThreshold = namedtuple('TemperatureCallbackThreshold', ['option', 'min', 'max'])

class Temperature(Device):
    """
    Device for sensing Temperature
    """

    CALLBACK_TEMPERATURE = 8
    CALLBACK_TEMPERATURE_REACHED = 9

    FUNCTION_GET_TEMPERATURE = 1
    FUNCTION_SET_TEMPERATURE_CALLBACK_PERIOD = 2
    FUNCTION_GET_TEMPERATURE_CALLBACK_PERIOD = 3
    FUNCTION_SET_TEMPERATURE_CALLBACK_THRESHOLD = 4
    FUNCTION_GET_TEMPERATURE_CALLBACK_THRESHOLD = 5
    FUNCTION_SET_DEBOUNCE_PERIOD = 6
    FUNCTION_GET_DEBOUNCE_PERIOD = 7

    def __init__(self, uid):
        """
        Creates an object with the unique device ID *uid*. This object can
        then be added to the IP connection.
        """
        Device.__init__(self, uid)

        self.expected_name = 'Temperature Bricklet'

        self.binding_version = [1, 0, 0]

        self.callback_formats[Temperature.CALLBACK_TEMPERATURE] = 'h'
        self.callback_formats[Temperature.CALLBACK_TEMPERATURE_REACHED] = 'h'

    def get_temperature(self):
        """
        Returns the temperature of the sensor. The value
        has a range of -2500 to 8500 and is given in °C/100,
        e.g. a value of 4223 means that a temperature of 42.23 °C is measured.
        
        If you want to get the temperature periodically, it is recommended 
        to use the callback :func:`Temperature` and set the period with 
        :func:`SetTemperatureCallbackPeriod`.
        """
        return self.ipcon.send_request(self, Temperature.FUNCTION_GET_TEMPERATURE, (), '', 'h')

    def set_temperature_callback_period(self, period):
        """
        Sets the period in ms with which the :func:`Temperature` callback is triggered
        periodically. A value of 0 turns the callback off.
        
        :func:`Temperature` is only triggered if the temperature has changed since the
        last triggering.
        
        The default value is 0.
        """
        self.ipcon.send_request(self, Temperature.FUNCTION_SET_TEMPERATURE_CALLBACK_PERIOD, (period,), 'I', '')

    def get_temperature_callback_period(self):
        """
        Returns the period as set by :func:`SetTemperatureCallbackPeriod`.
        """
        return self.ipcon.send_request(self, Temperature.FUNCTION_GET_TEMPERATURE_CALLBACK_PERIOD, (), '', 'I')

    def set_temperature_callback_threshold(self, option, min, max):
        """
        Sets the thresholds for the :func:`TemperatureReached` callback. 
        
        The following options are possible:
        
        .. csv-table::
         :header: "Option", "Description"
         :widths: 10, 100
        
         "'x'",    "Callback is turned off"
         "'o'",    "Callback is triggered when the temperature is *outside* the min and max values"
         "'i'",    "Callback is triggered when the temperature is *inside* the min and max values"
         "'<'",    "Callback is triggered when the temperature is smaller than the min value (max is ignored)"
         "'>'",    "Callback is triggered when the temperature is greater than the min value (max is ignored)"
        
        The default value is ('x', 0, 0).
        """
        self.ipcon.send_request(self, Temperature.FUNCTION_SET_TEMPERATURE_CALLBACK_THRESHOLD, (option, min, max), 'c h h', '')

    def get_temperature_callback_threshold(self):
        """
        Returns the threshold as set by :func:`SetTemperatureCallbackThreshold`.
        """
        return GetTemperatureCallbackThreshold(*self.ipcon.send_request(self, Temperature.FUNCTION_GET_TEMPERATURE_CALLBACK_THRESHOLD, (), '', 'c h h'))

    def set_debounce_period(self, debounce):
        """
        Sets the period in ms with which the threshold callback
        
         :func:`TemperatureReached`
        
        is triggered, if the threshold
        
         :func:`SetTemperatureCallbackThreshold`
        
        keeps being reached.
        
        The default value is 100.
        """
        self.ipcon.send_request(self, Temperature.FUNCTION_SET_DEBOUNCE_PERIOD, (debounce,), 'I', '')

    def get_debounce_period(self):
        """
        Returns the debounce period as set by :func:`SetDebouncePeriod`.
        """
        return self.ipcon.send_request(self, Temperature.FUNCTION_GET_DEBOUNCE_PERIOD, (), '', 'I')

    def register_callback(self, id, callback):
        """
        Registers a callback with ID id to the function callback.
        """
        self.registered_callbacks[id] = callback
