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

GetTemperatureCallbackConfiguration = namedtuple('TemperatureCallbackConfiguration', ['period', 'value_has_to_change', 'option', 'min', 'max'])
GetResistanceCallbackConfiguration = namedtuple('ResistanceCallbackConfiguration', ['period', 'value_has_to_change', 'option', 'min', 'max'])
GetMovingAverageConfiguration = namedtuple('MovingAverageConfiguration', ['moving_average_length_resistance', 'moving_average_length_temperature'])
GetSPITFPErrorCount = namedtuple('SPITFPErrorCount', ['error_count_ack_checksum', 'error_count_message_checksum', 'error_count_frame', 'error_count_overflow'])
GetIdentity = namedtuple('Identity', ['uid', 'connected_uid', 'position', 'hardware_version', 'firmware_version', 'device_identifier'])

class BrickletPTCV2(Device):
    """
    Reads temperatures from Pt100 und Pt1000 sensors
    """

    DEVICE_IDENTIFIER = 2101
    DEVICE_DISPLAY_NAME = 'PTC Bricklet 2.0'
    DEVICE_URL_PART = 'ptc_v2' # internal

    CALLBACK_TEMPERATURE = 4
    CALLBACK_RESISTANCE = 8
    CALLBACK_SENSOR_CONNECTED = 18


    FUNCTION_GET_TEMPERATURE = 1
    FUNCTION_SET_TEMPERATURE_CALLBACK_CONFIGURATION = 2
    FUNCTION_GET_TEMPERATURE_CALLBACK_CONFIGURATION = 3
    FUNCTION_GET_RESISTANCE = 5
    FUNCTION_SET_RESISTANCE_CALLBACK_CONFIGURATION = 6
    FUNCTION_GET_RESISTANCE_CALLBACK_CONFIGURATION = 7
    FUNCTION_SET_NOISE_REJECTION_FILTER = 9
    FUNCTION_GET_NOISE_REJECTION_FILTER = 10
    FUNCTION_IS_SENSOR_CONNECTED = 11
    FUNCTION_SET_WIRE_MODE = 12
    FUNCTION_GET_WIRE_MODE = 13
    FUNCTION_SET_MOVING_AVERAGE_CONFIGURATION = 14
    FUNCTION_GET_MOVING_AVERAGE_CONFIGURATION = 15
    FUNCTION_SET_SENSOR_CONNECTED_CALLBACK_CONFIGURATION = 16
    FUNCTION_GET_SENSOR_CONNECTED_CALLBACK_CONFIGURATION = 17
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

    THRESHOLD_OPTION_OFF = 'x'
    THRESHOLD_OPTION_OUTSIDE = 'o'
    THRESHOLD_OPTION_INSIDE = 'i'
    THRESHOLD_OPTION_SMALLER = '<'
    THRESHOLD_OPTION_GREATER = '>'
    FILTER_OPTION_50HZ = 0
    FILTER_OPTION_60HZ = 1
    WIRE_MODE_2 = 2
    WIRE_MODE_3 = 3
    WIRE_MODE_4 = 4
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

        self.response_expected[BrickletPTCV2.FUNCTION_GET_TEMPERATURE] = BrickletPTCV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletPTCV2.FUNCTION_SET_TEMPERATURE_CALLBACK_CONFIGURATION] = BrickletPTCV2.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletPTCV2.FUNCTION_GET_TEMPERATURE_CALLBACK_CONFIGURATION] = BrickletPTCV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletPTCV2.FUNCTION_GET_RESISTANCE] = BrickletPTCV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletPTCV2.FUNCTION_SET_RESISTANCE_CALLBACK_CONFIGURATION] = BrickletPTCV2.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletPTCV2.FUNCTION_GET_RESISTANCE_CALLBACK_CONFIGURATION] = BrickletPTCV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletPTCV2.FUNCTION_SET_NOISE_REJECTION_FILTER] = BrickletPTCV2.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletPTCV2.FUNCTION_GET_NOISE_REJECTION_FILTER] = BrickletPTCV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletPTCV2.FUNCTION_IS_SENSOR_CONNECTED] = BrickletPTCV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletPTCV2.FUNCTION_SET_WIRE_MODE] = BrickletPTCV2.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletPTCV2.FUNCTION_GET_WIRE_MODE] = BrickletPTCV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletPTCV2.FUNCTION_SET_MOVING_AVERAGE_CONFIGURATION] = BrickletPTCV2.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletPTCV2.FUNCTION_GET_MOVING_AVERAGE_CONFIGURATION] = BrickletPTCV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletPTCV2.FUNCTION_SET_SENSOR_CONNECTED_CALLBACK_CONFIGURATION] = BrickletPTCV2.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletPTCV2.FUNCTION_GET_SENSOR_CONNECTED_CALLBACK_CONFIGURATION] = BrickletPTCV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletPTCV2.FUNCTION_GET_SPITFP_ERROR_COUNT] = BrickletPTCV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletPTCV2.FUNCTION_SET_BOOTLOADER_MODE] = BrickletPTCV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletPTCV2.FUNCTION_GET_BOOTLOADER_MODE] = BrickletPTCV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletPTCV2.FUNCTION_SET_WRITE_FIRMWARE_POINTER] = BrickletPTCV2.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletPTCV2.FUNCTION_WRITE_FIRMWARE] = BrickletPTCV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletPTCV2.FUNCTION_SET_STATUS_LED_CONFIG] = BrickletPTCV2.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletPTCV2.FUNCTION_GET_STATUS_LED_CONFIG] = BrickletPTCV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletPTCV2.FUNCTION_GET_CHIP_TEMPERATURE] = BrickletPTCV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletPTCV2.FUNCTION_RESET] = BrickletPTCV2.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletPTCV2.FUNCTION_WRITE_UID] = BrickletPTCV2.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletPTCV2.FUNCTION_READ_UID] = BrickletPTCV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletPTCV2.FUNCTION_GET_IDENTITY] = BrickletPTCV2.RESPONSE_EXPECTED_ALWAYS_TRUE

        self.callback_formats[BrickletPTCV2.CALLBACK_TEMPERATURE] = 'i'
        self.callback_formats[BrickletPTCV2.CALLBACK_RESISTANCE] = 'i'
        self.callback_formats[BrickletPTCV2.CALLBACK_SENSOR_CONNECTED] = '!'


    def get_temperature(self):
        """
        Returns the temperature of the connected sensor. The value
        has a range of -246 to 849 °C and is given in °C/100,
        e.g. a value of 4223 means that a temperature of 42.23 °C is measured.


        If you want to get the value periodically, it is recommended to use the
        :cb:`Temperature` callback. You can set the callback configuration
        with :func:`Set Temperature Callback Configuration`.
        """
        return self.ipcon.send_request(self, BrickletPTCV2.FUNCTION_GET_TEMPERATURE, (), '', 'i')

    def set_temperature_callback_configuration(self, period, value_has_to_change, option, min, max):
        """
        The period in ms is the period with which the :cb:`Temperature` callback is triggered
        periodically. A value of 0 turns the callback off.

        If the `value has to change`-parameter is set to true, the callback is only
        triggered after the value has changed. If the value didn't change
        within the period, the callback is triggered immediately on change.

        If it is set to false, the callback is continuously triggered with the period,
        independent of the value.

        It is furthermore possible to constrain the callback with thresholds.

        The `option`-parameter together with min/max sets a threshold for the :cb:`Temperature` callback.

        The following options are possible:

        .. csv-table::
         :header: "Option", "Description"
         :widths: 10, 100

         "'x'",    "Threshold is turned off"
         "'o'",    "Threshold is triggered when the value is *outside* the min and max values"
         "'i'",    "Threshold is triggered when the value is *inside* or equal to the min and max values"
         "'<'",    "Threshold is triggered when the value is smaller than the min value (max is ignored)"
         "'>'",    "Threshold is triggered when the value is greater than the min value (max is ignored)"

        If the option is set to 'x' (threshold turned off) the callback is triggered with the fixed period.

        The default value is (0, false, 'x', 0, 0).
        """
        period = int(period)
        value_has_to_change = bool(value_has_to_change)
        option = create_char(option)
        min = int(min)
        max = int(max)

        self.ipcon.send_request(self, BrickletPTCV2.FUNCTION_SET_TEMPERATURE_CALLBACK_CONFIGURATION, (period, value_has_to_change, option, min, max), 'I ! c i i', '')

    def get_temperature_callback_configuration(self):
        """
        Returns the callback configuration as set by :func:`Set Temperature Callback Configuration`.
        """
        return GetTemperatureCallbackConfiguration(*self.ipcon.send_request(self, BrickletPTCV2.FUNCTION_GET_TEMPERATURE_CALLBACK_CONFIGURATION, (), '', 'I ! c i i'))

    def get_resistance(self):
        """
        Returns the value as measured by the MAX31865 precision delta-sigma ADC.

        The value can be converted with the following formulas:

        * Pt100:  resistance = (value * 390) / 32768
        * Pt1000: resistance = (value * 3900) / 32768


        If you want to get the value periodically, it is recommended to use the
        :cb:`Resistance` callback. You can set the callback configuration
        with :func:`Set Resistance Callback Configuration`.
        """
        return self.ipcon.send_request(self, BrickletPTCV2.FUNCTION_GET_RESISTANCE, (), '', 'i')

    def set_resistance_callback_configuration(self, period, value_has_to_change, option, min, max):
        """
        The period in ms is the period with which the :cb:`Resistance` callback is triggered
        periodically. A value of 0 turns the callback off.

        If the `value has to change`-parameter is set to true, the callback is only
        triggered after the value has changed. If the value didn't change
        within the period, the callback is triggered immediately on change.

        If it is set to false, the callback is continuously triggered with the period,
        independent of the value.

        It is furthermore possible to constrain the callback with thresholds.

        The `option`-parameter together with min/max sets a threshold for the :cb:`Resistance` callback.

        The following options are possible:

        .. csv-table::
         :header: "Option", "Description"
         :widths: 10, 100

         "'x'",    "Threshold is turned off"
         "'o'",    "Threshold is triggered when the value is *outside* the min and max values"
         "'i'",    "Threshold is triggered when the value is *inside* or equal to the min and max values"
         "'<'",    "Threshold is triggered when the value is smaller than the min value (max is ignored)"
         "'>'",    "Threshold is triggered when the value is greater than the min value (max is ignored)"

        If the option is set to 'x' (threshold turned off) the callback is triggered with the fixed period.

        The default value is (0, false, 'x', 0, 0).
        """
        period = int(period)
        value_has_to_change = bool(value_has_to_change)
        option = create_char(option)
        min = int(min)
        max = int(max)

        self.ipcon.send_request(self, BrickletPTCV2.FUNCTION_SET_RESISTANCE_CALLBACK_CONFIGURATION, (period, value_has_to_change, option, min, max), 'I ! c i i', '')

    def get_resistance_callback_configuration(self):
        """
        Returns the callback configuration as set by :func:`Set Resistance Callback Configuration`.
        """
        return GetResistanceCallbackConfiguration(*self.ipcon.send_request(self, BrickletPTCV2.FUNCTION_GET_RESISTANCE_CALLBACK_CONFIGURATION, (), '', 'I ! c i i'))

    def set_noise_rejection_filter(self, filter):
        """
        Sets the noise rejection filter to either 50Hz (0) or 60Hz (1).
        Noise from 50Hz or 60Hz power sources (including
        harmonics of the AC power's fundamental frequency) is
        attenuated by 82dB.

        Default value is 0 = 50Hz.
        """
        filter = int(filter)

        self.ipcon.send_request(self, BrickletPTCV2.FUNCTION_SET_NOISE_REJECTION_FILTER, (filter,), 'B', '')

    def get_noise_rejection_filter(self):
        """
        Returns the noise rejection filter option as set by
        :func:`Set Noise Rejection Filter`
        """
        return self.ipcon.send_request(self, BrickletPTCV2.FUNCTION_GET_NOISE_REJECTION_FILTER, (), '', 'B')

    def is_sensor_connected(self):
        """
        Returns *true* if the sensor is connected correctly.

        If this function
        returns *false*, there is either no Pt100 or Pt1000 sensor connected,
        the sensor is connected incorrectly or the sensor itself is faulty.

        If you want to get the status automatically, it is recommended to use the
        :cb:`Sensor Connected` callback. You can set the callback configuration
        with :func:`Set Sensor Connected Callback Configuration`.
        """
        return self.ipcon.send_request(self, BrickletPTCV2.FUNCTION_IS_SENSOR_CONNECTED, (), '', '!')

    def set_wire_mode(self, mode):
        """
        Sets the wire mode of the sensor. Possible values are 2, 3 and 4 which
        correspond to 2-, 3- and 4-wire sensors. The value has to match the jumper
        configuration on the Bricklet.

        The default value is 2 = 2-wire.
        """
        mode = int(mode)

        self.ipcon.send_request(self, BrickletPTCV2.FUNCTION_SET_WIRE_MODE, (mode,), 'B', '')

    def get_wire_mode(self):
        """
        Returns the wire mode as set by :func:`Set Wire Mode`
        """
        return self.ipcon.send_request(self, BrickletPTCV2.FUNCTION_GET_WIRE_MODE, (), '', 'B')

    def set_moving_average_configuration(self, moving_average_length_resistance, moving_average_length_temperature):
        """
        Sets the length of a `moving averaging <https://en.wikipedia.org/wiki/Moving_average>`__
        for the resistance and temperature.

        Setting the length to 1 will turn the averaging off. With less
        averaging, there is more noise on the data.

        The range for the averaging is 1-1000.

        New data is gathered every 20ms. With a moving average of length 1000 the resulting
        averaging window has a length of 20s. If you want to do long term measurements the longest
        moving average will give the cleanest results.

        The default value is 1 for resistance and 40 for temperature. The default values match
        the non-changeable averaging settings of the old PTC Bricklet 1.0
        """
        moving_average_length_resistance = int(moving_average_length_resistance)
        moving_average_length_temperature = int(moving_average_length_temperature)

        self.ipcon.send_request(self, BrickletPTCV2.FUNCTION_SET_MOVING_AVERAGE_CONFIGURATION, (moving_average_length_resistance, moving_average_length_temperature), 'H H', '')

    def get_moving_average_configuration(self):
        """
        Returns the moving average configuration as set by :func:`Set Moving Average Configuration`.
        """
        return GetMovingAverageConfiguration(*self.ipcon.send_request(self, BrickletPTCV2.FUNCTION_GET_MOVING_AVERAGE_CONFIGURATION, (), '', 'H H'))

    def set_sensor_connected_callback_configuration(self, enabled):
        """
        If you enable this callback, the :cb:`Sensor Connected` callback is triggered
        every time a Pt sensor is connected/disconnected.

        By default this callback is disabled.
        """
        enabled = bool(enabled)

        self.ipcon.send_request(self, BrickletPTCV2.FUNCTION_SET_SENSOR_CONNECTED_CALLBACK_CONFIGURATION, (enabled,), '!', '')

    def get_sensor_connected_callback_configuration(self):
        """
        Returns the configuration as set by :func:`Set Sensor Connected Callback Configuration`.
        """
        return self.ipcon.send_request(self, BrickletPTCV2.FUNCTION_GET_SENSOR_CONNECTED_CALLBACK_CONFIGURATION, (), '', '!')

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
        return GetSPITFPErrorCount(*self.ipcon.send_request(self, BrickletPTCV2.FUNCTION_GET_SPITFP_ERROR_COUNT, (), '', 'I I I I'))

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

        return self.ipcon.send_request(self, BrickletPTCV2.FUNCTION_SET_BOOTLOADER_MODE, (mode,), 'B', 'B')

    def get_bootloader_mode(self):
        """
        Returns the current bootloader mode, see :func:`Set Bootloader Mode`.
        """
        return self.ipcon.send_request(self, BrickletPTCV2.FUNCTION_GET_BOOTLOADER_MODE, (), '', 'B')

    def set_write_firmware_pointer(self, pointer):
        """
        Sets the firmware pointer for :func:`Write Firmware`. The pointer has
        to be increased by chunks of size 64. The data is written to flash
        every 4 chunks (which equals to one page of size 256).

        This function is used by Brick Viewer during flashing. It should not be
        necessary to call it in a normal user program.
        """
        pointer = int(pointer)

        self.ipcon.send_request(self, BrickletPTCV2.FUNCTION_SET_WRITE_FIRMWARE_POINTER, (pointer,), 'I', '')

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

        return self.ipcon.send_request(self, BrickletPTCV2.FUNCTION_WRITE_FIRMWARE, (data,), '64B', 'B')

    def set_status_led_config(self, config):
        """
        Sets the status LED configuration. By default the LED shows
        communication traffic between Brick and Bricklet, it flickers once
        for every 10 received data packets.

        You can also turn the LED permanently on/off or show a heartbeat.

        If the Bricklet is in bootloader mode, the LED is will show heartbeat by default.
        """
        config = int(config)

        self.ipcon.send_request(self, BrickletPTCV2.FUNCTION_SET_STATUS_LED_CONFIG, (config,), 'B', '')

    def get_status_led_config(self):
        """
        Returns the configuration as set by :func:`Set Status LED Config`
        """
        return self.ipcon.send_request(self, BrickletPTCV2.FUNCTION_GET_STATUS_LED_CONFIG, (), '', 'B')

    def get_chip_temperature(self):
        """
        Returns the temperature in °C as measured inside the microcontroller. The
        value returned is not the ambient temperature!

        The temperature is only proportional to the real temperature and it has bad
        accuracy. Practically it is only useful as an indicator for
        temperature changes.
        """
        return self.ipcon.send_request(self, BrickletPTCV2.FUNCTION_GET_CHIP_TEMPERATURE, (), '', 'h')

    def reset(self):
        """
        Calling this function will reset the Bricklet. All configurations
        will be lost.

        After a reset you have to create new device objects,
        calling functions on the existing ones will result in
        undefined behavior!
        """
        self.ipcon.send_request(self, BrickletPTCV2.FUNCTION_RESET, (), '', '')

    def write_uid(self, uid):
        """
        Writes a new UID into flash. If you want to set a new UID
        you have to decode the Base58 encoded UID string into an
        integer first.

        We recommend that you use Brick Viewer to change the UID.
        """
        uid = int(uid)

        self.ipcon.send_request(self, BrickletPTCV2.FUNCTION_WRITE_UID, (uid,), 'I', '')

    def read_uid(self):
        """
        Returns the current UID as an integer. Encode as
        Base58 to get the usual string version.
        """
        return self.ipcon.send_request(self, BrickletPTCV2.FUNCTION_READ_UID, (), '', 'I')

    def get_identity(self):
        """
        Returns the UID, the UID where the Bricklet is connected to,
        the position, the hardware and firmware version as well as the
        device identifier.

        The position can be 'a', 'b', 'c' or 'd'.

        The device identifier numbers can be found :ref:`here <device_identifier>`.
        |device_identifier_constant|
        """
        return GetIdentity(*self.ipcon.send_request(self, BrickletPTCV2.FUNCTION_GET_IDENTITY, (), '', '8s 8s c 3B 3B H'))

    def register_callback(self, callback_id, function):
        """
        Registers the given *function* with the given *callback_id*.
        """
        if function is None:
            self.registered_callbacks.pop(callback_id, None)
        else:
            self.registered_callbacks[callback_id] = function

PTCV2 = BrickletPTCV2 # for backward compatibility
