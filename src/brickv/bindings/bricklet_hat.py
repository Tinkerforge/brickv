# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2019-01-29.      #
#                                                           #
# Python Bindings Version 2.1.21                            #
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

GetBatteryStatistics = namedtuple('BatteryStatistics', ['battery_connected', 'capacity_full', 'capacity_nominal', 'capacity_remaining', 'percentage_charge', 'voltage_battery', 'voltage_usb', 'voltage_dc', 'current_flow', 'temperature_battery'])
GetPowerOff = namedtuple('PowerOff', ['power_off_delay', 'power_off_duration', 'raspberry_pi_off', 'bricklets_off', 'enable_sleep_indicator'])
GetTime = namedtuple('Time', ['year', 'month', 'day', 'hour', 'minute', 'second', 'weekday'])
GetBatteryParameters = namedtuple('BatteryParameters', ['nominal_capacity', 'charge_termination_current', 'empty_voltage', 'learned_parameters'])
GetSPITFPErrorCount = namedtuple('SPITFPErrorCount', ['error_count_ack_checksum', 'error_count_message_checksum', 'error_count_frame', 'error_count_overflow'])
GetIdentity = namedtuple('Identity', ['uid', 'connected_uid', 'position', 'hardware_version', 'firmware_version', 'device_identifier'])

class BrickletHAT(Device):
    """

    """

    DEVICE_IDENTIFIER = 2126
    DEVICE_DISPLAY_NAME = 'HAT Bricklet'
    DEVICE_URL_PART = 'hat' # internal



    FUNCTION_GET_BATTERY_STATISTICS = 1
    FUNCTION_SET_POWER_OFF = 2
    FUNCTION_GET_POWER_OFF = 3
    FUNCTION_SET_TIME = 4
    FUNCTION_GET_TIME = 5
    FUNCTION_SET_BATTERY_PARAMETERS = 6
    FUNCTION_GET_BATTERY_PARAMETERS = 7
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

    WEEKDAY_MONDAY = 1
    WEEKDAY_TUESDAY = 2
    WEEKDAY_WEDNESDAY = 3
    WEEKDAY_THURSDAY = 4
    WEEKDAY_FRIDAY = 5
    WEEKDAY_SATURDAY = 6
    WEEKDAY_SUNDAY = 7
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

        self.response_expected[BrickletHAT.FUNCTION_GET_BATTERY_STATISTICS] = BrickletHAT.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletHAT.FUNCTION_SET_POWER_OFF] = BrickletHAT.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletHAT.FUNCTION_GET_POWER_OFF] = BrickletHAT.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletHAT.FUNCTION_SET_TIME] = BrickletHAT.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletHAT.FUNCTION_GET_TIME] = BrickletHAT.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletHAT.FUNCTION_SET_BATTERY_PARAMETERS] = BrickletHAT.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletHAT.FUNCTION_GET_BATTERY_PARAMETERS] = BrickletHAT.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletHAT.FUNCTION_GET_SPITFP_ERROR_COUNT] = BrickletHAT.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletHAT.FUNCTION_SET_BOOTLOADER_MODE] = BrickletHAT.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletHAT.FUNCTION_GET_BOOTLOADER_MODE] = BrickletHAT.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletHAT.FUNCTION_SET_WRITE_FIRMWARE_POINTER] = BrickletHAT.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletHAT.FUNCTION_WRITE_FIRMWARE] = BrickletHAT.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletHAT.FUNCTION_SET_STATUS_LED_CONFIG] = BrickletHAT.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletHAT.FUNCTION_GET_STATUS_LED_CONFIG] = BrickletHAT.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletHAT.FUNCTION_GET_CHIP_TEMPERATURE] = BrickletHAT.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletHAT.FUNCTION_RESET] = BrickletHAT.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletHAT.FUNCTION_WRITE_UID] = BrickletHAT.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletHAT.FUNCTION_READ_UID] = BrickletHAT.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletHAT.FUNCTION_GET_IDENTITY] = BrickletHAT.RESPONSE_EXPECTED_ALWAYS_TRUE



    def get_battery_statistics(self):
        """

        """
        return GetBatteryStatistics(*self.ipcon.send_request(self, BrickletHAT.FUNCTION_GET_BATTERY_STATISTICS, (), '', '! i i i i i i i i i'))

    def set_power_off(self, power_off_delay, power_off_duration, raspberry_pi_off, bricklets_off, enable_sleep_indicator):
        """
        Enable Sleep Indicator => status led blinks in 1s interval => ~0.3mA
        """
        power_off_delay = int(power_off_delay)
        power_off_duration = int(power_off_duration)
        raspberry_pi_off = bool(raspberry_pi_off)
        bricklets_off = bool(bricklets_off)
        enable_sleep_indicator = bool(enable_sleep_indicator)

        self.ipcon.send_request(self, BrickletHAT.FUNCTION_SET_POWER_OFF, (power_off_delay, power_off_duration, raspberry_pi_off, bricklets_off, enable_sleep_indicator), 'I I ! ! !', '')

    def get_power_off(self):
        """

        """
        return GetPowerOff(*self.ipcon.send_request(self, BrickletHAT.FUNCTION_GET_POWER_OFF, (), '', 'I I ! ! !'))

    def set_time(self, year, month, day, hour, minute, second, weekday):
        """

        """
        year = int(year)
        month = int(month)
        day = int(day)
        hour = int(hour)
        minute = int(minute)
        second = int(second)
        weekday = int(weekday)

        self.ipcon.send_request(self, BrickletHAT.FUNCTION_SET_TIME, (year, month, day, hour, minute, second, weekday), 'H B B B B B B', '')

    def get_time(self):
        """

        """
        return GetTime(*self.ipcon.send_request(self, BrickletHAT.FUNCTION_GET_TIME, (), '', 'H B B B B B B'))

    def set_battery_parameters(self, nominal_capacity, charge_termination_current, empty_voltage, learned_parameters):
        """

        """
        nominal_capacity = int(nominal_capacity)
        charge_termination_current = int(charge_termination_current)
        empty_voltage = int(empty_voltage)
        learned_parameters = list(map(int, learned_parameters))

        self.ipcon.send_request(self, BrickletHAT.FUNCTION_SET_BATTERY_PARAMETERS, (nominal_capacity, charge_termination_current, empty_voltage, learned_parameters), 'H H H 5H', '')

    def get_battery_parameters(self):
        """

        """
        return GetBatteryParameters(*self.ipcon.send_request(self, BrickletHAT.FUNCTION_GET_BATTERY_PARAMETERS, (), '', 'H H H 5H'))

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
        return GetSPITFPErrorCount(*self.ipcon.send_request(self, BrickletHAT.FUNCTION_GET_SPITFP_ERROR_COUNT, (), '', 'I I I I'))

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

        return self.ipcon.send_request(self, BrickletHAT.FUNCTION_SET_BOOTLOADER_MODE, (mode,), 'B', 'B')

    def get_bootloader_mode(self):
        """
        Returns the current bootloader mode, see :func:`Set Bootloader Mode`.
        """
        return self.ipcon.send_request(self, BrickletHAT.FUNCTION_GET_BOOTLOADER_MODE, (), '', 'B')

    def set_write_firmware_pointer(self, pointer):
        """
        Sets the firmware pointer for :func:`Write Firmware`. The pointer has
        to be increased by chunks of size 64. The data is written to flash
        every 4 chunks (which equals to one page of size 256).

        This function is used by Brick Viewer during flashing. It should not be
        necessary to call it in a normal user program.
        """
        pointer = int(pointer)

        self.ipcon.send_request(self, BrickletHAT.FUNCTION_SET_WRITE_FIRMWARE_POINTER, (pointer,), 'I', '')

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

        return self.ipcon.send_request(self, BrickletHAT.FUNCTION_WRITE_FIRMWARE, (data,), '64B', 'B')

    def set_status_led_config(self, config):
        """
        Sets the status LED configuration. By default the LED shows
        communication traffic between Brick and Bricklet, it flickers once
        for every 10 received data packets.

        You can also turn the LED permanently on/off or show a heartbeat.

        If the Bricklet is in bootloader mode, the LED is will show heartbeat by default.
        """
        config = int(config)

        self.ipcon.send_request(self, BrickletHAT.FUNCTION_SET_STATUS_LED_CONFIG, (config,), 'B', '')

    def get_status_led_config(self):
        """
        Returns the configuration as set by :func:`Set Status LED Config`
        """
        return self.ipcon.send_request(self, BrickletHAT.FUNCTION_GET_STATUS_LED_CONFIG, (), '', 'B')

    def get_chip_temperature(self):
        """
        Returns the temperature in °C as measured inside the microcontroller. The
        value returned is not the ambient temperature!

        The temperature is only proportional to the real temperature and it has bad
        accuracy. Practically it is only useful as an indicator for
        temperature changes.
        """
        return self.ipcon.send_request(self, BrickletHAT.FUNCTION_GET_CHIP_TEMPERATURE, (), '', 'h')

    def reset(self):
        """
        Calling this function will reset the Bricklet. All configurations
        will be lost.

        After a reset you have to create new device objects,
        calling functions on the existing ones will result in
        undefined behavior!
        """
        self.ipcon.send_request(self, BrickletHAT.FUNCTION_RESET, (), '', '')

    def write_uid(self, uid):
        """
        Writes a new UID into flash. If you want to set a new UID
        you have to decode the Base58 encoded UID string into an
        integer first.

        We recommend that you use Brick Viewer to change the UID.
        """
        uid = int(uid)

        self.ipcon.send_request(self, BrickletHAT.FUNCTION_WRITE_UID, (uid,), 'I', '')

    def read_uid(self):
        """
        Returns the current UID as an integer. Encode as
        Base58 to get the usual string version.
        """
        return self.ipcon.send_request(self, BrickletHAT.FUNCTION_READ_UID, (), '', 'I')

    def get_identity(self):
        """
        Returns the UID, the UID where the Bricklet is connected to,
        the position, the hardware and firmware version as well as the
        device identifier.

        The position can be 'a', 'b', 'c' or 'd'.

        The device identifier numbers can be found :ref:`here <device_identifier>`.
        |device_identifier_constant|
        """
        return GetIdentity(*self.ipcon.send_request(self, BrickletHAT.FUNCTION_GET_IDENTITY, (), '', '8s 8s c 3B 3B H'))

HAT = BrickletHAT # for backward compatibility
