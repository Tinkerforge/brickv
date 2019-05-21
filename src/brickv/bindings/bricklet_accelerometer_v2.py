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

GetAcceleration = namedtuple('Acceleration', ['x', 'y', 'z'])
GetConfiguration = namedtuple('Configuration', ['data_rate', 'full_scale'])
GetAccelerationCallbackConfiguration = namedtuple('AccelerationCallbackConfiguration', ['period', 'value_has_to_change'])
GetContinuousAccelerationConfiguration = namedtuple('ContinuousAccelerationConfiguration', ['enable_x', 'enable_y', 'enable_z', 'resolution'])
GetSPITFPErrorCount = namedtuple('SPITFPErrorCount', ['error_count_ack_checksum', 'error_count_message_checksum', 'error_count_frame', 'error_count_overflow'])
GetIdentity = namedtuple('Identity', ['uid', 'connected_uid', 'position', 'hardware_version', 'firmware_version', 'device_identifier'])

class BrickletAccelerometerV2(Device):
    """
    Measures acceleration in three axis
    """

    DEVICE_IDENTIFIER = 2130
    DEVICE_DISPLAY_NAME = 'Accelerometer Bricklet 2.0'
    DEVICE_URL_PART = 'accelerometer_v2' # internal

    CALLBACK_ACCELERATION = 8
    CALLBACK_CONTINUOUS_ACCELERATION_16_BIT = 11
    CALLBACK_CONTINUOUS_ACCELERATION_8_BIT = 12


    FUNCTION_GET_ACCELERATION = 1
    FUNCTION_SET_CONFIGURATION = 2
    FUNCTION_GET_CONFIGURATION = 3
    FUNCTION_SET_ACCELERATION_CALLBACK_CONFIGURATION = 4
    FUNCTION_GET_ACCELERATION_CALLBACK_CONFIGURATION = 5
    FUNCTION_SET_INFO_LED_CONFIG = 6
    FUNCTION_GET_INFO_LED_CONFIG = 7
    FUNCTION_SET_CONTINUOUS_ACCELERATION_CONFIGURATION = 9
    FUNCTION_GET_CONTINUOUS_ACCELERATION_CONFIGURATION = 10
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

    DATA_RATE_0_781HZ = 0
    DATA_RATE_1_563HZ = 1
    DATA_RATE_3_125HZ = 2
    DATA_RATE_6_2512HZ = 3
    DATA_RATE_12_5HZ = 4
    DATA_RATE_25HZ = 5
    DATA_RATE_50HZ = 6
    DATA_RATE_100HZ = 7
    DATA_RATE_200HZ = 8
    DATA_RATE_400HZ = 9
    DATA_RATE_800HZ = 10
    DATA_RATE_1600HZ = 11
    DATA_RATE_3200HZ = 12
    DATA_RATE_6400HZ = 13
    DATA_RATE_12800HZ = 14
    DATA_RATE_25600HZ = 15
    FULL_SCALE_2G = 0
    FULL_SCALE_4G = 1
    FULL_SCALE_8G = 2
    INFO_LED_CONFIG_OFF = 0
    INFO_LED_CONFIG_ON = 1
    INFO_LED_CONFIG_SHOW_HEARTBEAT = 2
    RESOLUTION_8BIT = 0
    RESOLUTION_16BIT = 1
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

        self.response_expected[BrickletAccelerometerV2.FUNCTION_GET_ACCELERATION] = BrickletAccelerometerV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletAccelerometerV2.FUNCTION_SET_CONFIGURATION] = BrickletAccelerometerV2.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletAccelerometerV2.FUNCTION_GET_CONFIGURATION] = BrickletAccelerometerV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletAccelerometerV2.FUNCTION_SET_ACCELERATION_CALLBACK_CONFIGURATION] = BrickletAccelerometerV2.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletAccelerometerV2.FUNCTION_GET_ACCELERATION_CALLBACK_CONFIGURATION] = BrickletAccelerometerV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletAccelerometerV2.FUNCTION_SET_INFO_LED_CONFIG] = BrickletAccelerometerV2.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletAccelerometerV2.FUNCTION_GET_INFO_LED_CONFIG] = BrickletAccelerometerV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletAccelerometerV2.FUNCTION_SET_CONTINUOUS_ACCELERATION_CONFIGURATION] = BrickletAccelerometerV2.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletAccelerometerV2.FUNCTION_GET_CONTINUOUS_ACCELERATION_CONFIGURATION] = BrickletAccelerometerV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletAccelerometerV2.FUNCTION_GET_SPITFP_ERROR_COUNT] = BrickletAccelerometerV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletAccelerometerV2.FUNCTION_SET_BOOTLOADER_MODE] = BrickletAccelerometerV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletAccelerometerV2.FUNCTION_GET_BOOTLOADER_MODE] = BrickletAccelerometerV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletAccelerometerV2.FUNCTION_SET_WRITE_FIRMWARE_POINTER] = BrickletAccelerometerV2.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletAccelerometerV2.FUNCTION_WRITE_FIRMWARE] = BrickletAccelerometerV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletAccelerometerV2.FUNCTION_SET_STATUS_LED_CONFIG] = BrickletAccelerometerV2.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletAccelerometerV2.FUNCTION_GET_STATUS_LED_CONFIG] = BrickletAccelerometerV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletAccelerometerV2.FUNCTION_GET_CHIP_TEMPERATURE] = BrickletAccelerometerV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletAccelerometerV2.FUNCTION_RESET] = BrickletAccelerometerV2.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletAccelerometerV2.FUNCTION_WRITE_UID] = BrickletAccelerometerV2.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletAccelerometerV2.FUNCTION_READ_UID] = BrickletAccelerometerV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletAccelerometerV2.FUNCTION_GET_IDENTITY] = BrickletAccelerometerV2.RESPONSE_EXPECTED_ALWAYS_TRUE

        self.callback_formats[BrickletAccelerometerV2.CALLBACK_ACCELERATION] = 'i i i'
        self.callback_formats[BrickletAccelerometerV2.CALLBACK_CONTINUOUS_ACCELERATION_16_BIT] = '30h'
        self.callback_formats[BrickletAccelerometerV2.CALLBACK_CONTINUOUS_ACCELERATION_8_BIT] = '60b'


    def get_acceleration(self):
        """
        Returns the acceleration in x, y and z direction. The values
        are given in g/10000 (1g = 9.80665m/s²), not to be confused with grams.

        If you want to get the acceleration periodically, it is recommended
        to use the :cb:`Acceleration` callback and set the period with
        :func:`Set Acceleration Callback Configuration`.
        """
        return GetAcceleration(*self.ipcon.send_request(self, BrickletAccelerometerV2.FUNCTION_GET_ACCELERATION, (), '', 'i i i'))

    def set_configuration(self, data_rate, full_scale):
        """
        Configures the data rate and full scale range.
        Possible values are:

        * Data rate of 0.781Hz to 25600Hz.
        * Full scale range of -2g to +2g up to -8g to +8g.

        Decreasing data rate or full scale range will also decrease the noise on
        the data.

        The default values are 100Hz data rate and -2g to +2g range.
        """
        data_rate = int(data_rate)
        full_scale = int(full_scale)

        self.ipcon.send_request(self, BrickletAccelerometerV2.FUNCTION_SET_CONFIGURATION, (data_rate, full_scale), 'B B', '')

    def get_configuration(self):
        """
        Returns the configuration as set by :func:`Set Configuration`.
        """
        return GetConfiguration(*self.ipcon.send_request(self, BrickletAccelerometerV2.FUNCTION_GET_CONFIGURATION, (), '', 'B B'))

    def set_acceleration_callback_configuration(self, period, value_has_to_change):
        """
        The period in ms is the period with which the :cb:`Acceleration`
        callback is triggered periodically. A value of 0 turns the callback off.

        If the `value has to change`-parameter is set to true, the callback is only
        triggered after the value has changed. If the value didn't change within the
        period, the callback is triggered immediately on change.

        If it is set to false, the callback is continuously triggered with the period,
        independent of the value.

        If this callback is enabled, the :cb:`Continuous Acceleration 16 Bit` callback
        and :cb:`Continuous Acceleration 8 Bit` callback will automatically be disabled.

        The default value is (0, false).
        """
        period = int(period)
        value_has_to_change = bool(value_has_to_change)

        self.ipcon.send_request(self, BrickletAccelerometerV2.FUNCTION_SET_ACCELERATION_CALLBACK_CONFIGURATION, (period, value_has_to_change), 'I !', '')

    def get_acceleration_callback_configuration(self):
        """
        Returns the callback configuration as set by
        :func:`Set Acceleration Callback Configuration`.
        """
        return GetAccelerationCallbackConfiguration(*self.ipcon.send_request(self, BrickletAccelerometerV2.FUNCTION_GET_ACCELERATION_CALLBACK_CONFIGURATION, (), '', 'I !'))

    def set_info_led_config(self, config):
        """
        Configures the info LED (marked as "Force" on the Bricklet) to be either turned off,
        turned on, or blink in heartbeat mode.
        """
        config = int(config)

        self.ipcon.send_request(self, BrickletAccelerometerV2.FUNCTION_SET_INFO_LED_CONFIG, (config,), 'B', '')

    def get_info_led_config(self):
        """
        Returns the LED configuration as set by :func:`Set Info LED Config`
        """
        return self.ipcon.send_request(self, BrickletAccelerometerV2.FUNCTION_GET_INFO_LED_CONFIG, (), '', 'B')

    def set_continuous_acceleration_configuration(self, enable_x, enable_y, enable_z, resolution):
        """
        For high throughput of acceleration data (> 1000Hz) you have to use the
        :cb:`Continuous Acceleration 16 Bit` or :cb:`Continuous Acceleration 8 Bit`
        callbacks.

        You can enable the callback for each axis (x, y, z) individually and choose a
        resolution of 8 bit or 16 bit.

        If at least one of the axis is enabled and the resolution is set to 8 bit,
        the :cb:`Continuous Acceleration 8 Bit` callback is activated. If at least
        one of the axis is enabled and the resolution is set to 16 bit,
        the :cb:`Continuous Acceleration 16 Bit` callback is activated.

        If a resolution of 8 bit is used, only the 8 most significant bits will be
        transferred. This means that the unit changes from g/10000 to g*256/10000.

        If no axis is enabled, both callbacks are disabled. If one of the continuous
        callbacks is enabled, the :cb:`Acceleration` callback is disabled.

        The maximum throughput depends on the exact configuration:

        .. csv-table::
         :header: "Number of axis enabled", "Throughput 8 bit", "Throughout 16 bit"
         :widths: 20, 20, 20

         "1", "25600Hz", "25600Hz"
         "2", "25600Hz", "15000Hz"
         "3", "20000Hz", "10000Hz"
        """
        enable_x = bool(enable_x)
        enable_y = bool(enable_y)
        enable_z = bool(enable_z)
        resolution = int(resolution)

        self.ipcon.send_request(self, BrickletAccelerometerV2.FUNCTION_SET_CONTINUOUS_ACCELERATION_CONFIGURATION, (enable_x, enable_y, enable_z, resolution), '! ! ! B', '')

    def get_continuous_acceleration_configuration(self):
        """
        Returns the continuous acceleration configuration as set by
        :func:`Set Continuous Acceleration Configuration`.
        """
        return GetContinuousAccelerationConfiguration(*self.ipcon.send_request(self, BrickletAccelerometerV2.FUNCTION_GET_CONTINUOUS_ACCELERATION_CONFIGURATION, (), '', '! ! ! B'))

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
        return GetSPITFPErrorCount(*self.ipcon.send_request(self, BrickletAccelerometerV2.FUNCTION_GET_SPITFP_ERROR_COUNT, (), '', 'I I I I'))

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

        return self.ipcon.send_request(self, BrickletAccelerometerV2.FUNCTION_SET_BOOTLOADER_MODE, (mode,), 'B', 'B')

    def get_bootloader_mode(self):
        """
        Returns the current bootloader mode, see :func:`Set Bootloader Mode`.
        """
        return self.ipcon.send_request(self, BrickletAccelerometerV2.FUNCTION_GET_BOOTLOADER_MODE, (), '', 'B')

    def set_write_firmware_pointer(self, pointer):
        """
        Sets the firmware pointer for :func:`Write Firmware`. The pointer has
        to be increased by chunks of size 64. The data is written to flash
        every 4 chunks (which equals to one page of size 256).

        This function is used by Brick Viewer during flashing. It should not be
        necessary to call it in a normal user program.
        """
        pointer = int(pointer)

        self.ipcon.send_request(self, BrickletAccelerometerV2.FUNCTION_SET_WRITE_FIRMWARE_POINTER, (pointer,), 'I', '')

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

        return self.ipcon.send_request(self, BrickletAccelerometerV2.FUNCTION_WRITE_FIRMWARE, (data,), '64B', 'B')

    def set_status_led_config(self, config):
        """
        Sets the status LED configuration. By default the LED shows
        communication traffic between Brick and Bricklet, it flickers once
        for every 10 received data packets.

        You can also turn the LED permanently on/off or show a heartbeat.

        If the Bricklet is in bootloader mode, the LED is will show heartbeat by default.
        """
        config = int(config)

        self.ipcon.send_request(self, BrickletAccelerometerV2.FUNCTION_SET_STATUS_LED_CONFIG, (config,), 'B', '')

    def get_status_led_config(self):
        """
        Returns the configuration as set by :func:`Set Status LED Config`
        """
        return self.ipcon.send_request(self, BrickletAccelerometerV2.FUNCTION_GET_STATUS_LED_CONFIG, (), '', 'B')

    def get_chip_temperature(self):
        """
        Returns the temperature in °C as measured inside the microcontroller. The
        value returned is not the ambient temperature!

        The temperature is only proportional to the real temperature and it has bad
        accuracy. Practically it is only useful as an indicator for
        temperature changes.
        """
        return self.ipcon.send_request(self, BrickletAccelerometerV2.FUNCTION_GET_CHIP_TEMPERATURE, (), '', 'h')

    def reset(self):
        """
        Calling this function will reset the Bricklet. All configurations
        will be lost.

        After a reset you have to create new device objects,
        calling functions on the existing ones will result in
        undefined behavior!
        """
        self.ipcon.send_request(self, BrickletAccelerometerV2.FUNCTION_RESET, (), '', '')

    def write_uid(self, uid):
        """
        Writes a new UID into flash. If you want to set a new UID
        you have to decode the Base58 encoded UID string into an
        integer first.

        We recommend that you use Brick Viewer to change the UID.
        """
        uid = int(uid)

        self.ipcon.send_request(self, BrickletAccelerometerV2.FUNCTION_WRITE_UID, (uid,), 'I', '')

    def read_uid(self):
        """
        Returns the current UID as an integer. Encode as
        Base58 to get the usual string version.
        """
        return self.ipcon.send_request(self, BrickletAccelerometerV2.FUNCTION_READ_UID, (), '', 'I')

    def get_identity(self):
        """
        Returns the UID, the UID where the Bricklet is connected to,
        the position, the hardware and firmware version as well as the
        device identifier.

        The position can be 'a', 'b', 'c' or 'd'.

        The device identifier numbers can be found :ref:`here <device_identifier>`.
        |device_identifier_constant|
        """
        return GetIdentity(*self.ipcon.send_request(self, BrickletAccelerometerV2.FUNCTION_GET_IDENTITY, (), '', '8s 8s c 3B 3B H'))

    def register_callback(self, callback_id, function):
        """
        Registers the given *function* with the given *callback_id*.
        """
        if function is None:
            self.registered_callbacks.pop(callback_id, None)
        else:
            self.registered_callbacks[callback_id] = function

AccelerometerV2 = BrickletAccelerometerV2 # for backward compatibility
