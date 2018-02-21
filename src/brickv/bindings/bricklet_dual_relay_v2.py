# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2018-02-21.      #
#                                                           #
# Python Bindings Version 2.1.15                            #
#                                                           #
# If you have a bugfix for this file and want to commit it, #
# please fix the bug in the generator. You can find a link  #
# to the generators git repository on tinkerforge.com       #
#############################################################

#### __DEVICE_IS_NOT_RELEASED__ ####

from collections import namedtuple

try:
    from .ip_connection import Device, IPConnection, Error, create_char, create_char_list, create_string, create_chunk_data
except ValueError:
    from ip_connection import Device, IPConnection, Error, create_char, create_char_list, create_string, create_chunk_data

GetState = namedtuple('State', ['relay1', 'relay2'])
GetMonoflop = namedtuple('Monoflop', ['state', 'time', 'time_remaining'])
GetSPITFPErrorCount = namedtuple('SPITFPErrorCount', ['error_count_ack_checksum', 'error_count_message_checksum', 'error_count_frame', 'error_count_overflow'])
GetIdentity = namedtuple('Identity', ['uid', 'connected_uid', 'position', 'hardware_version', 'firmware_version', 'device_identifier'])

class BrickletDualRelayV2(Device):
    """
    Two relays to switch AC/DC devices
    """

    DEVICE_IDENTIFIER = 284
    DEVICE_DISPLAY_NAME = 'Dual Relay Bricklet 2.0'
    DEVICE_URL_PART = 'dual_relay_v2' # internal

    CALLBACK_MONOFLOP_DONE = 5


    FUNCTION_SET_STATE = 1
    FUNCTION_GET_STATE = 2
    FUNCTION_SET_MONOFLOP = 3
    FUNCTION_GET_MONOFLOP = 4
    FUNCTION_SET_SELECTED_STATE = 6
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

        self.response_expected[BrickletDualRelayV2.FUNCTION_SET_STATE] = BrickletDualRelayV2.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletDualRelayV2.FUNCTION_GET_STATE] = BrickletDualRelayV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletDualRelayV2.FUNCTION_SET_MONOFLOP] = BrickletDualRelayV2.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletDualRelayV2.FUNCTION_GET_MONOFLOP] = BrickletDualRelayV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletDualRelayV2.FUNCTION_SET_SELECTED_STATE] = BrickletDualRelayV2.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletDualRelayV2.FUNCTION_GET_SPITFP_ERROR_COUNT] = BrickletDualRelayV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletDualRelayV2.FUNCTION_SET_BOOTLOADER_MODE] = BrickletDualRelayV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletDualRelayV2.FUNCTION_GET_BOOTLOADER_MODE] = BrickletDualRelayV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletDualRelayV2.FUNCTION_SET_WRITE_FIRMWARE_POINTER] = BrickletDualRelayV2.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletDualRelayV2.FUNCTION_WRITE_FIRMWARE] = BrickletDualRelayV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletDualRelayV2.FUNCTION_SET_STATUS_LED_CONFIG] = BrickletDualRelayV2.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletDualRelayV2.FUNCTION_GET_STATUS_LED_CONFIG] = BrickletDualRelayV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletDualRelayV2.FUNCTION_GET_CHIP_TEMPERATURE] = BrickletDualRelayV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletDualRelayV2.FUNCTION_RESET] = BrickletDualRelayV2.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletDualRelayV2.FUNCTION_WRITE_UID] = BrickletDualRelayV2.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletDualRelayV2.FUNCTION_READ_UID] = BrickletDualRelayV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletDualRelayV2.FUNCTION_GET_IDENTITY] = BrickletDualRelayV2.RESPONSE_EXPECTED_ALWAYS_TRUE

        self.callback_formats[BrickletDualRelayV2.CALLBACK_MONOFLOP_DONE] = 'B !'


    def set_state(self, relay1, relay2):
        """
        Sets the state of the relays, *true* means on and *false* means off.
        For example: (true, false) turns relay 1 on and relay 2 off.

        If you just want to set one of the relays and don't know the current state
        of the other relay, you can get the state with :func:`Get State` or you
        can use :func:`Set Selected State`.

        Running monoflop timers will be overwritten if this function is called.

        The default value is (*false*, *false*).
        """
        relay1 = bool(relay1)
        relay2 = bool(relay2)

        self.ipcon.send_request(self, BrickletDualRelayV2.FUNCTION_SET_STATE, (relay1, relay2), '! !', '')

    def get_state(self):
        """
        Returns the state of the relays, *true* means on and *false* means off.
        """
        return GetState(*self.ipcon.send_request(self, BrickletDualRelayV2.FUNCTION_GET_STATE, (), '', '! !'))

    def set_monoflop(self, relay, state, time):
        """
        The first parameter can be 1 or 2 (relay 1 or relay 2). The second parameter
        is the desired state of the relay (*true* means on and *false* means off).
        The third parameter indicates the time (in ms) that the relay should hold
        the state.

        If this function is called with the parameters (1, true, 1500):
        Relay 1 will turn on and in 1.5s it will turn off again.

        A monoflop can be used as a failsafe mechanism. For example: Lets assume you
        have a RS485 bus and a Dual Relay Bricklet connected to one of the slave
        stacks. You can now call this function every second, with a time parameter
        of two seconds. The relay will be on all the time. If now the RS485
        connection is lost, the relay will turn off in at most two seconds.
        """
        relay = int(relay)
        state = bool(state)
        time = int(time)

        self.ipcon.send_request(self, BrickletDualRelayV2.FUNCTION_SET_MONOFLOP, (relay, state, time), 'B ! I', '')

    def get_monoflop(self, relay):
        """
        Returns (for the given relay) the current state and the time as set by
        :func:`Set Monoflop` as well as the remaining time until the state flips.

        If the timer is not running currently, the remaining time will be returned
        as 0.
        """
        relay = int(relay)

        return GetMonoflop(*self.ipcon.send_request(self, BrickletDualRelayV2.FUNCTION_GET_MONOFLOP, (relay,), 'B', '! I I'))

    def set_selected_state(self, relay, state):
        """
        Sets the state of the selected relay (1 or 2), *true* means on and *false* means off.

        The other relay remains untouched.
        """
        relay = int(relay)
        state = bool(state)

        self.ipcon.send_request(self, BrickletDualRelayV2.FUNCTION_SET_SELECTED_STATE, (relay, state), 'B !', '')

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
        return GetSPITFPErrorCount(*self.ipcon.send_request(self, BrickletDualRelayV2.FUNCTION_GET_SPITFP_ERROR_COUNT, (), '', 'I I I I'))

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
        mode = int(mode)

        return self.ipcon.send_request(self, BrickletDualRelayV2.FUNCTION_SET_BOOTLOADER_MODE, (mode,), 'B', 'B')

    def get_bootloader_mode(self):
        """
        Returns the current bootloader mode, see :func:`Set Bootloader Mode`.
        """
        return self.ipcon.send_request(self, BrickletDualRelayV2.FUNCTION_GET_BOOTLOADER_MODE, (), '', 'B')

    def set_write_firmware_pointer(self, pointer):
        """
        Sets the firmware pointer for :func:`Write Firmware`. The pointer has
        to be increased by chunks of size 64. The data is written to flash
        every 4 chunks (which equals to one page of size 256).

        This function is used by Brick Viewer during flashing. It should not be
        necessary to call it in a normal user program.
        """
        pointer = int(pointer)

        self.ipcon.send_request(self, BrickletDualRelayV2.FUNCTION_SET_WRITE_FIRMWARE_POINTER, (pointer,), 'I', '')

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

        return self.ipcon.send_request(self, BrickletDualRelayV2.FUNCTION_WRITE_FIRMWARE, (data,), '64B', 'B')

    def set_status_led_config(self, config):
        """
        Sets the status LED configuration. By default the LED shows
        communication traffic between Brick and Bricklet, it flickers once
        for every 10 received data packets.

        You can also turn the LED permanently on/off or show a heartbeat.

        If the Bricklet is in bootloader mode, the LED is will show heartbeat by default.
        """
        config = int(config)

        self.ipcon.send_request(self, BrickletDualRelayV2.FUNCTION_SET_STATUS_LED_CONFIG, (config,), 'B', '')

    def get_status_led_config(self):
        """
        Returns the configuration as set by :func:`Set Status LED Config`
        """
        return self.ipcon.send_request(self, BrickletDualRelayV2.FUNCTION_GET_STATUS_LED_CONFIG, (), '', 'B')

    def get_chip_temperature(self):
        """
        Returns the temperature in °C as measured inside the microcontroller. The
        value returned is not the ambient temperature!

        The temperature is only proportional to the real temperature and it has bad
        accuracy. Practically it is only useful as an indicator for
        temperature changes.
        """
        return self.ipcon.send_request(self, BrickletDualRelayV2.FUNCTION_GET_CHIP_TEMPERATURE, (), '', 'h')

    def reset(self):
        """
        Calling this function will reset the Bricklet. All configurations
        will be lost.

        After a reset you have to create new device objects,
        calling functions on the existing ones will result in
        undefined behavior!
        """
        self.ipcon.send_request(self, BrickletDualRelayV2.FUNCTION_RESET, (), '', '')

    def write_uid(self, uid):
        """
        Writes a new UID into flash. If you want to set a new UID
        you have to decode the Base58 encoded UID string into an
        integer first.

        We recommend that you use Brick Viewer to change the UID.
        """
        uid = int(uid)

        self.ipcon.send_request(self, BrickletDualRelayV2.FUNCTION_WRITE_UID, (uid,), 'I', '')

    def read_uid(self):
        """
        Returns the current UID as an integer. Encode as
        Base58 to get the usual string version.
        """
        return self.ipcon.send_request(self, BrickletDualRelayV2.FUNCTION_READ_UID, (), '', 'I')

    def get_identity(self):
        """
        Returns the UID, the UID where the Bricklet is connected to,
        the position, the hardware and firmware version as well as the
        device identifier.

        The position can be 'a', 'b', 'c' or 'd'.

        The device identifier numbers can be found :ref:`here <device_identifier>`.
        |device_identifier_constant|
        """
        return GetIdentity(*self.ipcon.send_request(self, BrickletDualRelayV2.FUNCTION_GET_IDENTITY, (), '', '8s 8s c 3B 3B H'))

    def register_callback(self, callback_id, function):
        """
        Registers the given *function* with the given *callback_id*.
        """
        if function is None:
            self.registered_callbacks.pop(callback_id, None)
        else:
            self.registered_callbacks[callback_id] = function

DualRelayV2 = BrickletDualRelayV2 # for backward compatibility
