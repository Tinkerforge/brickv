# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2012-07-02.      #
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

GetConfiguration = namedtuple('Configuration', ['direction_mask', 'value_mask'])

class IO4(Device):
    """
    Device for controlling up to 4 general purpose input/output pins
    """

    CALLBACK_INTERRUPT = 9

    FUNCTION_SET_VALUE = 1
    FUNCTION_GET_VALUE = 2
    FUNCTION_SET_CONFIGURATION = 3
    FUNCTION_GET_CONFIGURATION = 4
    FUNCTION_SET_DEBOUNCE_PERIOD = 5
    FUNCTION_GET_DEBOUNCE_PERIOD = 6
    FUNCTION_SET_INTERRUPT = 7
    FUNCTION_GET_INTERRUPT = 8

    def __init__(self, uid):
        """
        Creates an object with the unique device ID *uid*. This object can
        then be added to the IP connection.
        """
        Device.__init__(self, uid)

        self.expected_name = 'IO-4 Bricklet'

        self.binding_version = [1, 0, 0]

        self.callback_formats[IO4.CALLBACK_INTERRUPT] = 'B B'

    def set_value(self, value_mask):
        """
        Sets the output value (high or low) with a bit mask. The bit mask
        is 4 bit long, "true" refers to high and "false" refers to low.
        
        For example: The value 0b0011 will turn the pins 0-1 high and the
        pins 2-3 low.
        
         .. note::
          This function does nothing for pins that are configured as input.
          Pull up resistors can be switched on with :func:`SetPortConfiguration`.
        """
        self.ipcon.send_request(self, IO4.FUNCTION_SET_VALUE, (value_mask,), 'B', '')

    def get_value(self):
        """
        Returns a bit mask of the values that are currently measured.
        This function works if the pin is configured to input
        as well as if it is configured to output.
        """
        return self.ipcon.send_request(self, IO4.FUNCTION_GET_VALUE, (), '', 'B')

    def set_configuration(self, pin_mask, direction, value):
        """
        Configures the value and direction of the specified pins. Possible directions
        are "i" and "o" for input and output.
        
        If the direction is configured as output, the value is either high or low
        (set as true or false).
        
        If the direction is configured as input, the value is either pull up or
        default (set as true or false).
        
        For example: 
        
        * (15, 'i', true) will set all pins of as input pull up.
        * (8, 'i', false) will set pin 3 of as input default (floating if nothing is connected).
        * (3, 'o', false) will set pins 0 and 1 as output low.
        * (4, 'o', true) will set pin 2 of as output high.
        """
        self.ipcon.send_request(self, IO4.FUNCTION_SET_CONFIGURATION, (pin_mask, direction, value), 'B c ?', '')

    def get_configuration(self):
        """
        Returns a value bit mask and a direction bit mask.
        
        For example: A return value of 0b0011 and 0b0101 for
        direction and value means that:
        
        * pin 0 is configured as input pull up,
        * pin 1 is configured as input default,
        * pin 2 is configured as output high
        * and pin 3 is are configured as output low.
        """
        return GetConfiguration(*self.ipcon.send_request(self, IO4.FUNCTION_GET_CONFIGURATION, (), '', 'B B'))

    def set_debounce_period(self, debounce):
        """
        Sets the debounce period of the :func:`Interrupt` callback in ms.
        
        For example: If you set this value to 100, you will get the interrupt
        maximal every 100ms. This is necessary if something that bounces is
        connected to the IO-4 Bricklet, such as a button.
        
        The default value is 100.
        """
        self.ipcon.send_request(self, IO4.FUNCTION_SET_DEBOUNCE_PERIOD, (debounce,), 'I', '')

    def get_debounce_period(self):
        """
        Returns the debounce period as set by :func:`SetDebouncePeriod`.
        """
        return self.ipcon.send_request(self, IO4.FUNCTION_GET_DEBOUNCE_PERIOD, (), '', 'I')

    def set_interrupt(self, interrupt_mask):
        """
        Sets the pins on which an interrupt is activated with a bit mask. 
        Interrupts are triggered on changes of the voltage level of the pin,
        i.e. changes from high to low and low to high.
        
        For example: An interrupt bit mask of 9 will enable the interrupt for 
        pins 0 and 3.
        
        The interrupt is delivered with the callback :func:`Interrupt`.
        """
        self.ipcon.send_request(self, IO4.FUNCTION_SET_INTERRUPT, (interrupt_mask,), 'B', '')

    def get_interrupt(self):
        """
        Returns the interrupt bit mask as set by :func:`SetPortInterrupt`.
        """
        return self.ipcon.send_request(self, IO4.FUNCTION_GET_INTERRUPT, (), '', 'B')

    def register_callback(self, id, callback):
        """
        Registers a callback with ID id to the function callback.
        """
        self.registered_callbacks[id] = callback
