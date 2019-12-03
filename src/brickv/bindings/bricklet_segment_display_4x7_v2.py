# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2019-12-03.      #
#                                                           #
# Python Bindings Version 2.1.24                            #
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

GetSegments = namedtuple('Segments', ['digit0', 'digit1', 'digit2', 'digit3', 'colon', 'tick'])
GetSPITFPErrorCount = namedtuple('SPITFPErrorCount', ['error_count_ack_checksum', 'error_count_message_checksum', 'error_count_frame', 'error_count_overflow'])
GetIdentity = namedtuple('Identity', ['uid', 'connected_uid', 'position', 'hardware_version', 'firmware_version', 'device_identifier'])

class BrickletSegmentDisplay4x7V2(Device):
    """
    Four 7-segment displays with switchable dots
    """

    DEVICE_IDENTIFIER = 2137
    DEVICE_DISPLAY_NAME = 'Segment Display 4x7 Bricklet 2.0'
    DEVICE_URL_PART = 'segment_display_4x7_v2' # internal

    CALLBACK_COUNTER_FINISHED = 10


    FUNCTION_SET_SEGMENTS = 1
    FUNCTION_GET_SEGMENTS = 2
    FUNCTION_SET_BRIGHTNESS = 3
    FUNCTION_GET_BRIGHTNESS = 4
    FUNCTION_SET_NUMERIC_VALUE = 5
    FUNCTION_SET_SELECTED_SEGMENT = 6
    FUNCTION_GET_SELECTED_SEGMENT = 7
    FUNCTION_START_COUNTER = 8
    FUNCTION_GET_COUNTER_VALUE = 9
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

        self.response_expected[BrickletSegmentDisplay4x7V2.FUNCTION_SET_SEGMENTS] = BrickletSegmentDisplay4x7V2.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletSegmentDisplay4x7V2.FUNCTION_GET_SEGMENTS] = BrickletSegmentDisplay4x7V2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletSegmentDisplay4x7V2.FUNCTION_SET_BRIGHTNESS] = BrickletSegmentDisplay4x7V2.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletSegmentDisplay4x7V2.FUNCTION_GET_BRIGHTNESS] = BrickletSegmentDisplay4x7V2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletSegmentDisplay4x7V2.FUNCTION_SET_NUMERIC_VALUE] = BrickletSegmentDisplay4x7V2.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletSegmentDisplay4x7V2.FUNCTION_SET_SELECTED_SEGMENT] = BrickletSegmentDisplay4x7V2.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletSegmentDisplay4x7V2.FUNCTION_GET_SELECTED_SEGMENT] = BrickletSegmentDisplay4x7V2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletSegmentDisplay4x7V2.FUNCTION_START_COUNTER] = BrickletSegmentDisplay4x7V2.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletSegmentDisplay4x7V2.FUNCTION_GET_COUNTER_VALUE] = BrickletSegmentDisplay4x7V2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletSegmentDisplay4x7V2.FUNCTION_GET_SPITFP_ERROR_COUNT] = BrickletSegmentDisplay4x7V2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletSegmentDisplay4x7V2.FUNCTION_SET_BOOTLOADER_MODE] = BrickletSegmentDisplay4x7V2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletSegmentDisplay4x7V2.FUNCTION_GET_BOOTLOADER_MODE] = BrickletSegmentDisplay4x7V2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletSegmentDisplay4x7V2.FUNCTION_SET_WRITE_FIRMWARE_POINTER] = BrickletSegmentDisplay4x7V2.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletSegmentDisplay4x7V2.FUNCTION_WRITE_FIRMWARE] = BrickletSegmentDisplay4x7V2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletSegmentDisplay4x7V2.FUNCTION_SET_STATUS_LED_CONFIG] = BrickletSegmentDisplay4x7V2.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletSegmentDisplay4x7V2.FUNCTION_GET_STATUS_LED_CONFIG] = BrickletSegmentDisplay4x7V2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletSegmentDisplay4x7V2.FUNCTION_GET_CHIP_TEMPERATURE] = BrickletSegmentDisplay4x7V2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletSegmentDisplay4x7V2.FUNCTION_RESET] = BrickletSegmentDisplay4x7V2.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletSegmentDisplay4x7V2.FUNCTION_WRITE_UID] = BrickletSegmentDisplay4x7V2.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletSegmentDisplay4x7V2.FUNCTION_READ_UID] = BrickletSegmentDisplay4x7V2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletSegmentDisplay4x7V2.FUNCTION_GET_IDENTITY] = BrickletSegmentDisplay4x7V2.RESPONSE_EXPECTED_ALWAYS_TRUE

        self.callback_formats[BrickletSegmentDisplay4x7V2.CALLBACK_COUNTER_FINISHED] = ''


    def set_segments(self, digit0, digit1, digit2, digit3, colon, tick):
        """
        Sets the segments of the Segment Display 4x7 Bricklet 2.0 segment-by-segment.

        The data is split into the four digits, two colon dots and the tick mark.

        The indices of the segments in the digit and colon parameters are as follows:

        .. image:: /Images/Bricklets/bricklet_segment_display_4x7_v2_segment_index.png
           :scale: 100 %
           :alt: Indices of segments
           :align: center
        """
        digit0 = list(map(bool, digit0))
        digit1 = list(map(bool, digit1))
        digit2 = list(map(bool, digit2))
        digit3 = list(map(bool, digit3))
        colon = list(map(bool, colon))
        tick = bool(tick)

        self.ipcon.send_request(self, BrickletSegmentDisplay4x7V2.FUNCTION_SET_SEGMENTS, (digit0, digit1, digit2, digit3, colon, tick), '8! 8! 8! 8! 2! !', '')

    def get_segments(self):
        """
        Returns the segment data as set by :func:`Set Segments`.
        """
        return GetSegments(*self.ipcon.send_request(self, BrickletSegmentDisplay4x7V2.FUNCTION_GET_SEGMENTS, (), '', '8! 8! 8! 8! 2! !'))

    def set_brightness(self, brightness):
        """
        The brightness can be set between 0 (dark) and 7 (bright).
        """
        brightness = int(brightness)

        self.ipcon.send_request(self, BrickletSegmentDisplay4x7V2.FUNCTION_SET_BRIGHTNESS, (brightness,), 'B', '')

    def get_brightness(self):
        """
        Returns the brightness as set by :func:`Set Brightness`.
        """
        return self.ipcon.send_request(self, BrickletSegmentDisplay4x7V2.FUNCTION_GET_BRIGHTNESS, (), '', 'B')

    def set_numeric_value(self, value):
        """
        Sets a numeric value for each of the digits. They represent:

        * -2: minus sign
        * -1: blank
        * 0-9: 0-9
        * 10: A
        * 11: b
        * 12: C
        * 13: d
        * 14: E
        * 15: F

        Example: A call with [-2, -1, 4, 2] will result in a display of "- 42".
        """
        value = list(map(int, value))

        self.ipcon.send_request(self, BrickletSegmentDisplay4x7V2.FUNCTION_SET_NUMERIC_VALUE, (value,), '4b', '')

    def set_selected_segment(self, segment, value):
        """
        Turns one specified segment on or off.

        The indices of the segments are as follows:

        .. image:: /Images/Bricklets/bricklet_segment_display_4x7_v2_selected_segment_index.png
           :scale: 100 %
           :alt: Indices of selected segments
           :align: center
        """
        segment = int(segment)
        value = bool(value)

        self.ipcon.send_request(self, BrickletSegmentDisplay4x7V2.FUNCTION_SET_SELECTED_SEGMENT, (segment, value), 'B !', '')

    def get_selected_segment(self, segment):
        """
        Returns the value of a single segment.
        """
        segment = int(segment)

        return self.ipcon.send_request(self, BrickletSegmentDisplay4x7V2.FUNCTION_GET_SELECTED_SEGMENT, (segment,), 'B', '!')

    def start_counter(self, value_from, value_to, increment, length):
        """
        Starts a counter with the *from* value that counts to the *to*
        value with the each step incremented by *increment*.
        *length* is the pause between each increment.

        Example: If you set *from* to 0, *to* to 100, *increment* to 1 and
        *length* to 1000, a counter that goes from 0 to 100 with one second
        pause between each increment will be started.

        Using a negative *increment* allows to count backwards.

        You can stop the counter at every time by calling :func:`Set Segments`
        or :func:`Set Numeric Value`.
        """
        value_from = int(value_from)
        value_to = int(value_to)
        increment = int(increment)
        length = int(length)

        self.ipcon.send_request(self, BrickletSegmentDisplay4x7V2.FUNCTION_START_COUNTER, (value_from, value_to, increment, length), 'h h h I', '')

    def get_counter_value(self):
        """
        Returns the counter value that is currently shown on the display.

        If there is no counter running a 0 will be returned.
        """
        return self.ipcon.send_request(self, BrickletSegmentDisplay4x7V2.FUNCTION_GET_COUNTER_VALUE, (), '', 'H')

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
        return GetSPITFPErrorCount(*self.ipcon.send_request(self, BrickletSegmentDisplay4x7V2.FUNCTION_GET_SPITFP_ERROR_COUNT, (), '', 'I I I I'))

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

        return self.ipcon.send_request(self, BrickletSegmentDisplay4x7V2.FUNCTION_SET_BOOTLOADER_MODE, (mode,), 'B', 'B')

    def get_bootloader_mode(self):
        """
        Returns the current bootloader mode, see :func:`Set Bootloader Mode`.
        """
        return self.ipcon.send_request(self, BrickletSegmentDisplay4x7V2.FUNCTION_GET_BOOTLOADER_MODE, (), '', 'B')

    def set_write_firmware_pointer(self, pointer):
        """
        Sets the firmware pointer for :func:`Write Firmware`. The pointer has
        to be increased by chunks of size 64. The data is written to flash
        every 4 chunks (which equals to one page of size 256).

        This function is used by Brick Viewer during flashing. It should not be
        necessary to call it in a normal user program.
        """
        pointer = int(pointer)

        self.ipcon.send_request(self, BrickletSegmentDisplay4x7V2.FUNCTION_SET_WRITE_FIRMWARE_POINTER, (pointer,), 'I', '')

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

        return self.ipcon.send_request(self, BrickletSegmentDisplay4x7V2.FUNCTION_WRITE_FIRMWARE, (data,), '64B', 'B')

    def set_status_led_config(self, config):
        """
        Sets the status LED configuration. By default the LED shows
        communication traffic between Brick and Bricklet, it flickers once
        for every 10 received data packets.

        You can also turn the LED permanently on/off or show a heartbeat.

        If the Bricklet is in bootloader mode, the LED is will show heartbeat by default.
        """
        config = int(config)

        self.ipcon.send_request(self, BrickletSegmentDisplay4x7V2.FUNCTION_SET_STATUS_LED_CONFIG, (config,), 'B', '')

    def get_status_led_config(self):
        """
        Returns the configuration as set by :func:`Set Status LED Config`
        """
        return self.ipcon.send_request(self, BrickletSegmentDisplay4x7V2.FUNCTION_GET_STATUS_LED_CONFIG, (), '', 'B')

    def get_chip_temperature(self):
        """
        Returns the temperature in °C as measured inside the microcontroller. The
        value returned is not the ambient temperature!

        The temperature is only proportional to the real temperature and it has bad
        accuracy. Practically it is only useful as an indicator for
        temperature changes.
        """
        return self.ipcon.send_request(self, BrickletSegmentDisplay4x7V2.FUNCTION_GET_CHIP_TEMPERATURE, (), '', 'h')

    def reset(self):
        """
        Calling this function will reset the Bricklet. All configurations
        will be lost.

        After a reset you have to create new device objects,
        calling functions on the existing ones will result in
        undefined behavior!
        """
        self.ipcon.send_request(self, BrickletSegmentDisplay4x7V2.FUNCTION_RESET, (), '', '')

    def write_uid(self, uid):
        """
        Writes a new UID into flash. If you want to set a new UID
        you have to decode the Base58 encoded UID string into an
        integer first.

        We recommend that you use Brick Viewer to change the UID.
        """
        uid = int(uid)

        self.ipcon.send_request(self, BrickletSegmentDisplay4x7V2.FUNCTION_WRITE_UID, (uid,), 'I', '')

    def read_uid(self):
        """
        Returns the current UID as an integer. Encode as
        Base58 to get the usual string version.
        """
        return self.ipcon.send_request(self, BrickletSegmentDisplay4x7V2.FUNCTION_READ_UID, (), '', 'I')

    def get_identity(self):
        """
        Returns the UID, the UID where the Bricklet is connected to,
        the position, the hardware and firmware version as well as the
        device identifier.

        The position can be 'a', 'b', 'c', 'd', 'e', 'f', 'g' or 'h' (Bricklet Port).
        The Raspberry Pi HAT (Zero) Brick is always at position 'i' and the Bricklet
        connected to an :ref:`Isolator Bricklet <isolator_bricklet>` is always as
        position 'z'.

        The device identifier numbers can be found :ref:`here <device_identifier>`.
        |device_identifier_constant|
        """
        return GetIdentity(*self.ipcon.send_request(self, BrickletSegmentDisplay4x7V2.FUNCTION_GET_IDENTITY, (), '', '8s 8s c 3B 3B H'))

    def register_callback(self, callback_id, function):
        """
        Registers the given *function* with the given *callback_id*.
        """
        if function is None:
            self.registered_callbacks.pop(callback_id, None)
        else:
            self.registered_callbacks[callback_id] = function

SegmentDisplay4x7V2 = BrickletSegmentDisplay4x7V2 # for backward compatibility
