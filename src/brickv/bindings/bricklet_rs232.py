# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2018-03-15.      #
#                                                           #
# Python Bindings Version 2.1.16                            #
#                                                           #
# If you have a bugfix for this file and want to commit it, #
# please fix the bug in the generator. You can find a link  #
# to the generators git repository on tinkerforge.com       #
#############################################################

from collections import namedtuple

try:
    from .ip_connection import Device, IPConnection, Error, create_char, create_char_list, create_string, create_chunk_data
except ValueError:
    from ip_connection import Device, IPConnection, Error, create_char, create_char_list, create_string, create_chunk_data

Read = namedtuple('Read', ['message', 'length'])
GetConfiguration = namedtuple('Configuration', ['baudrate', 'parity', 'stopbits', 'wordlength', 'hardware_flowcontrol', 'software_flowcontrol'])
GetIdentity = namedtuple('Identity', ['uid', 'connected_uid', 'position', 'hardware_version', 'firmware_version', 'device_identifier'])

class BrickletRS232(Device):
    """
    Communicates with RS232 devices
    """

    DEVICE_IDENTIFIER = 254
    DEVICE_DISPLAY_NAME = 'RS232 Bricklet'
    DEVICE_URL_PART = 'rs232' # internal

    CALLBACK_READ = 8
    CALLBACK_ERROR = 9
    CALLBACK_READ_CALLBACK = 8 # for backward compatibility
    CALLBACK_ERROR_CALLBACK = 9 # for backward compatibility


    FUNCTION_WRITE = 1
    FUNCTION_READ = 2
    FUNCTION_ENABLE_READ_CALLBACK = 3
    FUNCTION_DISABLE_READ_CALLBACK = 4
    FUNCTION_IS_READ_CALLBACK_ENABLED = 5
    FUNCTION_SET_CONFIGURATION = 6
    FUNCTION_GET_CONFIGURATION = 7
    FUNCTION_SET_BREAK_CONDITION = 10
    FUNCTION_GET_IDENTITY = 255

    BAUDRATE_300 = 0
    BAUDRATE_600 = 1
    BAUDRATE_1200 = 2
    BAUDRATE_2400 = 3
    BAUDRATE_4800 = 4
    BAUDRATE_9600 = 5
    BAUDRATE_14400 = 6
    BAUDRATE_19200 = 7
    BAUDRATE_28800 = 8
    BAUDRATE_38400 = 9
    BAUDRATE_57600 = 10
    BAUDRATE_115200 = 11
    BAUDRATE_230400 = 12
    PARITY_NONE = 0
    PARITY_ODD = 1
    PARITY_EVEN = 2
    PARITY_FORCED_PARITY_1 = 3
    PARITY_FORCED_PARITY_0 = 4
    STOPBITS_1 = 1
    STOPBITS_2 = 2
    WORDLENGTH_5 = 5
    WORDLENGTH_6 = 6
    WORDLENGTH_7 = 7
    WORDLENGTH_8 = 8
    HARDWARE_FLOWCONTROL_OFF = 0
    HARDWARE_FLOWCONTROL_ON = 1
    SOFTWARE_FLOWCONTROL_OFF = 0
    SOFTWARE_FLOWCONTROL_ON = 1
    ERROR_OVERRUN = 1
    ERROR_PARITY = 2
    ERROR_FRAMING = 4

    def __init__(self, uid, ipcon):
        """
        Creates an object with the unique device ID *uid* and adds it to
        the IP Connection *ipcon*.
        """
        Device.__init__(self, uid, ipcon)

        self.api_version = (2, 0, 2)

        self.response_expected[BrickletRS232.FUNCTION_WRITE] = BrickletRS232.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletRS232.FUNCTION_READ] = BrickletRS232.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletRS232.FUNCTION_ENABLE_READ_CALLBACK] = BrickletRS232.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletRS232.FUNCTION_DISABLE_READ_CALLBACK] = BrickletRS232.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletRS232.FUNCTION_IS_READ_CALLBACK_ENABLED] = BrickletRS232.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletRS232.FUNCTION_SET_CONFIGURATION] = BrickletRS232.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletRS232.FUNCTION_GET_CONFIGURATION] = BrickletRS232.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletRS232.FUNCTION_SET_BREAK_CONDITION] = BrickletRS232.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletRS232.FUNCTION_GET_IDENTITY] = BrickletRS232.RESPONSE_EXPECTED_ALWAYS_TRUE

        self.callback_formats[BrickletRS232.CALLBACK_READ] = '60c B'
        self.callback_formats[BrickletRS232.CALLBACK_ERROR] = 'B'


    def write(self, message, length):
        """
        Writes a string of up to 60 characters to the RS232 interface. The string
        can be binary data, ASCII or similar is not necessary.

        The length of the string has to be given as an additional parameter.

        The return value is the number of bytes that could be written.

        See :func:`Set Configuration` for configuration possibilities
        regarding baudrate, parity and so on.
        """
        message = create_char_list(message)
        length = int(length)

        return self.ipcon.send_request(self, BrickletRS232.FUNCTION_WRITE, (message, length), '60c B', 'B')

    def read(self):
        """
        Returns the currently buffered message. The maximum length
        of message is 60. If the length is given as 0, there was no
        new data available.

        Instead of polling with this function, you can also use
        callbacks. See :func:`Enable Read Callback` and :cb:`Read` callback.
        """
        return Read(*self.ipcon.send_request(self, BrickletRS232.FUNCTION_READ, (), '', '60c B'))

    def enable_read_callback(self):
        """
        Enables the :cb:`Read` callback.

        By default the callback is disabled.
        """
        self.ipcon.send_request(self, BrickletRS232.FUNCTION_ENABLE_READ_CALLBACK, (), '', '')

    def disable_read_callback(self):
        """
        Disables the :cb:`Read` callback.

        By default the callback is disabled.
        """
        self.ipcon.send_request(self, BrickletRS232.FUNCTION_DISABLE_READ_CALLBACK, (), '', '')

    def is_read_callback_enabled(self):
        """
        Returns *true* if the :cb:`Read` callback is enabled,
        *false* otherwise.
        """
        return self.ipcon.send_request(self, BrickletRS232.FUNCTION_IS_READ_CALLBACK_ENABLED, (), '', '!')

    def set_configuration(self, baudrate, parity, stopbits, wordlength, hardware_flowcontrol, software_flowcontrol):
        """
        Sets the configuration for the RS232 communication. Available options:

        * Baudrate between 300 and 230400 baud.
        * Parity of none, odd, even or forced parity.
        * Stopbits can be 1 or 2.
        * Word length of 5 to 8.
        * Hard-/Software flow control can either be on or off but not both simultaneously on.

        The default is: 115200 baud, parity none, 1 stop bit, word length 8, hard-/software flow control off.
        """
        baudrate = int(baudrate)
        parity = int(parity)
        stopbits = int(stopbits)
        wordlength = int(wordlength)
        hardware_flowcontrol = int(hardware_flowcontrol)
        software_flowcontrol = int(software_flowcontrol)

        self.ipcon.send_request(self, BrickletRS232.FUNCTION_SET_CONFIGURATION, (baudrate, parity, stopbits, wordlength, hardware_flowcontrol, software_flowcontrol), 'B B B B B B', '')

    def get_configuration(self):
        """
        Returns the configuration as set by :func:`Set Configuration`.
        """
        return GetConfiguration(*self.ipcon.send_request(self, BrickletRS232.FUNCTION_GET_CONFIGURATION, (), '', 'B B B B B B'))

    def set_break_condition(self, break_time):
        """
        Sets a break condition (the TX output is forced to a logic 0 state).
        The parameter sets the hold-time of the break condition (in ms).

        .. versionadded:: 2.0.2$nbsp;(Plugin)
        """
        break_time = int(break_time)

        self.ipcon.send_request(self, BrickletRS232.FUNCTION_SET_BREAK_CONDITION, (break_time,), 'H', '')

    def get_identity(self):
        """
        Returns the UID, the UID where the Bricklet is connected to,
        the position, the hardware and firmware version as well as the
        device identifier.

        The position can be 'a', 'b', 'c' or 'd'.

        The device identifier numbers can be found :ref:`here <device_identifier>`.
        |device_identifier_constant|
        """
        return GetIdentity(*self.ipcon.send_request(self, BrickletRS232.FUNCTION_GET_IDENTITY, (), '', '8s 8s c 3B 3B H'))

    def register_callback(self, callback_id, function):
        """
        Registers the given *function* with the given *callback_id*.
        """
        if function is None:
            self.registered_callbacks.pop(callback_id, None)
        else:
            self.registered_callbacks[callback_id] = function

RS232 = BrickletRS232 # for backward compatibility
