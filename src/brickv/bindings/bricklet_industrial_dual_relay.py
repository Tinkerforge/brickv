# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2018-06-22.      #
#                                                           #
# Python Bindings Version 2.1.17                            #
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

GetValue = namedtuple('Value', ['channel0', 'channel1'])
GetMonoflop = namedtuple('Monoflop', ['value', 'time', 'time_remaining'])
GetSPITFPErrorCount = namedtuple('SPITFPErrorCount', ['error_count_ack_checksum', 'error_count_message_checksum', 'error_count_frame', 'error_count_overflow'])
GetIdentity = namedtuple('Identity', ['uid', 'connected_uid', 'position', 'hardware_version', 'firmware_version', 'device_identifier'])

class BrickletIndustrialDualRelay(Device):
    """
    Two relays to switch AC/DC devices
    """

    DEVICE_IDENTIFIER = 284
    DEVICE_DISPLAY_NAME = 'Industrial Dual Relay Bricklet'
    DEVICE_URL_PART = 'industrial_dual_relay' # internal

    CALLBACK_MONOFLOP_DONE = 5


    FUNCTION_SET_VALUE = 1
    FUNCTION_GET_VALUE = 2
    FUNCTION_SET_MONOFLOP = 3
    FUNCTION_GET_MONOFLOP = 4
    FUNCTION_SET_SELECTED_VALUE = 6
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

        self.response_expected[BrickletIndustrialDualRelay.FUNCTION_SET_VALUE] = BrickletIndustrialDualRelay.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletIndustrialDualRelay.FUNCTION_GET_VALUE] = BrickletIndustrialDualRelay.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletIndustrialDualRelay.FUNCTION_SET_MONOFLOP] = BrickletIndustrialDualRelay.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletIndustrialDualRelay.FUNCTION_GET_MONOFLOP] = BrickletIndustrialDualRelay.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletIndustrialDualRelay.FUNCTION_SET_SELECTED_VALUE] = BrickletIndustrialDualRelay.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletIndustrialDualRelay.FUNCTION_GET_SPITFP_ERROR_COUNT] = BrickletIndustrialDualRelay.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletIndustrialDualRelay.FUNCTION_SET_BOOTLOADER_MODE] = BrickletIndustrialDualRelay.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletIndustrialDualRelay.FUNCTION_GET_BOOTLOADER_MODE] = BrickletIndustrialDualRelay.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletIndustrialDualRelay.FUNCTION_SET_WRITE_FIRMWARE_POINTER] = BrickletIndustrialDualRelay.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletIndustrialDualRelay.FUNCTION_WRITE_FIRMWARE] = BrickletIndustrialDualRelay.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletIndustrialDualRelay.FUNCTION_SET_STATUS_LED_CONFIG] = BrickletIndustrialDualRelay.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletIndustrialDualRelay.FUNCTION_GET_STATUS_LED_CONFIG] = BrickletIndustrialDualRelay.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletIndustrialDualRelay.FUNCTION_GET_CHIP_TEMPERATURE] = BrickletIndustrialDualRelay.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletIndustrialDualRelay.FUNCTION_RESET] = BrickletIndustrialDualRelay.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletIndustrialDualRelay.FUNCTION_WRITE_UID] = BrickletIndustrialDualRelay.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletIndustrialDualRelay.FUNCTION_READ_UID] = BrickletIndustrialDualRelay.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletIndustrialDualRelay.FUNCTION_GET_IDENTITY] = BrickletIndustrialDualRelay.RESPONSE_EXPECTED_ALWAYS_TRUE

        self.callback_formats[BrickletIndustrialDualRelay.CALLBACK_MONOFLOP_DONE] = 'B !'


    def set_value(self, channel0, channel1):
        """
        Sets the state of the relays, *true* means on and *false* means off.
        For example: (true, false) turns relay 0 on and relay 1 off.

        If you just want to set one of the relays and don't know the current state
        of the other relay, you can get the state with :func:`Get Value` or you
        can use :func:`Set Selected Value`.

        Running monoflop timers will be overwritten if this function is called.

        The default value is (*false*, *false*).
        """
        channel0 = bool(channel0)
        channel1 = bool(channel1)

        self.ipcon.send_request(self, BrickletIndustrialDualRelay.FUNCTION_SET_VALUE, (channel0, channel1), '! !', '')

    def get_value(self):
        """
        Returns the state of the relays, *true* means on and *false* means off.
        """
        return GetValue(*self.ipcon.send_request(self, BrickletIndustrialDualRelay.FUNCTION_GET_VALUE, (), '', '! !'))

    def set_monoflop(self, channel, value, time):
        """
        The first parameter can be 0 or 1 (relay 0 or relay 1). The second parameter
        is the desired state of the relay (*true* means on and *false* means off).
        The third parameter indicates the time (in ms) that the relay should hold
        the state.

        If this function is called with the parameters (1, true, 1500):
        Relay 1 will turn on and in 1.5s it will turn off again.

        A monoflop can be used as a failsafe mechanism. For example: Lets assume you
        have a RS485 bus and a Industrial Dual Relay Bricklet connected to one of the
        slave stacks. You can now call this function every second, with a time parameter
        of two seconds. The relay will be on all the time. If now the RS485
        connection is lost, the relay will turn off in at most two seconds.
        """
        channel = int(channel)
        value = bool(value)
        time = int(time)

        self.ipcon.send_request(self, BrickletIndustrialDualRelay.FUNCTION_SET_MONOFLOP, (channel, value, time), 'B ! I', '')

    def get_monoflop(self, channel):
        """
        Returns (for the given relay) the current state and the time as set by
        :func:`Set Monoflop` as well as the remaining time until the state flips.

        If the timer is not running currently, the remaining time will be returned
        as 0.
        """
        channel = int(channel)

        return GetMonoflop(*self.ipcon.send_request(self, BrickletIndustrialDualRelay.FUNCTION_GET_MONOFLOP, (channel,), 'B', '! I I'))

    def set_selected_value(self, channel, value):
        """
        Sets the state of the selected relay (0 or 1), *true* means on and *false*
        means off.

        The other relay remains untouched.
        """
        channel = int(channel)
        value = bool(value)

        self.ipcon.send_request(self, BrickletIndustrialDualRelay.FUNCTION_SET_SELECTED_VALUE, (channel, value), 'B !', '')

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
        return GetSPITFPErrorCount(*self.ipcon.send_request(self, BrickletIndustrialDualRelay.FUNCTION_GET_SPITFP_ERROR_COUNT, (), '', 'I I I I'))

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

        return self.ipcon.send_request(self, BrickletIndustrialDualRelay.FUNCTION_SET_BOOTLOADER_MODE, (mode,), 'B', 'B')

    def get_bootloader_mode(self):
        """
        Returns the current bootloader mode, see :func:`Set Bootloader Mode`.
        """
        return self.ipcon.send_request(self, BrickletIndustrialDualRelay.FUNCTION_GET_BOOTLOADER_MODE, (), '', 'B')

    def set_write_firmware_pointer(self, pointer):
        """
        Sets the firmware pointer for :func:`Write Firmware`. The pointer has
        to be increased by chunks of size 64. The data is written to flash
        every 4 chunks (which equals to one page of size 256).

        This function is used by Brick Viewer during flashing. It should not be
        necessary to call it in a normal user program.
        """
        pointer = int(pointer)

        self.ipcon.send_request(self, BrickletIndustrialDualRelay.FUNCTION_SET_WRITE_FIRMWARE_POINTER, (pointer,), 'I', '')

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

        return self.ipcon.send_request(self, BrickletIndustrialDualRelay.FUNCTION_WRITE_FIRMWARE, (data,), '64B', 'B')

    def set_status_led_config(self, config):
        """
        Sets the status LED configuration. By default the LED shows
        communication traffic between Brick and Bricklet, it flickers once
        for every 10 received data packets.

        You can also turn the LED permanently on/off or show a heartbeat.

        If the Bricklet is in bootloader mode, the LED is will show heartbeat by default.
        """
        config = int(config)

        self.ipcon.send_request(self, BrickletIndustrialDualRelay.FUNCTION_SET_STATUS_LED_CONFIG, (config,), 'B', '')

    def get_status_led_config(self):
        """
        Returns the configuration as set by :func:`Set Status LED Config`
        """
        return self.ipcon.send_request(self, BrickletIndustrialDualRelay.FUNCTION_GET_STATUS_LED_CONFIG, (), '', 'B')

    def get_chip_temperature(self):
        """
        Returns the temperature in °C as measured inside the microcontroller. The
        value returned is not the ambient temperature!

        The temperature is only proportional to the real temperature and it has bad
        accuracy. Practically it is only useful as an indicator for
        temperature changes.
        """
        return self.ipcon.send_request(self, BrickletIndustrialDualRelay.FUNCTION_GET_CHIP_TEMPERATURE, (), '', 'h')

    def reset(self):
        """
        Calling this function will reset the Bricklet. All configurations
        will be lost.

        After a reset you have to create new device objects,
        calling functions on the existing ones will result in
        undefined behavior!
        """
        self.ipcon.send_request(self, BrickletIndustrialDualRelay.FUNCTION_RESET, (), '', '')

    def write_uid(self, uid):
        """
        Writes a new UID into flash. If you want to set a new UID
        you have to decode the Base58 encoded UID string into an
        integer first.

        We recommend that you use Brick Viewer to change the UID.
        """
        uid = int(uid)

        self.ipcon.send_request(self, BrickletIndustrialDualRelay.FUNCTION_WRITE_UID, (uid,), 'I', '')

    def read_uid(self):
        """
        Returns the current UID as an integer. Encode as
        Base58 to get the usual string version.
        """
        return self.ipcon.send_request(self, BrickletIndustrialDualRelay.FUNCTION_READ_UID, (), '', 'I')

    def get_identity(self):
        """
        Returns the UID, the UID where the Bricklet is connected to,
        the position, the hardware and firmware version as well as the
        device identifier.

        The position can be 'a', 'b', 'c' or 'd'.

        The device identifier numbers can be found :ref:`here <device_identifier>`.
        |device_identifier_constant|
        """
        return GetIdentity(*self.ipcon.send_request(self, BrickletIndustrialDualRelay.FUNCTION_GET_IDENTITY, (), '', '8s 8s c 3B 3B H'))

    def register_callback(self, callback_id, function):
        """
        Registers the given *function* with the given *callback_id*.
        """
        if function is None:
            self.registered_callbacks.pop(callback_id, None)
        else:
            self.registered_callbacks[callback_id] = function

IndustrialDualRelay = BrickletIndustrialDualRelay # for backward compatibility
