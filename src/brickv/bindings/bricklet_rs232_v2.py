# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2019-05-21.      #
#                                                           #
# Python Bindings Version 2.1.22                            #
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

ReadLowLevel = namedtuple('ReadLowLevel', ['message_length', 'message_chunk_offset', 'message_chunk_data'])
GetConfiguration = namedtuple('Configuration', ['baudrate', 'parity', 'stopbits', 'wordlength', 'flowcontrol'])
GetBufferConfig = namedtuple('BufferConfig', ['send_buffer_size', 'receive_buffer_size'])
GetBufferStatus = namedtuple('BufferStatus', ['send_buffer_used', 'receive_buffer_used'])
GetErrorCount = namedtuple('ErrorCount', ['error_count_overrun', 'error_count_parity'])
GetSPITFPErrorCount = namedtuple('SPITFPErrorCount', ['error_count_ack_checksum', 'error_count_message_checksum', 'error_count_frame', 'error_count_overflow'])
GetIdentity = namedtuple('Identity', ['uid', 'connected_uid', 'position', 'hardware_version', 'firmware_version', 'device_identifier'])

class BrickletRS232V2(Device):
    """
    Communicates with RS232 devices
    """

    DEVICE_IDENTIFIER = 2108
    DEVICE_DISPLAY_NAME = 'RS232 Bricklet 2.0'
    DEVICE_URL_PART = 'rs232_v2' # internal

    CALLBACK_READ_LOW_LEVEL = 12
    CALLBACK_ERROR_COUNT = 13

    CALLBACK_READ = -12

    FUNCTION_WRITE_LOW_LEVEL = 1
    FUNCTION_READ_LOW_LEVEL = 2
    FUNCTION_ENABLE_READ_CALLBACK = 3
    FUNCTION_DISABLE_READ_CALLBACK = 4
    FUNCTION_IS_READ_CALLBACK_ENABLED = 5
    FUNCTION_SET_CONFIGURATION = 6
    FUNCTION_GET_CONFIGURATION = 7
    FUNCTION_SET_BUFFER_CONFIG = 8
    FUNCTION_GET_BUFFER_CONFIG = 9
    FUNCTION_GET_BUFFER_STATUS = 10
    FUNCTION_GET_ERROR_COUNT = 11
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
    FLOWCONTROL_OFF = 0
    FLOWCONTROL_SOFTWARE = 1
    FLOWCONTROL_HARDWARE = 2
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
    STATUS_LED_CONFIG_SHOW_HEARTBEAT = 2
    STATUS_LED_CONFIG_SHOW_STATUS = 3

    def __init__(self, uid, ipcon):
        """
        Creates an object with the unique device ID *uid* and adds it to
        the IP Connection *ipcon*.
        """
        Device.__init__(self, uid, ipcon)

        self.api_version = (2, 0, 0)

        self.response_expected[BrickletRS232V2.FUNCTION_WRITE_LOW_LEVEL] = BrickletRS232V2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletRS232V2.FUNCTION_READ_LOW_LEVEL] = BrickletRS232V2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletRS232V2.FUNCTION_ENABLE_READ_CALLBACK] = BrickletRS232V2.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletRS232V2.FUNCTION_DISABLE_READ_CALLBACK] = BrickletRS232V2.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletRS232V2.FUNCTION_IS_READ_CALLBACK_ENABLED] = BrickletRS232V2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletRS232V2.FUNCTION_SET_CONFIGURATION] = BrickletRS232V2.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletRS232V2.FUNCTION_GET_CONFIGURATION] = BrickletRS232V2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletRS232V2.FUNCTION_SET_BUFFER_CONFIG] = BrickletRS232V2.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletRS232V2.FUNCTION_GET_BUFFER_CONFIG] = BrickletRS232V2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletRS232V2.FUNCTION_GET_BUFFER_STATUS] = BrickletRS232V2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletRS232V2.FUNCTION_GET_ERROR_COUNT] = BrickletRS232V2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletRS232V2.FUNCTION_GET_SPITFP_ERROR_COUNT] = BrickletRS232V2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletRS232V2.FUNCTION_SET_BOOTLOADER_MODE] = BrickletRS232V2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletRS232V2.FUNCTION_GET_BOOTLOADER_MODE] = BrickletRS232V2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletRS232V2.FUNCTION_SET_WRITE_FIRMWARE_POINTER] = BrickletRS232V2.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletRS232V2.FUNCTION_WRITE_FIRMWARE] = BrickletRS232V2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletRS232V2.FUNCTION_SET_STATUS_LED_CONFIG] = BrickletRS232V2.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletRS232V2.FUNCTION_GET_STATUS_LED_CONFIG] = BrickletRS232V2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletRS232V2.FUNCTION_GET_CHIP_TEMPERATURE] = BrickletRS232V2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletRS232V2.FUNCTION_RESET] = BrickletRS232V2.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletRS232V2.FUNCTION_WRITE_UID] = BrickletRS232V2.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletRS232V2.FUNCTION_READ_UID] = BrickletRS232V2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletRS232V2.FUNCTION_GET_IDENTITY] = BrickletRS232V2.RESPONSE_EXPECTED_ALWAYS_TRUE

        self.callback_formats[BrickletRS232V2.CALLBACK_READ_LOW_LEVEL] = 'H H 60c'
        self.callback_formats[BrickletRS232V2.CALLBACK_ERROR_COUNT] = 'I I'

        self.high_level_callbacks[BrickletRS232V2.CALLBACK_READ] = [('stream_length', 'stream_chunk_offset', 'stream_chunk_data'), {'fixed_length': None, 'single_chunk': False}, None]

    def write_low_level(self, message_length, message_chunk_offset, message_chunk_data):
        """
        Writes characters to the RS232 interface. The characters can be binary data,
        ASCII or similar is not necessary.

        The return value is the number of characters that were written.

        See :func:`Set Configuration` for configuration possibilities
        regarding baud rate, parity and so on.
        """
        message_length = int(message_length)
        message_chunk_offset = int(message_chunk_offset)
        message_chunk_data = create_char_list(message_chunk_data)

        return self.ipcon.send_request(self, BrickletRS232V2.FUNCTION_WRITE_LOW_LEVEL, (message_length, message_chunk_offset, message_chunk_data), 'H H 60c', 'B')

    def read_low_level(self, length):
        """
        Returns up to *length* characters from receive buffer.

        Instead of polling with this function, you can also use
        callbacks. But note that this function will return available
        data only when the read callback is disabled.
        See :func:`Enable Read Callback` and :cb:`Read` callback.
        """
        length = int(length)

        return ReadLowLevel(*self.ipcon.send_request(self, BrickletRS232V2.FUNCTION_READ_LOW_LEVEL, (length,), 'H', 'H H 60c'))

    def enable_read_callback(self):
        """
        Enables the :cb:`Read` callback.

        By default the callback is disabled.
        """
        self.ipcon.send_request(self, BrickletRS232V2.FUNCTION_ENABLE_READ_CALLBACK, (), '', '')

    def disable_read_callback(self):
        """
        Disables the :cb:`Read` callback.

        By default the callback is disabled.
        """
        self.ipcon.send_request(self, BrickletRS232V2.FUNCTION_DISABLE_READ_CALLBACK, (), '', '')

    def is_read_callback_enabled(self):
        """
        Returns *true* if the :cb:`Read` callback is enabled,
        *false* otherwise.
        """
        return self.ipcon.send_request(self, BrickletRS232V2.FUNCTION_IS_READ_CALLBACK_ENABLED, (), '', '!')

    def set_configuration(self, baudrate, parity, stopbits, wordlength, flowcontrol):
        """
        Sets the configuration for the RS232 communication. Available options:

        * Baud rate between 100 and 2000000 baud.
        * Parity of none, odd or even.
        * Stop bits can be 1 or 2.
        * Word length of 5 to 8.
        * Flow control can be off, software or hardware.

        The default is: 115200 baud, parity none, 1 stop bit, word length 8.
        """
        baudrate = int(baudrate)
        parity = int(parity)
        stopbits = int(stopbits)
        wordlength = int(wordlength)
        flowcontrol = int(flowcontrol)

        self.ipcon.send_request(self, BrickletRS232V2.FUNCTION_SET_CONFIGURATION, (baudrate, parity, stopbits, wordlength, flowcontrol), 'I B B B B', '')

    def get_configuration(self):
        """
        Returns the configuration as set by :func:`Set Configuration`.
        """
        return GetConfiguration(*self.ipcon.send_request(self, BrickletRS232V2.FUNCTION_GET_CONFIGURATION, (), '', 'I B B B B'))

    def set_buffer_config(self, send_buffer_size, receive_buffer_size):
        """
        Sets the send and receive buffer size in byte. In total the buffers have to be
        10240 byte (10kb) in size, the minimum buffer size is 1024 byte (1kb) for each.

        The current buffer content is lost if this function is called.

        The send buffer holds data that is given by :func:`Write` and
        can not be written yet. The receive buffer holds data that is
        received through RS232 but could not yet be send to the
        user, either by :func:`Read` or through :cb:`Read` callback.

        The default configuration is 5120 byte (5kb) per buffer.
        """
        send_buffer_size = int(send_buffer_size)
        receive_buffer_size = int(receive_buffer_size)

        self.ipcon.send_request(self, BrickletRS232V2.FUNCTION_SET_BUFFER_CONFIG, (send_buffer_size, receive_buffer_size), 'H H', '')

    def get_buffer_config(self):
        """
        Returns the buffer configuration as set by :func:`Set Buffer Config`.
        """
        return GetBufferConfig(*self.ipcon.send_request(self, BrickletRS232V2.FUNCTION_GET_BUFFER_CONFIG, (), '', 'H H'))

    def get_buffer_status(self):
        """
        Returns the currently used bytes for the send and received buffer.

        See :func:`Set Buffer Config` for buffer size configuration.
        """
        return GetBufferStatus(*self.ipcon.send_request(self, BrickletRS232V2.FUNCTION_GET_BUFFER_STATUS, (), '', 'H H'))

    def get_error_count(self):
        """
        Returns the current number of overrun and parity errors.
        """
        return GetErrorCount(*self.ipcon.send_request(self, BrickletRS232V2.FUNCTION_GET_ERROR_COUNT, (), '', 'I I'))

    def get_spitfp_error_count(self):
        """
        Returns the error count for the communication between Brick and Bricklet.

        The errors are divided into

        * ACK checksum errors,
        * message checksum errors,
        * framing errors and
        * overflow errors.

        The errors counts are for errors that occur on the Bricklet side. All
        Bricks have a similar function that returns the errors on the Brick side.
        """
        return GetSPITFPErrorCount(*self.ipcon.send_request(self, BrickletRS232V2.FUNCTION_GET_SPITFP_ERROR_COUNT, (), '', 'I I I I'))

    def set_bootloader_mode(self, mode):
        """
        Sets the bootloader mode and returns the status after the requested
        mode change was instigated.

        You can change from bootloader mode to firmware mode and vice versa. A change
        from bootloader mode to firmware mode will only take place if the entry function,
        device identifier and CRC are present and correct.

        This function is used by Brick Viewer during flashing. It should not be
        necessary to call it in a normal user program.
        """
        mode = int(mode)

        return self.ipcon.send_request(self, BrickletRS232V2.FUNCTION_SET_BOOTLOADER_MODE, (mode,), 'B', 'B')

    def get_bootloader_mode(self):
        """
        Returns the current bootloader mode, see :func:`Set Bootloader Mode`.
        """
        return self.ipcon.send_request(self, BrickletRS232V2.FUNCTION_GET_BOOTLOADER_MODE, (), '', 'B')

    def set_write_firmware_pointer(self, pointer):
        """
        Sets the firmware pointer for :func:`Write Firmware`. The pointer has
        to be increased by chunks of size 64. The data is written to flash
        every 4 chunks (which equals to one page of size 256).

        This function is used by Brick Viewer during flashing. It should not be
        necessary to call it in a normal user program.
        """
        pointer = int(pointer)

        self.ipcon.send_request(self, BrickletRS232V2.FUNCTION_SET_WRITE_FIRMWARE_POINTER, (pointer,), 'I', '')

    def write_firmware(self, data):
        """
        Writes 64 Bytes of firmware at the position as written by
        :func:`Set Write Firmware Pointer` before. The firmware is written
        to flash every 4 chunks.

        You can only write firmware in bootloader mode.

        This function is used by Brick Viewer during flashing. It should not be
        necessary to call it in a normal user program.
        """
        data = list(map(int, data))

        return self.ipcon.send_request(self, BrickletRS232V2.FUNCTION_WRITE_FIRMWARE, (data,), '64B', 'B')

    def set_status_led_config(self, config):
        """
        Sets the status LED configuration. By default the LED shows
        communication traffic between Brick and Bricklet, it flickers once
        for every 10 received data packets.

        You can also turn the LED permanently on/off or show a heartbeat.

        If the Bricklet is in bootloader mode, the LED is will show heartbeat by default.
        """
        config = int(config)

        self.ipcon.send_request(self, BrickletRS232V2.FUNCTION_SET_STATUS_LED_CONFIG, (config,), 'B', '')

    def get_status_led_config(self):
        """
        Returns the configuration as set by :func:`Set Status LED Config`
        """
        return self.ipcon.send_request(self, BrickletRS232V2.FUNCTION_GET_STATUS_LED_CONFIG, (), '', 'B')

    def get_chip_temperature(self):
        """
        Returns the temperature in °C as measured inside the microcontroller. The
        value returned is not the ambient temperature!

        The temperature is only proportional to the real temperature and it has bad
        accuracy. Practically it is only useful as an indicator for
        temperature changes.
        """
        return self.ipcon.send_request(self, BrickletRS232V2.FUNCTION_GET_CHIP_TEMPERATURE, (), '', 'h')

    def reset(self):
        """
        Calling this function will reset the Bricklet. All configurations
        will be lost.

        After a reset you have to create new device objects,
        calling functions on the existing ones will result in
        undefined behavior!
        """
        self.ipcon.send_request(self, BrickletRS232V2.FUNCTION_RESET, (), '', '')

    def write_uid(self, uid):
        """
        Writes a new UID into flash. If you want to set a new UID
        you have to decode the Base58 encoded UID string into an
        integer first.

        We recommend that you use Brick Viewer to change the UID.
        """
        uid = int(uid)

        self.ipcon.send_request(self, BrickletRS232V2.FUNCTION_WRITE_UID, (uid,), 'I', '')

    def read_uid(self):
        """
        Returns the current UID as an integer. Encode as
        Base58 to get the usual string version.
        """
        return self.ipcon.send_request(self, BrickletRS232V2.FUNCTION_READ_UID, (), '', 'I')

    def get_identity(self):
        """
        Returns the UID, the UID where the Bricklet is connected to,
        the position, the hardware and firmware version as well as the
        device identifier.

        The position can be 'a', 'b', 'c' or 'd'.

        The device identifier numbers can be found :ref:`here <device_identifier>`.
        |device_identifier_constant|
        """
        return GetIdentity(*self.ipcon.send_request(self, BrickletRS232V2.FUNCTION_GET_IDENTITY, (), '', '8s 8s c 3B 3B H'))

    def write(self, message):
        """
        Writes characters to the RS232 interface. The characters can be binary data,
        ASCII or similar is not necessary.

        The return value is the number of characters that were written.

        See :func:`Set Configuration` for configuration possibilities
        regarding baud rate, parity and so on.
        """
        message = create_char_list(message)

        if len(message) > 65535:
            raise Error(Error.INVALID_PARAMETER, 'Message can be at most 65535 items long')

        message_length = len(message)
        message_chunk_offset = 0

        if message_length == 0:
            message_chunk_data = ['\0'] * 60
            ret = self.write_low_level(message_length, message_chunk_offset, message_chunk_data)
            message_written = ret
        else:
            message_written = 0

            with self.stream_lock:
                while message_chunk_offset < message_length:
                    message_chunk_data = create_chunk_data(message, message_chunk_offset, 60, '\0')
                    ret = self.write_low_level(message_length, message_chunk_offset, message_chunk_data)
                    message_written += ret

                    if ret < 60:
                        break # either last chunk or short write

                    message_chunk_offset += 60

        return message_written

    def read(self, length):
        """
        Returns up to *length* characters from receive buffer.

        Instead of polling with this function, you can also use
        callbacks. But note that this function will return available
        data only when the read callback is disabled.
        See :func:`Enable Read Callback` and :cb:`Read` callback.
        """
        length = int(length)

        with self.stream_lock:
            ret = self.read_low_level(length)
            message_length = ret.message_length
            message_out_of_sync = ret.message_chunk_offset != 0
            message_data = ret.message_chunk_data

            while not message_out_of_sync and len(message_data) < message_length:
                ret = self.read_low_level(length)
                message_length = ret.message_length
                message_out_of_sync = ret.message_chunk_offset != len(message_data)
                message_data += ret.message_chunk_data

            if message_out_of_sync: # discard remaining stream to bring it back in-sync
                while ret.message_chunk_offset + 60 < message_length:
                    ret = self.read_low_level(length)
                    message_length = ret.message_length

                raise Error(Error.STREAM_OUT_OF_SYNC, 'Message stream is out-of-sync')

        return message_data[:message_length]

    def register_callback(self, callback_id, function):
        """
        Registers the given *function* with the given *callback_id*.
        """
        if function is None:
            self.registered_callbacks.pop(callback_id, None)
        else:
            self.registered_callbacks[callback_id] = function

RS232V2 = BrickletRS232V2 # for backward compatibility
