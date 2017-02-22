# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2017-02-22.      #
#                                                           #
# Python Bindings Version 2.1.11                            #
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

Read = namedtuple('Read', ['message', 'length'])
GetRS485Configuration = namedtuple('RS485Configuration', ['baudrate', 'parity', 'stopbits', 'wordlength', 'duplex'])
GetModbusConfiguration = namedtuple('ModbusConfiguration', ['slave_address', 'master_request_timeout'])
GetBufferConfig = namedtuple('BufferConfig', ['send_buffer_size', 'receive_buffer_size'])
GetBufferStatus = namedtuple('BufferStatus', ['send_buffer_used', 'receive_buffer_used'])
GetErrorCount = namedtuple('ErrorCount', ['overrun_error_count', 'parity_error_count'])
GetModbusCommonErrorCount = namedtuple('ModbusCommonErrorCount', ['timeout_error_count', 'checksum_error_count', 'frame_too_big_error_count', 'illegal_function_error_count', 'illegal_data_address_error_count', 'illegal_data_value_error_count', 'slave_device_failure_error_count'])
GetSPITFPErrorCount = namedtuple('SPITFPErrorCount', ['error_count_ack_checksum', 'error_count_message_checksum', 'error_count_frame', 'error_count_overflow'])
GetIdentity = namedtuple('Identity', ['uid', 'connected_uid', 'position', 'hardware_version', 'firmware_version', 'device_identifier'])

class BrickletRS485(Device):
    """
    Communicates with RS485 devices with full- or half-duplex
    """

    DEVICE_IDENTIFIER = 277
    DEVICE_DISPLAY_NAME = 'RS485 Bricklet'

    CALLBACK_READ_CALLBACK = 34
    CALLBACK_ERROR_COUNT = 35
    CALLBACK_MODBUS_READ_COILS_REQUEST = 36
    CALLBACK_MODBUS_READ_COILS_RESPONSE_LOW_LEVEL = 37
    CALLBACK_MODBUS_READ_HOLDING_REGISTERS_REQUEST = 38
    CALLBACK_MODBUS_READ_HOLDING_REGISTERS_RESPONSE_LOW_LEVEL = 39
    CALLBACK_MODBUS_WRITE_SINGLE_COIL_REQUEST = 40
    CALLBACK_MODBUS_WRITE_SINGLE_COIL_RESPONSE = 41
    CALLBACK_MODBUS_WRITE_SINGLE_REGISTER_REQUEST = 42
    CALLBACK_MODBUS_WRITE_SINGLE_REGISTER_RESPONSE = 43

    CALLBACK_MODBUS_READ_COILS_RESPONSE = -37
    CALLBACK_MODBUS_READ_HOLDING_REGISTERS_RESPONSE = -39

    FUNCTION_WRITE = 1
    FUNCTION_READ = 2
    FUNCTION_ENABLE_READ_CALLBACK = 3
    FUNCTION_DISABLE_READ_CALLBACK = 4
    FUNCTION_IS_READ_CALLBACK_ENABLED = 5
    FUNCTION_SET_RS485_CONFIGURATION = 6
    FUNCTION_GET_RS485_CONFIGURATION = 7
    FUNCTION_SET_MODBUS_CONFIGURATION = 8
    FUNCTION_GET_MODBUS_CONFIGURATION = 9
    FUNCTION_SET_MODE = 10
    FUNCTION_GET_MODE = 11
    FUNCTION_APPLY_CONFIGURATION = 12
    FUNCTION_SET_COMMUNICATION_LED_CONFIG = 13
    FUNCTION_GET_COMMUNICATION_LED_CONFIG = 14
    FUNCTION_SET_ERROR_LED_CONFIG = 15
    FUNCTION_GET_ERROR_LED_CONFIG = 16
    FUNCTION_SET_BUFFER_CONFIG = 17
    FUNCTION_GET_BUFFER_CONFIG = 18
    FUNCTION_GET_BUFFER_STATUS = 19
    FUNCTION_ENABLE_ERROR_COUNT_CALLBACK = 20
    FUNCTION_DISABLE_ERROR_COUNT_CALLBACK = 21
    FUNCTION_IS_ERROR_COUNT_CALLBACK_ENABLED = 22
    FUNCTION_GET_ERROR_COUNT = 23
    FUNCTION_GET_MODBUS_COMMON_ERROR_COUNT = 24
    FUNCTION_MODBUS_REPORT_EXCEPTION = 25
    FUNCTION_MODBUS_ANSWER_READ_COILS_REQUEST_LOW_LEVEL = 26
    FUNCTION_MODBUS_READ_COILS = 27
    FUNCTION_MODBUS_ANSWER_READ_HOLDING_REGISTERS_REQUEST_LOW_LEVEL = 28
    FUNCTION_MODBUS_READ_HOLDING_REGISTERS = 29
    FUNCTION_MODBUS_ANSWER_WRITE_SINGLE_COIL_REQUEST = 30
    FUNCTION_MODBUS_WRITE_SINGLE_COIL = 31
    FUNCTION_MODBUS_ANSWER_WRITE_SINGLE_REGISTER_REQUEST = 32
    FUNCTION_MODBUS_WRITE_SINGLE_REGISTER = 33
    FUNCTION_GET_SPITFP_ERROR_COUNT = 234
    FUNCTION_SET_BOOTLOADER_MODE = 235
    FUNCTION_GET_BOOTLOADER_MODE = 236
    FUNCTION_SET_WRITE_FIRMWARE_POINTER = 237
    FUNCTION_WRITE_FIRMWARE = 238
    FUNCTION_SET_STATUS_LED_CONFIG = 239
    FUNCTION_GET_STATUS_LED_CONFIG = 240
    FUNCTION_GET_CHIP_TEMPERATURE = 242
    FUNCTION_RESET = 243
    FUNCTION_WRITE_UID = 248
    FUNCTION_READ_UID = 249
    FUNCTION_GET_IDENTITY = 255

    PARITY_NONE = 0
    PARITY_ODD = 1
    PARITY_EVEN = 2
    STOPBITS_1 = 1
    STOPBITS_2 = 2
    WORDLENGTH_5 = 5
    WORDLENGTH_6 = 6
    WORDLENGTH_7 = 7
    WORDLENGTH_8 = 8
    DUPLEX_HALF = 0
    DUPLEX_FULL = 1
    MODE_RS485 = 0
    MODE_MODBUS_SLAVE_RTU = 1
    MODE_MODBUS_MASTER_RTU = 2
    COMMUNICATION_LED_CONFIG_OFF = 0
    COMMUNICATION_LED_CONFIG_ON = 1
    COMMUNICATION_LED_CONFIG_SHOW_COMMUNICATION = 2
    COMMUNICATION_LED_CONFIG_SHOW_HEARTBEAT = 3
    ERROR_LED_CONFIG_OFF = 0
    ERROR_LED_CONFIG_ON = 1
    ERROR_LED_CONFIG_SHOW_ERROR = 2
    ERROR_LED_CONFIG_SHOW_HEARTBEAT = 3
    BOOTLOADER_MODE_BOOTLOADER = 0
    BOOTLOADER_MODE_FIRMWARE = 1
    BOOTLOADER_MODE_BOOTLOADER_WAIT_FOR_REBOOT = 2
    BOOTLOADER_MODE_FIRMWARE_WAIT_FOR_REBOOT = 3
    BOOTLOADER_MODE_FIRMWARE_WAIT_FOR_ERASE_AND_REBOOT = 4
    BOOTLOADER_STATUS_OK = 0
    BOOTLOADER_STATUS_INVALID_MODE = 1
    BOOTLOADER_STATUS_NO_CHANGE = 2
    BOOTLOADER_STATUS_ENTRY_FUNCTION_NOT_PRESENT = 3
    BOOTLOADER_STATUS_DEVICE_IDENTIFIER_INCORRECT = 4
    BOOTLOADER_STATUS_CRC_MISMATCH = 5
    STATUS_LED_CONFIG_OFF = 0
    STATUS_LED_CONFIG_ON = 1
    STATUS_LED_CONFIG_SHOW_STATUS = 2
    STATUS_LED_CONFIG_SHOW_HEARTBEAT = 3

    def __init__(self, uid, ipcon):
        """
        Creates an object with the unique device ID *uid* and adds it to
        the IP Connection *ipcon*.
        """
        Device.__init__(self, uid, ipcon)

        self.api_version = (2, 0, 0)

        self.response_expected[BrickletRS485.FUNCTION_WRITE] = BrickletRS485.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletRS485.FUNCTION_READ] = BrickletRS485.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletRS485.FUNCTION_ENABLE_READ_CALLBACK] = BrickletRS485.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletRS485.FUNCTION_DISABLE_READ_CALLBACK] = BrickletRS485.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletRS485.FUNCTION_IS_READ_CALLBACK_ENABLED] = BrickletRS485.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletRS485.FUNCTION_SET_RS485_CONFIGURATION] = BrickletRS485.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletRS485.FUNCTION_GET_RS485_CONFIGURATION] = BrickletRS485.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletRS485.FUNCTION_SET_MODBUS_CONFIGURATION] = BrickletRS485.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletRS485.FUNCTION_GET_MODBUS_CONFIGURATION] = BrickletRS485.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletRS485.FUNCTION_SET_MODE] = BrickletRS485.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletRS485.FUNCTION_GET_MODE] = BrickletRS485.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletRS485.FUNCTION_APPLY_CONFIGURATION] = BrickletRS485.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletRS485.FUNCTION_SET_COMMUNICATION_LED_CONFIG] = BrickletRS485.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletRS485.FUNCTION_GET_COMMUNICATION_LED_CONFIG] = BrickletRS485.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletRS485.FUNCTION_SET_ERROR_LED_CONFIG] = BrickletRS485.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletRS485.FUNCTION_GET_ERROR_LED_CONFIG] = BrickletRS485.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletRS485.FUNCTION_SET_BUFFER_CONFIG] = BrickletRS485.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletRS485.FUNCTION_GET_BUFFER_CONFIG] = BrickletRS485.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletRS485.FUNCTION_GET_BUFFER_STATUS] = BrickletRS485.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletRS485.FUNCTION_ENABLE_ERROR_COUNT_CALLBACK] = BrickletRS485.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletRS485.FUNCTION_DISABLE_ERROR_COUNT_CALLBACK] = BrickletRS485.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletRS485.FUNCTION_IS_ERROR_COUNT_CALLBACK_ENABLED] = BrickletRS485.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletRS485.FUNCTION_GET_ERROR_COUNT] = BrickletRS485.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletRS485.FUNCTION_GET_MODBUS_COMMON_ERROR_COUNT] = BrickletRS485.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletRS485.FUNCTION_MODBUS_REPORT_EXCEPTION] = BrickletRS485.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletRS485.FUNCTION_MODBUS_ANSWER_READ_COILS_REQUEST_LOW_LEVEL] = BrickletRS485.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletRS485.FUNCTION_MODBUS_READ_COILS] = BrickletRS485.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletRS485.FUNCTION_MODBUS_ANSWER_READ_HOLDING_REGISTERS_REQUEST_LOW_LEVEL] = BrickletRS485.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletRS485.FUNCTION_MODBUS_READ_HOLDING_REGISTERS] = BrickletRS485.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletRS485.FUNCTION_MODBUS_ANSWER_WRITE_SINGLE_COIL_REQUEST] = BrickletRS485.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletRS485.FUNCTION_MODBUS_WRITE_SINGLE_COIL] = BrickletRS485.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletRS485.FUNCTION_MODBUS_ANSWER_WRITE_SINGLE_REGISTER_REQUEST] = BrickletRS485.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletRS485.FUNCTION_MODBUS_WRITE_SINGLE_REGISTER] = BrickletRS485.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletRS485.CALLBACK_READ_CALLBACK] = BrickletRS485.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletRS485.CALLBACK_ERROR_COUNT] = BrickletRS485.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletRS485.CALLBACK_MODBUS_READ_COILS_REQUEST] = BrickletRS485.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletRS485.CALLBACK_MODBUS_READ_COILS_RESPONSE_LOW_LEVEL] = BrickletRS485.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletRS485.CALLBACK_MODBUS_READ_HOLDING_REGISTERS_REQUEST] = BrickletRS485.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletRS485.CALLBACK_MODBUS_READ_HOLDING_REGISTERS_RESPONSE_LOW_LEVEL] = BrickletRS485.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletRS485.CALLBACK_MODBUS_WRITE_SINGLE_COIL_REQUEST] = BrickletRS485.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletRS485.CALLBACK_MODBUS_WRITE_SINGLE_COIL_RESPONSE] = BrickletRS485.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletRS485.CALLBACK_MODBUS_WRITE_SINGLE_REGISTER_REQUEST] = BrickletRS485.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletRS485.CALLBACK_MODBUS_WRITE_SINGLE_REGISTER_RESPONSE] = BrickletRS485.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletRS485.FUNCTION_GET_SPITFP_ERROR_COUNT] = BrickletRS485.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletRS485.FUNCTION_SET_BOOTLOADER_MODE] = BrickletRS485.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletRS485.FUNCTION_GET_BOOTLOADER_MODE] = BrickletRS485.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletRS485.FUNCTION_SET_WRITE_FIRMWARE_POINTER] = BrickletRS485.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletRS485.FUNCTION_WRITE_FIRMWARE] = BrickletRS485.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletRS485.FUNCTION_SET_STATUS_LED_CONFIG] = BrickletRS485.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletRS485.FUNCTION_GET_STATUS_LED_CONFIG] = BrickletRS485.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletRS485.FUNCTION_GET_CHIP_TEMPERATURE] = BrickletRS485.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletRS485.FUNCTION_RESET] = BrickletRS485.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletRS485.FUNCTION_WRITE_UID] = BrickletRS485.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletRS485.FUNCTION_READ_UID] = BrickletRS485.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletRS485.FUNCTION_GET_IDENTITY] = BrickletRS485.RESPONSE_EXPECTED_ALWAYS_TRUE

        self.callback_formats[BrickletRS485.CALLBACK_READ_CALLBACK] = '60c B'
        self.callback_formats[BrickletRS485.CALLBACK_ERROR_COUNT] = 'I I'
        self.callback_formats[BrickletRS485.CALLBACK_MODBUS_READ_COILS_REQUEST] = 'B H H'
        self.callback_formats[BrickletRS485.CALLBACK_MODBUS_READ_COILS_RESPONSE_LOW_LEVEL] = 'B b H H 58B'
        self.callback_formats[BrickletRS485.CALLBACK_MODBUS_READ_HOLDING_REGISTERS_REQUEST] = 'B H H'
        self.callback_formats[BrickletRS485.CALLBACK_MODBUS_READ_HOLDING_REGISTERS_RESPONSE_LOW_LEVEL] = 'B b H H 29H'
        self.callback_formats[BrickletRS485.CALLBACK_MODBUS_WRITE_SINGLE_COIL_REQUEST] = 'B H H'
        self.callback_formats[BrickletRS485.CALLBACK_MODBUS_WRITE_SINGLE_COIL_RESPONSE] = 'B b H H'
        self.callback_formats[BrickletRS485.CALLBACK_MODBUS_WRITE_SINGLE_REGISTER_REQUEST] = 'B H H'
        self.callback_formats[BrickletRS485.CALLBACK_MODBUS_WRITE_SINGLE_REGISTER_RESPONSE] = 'B b H H'

        self.low_level_callbacks[BrickletRS485.CALLBACK_MODBUS_READ_COILS_RESPONSE_LOW_LEVEL] = [BrickletRS485.CALLBACK_MODBUS_READ_COILS_RESPONSE, {'stream': {'fixed_total_length': None}}, None]
        self.low_level_callbacks[BrickletRS485.CALLBACK_MODBUS_READ_HOLDING_REGISTERS_RESPONSE_LOW_LEVEL] = [BrickletRS485.CALLBACK_MODBUS_READ_HOLDING_REGISTERS_RESPONSE, {'stream': {'fixed_total_length': None}}, None]

    def write(self, message, length):
        """
        Writes a string of up to 60 characters to the RS485 interface. The string
        can be binary data, ASCII or similar is not necessary.
        
        The length of the string has to be given as an additional parameter.
        
        The return value is the number of bytes that could be written.
        
        See :func:`Set RS485 Configuration` for configuration possibilities
        regarding baudrate, parity and so on.
        """
        return self.ipcon.send_request(self, BrickletRS485.FUNCTION_WRITE, (message, length), '60c B', 'B')

    def read(self):
        """
        Returns the currently buffered message. The maximum length
        of message is 60. If the length is given as 0, there was no
        new data available.
        
        Instead of polling with this function, you can also use
        callbacks. See :func:`Enable Read Callback` and :cb:`Read Callback` callback.
        """
        return Read(*self.ipcon.send_request(self, BrickletRS485.FUNCTION_READ, (), '', '60c B'))

    def enable_read_callback(self):
        """
        Enables the :cb:`Read Callback` callback.
        
        By default the callback is disabled.
        """
        self.ipcon.send_request(self, BrickletRS485.FUNCTION_ENABLE_READ_CALLBACK, (), '', '')

    def disable_read_callback(self):
        """
        Disables the :cb:`Read Callback` callback.
        
        By default the callback is disabled.
        """
        self.ipcon.send_request(self, BrickletRS485.FUNCTION_DISABLE_READ_CALLBACK, (), '', '')

    def is_read_callback_enabled(self):
        """
        Returns *true* if the :cb:`Read Callback` callback is enabled,
        *false* otherwise.
        """
        return self.ipcon.send_request(self, BrickletRS485.FUNCTION_IS_READ_CALLBACK_ENABLED, (), '', '?')

    def set_rs485_configuration(self, baudrate, parity, stopbits, wordlength, duplex):
        """
        Sets the configuration for the RS485 communication. Available options:
        
        * Baudrate between 100 and 2000000 baud.
        * Parity of none, odd or even.
        * Stopbits can be 1 or 2.
        * Word length of 5 to 8.
        * Half- or Full-Duplex.
        
        The default is: 115200 baud, parity none, 1 stop bit, word length 8, half duplex.
        """
        self.ipcon.send_request(self, BrickletRS485.FUNCTION_SET_RS485_CONFIGURATION, (baudrate, parity, stopbits, wordlength, duplex), 'I B B B B', '')

    def get_rs485_configuration(self):
        """
        Returns the configuration as set by :func:`Set RS485 Configuration`.
        """
        return GetRS485Configuration(*self.ipcon.send_request(self, BrickletRS485.FUNCTION_GET_RS485_CONFIGURATION, (), '', 'I B B B B'))

    def set_modbus_configuration(self, slave_address, master_request_timeout):
        """
        Sets the configuration for the RS485 Modbus communication. Available options:
        
        * Slave Address to be used in Modbus slave mode.
        * Master Request Timeout specifies how long the master should wait for a response from a slave in milliseconds.
        """
        self.ipcon.send_request(self, BrickletRS485.FUNCTION_SET_MODBUS_CONFIGURATION, (slave_address, master_request_timeout), 'B I', '')

    def get_modbus_configuration(self):
        """
        Returns the configuration as set by :func:`Set Modbus Configuration`.
        """
        return GetModbusConfiguration(*self.ipcon.send_request(self, BrickletRS485.FUNCTION_GET_MODBUS_CONFIGURATION, (), '', 'B I'))

    def set_mode(self, mode):
        """
        Sets the mode of the Bricklet on which it operates.
        """
        self.ipcon.send_request(self, BrickletRS485.FUNCTION_SET_MODE, (mode,), 'B', '')

    def get_mode(self):
        """
        Returns the configuration as set by :func:`Set Mode`.
        """
        return self.ipcon.send_request(self, BrickletRS485.FUNCTION_GET_MODE, (), '', 'B')

    def apply_configuration(self):
        """
        This function must be called after any configuration changes.
        """
        self.ipcon.send_request(self, BrickletRS485.FUNCTION_APPLY_CONFIGURATION, (), '', '')

    def set_communication_led_config(self, config):
        """
        Sets the communication LED configuration. By default the LED shows
        communication traffic, it flickers once for every 10 received data packets.
        
        You can also turn the LED permanently on/off or show a heartbeat.
        
        If the Bricklet is in bootloader mode, the LED is off.
        """
        self.ipcon.send_request(self, BrickletRS485.FUNCTION_SET_COMMUNICATION_LED_CONFIG, (config,), 'B', '')

    def get_communication_led_config(self):
        """
        Returns the configuration as set by :func:`Set Communication LED Config`
        """
        return self.ipcon.send_request(self, BrickletRS485.FUNCTION_GET_COMMUNICATION_LED_CONFIG, (), '', 'B')

    def set_error_led_config(self, config):
        """
        Sets the error LED configuration.
        
        By default the error LED turns on if there is any error (see :cb:`Error Count`
        callback). If you call this function with the SHOW ERROR option again, the LED
        will turn off until the next error occurs.
        
        You can also turn the LED permanently on/off or show a heartbeat.
        
        If the Bricklet is in bootloader mode, the LED is off.
        """
        self.ipcon.send_request(self, BrickletRS485.FUNCTION_SET_ERROR_LED_CONFIG, (config,), 'B', '')

    def get_error_led_config(self):
        """
        Returns the configuration as set by :func:`Set Error LED Config`.
        """
        return self.ipcon.send_request(self, BrickletRS485.FUNCTION_GET_ERROR_LED_CONFIG, (), '', 'B')

    def set_buffer_config(self, send_buffer_size, receive_buffer_size):
        """
        Sets the send and receive buffer size in byte. In sum there is
        10240 byte (10kb) buffer available and the minimum buffer size
        is 1024 byte (1kb) for both.
        
        The current buffer content is lost if this function is called.
        
        The send buffer holds data that is given by :func:`Write` and
        can not be written yet. The receive buffer holds data that is
        received through RS485 but could not yet be send to the
        user, either by :func:`Read` or through :cb:`Read Callback` callback.
        
        The default configuration is 5120 byte (5kb) per buffer.
        """
        self.ipcon.send_request(self, BrickletRS485.FUNCTION_SET_BUFFER_CONFIG, (send_buffer_size, receive_buffer_size), 'H H', '')

    def get_buffer_config(self):
        """
        Returns the buffer configuration as set by :func:`Set Buffer Config`.
        """
        return GetBufferConfig(*self.ipcon.send_request(self, BrickletRS485.FUNCTION_GET_BUFFER_CONFIG, (), '', 'H H'))

    def get_buffer_status(self):
        """
        Returns the currently used bytes for the send and received buffer.
        
        See :func:`Set Buffer Config` for buffer size configuration.
        """
        return GetBufferStatus(*self.ipcon.send_request(self, BrickletRS485.FUNCTION_GET_BUFFER_STATUS, (), '', 'H H'))

    def enable_error_count_callback(self):
        """
        Enables the :cb:`Error Count` callback.
        
        By default the callback is disabled.
        """
        self.ipcon.send_request(self, BrickletRS485.FUNCTION_ENABLE_ERROR_COUNT_CALLBACK, (), '', '')

    def disable_error_count_callback(self):
        """
        Disables the :cb:`Error Count` callback.
        
        By default the callback is disabled.
        """
        self.ipcon.send_request(self, BrickletRS485.FUNCTION_DISABLE_ERROR_COUNT_CALLBACK, (), '', '')

    def is_error_count_callback_enabled(self):
        """
        Returns *true* if the :cb:`Error Count` callback is enabled,
        *false* otherwise.
        """
        return self.ipcon.send_request(self, BrickletRS485.FUNCTION_IS_ERROR_COUNT_CALLBACK_ENABLED, (), '', '?')

    def get_error_count(self):
        """
        Returns the current number of overrun and parity errors.
        """
        return GetErrorCount(*self.ipcon.send_request(self, BrickletRS485.FUNCTION_GET_ERROR_COUNT, (), '', 'I I'))

    def get_modbus_common_error_count(self):
        """
        -
        """
        return GetModbusCommonErrorCount(*self.ipcon.send_request(self, BrickletRS485.FUNCTION_GET_MODBUS_COMMON_ERROR_COUNT, (), '', 'I I I I I I I'))

    def modbus_report_exception(self, request_id, exception_code):
        """
        -
        """
        self.ipcon.send_request(self, BrickletRS485.FUNCTION_MODBUS_REPORT_EXCEPTION, (request_id, exception_code), 'B B', '')

    def modbus_answer_read_coils_request_low_level(self, request_id, stream_total_length, stream_chunk_offset, stream_chunk_data):
        """
        -
        """
        self.ipcon.send_request(self, BrickletRS485.FUNCTION_MODBUS_ANSWER_READ_COILS_REQUEST_LOW_LEVEL, (request_id, stream_total_length, stream_chunk_offset, stream_chunk_data), 'B H H 59B', '')

    def modbus_read_coils(self, slave_address, starting_address, count):
        """
        -
        """
        return self.ipcon.send_request(self, BrickletRS485.FUNCTION_MODBUS_READ_COILS, (slave_address, starting_address, count), 'B H H', 'B')

    def modbus_answer_read_holding_registers_request_low_level(self, request_id, stream_total_length, stream_chunk_offset, stream_chunk_data):
        """
        -
        """
        self.ipcon.send_request(self, BrickletRS485.FUNCTION_MODBUS_ANSWER_READ_HOLDING_REGISTERS_REQUEST_LOW_LEVEL, (request_id, stream_total_length, stream_chunk_offset, stream_chunk_data), 'B H H 29H', '')

    def modbus_read_holding_registers(self, slave_address, starting_address, count):
        """
        -
        """
        return self.ipcon.send_request(self, BrickletRS485.FUNCTION_MODBUS_READ_HOLDING_REGISTERS, (slave_address, starting_address, count), 'B H H', 'B')

    def modbus_answer_write_single_coil_request(self, request_id, coil_address, coil_value):
        """
        -
        """
        self.ipcon.send_request(self, BrickletRS485.FUNCTION_MODBUS_ANSWER_WRITE_SINGLE_COIL_REQUEST, (request_id, coil_address, coil_value), 'B H H', '')

    def modbus_write_single_coil(self, slave_address, coil_address, coil_value):
        """
        -
        """
        return self.ipcon.send_request(self, BrickletRS485.FUNCTION_MODBUS_WRITE_SINGLE_COIL, (slave_address, coil_address, coil_value), 'B H H', 'B')

    def modbus_answer_write_single_register_request(self, request_id, register_address, register_value):
        """
        -
        """
        self.ipcon.send_request(self, BrickletRS485.FUNCTION_MODBUS_ANSWER_WRITE_SINGLE_REGISTER_REQUEST, (request_id, register_address, register_value), 'B H H', '')

    def modbus_write_single_register(self, slave_address, register_address, register_value):
        """
        -
        """
        return self.ipcon.send_request(self, BrickletRS485.FUNCTION_MODBUS_WRITE_SINGLE_REGISTER, (slave_address, register_address, register_value), 'B H H', 'B')

    def get_spitfp_error_count(self):
        """
        Returns the error count for the communication between Brick and Bricklet.
        
        The errors are divided into
        
        * ack checksum errors,
        * message checksum errors,
        * frameing errors and
        * overflow errors.
        
        The errors counts are for errors that occur on the Bricklet side. All
        Bricks have a similar function that returns the errors on the Brick side.
        """
        return GetSPITFPErrorCount(*self.ipcon.send_request(self, BrickletRS485.FUNCTION_GET_SPITFP_ERROR_COUNT, (), '', 'I I I I'))

    def set_bootloader_mode(self, mode):
        """
        Sets the bootloader mode and returns the status after the requested
        mode change was instigated.
        
        You can change from bootloader mode to firmware mode and vice versa. A change
        from bootloader mode to firmware mode will only take place if the entry function,
        device identifier und crc are present and correct.
        
        This function is used by Brick Viewer during flashing. It should not be
        necessary to call it in a normal user program.
        """
        return self.ipcon.send_request(self, BrickletRS485.FUNCTION_SET_BOOTLOADER_MODE, (mode,), 'B', 'B')

    def get_bootloader_mode(self):
        """
        Returns the current bootloader mode, see :func:`Set Bootloader Mode`.
        """
        return self.ipcon.send_request(self, BrickletRS485.FUNCTION_GET_BOOTLOADER_MODE, (), '', 'B')

    def set_write_firmware_pointer(self, pointer):
        """
        Sets the firmware pointer for func:`WriteFirmware`. The pointer has
        to be increased by chunks of size 64. The data is written to flash
        every 4 chunks (which equals to one page of size 256).
        
        This function is used by Brick Viewer during flashing. It should not be
        necessary to call it in a normal user program.
        """
        self.ipcon.send_request(self, BrickletRS485.FUNCTION_SET_WRITE_FIRMWARE_POINTER, (pointer,), 'I', '')

    def write_firmware(self, data):
        """
        Writes 64 Bytes of firmware at the position as written by
        :func:`Set Write Firmware Pointer` before. The firmware is written
        to flash every 4 chunks.
        
        You can only write firmware in bootloader mode.
        
        This function is used by Brick Viewer during flashing. It should not be
        necessary to call it in a normal user program.
        """
        return self.ipcon.send_request(self, BrickletRS485.FUNCTION_WRITE_FIRMWARE, (data,), '64B', 'B')

    def set_status_led_config(self, config):
        """
        Sets the status LED configuration. By default the LED shows
        communication traffic between Brick and Bricklet, it flickers once
        for every 10 received data packets.
        
        You can also turn the LED permanently on/off or show a heartbeat.
        
        If the Bricklet is in bootloader mode, the LED is will show heartbeat by default.
        """
        self.ipcon.send_request(self, BrickletRS485.FUNCTION_SET_STATUS_LED_CONFIG, (config,), 'B', '')

    def get_status_led_config(self):
        """
        Returns the configuration as set by :func:`Set Status LED Config`
        """
        return self.ipcon.send_request(self, BrickletRS485.FUNCTION_GET_STATUS_LED_CONFIG, (), '', 'B')

    def get_chip_temperature(self):
        """
        Returns the temperature in °C as measured inside the microcontroller. The
        value returned is not the ambient temperature!
        
        The temperature is only proportional to the real temperature and it has bad
        accuracy. Practically it is only useful as an indicator for
        temperature changes.
        """
        return self.ipcon.send_request(self, BrickletRS485.FUNCTION_GET_CHIP_TEMPERATURE, (), '', 'h')

    def reset(self):
        """
        Calling this function will reset the Bricklet. All configurations
        will be lost.
        
        After a reset you have to create new device objects,
        calling functions on the existing ones will result in
        undefined behavior!
        """
        self.ipcon.send_request(self, BrickletRS485.FUNCTION_RESET, (), '', '')

    def write_uid(self, uid):
        """
        Writes a new UID into flash. If you want to set a new UID
        you have to decode the Base58 encoded UID string into an
        integer first.
        
        We recommend that you use Brick Viewer to change the UID.
        """
        self.ipcon.send_request(self, BrickletRS485.FUNCTION_WRITE_UID, (uid,), 'I', '')

    def read_uid(self):
        """
        Returns the current UID as an integer. Encode as
        Base58 to get the usual string version.
        """
        return self.ipcon.send_request(self, BrickletRS485.FUNCTION_READ_UID, (), '', 'I')

    def get_identity(self):
        """
        Returns the UID, the UID where the Bricklet is connected to,
        the position, the hardware and firmware version as well as the
        device identifier.
        
        The position can be 'a', 'b', 'c' or 'd'.
        
        The device identifier numbers can be found :ref:`here <device_identifier>`.
        |device_identifier_constant|
        """
        return GetIdentity(*self.ipcon.send_request(self, BrickletRS485.FUNCTION_GET_IDENTITY, (), '', '8s 8s c 3B 3B H'))

    def modbus_answer_read_coils_request(self, request_id, data):
        stream_total_length = len(data)
        stream_chunk_offset = 0

        while stream_chunk_offset < stream_total_length:
            stream_chunk_data = data[stream_chunk_offset:stream_chunk_offset + 59]

            if len(stream_chunk_data) < 59:
                stream_chunk_data.extend([0]*(59 - len(stream_chunk_data)))

            self.modbus_answer_read_coils_request_low_level(request_id, stream_total_length, stream_chunk_offset, stream_chunk_data)

            stream_chunk_offset += 59

    def modbus_answer_read_holding_registers_request(self, request_id, data):
        stream_total_length = len(data)
        stream_chunk_offset = 0

        while stream_chunk_offset < stream_total_length:
            stream_chunk_data = data[stream_chunk_offset:stream_chunk_offset + 29]

            if len(stream_chunk_data) < 29:
                stream_chunk_data.extend([0]*(29 - len(stream_chunk_data)))

            self.modbus_answer_read_holding_registers_request_low_level(request_id, stream_total_length, stream_chunk_offset, stream_chunk_data)

            stream_chunk_offset += 29

    def register_callback(self, id_, callback):
        """
        Registers a callback with ID *id* to the function *callback*.
        """
        if callback is None:
            self.registered_callbacks.pop(id_, None)
        else:
            self.registered_callbacks[id_] = callback

RS485 = BrickletRS485 # for backward compatibility
