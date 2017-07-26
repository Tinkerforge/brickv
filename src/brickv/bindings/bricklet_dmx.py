# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2017-07-26.      #
#                                                           #
# Python Bindings Version 2.1.14                            #
#                                                           #
# If you have a bugfix for this file and want to commit it, #
# please fix the bug in the generator. You can find a link  #
# to the generators git repository on tinkerforge.com       #
#############################################################

#### __DEVICE_IS_NOT_RELEASED__ ####

from collections import namedtuple

try:
    from .ip_connection import Device, IPConnection, Error, create_chunk_data
except ValueError:
    from ip_connection import Device, IPConnection, Error, create_chunk_data

ReadFrameLowLevel = namedtuple('ReadFrameLowLevel', ['frame_length', 'frame_chunk_offset', 'frame_chunk_data', 'frame_number'])
GetFrameErrorCount = namedtuple('FrameErrorCount', ['overrun_error_count', 'framing_error_count'])
GetFrameCallbackConfig = namedtuple('FrameCallbackConfig', ['frame_started_callback_enabled', 'frame_available_callback_enabled', 'frame_callback_enabled', 'frame_error_count_callback_enabled'])
GetSPITFPErrorCount = namedtuple('SPITFPErrorCount', ['error_count_ack_checksum', 'error_count_message_checksum', 'error_count_frame', 'error_count_overflow'])
GetIdentity = namedtuple('Identity', ['uid', 'connected_uid', 'position', 'hardware_version', 'firmware_version', 'device_identifier'])
ReadFrame = namedtuple('ReadFrame', ['frame', 'frame_number'])

class BrickletDMX(Device):
    """
    DMX Master and Slave
    """

    DEVICE_IDENTIFIER = 285
    DEVICE_DISPLAY_NAME = 'DMX Bricklet'

    CALLBACK_FRAME_STARTED = 15
    CALLBACK_FRAME_AVAILABLE = 16
    CALLBACK_FRAME_LOW_LEVEL = 17
    CALLBACK_FRAME_ERROR_COUNT = 18

    CALLBACK_FRAME = -17

    FUNCTION_SET_DMX_MODE = 1
    FUNCTION_GET_DMX_MODE = 2
    FUNCTION_WRITE_FRAME_LOW_LEVEL = 3
    FUNCTION_READ_FRAME_LOW_LEVEL = 4
    FUNCTION_SET_FRAME_DURATION = 5
    FUNCTION_GET_FRAME_DURATION = 6
    FUNCTION_DRAW_FRAME = 7
    FUNCTION_GET_FRAME_ERROR_COUNT = 8
    FUNCTION_SET_COMMUNICATION_LED_CONFIG = 9
    FUNCTION_GET_COMMUNICATION_LED_CONFIG = 10
    FUNCTION_SET_ERROR_LED_CONFIG = 11
    FUNCTION_GET_ERROR_LED_CONFIG = 12
    FUNCTION_SET_FRAME_CALLBACK_CONFIG = 13
    FUNCTION_GET_FRAME_CALLBACK_CONFIG = 14
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

    DMX_MODE_MASTER = 0
    DMX_MODE_SLAVE = 1
    COMMUNICATION_LED_CONFIG_OFF = 0
    COMMUNICATION_LED_CONFIG_ON = 1
    COMMUNICATION_LED_CONFIG_SHOW_HEARTBEAT = 2
    COMMUNICATION_LED_CONFIG_SHOW_COMMUNICATION = 3
    ERROR_LED_CONFIG_OFF = 0
    ERROR_LED_CONFIG_ON = 1
    ERROR_LED_CONFIG_SHOW_HEARTBEAT = 2
    ERROR_LED_CONFIG_SHOW_ERROR = 3
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

        self.response_expected[BrickletDMX.FUNCTION_SET_DMX_MODE] = BrickletDMX.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletDMX.FUNCTION_GET_DMX_MODE] = BrickletDMX.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletDMX.FUNCTION_WRITE_FRAME_LOW_LEVEL] = BrickletDMX.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletDMX.FUNCTION_READ_FRAME_LOW_LEVEL] = BrickletDMX.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletDMX.FUNCTION_SET_FRAME_DURATION] = BrickletDMX.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletDMX.FUNCTION_GET_FRAME_DURATION] = BrickletDMX.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletDMX.FUNCTION_DRAW_FRAME] = BrickletDMX.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletDMX.FUNCTION_GET_FRAME_ERROR_COUNT] = BrickletDMX.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletDMX.FUNCTION_SET_COMMUNICATION_LED_CONFIG] = BrickletDMX.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletDMX.FUNCTION_GET_COMMUNICATION_LED_CONFIG] = BrickletDMX.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletDMX.FUNCTION_SET_ERROR_LED_CONFIG] = BrickletDMX.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletDMX.FUNCTION_GET_ERROR_LED_CONFIG] = BrickletDMX.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletDMX.FUNCTION_SET_FRAME_CALLBACK_CONFIG] = BrickletDMX.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletDMX.FUNCTION_GET_FRAME_CALLBACK_CONFIG] = BrickletDMX.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletDMX.FUNCTION_GET_SPITFP_ERROR_COUNT] = BrickletDMX.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletDMX.FUNCTION_SET_BOOTLOADER_MODE] = BrickletDMX.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletDMX.FUNCTION_GET_BOOTLOADER_MODE] = BrickletDMX.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletDMX.FUNCTION_SET_WRITE_FIRMWARE_POINTER] = BrickletDMX.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletDMX.FUNCTION_WRITE_FIRMWARE] = BrickletDMX.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletDMX.FUNCTION_SET_STATUS_LED_CONFIG] = BrickletDMX.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletDMX.FUNCTION_GET_STATUS_LED_CONFIG] = BrickletDMX.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletDMX.FUNCTION_GET_CHIP_TEMPERATURE] = BrickletDMX.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletDMX.FUNCTION_RESET] = BrickletDMX.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletDMX.FUNCTION_WRITE_UID] = BrickletDMX.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletDMX.FUNCTION_READ_UID] = BrickletDMX.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletDMX.FUNCTION_GET_IDENTITY] = BrickletDMX.RESPONSE_EXPECTED_ALWAYS_TRUE

        self.callback_formats[BrickletDMX.CALLBACK_FRAME_STARTED] = ''
        self.callback_formats[BrickletDMX.CALLBACK_FRAME_AVAILABLE] = 'I'
        self.callback_formats[BrickletDMX.CALLBACK_FRAME_LOW_LEVEL] = 'H H 56B I'
        self.callback_formats[BrickletDMX.CALLBACK_FRAME_ERROR_COUNT] = 'I I'

        self.high_level_callbacks[BrickletDMX.CALLBACK_FRAME] = [('stream_length', 'stream_chunk_offset', 'stream_chunk_data', None), {'fixed_length': None, 'single_chunk': False}, None]

    def set_dmx_mode(self, dmx_mode):
        """
        Calling this sets frame number to 0
        """
        self.ipcon.send_request(self, BrickletDMX.FUNCTION_SET_DMX_MODE, (dmx_mode,), 'B', '')

    def get_dmx_mode(self):
        """

        """
        return self.ipcon.send_request(self, BrickletDMX.FUNCTION_GET_DMX_MODE, (), '', 'B')

    def write_frame_low_level(self, frame_length, frame_chunk_offset, frame_chunk_data):
        """

        """
        self.ipcon.send_request(self, BrickletDMX.FUNCTION_WRITE_FRAME_LOW_LEVEL, (frame_length, frame_chunk_offset, frame_chunk_data), 'H H 60B', '')

    def read_frame_low_level(self):
        """

        """
        return ReadFrameLowLevel(*self.ipcon.send_request(self, BrickletDMX.FUNCTION_READ_FRAME_LOW_LEVEL, (), '', 'H H 56B I'))

    def set_frame_duration(self, frame_duration):
        """

        """
        self.ipcon.send_request(self, BrickletDMX.FUNCTION_SET_FRAME_DURATION, (frame_duration,), 'H', '')

    def get_frame_duration(self):
        """

        """
        return self.ipcon.send_request(self, BrickletDMX.FUNCTION_GET_FRAME_DURATION, (), '', 'H')

    def draw_frame(self):
        """

        """
        self.ipcon.send_request(self, BrickletDMX.FUNCTION_DRAW_FRAME, (), '', '')

    def get_frame_error_count(self):
        """
        Returns the current number of overrun and framing errors.
        """
        return GetFrameErrorCount(*self.ipcon.send_request(self, BrickletDMX.FUNCTION_GET_FRAME_ERROR_COUNT, (), '', 'I I'))

    def set_communication_led_config(self, config):
        """
        Sets the communication LED configuration. By default the LED shows
        communication traffic, it flickers once for every 10 received data packets.

        You can also turn the LED permanently on/off or show a heartbeat.

        If the Bricklet is in bootloader mode, the LED is off.
        """
        self.ipcon.send_request(self, BrickletDMX.FUNCTION_SET_COMMUNICATION_LED_CONFIG, (config,), 'B', '')

    def get_communication_led_config(self):
        """
        Returns the configuration as set by :func:`Set Communication LED Config`
        """
        return self.ipcon.send_request(self, BrickletDMX.FUNCTION_GET_COMMUNICATION_LED_CONFIG, (), '', 'B')

    def set_error_led_config(self, config):
        """
        Sets the error LED configuration.

        By default the error LED turns on if there is any error (see :cb:`Frame Error Count`
        callback). If you call this function with the Show-Error option again, the LED
        will turn off until the next error occurs.

        You can also turn the LED permanently on/off or show a heartbeat.

        If the Bricklet is in bootloader mode, the LED is off.
        """
        self.ipcon.send_request(self, BrickletDMX.FUNCTION_SET_ERROR_LED_CONFIG, (config,), 'B', '')

    def get_error_led_config(self):
        """
        Returns the configuration as set by :func:`Set Error LED Config`.
        """
        return self.ipcon.send_request(self, BrickletDMX.FUNCTION_GET_ERROR_LED_CONFIG, (), '', 'B')

    def set_frame_callback_config(self, frame_started_callback_enabled, frame_available_callback_enabled, frame_callback_enabled, frame_error_count_callback_enabled):
        """
        default: true,true,false
        """
        self.ipcon.send_request(self, BrickletDMX.FUNCTION_SET_FRAME_CALLBACK_CONFIG, (frame_started_callback_enabled, frame_available_callback_enabled, frame_callback_enabled, frame_error_count_callback_enabled), '! ! ! !', '')

    def get_frame_callback_config(self):
        """

        """
        return GetFrameCallbackConfig(*self.ipcon.send_request(self, BrickletDMX.FUNCTION_GET_FRAME_CALLBACK_CONFIG, (), '', '! ! ! !'))

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
        return GetSPITFPErrorCount(*self.ipcon.send_request(self, BrickletDMX.FUNCTION_GET_SPITFP_ERROR_COUNT, (), '', 'I I I I'))

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
        return self.ipcon.send_request(self, BrickletDMX.FUNCTION_SET_BOOTLOADER_MODE, (mode,), 'B', 'B')

    def get_bootloader_mode(self):
        """
        Returns the current bootloader mode, see :func:`Set Bootloader Mode`.
        """
        return self.ipcon.send_request(self, BrickletDMX.FUNCTION_GET_BOOTLOADER_MODE, (), '', 'B')

    def set_write_firmware_pointer(self, pointer):
        """
        Sets the firmware pointer for func:`WriteFirmware`. The pointer has
        to be increased by chunks of size 64. The data is written to flash
        every 4 chunks (which equals to one page of size 256).

        This function is used by Brick Viewer during flashing. It should not be
        necessary to call it in a normal user program.
        """
        self.ipcon.send_request(self, BrickletDMX.FUNCTION_SET_WRITE_FIRMWARE_POINTER, (pointer,), 'I', '')

    def write_firmware(self, data):
        """
        Writes 64 Bytes of firmware at the position as written by
        :func:`Set Write Firmware Pointer` before. The firmware is written
        to flash every 4 chunks.

        You can only write firmware in bootloader mode.

        This function is used by Brick Viewer during flashing. It should not be
        necessary to call it in a normal user program.
        """
        return self.ipcon.send_request(self, BrickletDMX.FUNCTION_WRITE_FIRMWARE, (data,), '64B', 'B')

    def set_status_led_config(self, config):
        """
        Sets the status LED configuration. By default the LED shows
        communication traffic between Brick and Bricklet, it flickers once
        for every 10 received data packets.

        You can also turn the LED permanently on/off or show a heartbeat.

        If the Bricklet is in bootloader mode, the LED is will show heartbeat by default.
        """
        self.ipcon.send_request(self, BrickletDMX.FUNCTION_SET_STATUS_LED_CONFIG, (config,), 'B', '')

    def get_status_led_config(self):
        """
        Returns the configuration as set by :func:`Set Status LED Config`
        """
        return self.ipcon.send_request(self, BrickletDMX.FUNCTION_GET_STATUS_LED_CONFIG, (), '', 'B')

    def get_chip_temperature(self):
        """
        Returns the temperature in °C as measured inside the microcontroller. The
        value returned is not the ambient temperature!

        The temperature is only proportional to the real temperature and it has bad
        accuracy. Practically it is only useful as an indicator for
        temperature changes.
        """
        return self.ipcon.send_request(self, BrickletDMX.FUNCTION_GET_CHIP_TEMPERATURE, (), '', 'h')

    def reset(self):
        """
        Calling this function will reset the Bricklet. All configurations
        will be lost.

        After a reset you have to create new device objects,
        calling functions on the existing ones will result in
        undefined behavior!
        """
        self.ipcon.send_request(self, BrickletDMX.FUNCTION_RESET, (), '', '')

    def write_uid(self, uid):
        """
        Writes a new UID into flash. If you want to set a new UID
        you have to decode the Base58 encoded UID string into an
        integer first.

        We recommend that you use Brick Viewer to change the UID.
        """
        self.ipcon.send_request(self, BrickletDMX.FUNCTION_WRITE_UID, (uid,), 'I', '')

    def read_uid(self):
        """
        Returns the current UID as an integer. Encode as
        Base58 to get the usual string version.
        """
        return self.ipcon.send_request(self, BrickletDMX.FUNCTION_READ_UID, (), '', 'I')

    def get_identity(self):
        """
        Returns the UID, the UID where the Bricklet is connected to,
        the position, the hardware and firmware version as well as the
        device identifier.

        The position can be 'a', 'b', 'c' or 'd'.

        The device identifier numbers can be found :ref:`here <device_identifier>`.
        |device_identifier_constant|
        """
        return GetIdentity(*self.ipcon.send_request(self, BrickletDMX.FUNCTION_GET_IDENTITY, (), '', '8s 8s c 3B 3B H'))

    def write_frame(self, frame):
        """

        """
        if len(frame) > 65535:
            raise Error(Error.INVALID_PARAMETER, 'Frame can be at most 65535 items long')

        frame = list(frame) # convert potential tuple to list
        frame_length = len(frame)
        frame_chunk_offset = 0

        if frame_length == 0:
            frame_chunk_data = [0] * 60
            ret = self.write_frame_low_level(frame_length, frame_chunk_offset, frame_chunk_data)
        else:
            with self.stream_lock:
                while frame_chunk_offset < frame_length:
                    frame_chunk_data = create_chunk_data(frame, frame_chunk_offset, 60, 0)
                    ret = self.write_frame_low_level(frame_length, frame_chunk_offset, frame_chunk_data)
                    frame_chunk_offset += 60

        return ret

    def read_frame(self):
        """

        """
        with self.stream_lock:
            ret = self.read_frame_low_level()
            frame_length = ret.frame_length
            frame_out_of_sync = ret.frame_chunk_offset != 0
            frame_data = ret.frame_chunk_data

            while not frame_out_of_sync and len(frame_data) < frame_length:
                ret = self.read_frame_low_level()
                frame_length = ret.frame_length
                frame_out_of_sync = ret.frame_chunk_offset != len(frame_data)
                frame_data += ret.frame_chunk_data

            if frame_out_of_sync: # discard remaining stream to bring it back in-sync
                while ret.frame_chunk_offset + 56 < frame_length:
                    ret = self.read_frame_low_level()
                    frame_length = ret.frame_length

                raise Error(Error.STREAM_OUT_OF_SYNC, 'Frame stream is out-of-sync')

        return ReadFrame(frame_data[:frame_length], ret.frame_number)

    def register_callback(self, callback_id, function):
        """
        Registers the given *function* with the given *callback_id*.
        """
        if function is None:
            self.registered_callbacks.pop(callback_id, None)
        else:
            self.registered_callbacks[callback_id] = function

DMX = BrickletDMX # for backward compatibility
