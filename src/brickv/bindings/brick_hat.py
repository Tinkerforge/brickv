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

GetSleepMode = namedtuple('SleepMode', ['power_off_delay', 'power_off_duration', 'raspberry_pi_off', 'bricklets_off', 'enable_sleep_indicator'])
GetVoltages = namedtuple('Voltages', ['voltage_usb', 'voltage_dc'])
GetSPITFPErrorCount = namedtuple('SPITFPErrorCount', ['error_count_ack_checksum', 'error_count_message_checksum', 'error_count_frame', 'error_count_overflow'])
GetIdentity = namedtuple('Identity', ['uid', 'connected_uid', 'position', 'hardware_version', 'firmware_version', 'device_identifier'])

class BrickHAT(Device):
    """
    HAT for Raspberry Pi with 8 Bricklets ports and real-time clock
    """

    DEVICE_IDENTIFIER = 111
    DEVICE_DISPLAY_NAME = 'HAT Brick'
    DEVICE_URL_PART = 'hat' # internal



    FUNCTION_SET_SLEEP_MODE = 1
    FUNCTION_GET_SLEEP_MODE = 2
    FUNCTION_SET_BRICKLET_POWER = 3
    FUNCTION_GET_BRICKLET_POWER = 4
    FUNCTION_GET_VOLTAGES = 5
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

        self.response_expected[BrickHAT.FUNCTION_SET_SLEEP_MODE] = BrickHAT.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickHAT.FUNCTION_GET_SLEEP_MODE] = BrickHAT.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickHAT.FUNCTION_SET_BRICKLET_POWER] = BrickHAT.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickHAT.FUNCTION_GET_BRICKLET_POWER] = BrickHAT.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickHAT.FUNCTION_GET_VOLTAGES] = BrickHAT.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickHAT.FUNCTION_GET_SPITFP_ERROR_COUNT] = BrickHAT.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickHAT.FUNCTION_SET_BOOTLOADER_MODE] = BrickHAT.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickHAT.FUNCTION_GET_BOOTLOADER_MODE] = BrickHAT.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickHAT.FUNCTION_SET_WRITE_FIRMWARE_POINTER] = BrickHAT.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickHAT.FUNCTION_WRITE_FIRMWARE] = BrickHAT.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickHAT.FUNCTION_SET_STATUS_LED_CONFIG] = BrickHAT.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickHAT.FUNCTION_GET_STATUS_LED_CONFIG] = BrickHAT.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickHAT.FUNCTION_GET_CHIP_TEMPERATURE] = BrickHAT.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickHAT.FUNCTION_RESET] = BrickHAT.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickHAT.FUNCTION_WRITE_UID] = BrickHAT.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickHAT.FUNCTION_READ_UID] = BrickHAT.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickHAT.FUNCTION_GET_IDENTITY] = BrickHAT.RESPONSE_EXPECTED_ALWAYS_TRUE



    def set_sleep_mode(self, power_off_delay, power_off_duration, raspberry_pi_off, bricklets_off, enable_sleep_indicator):
        """
        Sets the sleep mode.

        Parameters:

        * Power Off Delay: Time before the RPi/Bricklets are powered off in seconds.
        * Power Off Duration: Duration that the RPi/Bricklets stay powered off in seconds.
        * Raspberry Pi Off: RPi if powereed off if set to true.
        * Bricklets Off: Bricklets are powered off if set to true.
        * Enable Sleep Indicator: If set to true, the status LED will blink in a 1s interval
          during the whole power off duration. This will draw an additional 0.3mA.

        Example: To turn RPi and Bricklets off in 5 seconds for 10 minutes with sleep
        indicator enabled call (5, 60*10, true, true, true).

        This function can also be used to implement a watchdog. To do this you can
        write a program that calls this function once per second in a loop with
        (10, 2, true, false, false). If the RPi crashes or gets stuck
        the HAT will reset the RPi after 10 seconds.
        """
        power_off_delay = int(power_off_delay)
        power_off_duration = int(power_off_duration)
        raspberry_pi_off = bool(raspberry_pi_off)
        bricklets_off = bool(bricklets_off)
        enable_sleep_indicator = bool(enable_sleep_indicator)

        self.ipcon.send_request(self, BrickHAT.FUNCTION_SET_SLEEP_MODE, (power_off_delay, power_off_duration, raspberry_pi_off, bricklets_off, enable_sleep_indicator), 'I I ! ! !', '')

    def get_sleep_mode(self):
        """
        Returns the sleep mode settings as set by :func:`Set Sleep Mode`.
        """
        return GetSleepMode(*self.ipcon.send_request(self, BrickHAT.FUNCTION_GET_SLEEP_MODE, (), '', 'I I ! ! !'))

    def set_bricklet_power(self, bricklet_power):
        """
        Set to true/false to turn the power supply of the connected Bricklets on/off.

        By default the Bricklets are on.
        """
        bricklet_power = bool(bricklet_power)

        self.ipcon.send_request(self, BrickHAT.FUNCTION_SET_BRICKLET_POWER, (bricklet_power,), '!', '')

    def get_bricklet_power(self):
        """
        Returns the power status of the connected Bricklets as set by :func:`Set Bricklet Power`.
        """
        return self.ipcon.send_request(self, BrickHAT.FUNCTION_GET_BRICKLET_POWER, (), '', '!')

    def get_voltages(self):
        """
        Returns the USB supply voltage and the DC input supply voltage in mV.

        There are three possible combinations:

        * Only USB connected: The USB supply voltage will be fed back to the
          DC input connector. You will read the USB voltage and a slightly lower
          voltage on the DC input.
        * Only DC input connected: The DC voltage will not be fed back to the
          USB connector. You will read the DC input voltage and the USB voltage
          will be 0.
        * USB and DC input connected: You will read both voltages. In this case
          the USB supply will be without load, but it will work as backup if you
          disconnect the DC input (or if the DC input voltage falls below the
          USB voltage).
        """
        return GetVoltages(*self.ipcon.send_request(self, BrickHAT.FUNCTION_GET_VOLTAGES, (), '', 'H H'))

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
        return GetSPITFPErrorCount(*self.ipcon.send_request(self, BrickHAT.FUNCTION_GET_SPITFP_ERROR_COUNT, (), '', 'I I I I'))

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

        return self.ipcon.send_request(self, BrickHAT.FUNCTION_SET_BOOTLOADER_MODE, (mode,), 'B', 'B')

    def get_bootloader_mode(self):
        """
        Returns the current bootloader mode, see :func:`Set Bootloader Mode`.
        """
        return self.ipcon.send_request(self, BrickHAT.FUNCTION_GET_BOOTLOADER_MODE, (), '', 'B')

    def set_write_firmware_pointer(self, pointer):
        """
        Sets the firmware pointer for :func:`Write Firmware`. The pointer has
        to be increased by chunks of size 64. The data is written to flash
        every 4 chunks (which equals to one page of size 256).

        This function is used by Brick Viewer during flashing. It should not be
        necessary to call it in a normal user program.
        """
        pointer = int(pointer)

        self.ipcon.send_request(self, BrickHAT.FUNCTION_SET_WRITE_FIRMWARE_POINTER, (pointer,), 'I', '')

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

        return self.ipcon.send_request(self, BrickHAT.FUNCTION_WRITE_FIRMWARE, (data,), '64B', 'B')

    def set_status_led_config(self, config):
        """
        Sets the status LED configuration. By default the LED shows
        communication traffic between Brick and Bricklet, it flickers once
        for every 10 received data packets.

        You can also turn the LED permanently on/off or show a heartbeat.

        If the Bricklet is in bootloader mode, the LED is will show heartbeat by default.
        """
        config = int(config)

        self.ipcon.send_request(self, BrickHAT.FUNCTION_SET_STATUS_LED_CONFIG, (config,), 'B', '')

    def get_status_led_config(self):
        """
        Returns the configuration as set by :func:`Set Status LED Config`
        """
        return self.ipcon.send_request(self, BrickHAT.FUNCTION_GET_STATUS_LED_CONFIG, (), '', 'B')

    def get_chip_temperature(self):
        """
        Returns the temperature in °C as measured inside the microcontroller. The
        value returned is not the ambient temperature!

        The temperature is only proportional to the real temperature and it has bad
        accuracy. Practically it is only useful as an indicator for
        temperature changes.
        """
        return self.ipcon.send_request(self, BrickHAT.FUNCTION_GET_CHIP_TEMPERATURE, (), '', 'h')

    def reset(self):
        """
        Calling this function will reset the Bricklet. All configurations
        will be lost.

        After a reset you have to create new device objects,
        calling functions on the existing ones will result in
        undefined behavior!
        """
        self.ipcon.send_request(self, BrickHAT.FUNCTION_RESET, (), '', '')

    def write_uid(self, uid):
        """
        Writes a new UID into flash. If you want to set a new UID
        you have to decode the Base58 encoded UID string into an
        integer first.

        We recommend that you use Brick Viewer to change the UID.
        """
        uid = int(uid)

        self.ipcon.send_request(self, BrickHAT.FUNCTION_WRITE_UID, (uid,), 'I', '')

    def read_uid(self):
        """
        Returns the current UID as an integer. Encode as
        Base58 to get the usual string version.
        """
        return self.ipcon.send_request(self, BrickHAT.FUNCTION_READ_UID, (), '', 'I')

    def get_identity(self):
        """
        Returns the UID, the UID where the Bricklet is connected to,
        the position, the hardware and firmware version as well as the
        device identifier.

        The position can be 'a', 'b', 'c' or 'd'.

        The device identifier numbers can be found :ref:`here <device_identifier>`.
        |device_identifier_constant|
        """
        return GetIdentity(*self.ipcon.send_request(self, BrickHAT.FUNCTION_GET_IDENTITY, (), '', '8s 8s c 3B 3B H'))

HAT = BrickHAT # for backward compatibility
