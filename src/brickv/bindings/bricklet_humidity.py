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

GetHumidityCallbackThreshold = namedtuple('HumidityCallbackThreshold', ['option', 'min', 'max'])
GetAnalogValueCallbackThreshold = namedtuple('AnalogValueCallbackThreshold', ['option', 'min', 'max'])

class Humidity(Device):
    """
    Device for sensing Humidity
    """

    CALLBACK_HUMIDITY = 13
    CALLBACK_ANALOG_VALUE = 14
    CALLBACK_HUMIDITY_REACHED = 15
    CALLBACK_ANALOG_VALUE_REACHED = 16

    FUNCTION_GET_HUMIDITY = 1
    FUNCTION_GET_ANALOG_VALUE = 2
    FUNCTION_SET_HUMIDITY_CALLBACK_PERIOD = 3
    FUNCTION_GET_HUMIDITY_CALLBACK_PERIOD = 4
    FUNCTION_SET_ANALOG_VALUE_CALLBACK_PERIOD = 5
    FUNCTION_GET_ANALOG_VALUE_CALLBACK_PERIOD = 6
    FUNCTION_SET_HUMIDITY_CALLBACK_THRESHOLD = 7
    FUNCTION_GET_HUMIDITY_CALLBACK_THRESHOLD = 8
    FUNCTION_SET_ANALOG_VALUE_CALLBACK_THRESHOLD = 9
    FUNCTION_GET_ANALOG_VALUE_CALLBACK_THRESHOLD = 10
    FUNCTION_SET_DEBOUNCE_PERIOD = 11
    FUNCTION_GET_DEBOUNCE_PERIOD = 12

    def __init__(self, uid):
        """
        Creates an object with the unique device ID *uid*. This object can
        then be added to the IP connection.
        """
        Device.__init__(self, uid)

        self.expected_name = 'Humidity Bricklet'

        self.binding_version = [1, 0, 0]

        self.callback_formats[Humidity.CALLBACK_HUMIDITY] = 'H'
        self.callback_formats[Humidity.CALLBACK_ANALOG_VALUE] = 'H'
        self.callback_formats[Humidity.CALLBACK_HUMIDITY_REACHED] = 'H'
        self.callback_formats[Humidity.CALLBACK_ANALOG_VALUE_REACHED] = 'H'

    def get_humidity(self):
        """
        Returns the humidity of the sensor. The value
        has a range of 0 to 1000 and is given in %RH/10 (Relative Humidity), 
        i.e. a value of 421 means that a humidity of 42.1 %RH is measured.
        
        If you want to get the humidity periodically, it is recommended to use the
        callback :func:`Humidity` and set the period with 
        :func:`SetHumidityCallbackPeriod`.
        """
        return self.ipcon.send_request(self, Humidity.FUNCTION_GET_HUMIDITY, (), '', 'H')

    def get_analog_value(self):
        """
        Returns the value as read by a 12-bit analog-to-digital converter.
        The value is between 0 and 4095.
        
        .. note::
         The value returned by :func:`GetHumidity` is averaged over several samples
         to yield less noise, while :func:`GetAnalogValue` gives back raw
         unfiltered analog values. The returned humidity value is calibrated for
         room temperatures, if you use the sensor in extreme cold or extreme
         warm environments, you might want to calculate the humidity from
         the analog value yourself. See the `HIH 5030 datasheet
         <https://github.com/Tinkerforge/humidity-bricklet/raw/master/datasheets/hih-5030.pdf>`__.
        
        If you want the analog value periodically, it is recommended to use the 
        callback :func:`AnalogValue` and set the period with 
        :func:`SetAnalogValueCallbackPeriod`.
        """
        return self.ipcon.send_request(self, Humidity.FUNCTION_GET_ANALOG_VALUE, (), '', 'H')

    def set_humidity_callback_period(self, period):
        """
        Sets the period in ms with which the :func:`Humidity` callback is triggered
        periodically. A value of 0 turns the callback off.
        
        :func:`Humidity` is only triggered if the humidity has changed since the
        last triggering.
        
        The default value is 0.
        """
        self.ipcon.send_request(self, Humidity.FUNCTION_SET_HUMIDITY_CALLBACK_PERIOD, (period,), 'I', '')

    def get_humidity_callback_period(self):
        """
        Returns the period as set by :func:`SetHumidityCallbackPeriod`.
        """
        return self.ipcon.send_request(self, Humidity.FUNCTION_GET_HUMIDITY_CALLBACK_PERIOD, (), '', 'I')

    def set_analog_value_callback_period(self, period):
        """
        Sets the period in ms with which the :func:`AnalogValue` callback is triggered
        periodically. A value of 0 turns the callback off.
        
        :func:`AnalogValue` is only triggered if the analog value has changed since the
        last triggering.
        
        The default value is 0.
        """
        self.ipcon.send_request(self, Humidity.FUNCTION_SET_ANALOG_VALUE_CALLBACK_PERIOD, (period,), 'I', '')

    def get_analog_value_callback_period(self):
        """
        Returns the period as set by :func:`SetAnalogValueCallbackPeriod`.
        """
        return self.ipcon.send_request(self, Humidity.FUNCTION_GET_ANALOG_VALUE_CALLBACK_PERIOD, (), '', 'I')

    def set_humidity_callback_threshold(self, option, min, max):
        """
        Sets the thresholds for the :func:`HumidityReached` callback. 
        
        The following options are possible:
        
        .. csv-table::
         :header: "Option", "Description"
         :widths: 10, 100
        
         "'x'",    "Callback is turned off"
         "'o'",    "Callback is triggered when the humidity is *outside* the min and max values"
         "'i'",    "Callback is triggered when the humidity is *inside* the min and max values"
         "'<'",    "Callback is triggered when the humidity is smaller than the min value (max is ignored)"
         "'>'",    "Callback is triggered when the humidity is greater than the min value (max is ignored)"
        
        The default value is ('x', 0, 0).
        """
        self.ipcon.send_request(self, Humidity.FUNCTION_SET_HUMIDITY_CALLBACK_THRESHOLD, (option, min, max), 'c h h', '')

    def get_humidity_callback_threshold(self):
        """
        Returns the threshold as set by :func:`SetHumidityCallbackThreshold`.
        """
        return GetHumidityCallbackThreshold(*self.ipcon.send_request(self, Humidity.FUNCTION_GET_HUMIDITY_CALLBACK_THRESHOLD, (), '', 'c h h'))

    def set_analog_value_callback_threshold(self, option, min, max):
        """
        Sets the thresholds for the :func:`AnalogValueReached` callback. 
        
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
        self.ipcon.send_request(self, Humidity.FUNCTION_SET_ANALOG_VALUE_CALLBACK_THRESHOLD, (option, min, max), 'c H H', '')

    def get_analog_value_callback_threshold(self):
        """
        Returns the threshold as set by :func:`SetAnalogValueCallbackThreshold`.
        """
        return GetAnalogValueCallbackThreshold(*self.ipcon.send_request(self, Humidity.FUNCTION_GET_ANALOG_VALUE_CALLBACK_THRESHOLD, (), '', 'c H H'))

    def set_debounce_period(self, debounce):
        """
        Sets the period in ms with which the threshold callbacks
        
         :func:`HumidityReached`, :func:`AnalogValueReached`
        
        are triggered, if the thresholds
        
         :func:`SetHumidityCallbackThreshold`, :func:`SetAnalogValueCallbackThreshold`
        
        keep being reached.
        
        The default value is 100.
        """
        self.ipcon.send_request(self, Humidity.FUNCTION_SET_DEBOUNCE_PERIOD, (debounce,), 'I', '')

    def get_debounce_period(self):
        """
        Returns the debounce period as set by :func:`SetDebouncePeriod`.
        """
        return self.ipcon.send_request(self, Humidity.FUNCTION_GET_DEBOUNCE_PERIOD, (), '', 'I')

    def register_callback(self, id, callback):
        """
        Registers a callback with ID id to the function callback.
        """
        self.registered_callbacks[id] = callback
