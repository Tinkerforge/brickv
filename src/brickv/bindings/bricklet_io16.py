# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2012-05-23.      #
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

GetPortConfiguration = namedtuple('PortConfiguration', ['direction_mask', 'value_mask'])

class IO16(Device):
    """
    Device for controlling up to 16 general purpose input/output pins
    """

    CALLBACK_INTERRUPT = 9

    FUNCTION_SET_PORT = 1
    FUNCTION_GET_PORT = 2
    FUNCTION_SET_PORT_CONFIGURATION = 3
    FUNCTION_GET_PORT_CONFIGURATION = 4
    FUNCTION_SET_DEBOUNCE_PERIOD = 5
    FUNCTION_GET_DEBOUNCE_PERIOD = 6
    FUNCTION_SET_PORT_INTERRUPT = 7
    FUNCTION_GET_PORT_INTERRUPT = 8

    def __init__(self, uid):
        """
        Creates an object with the unique device ID *uid*. This object can
        then be added to the IP connection.
        """
        Device.__init__(self, uid)

        self.expected_name = 'IO-16 Bricklet'

        self.binding_version = [1, 0, 0]

        self.callbacks_format[IO16.CALLBACK_INTERRUPT] = 'c B B'

    def set_port(self, port, value_mask):
        """
        Sets the output value (high or low) for a port ("a" or "b") with a bit mask. 
        The bit mask is 8 bit long, "true" refers to high and "false" refers to low.
        
        For example: The bitstring "11110000" will turn the pins 0-3 high and the
        pins 4-7 low for the specified port.
        
         .. note::
          This function does nothing for pins that are configured as input.
          Pull up resistors can be switched on with :func:`SetPortConfiguration`.
        """
        self.ipcon.write(self, IO16.FUNCTION_SET_PORT, (port, value_mask), 'c B', '')

    def get_port(self, port):
        """
        Returns a bit mask of the values that are currently measured on the
        specified port. This function works if the pin is configured to input
        as well as if it is configured to output.
        """
        return self.ipcon.write(self, IO16.FUNCTION_GET_PORT, (port,), 'c', 'B')

    def set_port_configuration(self, port, port_mask, direction, value):
        """
        Configures the value and direction of a specified port. Possible directions
        are "i" and "o" for input and output.
        
        If the direction is configured as output, the value is either high or low
        (set as true or false).
        
        If the direction is configured as output, the value is either pull up or
        default (set as true or false).
        
        For example: 
        
         * ("a", 0xFF, 'i', true) will set all pins of port a as input pull up. 
         * ("a", 128, 'i', false) will set pin 7 of port a as input default (floating if nothing is connected). 
         * ("b", 3, 'o', false) will set pins 0 and 1 of port b as output low.
         * ("b", 4, 'o', true) will set pin 2 of port b as output high.
        """
        self.ipcon.write(self, IO16.FUNCTION_SET_PORT_CONFIGURATION, (port, port_mask, direction, value), 'c B c ?', '')

    def get_port_configuration(self, port):
        """
        Returns a value bit mask and a direction bit mask for the specified port.
        
        For example: A return value of the bitstrings "11110000" and "11001100" for
        direction and value means that:
        
         * pins 0 and 1 are configured as input pull up, 
         * pins 2 and 3 are configured as input default,
         * pins 4 and 5 are configured as output high
         * and pins 6 and 7 are configured as output low.
        """
        return GetPortConfiguration(*self.ipcon.write(self, IO16.FUNCTION_GET_PORT_CONFIGURATION, (port,), 'c', 'B B'))

    def set_debounce_period(self, debounce):
        """
        Sets the debounce period of the :func:`Interrupt` callback in ms.
        
        For example: If you set this value to 100, you will get the interrupt
        maximal every 100ms. This is necessary if something that bounces is
        connected to the IO-16 Bricklet, such as a button.
        
        The default value is 100.
        """
        self.ipcon.write(self, IO16.FUNCTION_SET_DEBOUNCE_PERIOD, (debounce,), 'I', '')

    def get_debounce_period(self):
        """
        Returns the debounce period as set by :func:`SetDebouncePeriod`.
        """
        return self.ipcon.write(self, IO16.FUNCTION_GET_DEBOUNCE_PERIOD, (), '', 'I')

    def set_port_interrupt(self, port, interrupt_mask):
        """
        Sets the pins on which an interrupt is activated with a bit mask. 
        Interrupts are triggered on changes of the voltage level of the pin,
        i.e. changes from high to low and low to high.
        
        For example: ('a', 129) will enable the interrupt for pins 0 and 7 of
        port a.
        
        The interrupt is delivered with the callback :func:`Interrupt`.
        """
        self.ipcon.write(self, IO16.FUNCTION_SET_PORT_INTERRUPT, (port, interrupt_mask), 'c B', '')

    def get_port_interrupt(self, port):
        """
        Returns the interrupt bit mask for the specified port as set by
        :func:`SetPortInterrupt`.
        """
        return self.ipcon.write(self, IO16.FUNCTION_GET_PORT_INTERRUPT, (port,), 'c', 'B')

    def register_callback(self, cb, func):
        """
        Registers a callback with ID cb to the function func.
        """
        self.callbacks[cb] = func
