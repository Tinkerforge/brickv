# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2012-06-26.      #
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

GetChibiErrorLog = namedtuple('ChibiErrorLog', ['underrun', 'crc_error', 'no_ack', 'overflow'])
GetRS485Configuration = namedtuple('RS485Configuration', ['speed', 'parity', 'stopbits'])

class Master(Device):
    """
    Device for controlling Stacks and four Bricklets
    """


    FUNCTION_GET_STACK_VOLTAGE = 1
    FUNCTION_GET_STACK_CURRENT = 2
    FUNCTION_SET_EXTENSION_TYPE = 3
    FUNCTION_GET_EXTENSION_TYPE = 4
    FUNCTION_IS_CHIBI_PRESENT = 5
    FUNCTION_SET_CHIBI_ADDRESS = 6
    FUNCTION_GET_CHIBI_ADDRESS = 7
    FUNCTION_SET_CHIBI_MASTER_ADDRESS = 8
    FUNCTION_GET_CHIBI_MASTER_ADDRESS = 9
    FUNCTION_SET_CHIBI_SLAVE_ADDRESS = 10
    FUNCTION_GET_CHIBI_SLAVE_ADDRESS = 11
    FUNCTION_GET_CHIBI_SIGNAL_STRENGTH = 12
    FUNCTION_GET_CHIBI_ERROR_LOG = 13
    FUNCTION_SET_CHIBI_FREQUENCY = 14
    FUNCTION_GET_CHIBI_FREQUENCY = 15
    FUNCTION_SET_CHIBI_CHANNEL = 16
    FUNCTION_GET_CHIBI_CHANNEL = 17
    FUNCTION_IS_RS485_PRESENT = 18
    FUNCTION_SET_RS485_ADDRESS = 19
    FUNCTION_GET_RS485_ADDRESS = 20
    FUNCTION_SET_RS485_SLAVE_ADDRESS = 21
    FUNCTION_GET_RS485_SLAVE_ADDRESS = 22
    FUNCTION_GET_RS485_ERROR_LOG = 23
    FUNCTION_SET_RS485_CONFIGURATION = 24
    FUNCTION_GET_RS485_CONFIGURATION = 25

    def __init__(self, uid):
        """
        Creates an object with the unique device ID *uid*. This object can
        then be added to the IP connection.
        """
        Device.__init__(self, uid)

        self.expected_name = 'Master Brick'

        self.binding_version = [1, 1, 0]


    def get_stack_voltage(self):
        """
        Returns the stack voltage in mV. The stack voltage is the
        voltage that is supplied via the stack, i.e. it is given by a 
        Step-Down or Step-Up Power Supply.
        """
        return self.ipcon.send_request(self, Master.FUNCTION_GET_STACK_VOLTAGE, (), '', 'H')

    def get_stack_current(self):
        """
        Returns the stack current in mA. The stack current is the
        current that is drawn via the stack, i.e. it is given by a
        Step-Down or Step-Up Power Supply.
        """
        return self.ipcon.send_request(self, Master.FUNCTION_GET_STACK_CURRENT, (), '', 'H')

    def set_extension_type(self, extension, exttype):
        """
        Writes the extension type to the EEPROM of a specified extension. 
        The extension is either 0 or 1 (0 is the on the bottom, 1 is the on on top, 
        if only one extension is present use 0).
        
        Possible extension types:
        
        .. csv-table::
         :header: "Type", "Description"
         :widths: 10, 100
        
         "1",    "Chibi"
         "2",    "RS485"
        
        The extension type is already set when bought and it can be set with the 
        Brick Viewer, it is unlikely that you need this function.
        
        The value will be saved in the EEPROM of the Chibi Extension, it does not
        have to be set on every startup.
        """
        self.ipcon.send_request(self, Master.FUNCTION_SET_EXTENSION_TYPE, (extension, exttype), 'B I', '')

    def get_extension_type(self, extension):
        """
        Returns the extension type for a given extension as set by 
        :func:`SetExtensionType`.
        """
        return self.ipcon.send_request(self, Master.FUNCTION_GET_EXTENSION_TYPE, (extension,), 'B', 'I')

    def is_chibi_present(self):
        """
        Returns true if a Chibi Extension is available to be used by the Master.
        """
        return self.ipcon.send_request(self, Master.FUNCTION_IS_CHIBI_PRESENT, (), '', '?')

    def set_chibi_address(self, address):
        """
        Sets the address (1-255) belonging to the Chibi Extension.
        
        It is possible to set the address with the Brick Viewer and it will be 
        saved in the EEPROM of the Chibi Extension, it does not
        have to be set on every startup.
        """
        self.ipcon.send_request(self, Master.FUNCTION_SET_CHIBI_ADDRESS, (address,), 'B', '')

    def get_chibi_address(self):
        """
        Returns the address as set by :func:`SetChibiAddress`.
        """
        return self.ipcon.send_request(self, Master.FUNCTION_GET_CHIBI_ADDRESS, (), '', 'B')

    def set_chibi_master_address(self, address):
        """
        Sets the address (1-255) of the Chibi Master. This address is used if the
        Chibi Extension is used as slave (i.e. it does not have a USB connection).
        
        It is possible to set the address with the Brick Viewer and it will be 
        saved in the EEPROM of the Chibi Extension, it does not
        have to be set on every startup.
        """
        self.ipcon.send_request(self, Master.FUNCTION_SET_CHIBI_MASTER_ADDRESS, (address,), 'B', '')

    def get_chibi_master_address(self):
        """
        Returns the address as set by :func:`SetChibiMasterAddress`.
        """
        return self.ipcon.send_request(self, Master.FUNCTION_GET_CHIBI_MASTER_ADDRESS, (), '', 'B')

    def set_chibi_slave_address(self, num, address):
        """
        Sets up to 256 slave addresses. The address numeration has to be used 
        ascending from 0. For example: If you use the Chibi Extension in Master mode
        (i.e. the stack has an USB connection) and you want to talk to three other
        Chibi stacks with the IDs 17, 23, and 42, you should call with "(0, 17),
        (1, 23) and (2, 42)".
        
        It is possible to set the addresses with the Brick Viewer and it will be 
        saved in the EEPROM of the Chibi Extension, they don't
        have to be set on every startup.
        """
        self.ipcon.send_request(self, Master.FUNCTION_SET_CHIBI_SLAVE_ADDRESS, (num, address), 'B B', '')

    def get_chibi_slave_address(self, num):
        """
        Returns the slave address for a given num as set by 
        :func:`SetChibiSlaveAddress`.
        """
        return self.ipcon.send_request(self, Master.FUNCTION_GET_CHIBI_SLAVE_ADDRESS, (num,), 'B', 'B')

    def get_chibi_signal_strength(self):
        """
        Returns the signal strength in dBm. The signal strength updates every time a
        packet is received.
        """
        return self.ipcon.send_request(self, Master.FUNCTION_GET_CHIBI_SIGNAL_STRENGTH, (), '', 'B')

    def get_chibi_error_log(self):
        """
        Returns underrun, CRC error, no ACK and overflow error counts of the Chibi
        communication. If these errors start rising, it is likely that either the
        distance between two Chibi stacks is becoming too big or there are
        interferences.
        """
        return GetChibiErrorLog(*self.ipcon.send_request(self, Master.FUNCTION_GET_CHIBI_ERROR_LOG, (), '', 'H H H H'))

    def set_chibi_frequency(self, frequency):
        """
        Sets the Chibi frequency range for the Chibi Extension. Possible values are:
        
        .. csv-table::
         :header: "Type", "Description"
         :widths: 10, 100
        
         "0",    "OQPSK 868Mhz (Europe)"
         "1",    "OQPSK 915Mhz (US)"
         "2",    "OQPSK 780Mhz (China)"
         "3",    "BPSK40 915Mhz"
        
        It is possible to set the frequency with the Brick Viewer and it will be 
        saved in the EEPROM of the Chibi Extension, it does not
        have to be set on every startup.
        """
        self.ipcon.send_request(self, Master.FUNCTION_SET_CHIBI_FREQUENCY, (frequency,), 'B', '')

    def get_chibi_frequency(self):
        """
        Returns the frequency value as set by :func:`SetChibiFrequency`.
        """
        return self.ipcon.send_request(self, Master.FUNCTION_GET_CHIBI_FREQUENCY, (), '', 'B')

    def set_chibi_channel(self, channel):
        """
        Sets the channel used by the Chibi Extension. Possible channels are
        different for different frequencies:
        
        .. csv-table::
         :header: "Frequency",             "Possible Channels"
         :widths: 40, 60
        
         "OQPSK 868Mhz (Europe)", "0"
         "OQPSK 915Mhz (US)",     "1, 2, 3, 4, 5, 6, 7, 8, 9, 10"
         "OQPSK 780Mhz (China)",  "0, 1, 2, 3"
         "BPSK40 915Mhz",         "1, 2, 3, 4, 5, 6, 7, 8, 9, 10"
        
        It is possible to set the frequency with the Brick Viewer and it will be 
        saved in the EEPROM of the Chibi Extension, it does not
        have to be set on every startup.
        """
        self.ipcon.send_request(self, Master.FUNCTION_SET_CHIBI_CHANNEL, (channel,), 'B', '')

    def get_chibi_channel(self):
        """
        Returns the channel as set by :func:`SetChibiChannel`.
        """
        return self.ipcon.send_request(self, Master.FUNCTION_GET_CHIBI_CHANNEL, (), '', 'B')

    def is_rs485_present(self):
        """
        Returns true if a RS485 Extension is available to be used by the Master.
        """
        return self.ipcon.send_request(self, Master.FUNCTION_IS_RS485_PRESENT, (), '', '?')

    def set_rs485_address(self, address):
        """
        Sets the address (1-255) belonging to the RS485 Extension.
        
        Set to 0 if the RS485 Extension should be the RS485 Master (i.e.
        connected to a PC via USB).
        
        It is possible to set the address with the Brick Viewer and it will be 
        saved in the EEPROM of the RS485 Extension, it does not
        have to be set on every startup.
        """
        self.ipcon.send_request(self, Master.FUNCTION_SET_RS485_ADDRESS, (address,), 'B', '')

    def get_rs485_address(self):
        """
        Returns the address as set by :func:`SetRS485Address`.
        """
        return self.ipcon.send_request(self, Master.FUNCTION_GET_RS485_ADDRESS, (), '', 'B')

    def set_rs485_slave_address(self, num, address):
        """
        Sets up to 256 slave addresses. The address numeration has to be used 
        ascending from 0. For example: If you use the RS485 Extension in Master mode
        (i.e. the stack has an USB connection) and you want to talk to three other
        RS485 stacks with the IDs 17, 23, and 42, you should call with "(0, 17),
        (1, 23) and (2, 42)".
        
        It is possible to set the addresses with the Brick Viewer and it will be 
        saved in the EEPROM of the RS485 Extension, they don't
        have to be set on every startup.
        """
        self.ipcon.send_request(self, Master.FUNCTION_SET_RS485_SLAVE_ADDRESS, (num, address), 'B B', '')

    def get_rs485_slave_address(self, num):
        """
        Returns the slave address for a given num as set by 
        :func:`SetRS485SlaveAddress`.
        """
        return self.ipcon.send_request(self, Master.FUNCTION_GET_RS485_SLAVE_ADDRESS, (num,), 'B', 'B')

    def get_rs485_error_log(self):
        """
        Returns CRC error counts of the RS485 communication.
        If this counter starts rising, it is likely that the distance
        between the RS485 nodes is too big or there is some kind of
        interference.
        """
        return self.ipcon.send_request(self, Master.FUNCTION_GET_RS485_ERROR_LOG, (), '', 'H')

    def set_rs485_configuration(self, speed, parity, stopbits):
        """
        Sets the configuration of the RS485 extension. Speed is given in baud. The
        Master Brick will try to match the given baud rate as exactly as possible.
        The maximum recommended baud rate is 2000000 (2Mbit).
        Possible values for parity are 'n' (none), 'e' (even) and 'o' (odd).
        Possible values for stopbits are 1 and 2.
        
        The values are stored in the EEPROM and only applied on startup. That means
        you have to restart the Master Brick after configuration.
        """
        self.ipcon.send_request(self, Master.FUNCTION_SET_RS485_CONFIGURATION, (speed, parity, stopbits), 'I c B', '')

    def get_rs485_configuration(self):
        """
        Returns the configuration as set by :func:`SetRS485SlaveAddress`.
        """
        return GetRS485Configuration(*self.ipcon.send_request(self, Master.FUNCTION_GET_RS485_CONFIGURATION, (), '', 'I c B'))
