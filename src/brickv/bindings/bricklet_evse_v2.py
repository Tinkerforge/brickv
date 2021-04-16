# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2021-04-15.      #
#                                                           #
# Python Bindings Version 2.1.28                            #
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

GetState = namedtuple('State', ['iec61851_state', 'vehicle_state', 'contactor_state', 'contactor_error', 'charge_release', 'allowed_charging_current', 'error_state', 'lock_state', 'time_since_state_change', 'uptime'])
GetHardwareConfiguration = namedtuple('HardwareConfiguration', ['jumper_configuration', 'has_lock_switch'])
GetLowLevelState = namedtuple('LowLevelState', ['led_state', 'cp_pwm_duty_cycle', 'adc_values', 'voltages', 'resistances', 'gpio'])
GetMaxChargingCurrent = namedtuple('MaxChargingCurrent', ['max_current_configured', 'max_current_incoming_cable', 'max_current_outgoing_cable'])
GetEnergyMeterValues = namedtuple('EnergyMeterValues', ['power', 'energy_relative', 'energy_absolute'])
GetEnergyMeterState = namedtuple('EnergyMeterState', ['available', 'error_count'])
GetGPIOConfiguration = namedtuple('GPIOConfiguration', ['input_configuration', 'output_configuration'])
GetSPITFPErrorCount = namedtuple('SPITFPErrorCount', ['error_count_ack_checksum', 'error_count_message_checksum', 'error_count_frame', 'error_count_overflow'])
GetIdentity = namedtuple('Identity', ['uid', 'connected_uid', 'position', 'hardware_version', 'firmware_version', 'device_identifier'])

class BrickletEVSEV2(Device):
    """
    TBD
    """

    DEVICE_IDENTIFIER = 2167
    DEVICE_DISPLAY_NAME = 'EVSE Bricklet 2.0'
    DEVICE_URL_PART = 'evse_v2' # internal



    FUNCTION_GET_STATE = 1
    FUNCTION_GET_HARDWARE_CONFIGURATION = 2
    FUNCTION_GET_LOW_LEVEL_STATE = 3
    FUNCTION_SET_MAX_CHARGING_CURRENT = 4
    FUNCTION_GET_MAX_CHARGING_CURRENT = 5
    FUNCTION_START_CHARGING = 6
    FUNCTION_STOP_CHARGING = 7
    FUNCTION_SET_CHARGING_AUTOSTART = 8
    FUNCTION_GET_CHARGING_AUTOSTART = 9
    FUNCTION_GET_ENERGY_METER_VALUES = 10
    FUNCTION_GET_ENERGY_METER_STATE = 11
    FUNCTION_RESET_ENERGY_METER = 12
    FUNCTION_GET_DC_FAULT_CURRENT_STATE = 13
    FUNCTION_RESET_DC_FAULT_CURRENT = 14
    FUNCTION_SET_GPIO_CONFIGURATION = 15
    FUNCTION_GET_GPIO_CONFIGURATION = 16
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

    IEC61851_STATE_A = 0
    IEC61851_STATE_B = 1
    IEC61851_STATE_C = 2
    IEC61851_STATE_D = 3
    IEC61851_STATE_EF = 4
    LED_STATE_OFF = 0
    LED_STATE_ON = 1
    LED_STATE_BLINKING = 2
    LED_STATE_FLICKER = 3
    LED_STATE_BREATHING = 4
    VEHICLE_STATE_NOT_CONNECTED = 0
    VEHICLE_STATE_CONNECTED = 1
    VEHICLE_STATE_CHARGING = 2
    VEHICLE_STATE_ERROR = 3
    CONTACTOR_STATE_AC1_NLIVE_AC2_NLIVE = 0
    CONTACTOR_STATE_AC1_LIVE_AC2_NLIVE = 1
    CONTACTOR_STATE_AC1_NLIVE_AC2_LIVE = 2
    CONTACTOR_STATE_AC1_LIVE_AC2_LIVE = 3
    LOCK_STATE_INIT = 0
    LOCK_STATE_OPEN = 1
    LOCK_STATE_CLOSING = 2
    LOCK_STATE_CLOSE = 3
    LOCK_STATE_OPENING = 4
    LOCK_STATE_ERROR = 5
    ERROR_STATE_OK = 0
    ERROR_STATE_SWITCH = 2
    ERROR_STATE_CALIBRATION = 3
    ERROR_STATE_CONTACTOR = 4
    ERROR_STATE_COMMUNICATION = 5
    JUMPER_CONFIGURATION_6A = 0
    JUMPER_CONFIGURATION_10A = 1
    JUMPER_CONFIGURATION_13A = 2
    JUMPER_CONFIGURATION_16A = 3
    JUMPER_CONFIGURATION_20A = 4
    JUMPER_CONFIGURATION_25A = 5
    JUMPER_CONFIGURATION_32A = 6
    JUMPER_CONFIGURATION_SOFTWARE = 7
    JUMPER_CONFIGURATION_UNCONFIGURED = 8
    CHARGE_RELEASE_AUTOMATIC = 0
    CHARGE_RELEASE_MANUAL = 1
    CHARGE_RELEASE_DEACTIVATED = 2
    DC_FAULT_CURRENT_STATE_NORMAL_CONDITION = 0
    DC_FAULT_CURRENT_STATE_6_MA = 1
    DC_FAULT_CURRENT_STATE_SYSTEM = 2
    DC_FAULT_CURRENT_STATE_UNKNOWN = 3
    DC_FAULT_CURRENT_STATE_CALIBRATION = 4
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
        Device.__init__(self, uid, ipcon, BrickletEVSEV2.DEVICE_IDENTIFIER, BrickletEVSEV2.DEVICE_DISPLAY_NAME)

        self.api_version = (2, 0, 0)

        self.response_expected[BrickletEVSEV2.FUNCTION_GET_STATE] = BrickletEVSEV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletEVSEV2.FUNCTION_GET_HARDWARE_CONFIGURATION] = BrickletEVSEV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletEVSEV2.FUNCTION_GET_LOW_LEVEL_STATE] = BrickletEVSEV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletEVSEV2.FUNCTION_SET_MAX_CHARGING_CURRENT] = BrickletEVSEV2.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletEVSEV2.FUNCTION_GET_MAX_CHARGING_CURRENT] = BrickletEVSEV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletEVSEV2.FUNCTION_START_CHARGING] = BrickletEVSEV2.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletEVSEV2.FUNCTION_STOP_CHARGING] = BrickletEVSEV2.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletEVSEV2.FUNCTION_SET_CHARGING_AUTOSTART] = BrickletEVSEV2.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletEVSEV2.FUNCTION_GET_CHARGING_AUTOSTART] = BrickletEVSEV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletEVSEV2.FUNCTION_GET_ENERGY_METER_VALUES] = BrickletEVSEV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletEVSEV2.FUNCTION_GET_ENERGY_METER_STATE] = BrickletEVSEV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletEVSEV2.FUNCTION_RESET_ENERGY_METER] = BrickletEVSEV2.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletEVSEV2.FUNCTION_GET_DC_FAULT_CURRENT_STATE] = BrickletEVSEV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletEVSEV2.FUNCTION_RESET_DC_FAULT_CURRENT] = BrickletEVSEV2.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletEVSEV2.FUNCTION_SET_GPIO_CONFIGURATION] = BrickletEVSEV2.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletEVSEV2.FUNCTION_GET_GPIO_CONFIGURATION] = BrickletEVSEV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletEVSEV2.FUNCTION_GET_SPITFP_ERROR_COUNT] = BrickletEVSEV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletEVSEV2.FUNCTION_SET_BOOTLOADER_MODE] = BrickletEVSEV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletEVSEV2.FUNCTION_GET_BOOTLOADER_MODE] = BrickletEVSEV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletEVSEV2.FUNCTION_SET_WRITE_FIRMWARE_POINTER] = BrickletEVSEV2.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletEVSEV2.FUNCTION_WRITE_FIRMWARE] = BrickletEVSEV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletEVSEV2.FUNCTION_SET_STATUS_LED_CONFIG] = BrickletEVSEV2.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletEVSEV2.FUNCTION_GET_STATUS_LED_CONFIG] = BrickletEVSEV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletEVSEV2.FUNCTION_GET_CHIP_TEMPERATURE] = BrickletEVSEV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletEVSEV2.FUNCTION_RESET] = BrickletEVSEV2.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletEVSEV2.FUNCTION_WRITE_UID] = BrickletEVSEV2.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletEVSEV2.FUNCTION_READ_UID] = BrickletEVSEV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletEVSEV2.FUNCTION_GET_IDENTITY] = BrickletEVSEV2.RESPONSE_EXPECTED_ALWAYS_TRUE


        ipcon.add_device(self)

    def get_state(self):
        """
        TODO
        """
        self.check_validity()

        return GetState(*self.ipcon.send_request(self, BrickletEVSEV2.FUNCTION_GET_STATE, (), '', 25, 'B B B B B H B B I I'))

    def get_hardware_configuration(self):
        """
        TODO
        """
        self.check_validity()

        return GetHardwareConfiguration(*self.ipcon.send_request(self, BrickletEVSEV2.FUNCTION_GET_HARDWARE_CONFIGURATION, (), '', 10, 'B !'))

    def get_low_level_state(self):
        """
        TODO
        """
        self.check_validity()

        return GetLowLevelState(*self.ipcon.send_request(self, BrickletEVSEV2.FUNCTION_GET_LOW_LEVEL_STATE, (), '', 42, 'B H 5H 5h 2I 24!'))

    def set_max_charging_current(self, max_current):
        """
        TODO
        """
        self.check_validity()

        max_current = int(max_current)

        self.ipcon.send_request(self, BrickletEVSEV2.FUNCTION_SET_MAX_CHARGING_CURRENT, (max_current,), 'H', 0, '')

    def get_max_charging_current(self):
        """
        * Max Current Configured -> set with :func:`Set Max Charging Current`
        * Max Current Incoming Cable -> set with jumper on EVSE
        * Max Current Outgoing Cable -> set with resistor between PP/PE (if fixed cable is used)

        TODO
        """
        self.check_validity()

        return GetMaxChargingCurrent(*self.ipcon.send_request(self, BrickletEVSEV2.FUNCTION_GET_MAX_CHARGING_CURRENT, (), '', 14, 'H H H'))

    def start_charging(self):
        """
        TODO
        """
        self.check_validity()

        self.ipcon.send_request(self, BrickletEVSEV2.FUNCTION_START_CHARGING, (), '', 0, '')

    def stop_charging(self):
        """
        TODO
        """
        self.check_validity()

        self.ipcon.send_request(self, BrickletEVSEV2.FUNCTION_STOP_CHARGING, (), '', 0, '')

    def set_charging_autostart(self, autostart):
        """
        TODO
        """
        self.check_validity()

        autostart = bool(autostart)

        self.ipcon.send_request(self, BrickletEVSEV2.FUNCTION_SET_CHARGING_AUTOSTART, (autostart,), '!', 0, '')

    def get_charging_autostart(self):
        """
        TODO
        """
        self.check_validity()

        return self.ipcon.send_request(self, BrickletEVSEV2.FUNCTION_GET_CHARGING_AUTOSTART, (), '', 9, '!')

    def get_energy_meter_values(self):
        """
        TODO
        """
        self.check_validity()

        return GetEnergyMeterValues(*self.ipcon.send_request(self, BrickletEVSEV2.FUNCTION_GET_ENERGY_METER_VALUES, (), '', 20, 'I I I'))

    def get_energy_meter_state(self):
        """
        TODO
        """
        self.check_validity()

        return GetEnergyMeterState(*self.ipcon.send_request(self, BrickletEVSEV2.FUNCTION_GET_ENERGY_METER_STATE, (), '', 33, '! 6I'))

    def reset_energy_meter(self):
        """
        TODO
        """
        self.check_validity()

        self.ipcon.send_request(self, BrickletEVSEV2.FUNCTION_RESET_ENERGY_METER, (), '', 0, '')

    def get_dc_fault_current_state(self):
        """
        TODO
        """
        self.check_validity()

        return self.ipcon.send_request(self, BrickletEVSEV2.FUNCTION_GET_DC_FAULT_CURRENT_STATE, (), '', 9, 'B')

    def reset_dc_fault_current(self, password):
        """
        TODO
        """
        self.check_validity()

        password = int(password)

        self.ipcon.send_request(self, BrickletEVSEV2.FUNCTION_RESET_DC_FAULT_CURRENT, (password,), 'I', 0, '')

    def set_gpio_configuration(self, input_configuration, output_configuration):
        """
        TODO
        """
        self.check_validity()

        input_configuration = int(input_configuration)
        output_configuration = int(output_configuration)

        self.ipcon.send_request(self, BrickletEVSEV2.FUNCTION_SET_GPIO_CONFIGURATION, (input_configuration, output_configuration), 'B B', 0, '')

    def get_gpio_configuration(self):
        """
        TODO
        """
        self.check_validity()

        return GetGPIOConfiguration(*self.ipcon.send_request(self, BrickletEVSEV2.FUNCTION_GET_GPIO_CONFIGURATION, (), '', 10, 'B B'))

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
        self.check_validity()

        return GetSPITFPErrorCount(*self.ipcon.send_request(self, BrickletEVSEV2.FUNCTION_GET_SPITFP_ERROR_COUNT, (), '', 24, 'I I I I'))

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
        self.check_validity()

        mode = int(mode)

        return self.ipcon.send_request(self, BrickletEVSEV2.FUNCTION_SET_BOOTLOADER_MODE, (mode,), 'B', 9, 'B')

    def get_bootloader_mode(self):
        """
        Returns the current bootloader mode, see :func:`Set Bootloader Mode`.
        """
        self.check_validity()

        return self.ipcon.send_request(self, BrickletEVSEV2.FUNCTION_GET_BOOTLOADER_MODE, (), '', 9, 'B')

    def set_write_firmware_pointer(self, pointer):
        """
        Sets the firmware pointer for :func:`Write Firmware`. The pointer has
        to be increased by chunks of size 64. The data is written to flash
        every 4 chunks (which equals to one page of size 256).

        This function is used by Brick Viewer during flashing. It should not be
        necessary to call it in a normal user program.
        """
        self.check_validity()

        pointer = int(pointer)

        self.ipcon.send_request(self, BrickletEVSEV2.FUNCTION_SET_WRITE_FIRMWARE_POINTER, (pointer,), 'I', 0, '')

    def write_firmware(self, data):
        """
        Writes 64 Bytes of firmware at the position as written by
        :func:`Set Write Firmware Pointer` before. The firmware is written
        to flash every 4 chunks.

        You can only write firmware in bootloader mode.

        This function is used by Brick Viewer during flashing. It should not be
        necessary to call it in a normal user program.
        """
        self.check_validity()

        data = list(map(int, data))

        return self.ipcon.send_request(self, BrickletEVSEV2.FUNCTION_WRITE_FIRMWARE, (data,), '64B', 9, 'B')

    def set_status_led_config(self, config):
        """
        Sets the status LED configuration. By default the LED shows
        communication traffic between Brick and Bricklet, it flickers once
        for every 10 received data packets.

        You can also turn the LED permanently on/off or show a heartbeat.

        If the Bricklet is in bootloader mode, the LED is will show heartbeat by default.
        """
        self.check_validity()

        config = int(config)

        self.ipcon.send_request(self, BrickletEVSEV2.FUNCTION_SET_STATUS_LED_CONFIG, (config,), 'B', 0, '')

    def get_status_led_config(self):
        """
        Returns the configuration as set by :func:`Set Status LED Config`
        """
        self.check_validity()

        return self.ipcon.send_request(self, BrickletEVSEV2.FUNCTION_GET_STATUS_LED_CONFIG, (), '', 9, 'B')

    def get_chip_temperature(self):
        """
        Returns the temperature as measured inside the microcontroller. The
        value returned is not the ambient temperature!

        The temperature is only proportional to the real temperature and it has bad
        accuracy. Practically it is only useful as an indicator for
        temperature changes.
        """
        self.check_validity()

        return self.ipcon.send_request(self, BrickletEVSEV2.FUNCTION_GET_CHIP_TEMPERATURE, (), '', 10, 'h')

    def reset(self):
        """
        Calling this function will reset the Bricklet. All configurations
        will be lost.

        After a reset you have to create new device objects,
        calling functions on the existing ones will result in
        undefined behavior!
        """
        self.check_validity()

        self.ipcon.send_request(self, BrickletEVSEV2.FUNCTION_RESET, (), '', 0, '')

    def write_uid(self, uid):
        """
        Writes a new UID into flash. If you want to set a new UID
        you have to decode the Base58 encoded UID string into an
        integer first.

        We recommend that you use Brick Viewer to change the UID.
        """
        self.check_validity()

        uid = int(uid)

        self.ipcon.send_request(self, BrickletEVSEV2.FUNCTION_WRITE_UID, (uid,), 'I', 0, '')

    def read_uid(self):
        """
        Returns the current UID as an integer. Encode as
        Base58 to get the usual string version.
        """
        self.check_validity()

        return self.ipcon.send_request(self, BrickletEVSEV2.FUNCTION_READ_UID, (), '', 12, 'I')

    def get_identity(self):
        """
        Returns the UID, the UID where the Bricklet is connected to,
        the position, the hardware and firmware version as well as the
        device identifier.

        The position can be 'a', 'b', 'c', 'd', 'e', 'f', 'g' or 'h' (Bricklet Port).
        A Bricklet connected to an :ref:`Isolator Bricklet <isolator_bricklet>` is always at
        position 'z'.

        The device identifier numbers can be found :ref:`here <device_identifier>`.
        |device_identifier_constant|
        """
        return GetIdentity(*self.ipcon.send_request(self, BrickletEVSEV2.FUNCTION_GET_IDENTITY, (), '', 33, '8s 8s c 3B 3B H'))

EVSEV2 = BrickletEVSEV2 # for backward compatibility
