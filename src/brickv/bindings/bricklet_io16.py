# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2013-02-06.      #
#                                                           #
# Bindings Version 2.0.3                                    #
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

GetPortConfiguration = namedtuple('PortConfiguration', ['direction_mask', 'value_mask'])
GetPortMonoflop = namedtuple('PortMonoflop', ['value', 'time', 'time_remaining'])
GetIdentity = namedtuple('Identity', ['uid', 'connected_uid', 'position', 'hardware_version', 'firmware_version', 'device_identifier'])

class BrickletIO16(Device):
    """
    Device for controlling up to 16 general purpose input/output pins
    """

    DEVICE_IDENTIFIER = 28

    CALLBACK_INTERRUPT = 9
    CALLBACK_MONOFLOP_DONE = 12

    FUNCTION_SET_PORT = 1
    FUNCTION_GET_PORT = 2
    FUNCTION_SET_PORT_CONFIGURATION = 3
    FUNCTION_GET_PORT_CONFIGURATION = 4
    FUNCTION_SET_DEBOUNCE_PERIOD = 5
    FUNCTION_GET_DEBOUNCE_PERIOD = 6
    FUNCTION_SET_PORT_INTERRUPT = 7
    FUNCTION_GET_PORT_INTERRUPT = 8
    FUNCTION_SET_PORT_MONOFLOP = 10
    FUNCTION_GET_PORT_MONOFLOP = 11
    FUNCTION_SET_SELECTED_VALUES = 13
    FUNCTION_GET_IDENTITY = 255

    DIRECTION_IN = 'i'
    DIRECTION_OUT = 'o'

    def __init__(self, uid, ipcon):
        """
        Creates an object with the unique device ID *uid* and adds it to
        the IP Connection *ipcon*.
        """
        Device.__init__(self, uid, ipcon)

        self.api_version = (2, 0, 0)

        self.response_expected[BrickletIO16.FUNCTION_SET_PORT] = BrickletIO16.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletIO16.FUNCTION_GET_PORT] = BrickletIO16.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletIO16.FUNCTION_SET_PORT_CONFIGURATION] = BrickletIO16.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletIO16.FUNCTION_GET_PORT_CONFIGURATION] = BrickletIO16.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletIO16.FUNCTION_SET_DEBOUNCE_PERIOD] = BrickletIO16.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletIO16.FUNCTION_GET_DEBOUNCE_PERIOD] = BrickletIO16.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletIO16.FUNCTION_SET_PORT_INTERRUPT] = BrickletIO16.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletIO16.FUNCTION_GET_PORT_INTERRUPT] = BrickletIO16.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletIO16.CALLBACK_INTERRUPT] = BrickletIO16.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletIO16.FUNCTION_SET_PORT_MONOFLOP] = BrickletIO16.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletIO16.FUNCTION_GET_PORT_MONOFLOP] = BrickletIO16.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletIO16.CALLBACK_MONOFLOP_DONE] = BrickletIO16.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletIO16.FUNCTION_SET_SELECTED_VALUES] = BrickletIO16.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletIO16.FUNCTION_GET_IDENTITY] = BrickletIO16.RESPONSE_EXPECTED_ALWAYS_TRUE

        self.callback_formats[BrickletIO16.CALLBACK_INTERRUPT] = 'c B B'
        self.callback_formats[BrickletIO16.CALLBACK_MONOFLOP_DONE] = 'c B B'

    def set_port(self, port, value_mask):
        """
        Sets the output value (high or low) for a port ("a" or "b") with a bitmask.
        The bitmask is 8 bit long, *true* refers to high and *false* refers to low.
        
        For example: The value 0b00001111 will turn the pins 0-3 high and the
        pins 4-7 low for the specified port.
        
        .. note::
         This function does nothing for pins that are configured as input.
         Pull-up resistors can be switched on with :func:`SetPortConfiguration`.
        """
        self.ipcon.send_request(self, BrickletIO16.FUNCTION_SET_PORT, (port, value_mask), 'c B', '')

    def get_port(self, port):
        """
        Returns a bitmask of the values that are currently measured on the
        specified port. This function works if the pin is configured to input
        as well as if it is configured to output.
        """
        return self.ipcon.send_request(self, BrickletIO16.FUNCTION_GET_PORT, (port,), 'c', 'B')

    def set_port_configuration(self, port, selection_mask, direction, value):
        """
        Configures the value and direction of a specified port. Possible directions
        are "i" and "o" for input and output.
        
        If the direction is configured as output, the value is either high or low
        (set as *true* or *false*).
        
        If the direction is configured as input, the value is either pull-up or
        default (set as *true* or *false*).
        
        For example:
        
        * ("a", 0xFF, 'i', true) will set all pins of port a as input pull-up.
        * ("a", 128, 'i', false) will set pin 7 of port a as input default (floating if nothing is connected).
        * ("b", 3, 'o', false) will set pins 0 and 1 of port b as output low.
        * ("b", 4, 'o', true) will set pin 2 of port b as output high.
        """
        self.ipcon.send_request(self, BrickletIO16.FUNCTION_SET_PORT_CONFIGURATION, (port, selection_mask, direction, value), 'c B c ?', '')

    def get_port_configuration(self, port):
        """
        Returns a direction bitmask and a value bitmask for the specified port.
        
        For example: A return value of 0b00001111 and 0b00110011 for
        direction and value means that:
        
        * pins 0 and 1 are configured as input pull-up,
        * pins 2 and 3 are configured as input default,
        * pins 4 and 5 are configured as output high
        * and pins 6 and 7 are configured as output low.
        """
        return GetPortConfiguration(*self.ipcon.send_request(self, BrickletIO16.FUNCTION_GET_PORT_CONFIGURATION, (port,), 'c', 'B B'))

    def set_debounce_period(self, debounce):
        """
        Sets the debounce period of the :func:`Interrupt` callback in ms.
        
        For example: If you set this value to 100, you will get the interrupt
        maximal every 100ms. This is necessary if something that bounces is
        connected to the IO-16 Bricklet, such as a button.
        
        The default value is 100.
        """
        self.ipcon.send_request(self, BrickletIO16.FUNCTION_SET_DEBOUNCE_PERIOD, (debounce,), 'I', '')

    def get_debounce_period(self):
        """
        Returns the debounce period as set by :func:`SetDebouncePeriod`.
        """
        return self.ipcon.send_request(self, BrickletIO16.FUNCTION_GET_DEBOUNCE_PERIOD, (), '', 'I')

    def set_port_interrupt(self, port, interrupt_mask):
        """
        Sets the pins on which an interrupt is activated with a bitmask.
        Interrupts are triggered on changes of the voltage level of the pin,
        i.e. changes from high to low and low to high.
        
        For example: ('a', 129) will enable the interrupt for pins 0 and 7 of
        port a.
        
        The interrupt is delivered with the callback :func:`Interrupt`.
        """
        self.ipcon.send_request(self, BrickletIO16.FUNCTION_SET_PORT_INTERRUPT, (port, interrupt_mask), 'c B', '')

    def get_port_interrupt(self, port):
        """
        Returns the interrupt bitmask for the specified port as set by
        :func:`SetPortInterrupt`.
        """
        return self.ipcon.send_request(self, BrickletIO16.FUNCTION_GET_PORT_INTERRUPT, (port,), 'c', 'B')

    def set_port_monoflop(self, port, selection_mask, value_mask, time):
        """
        Configures a monoflop of the pins specified by the second parameter as 8 bit
        long bitmask. The specified pins must be configured for output. Non-output
        pins will be ignored.
        
        The third parameter is a bitmask with the desired value of the specified
        output pins (*true* means high and *false* means low).
        
        The forth parameter indicates the time (in ms) that the pins should hold
        the value.
        
        If this function is called with the parameters ('a', (1 << 0) | (1 << 3), (1 << 0), 1500):
        Pin 0 will get high and pin 3 will get low on port 'a'. In 1.5s pin 0 will get
        low and pin 3 will get high again.
        
        A monoflop can be used as a fail-safe mechanism. For example: Lets assume you
        have a RS485 bus and an IO-16 Bricklet connected to one of the slave
        stacks. You can now call this function every second, with a time parameter
        of two seconds and pin 0 set to high. Pin 0 will be high all the time. If now
        the RS485 connection is lost, then pin 0 will get low in at most two seconds.
        
        .. versionadded:: 1.1.2~(Plugin)
        """
        self.ipcon.send_request(self, BrickletIO16.FUNCTION_SET_PORT_MONOFLOP, (port, selection_mask, value_mask, time), 'c B B I', '')

    def get_port_monoflop(self, port, pin):
        """
        Returns (for the given pin) the current value and the time as set by
        :func:`SetPortMonoflop` as well as the remaining time until the value flips.
        
        If the timer is not running currently, the remaining time will be returned
        as 0.
        
        .. versionadded:: 1.1.2~(Plugin)
        """
        return GetPortMonoflop(*self.ipcon.send_request(self, BrickletIO16.FUNCTION_GET_PORT_MONOFLOP, (port, pin), 'c B', 'B I I'))

    def set_selected_values(self, port, selection_mask, value_mask):
        """
        Sets the output value (high or low) for a port ("a" or "b" with a bitmask, 
        according to the selction mask. The bitmask is 4 bit long, *true* refers 
        to high and *false* refers to low.
        
        For example: The values 0b11000000, 0b10000000 will turn pin 7 high and
        pin 6 low, pins 0-6 will remain untouched.
        
        .. note::
         This function does nothing for pins that are configured as input.
         Pull-up resistors can be switched on with :func:`SetConfiguration`.
        
        .. versionadded:: 2.0.0~(Plugin)
        """
        self.ipcon.send_request(self, BrickletIO16.FUNCTION_SET_SELECTED_VALUES, (port, selection_mask, value_mask), 'c B B', '')

    def get_identity(self):
        """
        Returns the UID, the UID where the Bricklet is connected to, 
        the position, the hardware and firmware version as well as the
        device identifier.
        
        The position can be 'a', 'b', 'c' or 'd'.
        
        The device identifiers can be found :ref:`here <device_identifier>`.
        
        .. versionadded:: 2.0.0~(Plugin)
        """
        return GetIdentity(*self.ipcon.send_request(self, BrickletIO16.FUNCTION_GET_IDENTITY, (), '', '8s 8s c 3B 3B H'))

    def register_callback(self, id, callback):
        """
        Registers a callback with ID *id* to the function *callback*.
        """
        self.registered_callbacks[id] = callback

IO16 = BrickletIO16 # for backward compatibility
