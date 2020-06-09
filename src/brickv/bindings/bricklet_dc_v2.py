# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2020-06-09.      #
#                                                           #
# Python Bindings Version 2.1.26                            #
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

GetMotion = namedtuple('Motion', ['acceleration', 'deceleration'])
GetPowerStatistics = namedtuple('PowerStatistics', ['voltage', 'current'])
GetGPIOConfiguration = namedtuple('GPIOConfiguration', ['debounce', 'stop_deceleration'])
GetSPITFPErrorCount = namedtuple('SPITFPErrorCount', ['error_count_ack_checksum', 'error_count_message_checksum', 'error_count_frame', 'error_count_overflow'])
GetIdentity = namedtuple('Identity', ['uid', 'connected_uid', 'position', 'hardware_version', 'firmware_version', 'device_identifier'])

class BrickletDCV2(Device):
    """
    TBD
    """

    DEVICE_IDENTIFIER = 2156
    DEVICE_DISPLAY_NAME = 'DC Bricklet 2.0'
    DEVICE_URL_PART = 'dc_v2' # internal



    FUNCTION_SET_ENABLED = 1
    FUNCTION_GET_ENABLED = 2
    FUNCTION_SET_VELOCITY = 3
    FUNCTION_GET_VELOCITY = 4
    FUNCTION_GET_CURRENT_VELOCITY = 5
    FUNCTION_SET_MOTION = 6
    FUNCTION_GET_MOTION = 7
    FUNCTION_FULL_BRAKE = 8
    FUNCTION_SET_DRIVE_MODE = 9
    FUNCTION_GET_DRIVE_MODE = 10
    FUNCTION_SET_PWM_FREQUENCY = 11
    FUNCTION_GET_PWM_FREQUENCY = 12
    FUNCTION_GET_POWER_STATISTICS = 13
    FUNCTION_SET_GPIO_CONFIGURATION = 14
    FUNCTION_GET_GPIO_CONFIGURATION = 15
    FUNCTION_SET_GPIO_ACTION = 16
    FUNCTION_GET_GPIO_ACTION = 17
    FUNCTION_GET_GPIO_STATE = 18
    FUNCTION_SET_ERROR_LED_CONFIG = 19
    FUNCTION_GET_ERROR_LED_CONFIG = 20
    FUNCTION_SET_CW_LED_CONFIG = 21
    FUNCTION_GET_CW_LED_CONFIG = 22
    FUNCTION_SET_CCW_LED_CONFIG = 23
    FUNCTION_GET_CCW_LED_CONFIG = 24
    FUNCTION_SET_GPIO_LED_CONFIG = 25
    FUNCTION_GET_GPIO_LED_CONFIG = 26
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

    DRIVE_MODE_DRIVE_BRAKE = 0
    DRIVE_MODE_DRIVE_COAST = 1
    GPIO_ACTION_NONE = 0
    GPIO_ACTION_NORMAL_STOP_RISING_EDGE = 1
    GPIO_ACTION_NORMAL_STOP_FALLING_EDGE = 2
    GPIO_ACTION_FULL_BRAKE_RISING_EDGE = 4
    GPIO_ACTION_FULL_BRAKE_FALLING_EDGE = 8
    GPIO_ACTION_CALLBACK_RISING_EDGE = 16
    GPIO_ACTION_CALLBACK_FALLING_EDGE = 32
    ERROR_LED_CONFIG_OFF = 0
    ERROR_LED_CONFIG_ON = 1
    ERROR_LED_CONFIG_SHOW_HEARTBEAT = 2
    ERROR_LED_CONFIG_SHOW_ERROR = 3
    CW_LED_CONFIG_OFF = 0
    CW_LED_CONFIG_ON = 1
    CW_LED_CONFIG_SHOW_HEARTBEAT = 2
    CW_LED_CONFIG_SHOW_CW_AS_FORWARD = 3
    CW_LED_CONFIG_SHOW_CW_AS_BACKWARD = 4
    CCW_LED_CONFIG_OFF = 0
    CCW_LED_CONFIG_ON = 1
    CCW_LED_CONFIG_SHOW_HEARTBEAT = 2
    CCW_LED_CONFIG_SHOW_CCW_AS_FORWARD = 3
    CCW_LED_CONFIG_SHOW_CCW_AS_BACKWARD = 4
    GPIO_LED_CONFIG_OFF = 0
    GPIO_LED_CONFIG_ON = 1
    GPIO_LED_CONFIG_SHOW_HEARTBEAT = 2
    GPIO_LED_CONFIG_SHOW_GPIO_ACTIVE_HIGH = 3
    GPIO_LED_CONFIG_SHOW_GPIO_ACTIVE_LOW = 4
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
        Device.__init__(self, uid, ipcon, BrickletDCV2.DEVICE_IDENTIFIER, BrickletDCV2.DEVICE_DISPLAY_NAME)

        self.api_version = (2, 0, 0)

        self.response_expected[BrickletDCV2.FUNCTION_SET_ENABLED] = BrickletDCV2.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletDCV2.FUNCTION_GET_ENABLED] = BrickletDCV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletDCV2.FUNCTION_SET_VELOCITY] = BrickletDCV2.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletDCV2.FUNCTION_GET_VELOCITY] = BrickletDCV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletDCV2.FUNCTION_GET_CURRENT_VELOCITY] = BrickletDCV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletDCV2.FUNCTION_SET_MOTION] = BrickletDCV2.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletDCV2.FUNCTION_GET_MOTION] = BrickletDCV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletDCV2.FUNCTION_FULL_BRAKE] = BrickletDCV2.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletDCV2.FUNCTION_SET_DRIVE_MODE] = BrickletDCV2.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletDCV2.FUNCTION_GET_DRIVE_MODE] = BrickletDCV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletDCV2.FUNCTION_SET_PWM_FREQUENCY] = BrickletDCV2.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletDCV2.FUNCTION_GET_PWM_FREQUENCY] = BrickletDCV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletDCV2.FUNCTION_GET_POWER_STATISTICS] = BrickletDCV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletDCV2.FUNCTION_SET_GPIO_CONFIGURATION] = BrickletDCV2.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletDCV2.FUNCTION_GET_GPIO_CONFIGURATION] = BrickletDCV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletDCV2.FUNCTION_SET_GPIO_ACTION] = BrickletDCV2.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletDCV2.FUNCTION_GET_GPIO_ACTION] = BrickletDCV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletDCV2.FUNCTION_GET_GPIO_STATE] = BrickletDCV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletDCV2.FUNCTION_SET_ERROR_LED_CONFIG] = BrickletDCV2.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletDCV2.FUNCTION_GET_ERROR_LED_CONFIG] = BrickletDCV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletDCV2.FUNCTION_SET_CW_LED_CONFIG] = BrickletDCV2.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletDCV2.FUNCTION_GET_CW_LED_CONFIG] = BrickletDCV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletDCV2.FUNCTION_SET_CCW_LED_CONFIG] = BrickletDCV2.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletDCV2.FUNCTION_GET_CCW_LED_CONFIG] = BrickletDCV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletDCV2.FUNCTION_SET_GPIO_LED_CONFIG] = BrickletDCV2.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletDCV2.FUNCTION_GET_GPIO_LED_CONFIG] = BrickletDCV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletDCV2.FUNCTION_GET_SPITFP_ERROR_COUNT] = BrickletDCV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletDCV2.FUNCTION_SET_BOOTLOADER_MODE] = BrickletDCV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletDCV2.FUNCTION_GET_BOOTLOADER_MODE] = BrickletDCV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletDCV2.FUNCTION_SET_WRITE_FIRMWARE_POINTER] = BrickletDCV2.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletDCV2.FUNCTION_WRITE_FIRMWARE] = BrickletDCV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletDCV2.FUNCTION_SET_STATUS_LED_CONFIG] = BrickletDCV2.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletDCV2.FUNCTION_GET_STATUS_LED_CONFIG] = BrickletDCV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletDCV2.FUNCTION_GET_CHIP_TEMPERATURE] = BrickletDCV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletDCV2.FUNCTION_RESET] = BrickletDCV2.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletDCV2.FUNCTION_WRITE_UID] = BrickletDCV2.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletDCV2.FUNCTION_READ_UID] = BrickletDCV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletDCV2.FUNCTION_GET_IDENTITY] = BrickletDCV2.RESPONSE_EXPECTED_ALWAYS_TRUE


        ipcon.add_device(self)

    def set_enabled(self, enabled):
        """
        TBD
        """
        self.check_validity()

        enabled = bool(enabled)

        self.ipcon.send_request(self, BrickletDCV2.FUNCTION_SET_ENABLED, (enabled,), '!', 0, '')

    def get_enabled(self):
        """
        TBD
        """
        self.check_validity()

        return self.ipcon.send_request(self, BrickletDCV2.FUNCTION_GET_ENABLED, (), '', 9, '!')

    def set_velocity(self, velocity):
        """
        Sets the velocity of the motor. Whereas -32767 is full speed backward,
        0 is stop and 32767 is full speed forward. Depending on the
        acceleration (see TBD), the motor is not immediately
        brought to the velocity but smoothly accelerated.

        The velocity describes the duty cycle of the PWM with which the motor is
        controlled, e.g. a velocity of 3277 sets a PWM with a 10% duty cycle.
        You can not only control the duty cycle of the PWM but also the frequency,
        see TBD.
        """
        self.check_validity()

        velocity = int(velocity)

        self.ipcon.send_request(self, BrickletDCV2.FUNCTION_SET_VELOCITY, (velocity,), 'h', 0, '')

    def get_velocity(self):
        """
        Returns the velocity as set by :func:`Set Velocity`.
        """
        self.check_validity()

        return self.ipcon.send_request(self, BrickletDCV2.FUNCTION_GET_VELOCITY, (), '', 10, 'h')

    def get_current_velocity(self):
        """
        Returns the *current* velocity of the motor. This value is different
        from :func:`Get Velocity` whenever the motor is currently accelerating
        to a goal set by :func:`Set Velocity`.
        """
        self.check_validity()

        return self.ipcon.send_request(self, BrickletDCV2.FUNCTION_GET_CURRENT_VELOCITY, (), '', 10, 'h')

    def set_motion(self, acceleration, deceleration):
        """
        Sets the acceleration of the motor. It is given in *velocity/s*. An
        acceleration of 10000 means, that every second the velocity is increased
        by 10000 (or about 30% duty cycle).

        For example: If the current velocity is 0 and you want to accelerate to a
        velocity of 16000 (about 50% duty cycle) in 10 seconds, you should set
        an acceleration of 1600.

        If acceleration is set to 0, there is no speed ramping, i.e. a new velocity
        is immediately given to the motor.
        """
        self.check_validity()

        acceleration = int(acceleration)
        deceleration = int(deceleration)

        self.ipcon.send_request(self, BrickletDCV2.FUNCTION_SET_MOTION, (acceleration, deceleration), 'H H', 0, '')

    def get_motion(self):
        """
        Returns the acceleration as set by :func:`Set Motion`.
        """
        self.check_validity()

        return GetMotion(*self.ipcon.send_request(self, BrickletDCV2.FUNCTION_GET_MOTION, (), '', 12, 'H H'))

    def full_brake(self):
        """
        Executes an active full brake.

        .. warning::
         This function is for emergency purposes,
         where an immediate brake is necessary. Depending on the current velocity and
         the strength of the motor, a full brake can be quite violent.

        Call :func:`Set Velocity` with 0 if you just want to stop the motor.
        """
        self.check_validity()

        self.ipcon.send_request(self, BrickletDCV2.FUNCTION_FULL_BRAKE, (), '', 0, '')

    def set_drive_mode(self, mode):
        """
        Sets the drive mode. Possible modes are:

        * 0 = Drive/Brake
        * 1 = Drive/Coast

        These modes are different kinds of motor controls.

        In Drive/Brake mode, the motor is always either driving or braking. There
        is no freewheeling. Advantages are: A more linear correlation between
        PWM and velocity, more exact accelerations and the possibility to drive
        with slower velocities.

        In Drive/Coast mode, the motor is always either driving or freewheeling.
        Advantages are: Less current consumption and less demands on the motor and
        driver chip.
        """
        self.check_validity()

        mode = int(mode)

        self.ipcon.send_request(self, BrickletDCV2.FUNCTION_SET_DRIVE_MODE, (mode,), 'B', 0, '')

    def get_drive_mode(self):
        """
        Returns the drive mode, as set by :func:`Set Drive Mode`.
        """
        self.check_validity()

        return self.ipcon.send_request(self, BrickletDCV2.FUNCTION_GET_DRIVE_MODE, (), '', 9, 'B')

    def set_pwm_frequency(self, frequency):
        """
        Sets the frequency of the PWM with which the motor is driven.
        Often a high frequency
        is less noisy and the motor runs smoother. However, with a low frequency
        there are less switches and therefore fewer switching losses. Also with
        most motors lower frequencies enable higher torque.

        If you have no idea what all this means, just ignore this function and use
        the default frequency, it will very likely work fine.
        """
        self.check_validity()

        frequency = int(frequency)

        self.ipcon.send_request(self, BrickletDCV2.FUNCTION_SET_PWM_FREQUENCY, (frequency,), 'H', 0, '')

    def get_pwm_frequency(self):
        """
        Returns the PWM frequency as set by :func:`Set PWM Frequency`.
        """
        self.check_validity()

        return self.ipcon.send_request(self, BrickletDCV2.FUNCTION_GET_PWM_FREQUENCY, (), '', 10, 'H')

    def get_power_statistics(self):
        """
        TBD
        """
        self.check_validity()

        return GetPowerStatistics(*self.ipcon.send_request(self, BrickletDCV2.FUNCTION_GET_POWER_STATISTICS, (), '', 12, 'H H'))

    def set_gpio_configuration(self, channel, debounce, stop_deceleration):
        """
        TBD
        """
        self.check_validity()

        channel = int(channel)
        debounce = int(debounce)
        stop_deceleration = int(stop_deceleration)

        self.ipcon.send_request(self, BrickletDCV2.FUNCTION_SET_GPIO_CONFIGURATION, (channel, debounce, stop_deceleration), 'B H H', 0, '')

    def get_gpio_configuration(self, channel):
        """
        TBD
        """
        self.check_validity()

        channel = int(channel)

        return GetGPIOConfiguration(*self.ipcon.send_request(self, BrickletDCV2.FUNCTION_GET_GPIO_CONFIGURATION, (channel,), 'B', 12, 'H H'))

    def set_gpio_action(self, channel, action):
        """
        TBD
        """
        self.check_validity()

        channel = int(channel)
        action = int(action)

        self.ipcon.send_request(self, BrickletDCV2.FUNCTION_SET_GPIO_ACTION, (channel, action), 'B I', 0, '')

    def get_gpio_action(self, channel):
        """
        TBD
        """
        self.check_validity()

        channel = int(channel)

        return self.ipcon.send_request(self, BrickletDCV2.FUNCTION_GET_GPIO_ACTION, (channel,), 'B', 12, 'I')

    def get_gpio_state(self):
        """
        TBD
        """
        self.check_validity()

        return self.ipcon.send_request(self, BrickletDCV2.FUNCTION_GET_GPIO_STATE, (), '', 9, '2!')

    def set_error_led_config(self, config):
        """
        Configures the touch LED to be either turned off, turned on, blink in
        heartbeat mode or show TBD.

        TODO:

        * one second interval blink: Input voltage too small
        * 250ms interval blink: Overtemperature warning
        * full red: motor disabled because of short to ground in phase a or b or because of overtemperature
        """
        self.check_validity()

        config = int(config)

        self.ipcon.send_request(self, BrickletDCV2.FUNCTION_SET_ERROR_LED_CONFIG, (config,), 'B', 0, '')

    def get_error_led_config(self):
        """
        Returns the LED configuration as set by :func:`Set Error LED Config`
        """
        self.check_validity()

        return self.ipcon.send_request(self, BrickletDCV2.FUNCTION_GET_ERROR_LED_CONFIG, (), '', 9, 'B')

    def set_cw_led_config(self, config):
        """
        TBD
        """
        self.check_validity()

        config = int(config)

        self.ipcon.send_request(self, BrickletDCV2.FUNCTION_SET_CW_LED_CONFIG, (config,), 'B', 0, '')

    def get_cw_led_config(self):
        """
        Returns the LED configuration as set by :func:`Set CW LED Config`
        """
        self.check_validity()

        return self.ipcon.send_request(self, BrickletDCV2.FUNCTION_GET_CW_LED_CONFIG, (), '', 9, 'B')

    def set_ccw_led_config(self, config):
        """
        TBD
        """
        self.check_validity()

        config = int(config)

        self.ipcon.send_request(self, BrickletDCV2.FUNCTION_SET_CCW_LED_CONFIG, (config,), 'B', 0, '')

    def get_ccw_led_config(self):
        """
        Returns the LED configuration as set by :func:`Set CCW LED Config`
        """
        self.check_validity()

        return self.ipcon.send_request(self, BrickletDCV2.FUNCTION_GET_CCW_LED_CONFIG, (), '', 9, 'B')

    def set_gpio_led_config(self, channel, config):
        """
        Configures the touch LED to be either turned off, turned on, blink in
        heartbeat mode or show TBD.
        """
        self.check_validity()

        channel = int(channel)
        config = int(config)

        self.ipcon.send_request(self, BrickletDCV2.FUNCTION_SET_GPIO_LED_CONFIG, (channel, config), 'B B', 0, '')

    def get_gpio_led_config(self, channel):
        """
        Returns the LED configuration as set by :func:`Set GPIO LED Config`
        """
        self.check_validity()

        channel = int(channel)

        return self.ipcon.send_request(self, BrickletDCV2.FUNCTION_GET_GPIO_LED_CONFIG, (channel,), 'B', 9, 'B')

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

        return GetSPITFPErrorCount(*self.ipcon.send_request(self, BrickletDCV2.FUNCTION_GET_SPITFP_ERROR_COUNT, (), '', 24, 'I I I I'))

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

        return self.ipcon.send_request(self, BrickletDCV2.FUNCTION_SET_BOOTLOADER_MODE, (mode,), 'B', 9, 'B')

    def get_bootloader_mode(self):
        """
        Returns the current bootloader mode, see :func:`Set Bootloader Mode`.
        """
        self.check_validity()

        return self.ipcon.send_request(self, BrickletDCV2.FUNCTION_GET_BOOTLOADER_MODE, (), '', 9, 'B')

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

        self.ipcon.send_request(self, BrickletDCV2.FUNCTION_SET_WRITE_FIRMWARE_POINTER, (pointer,), 'I', 0, '')

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

        return self.ipcon.send_request(self, BrickletDCV2.FUNCTION_WRITE_FIRMWARE, (data,), '64B', 9, 'B')

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

        self.ipcon.send_request(self, BrickletDCV2.FUNCTION_SET_STATUS_LED_CONFIG, (config,), 'B', 0, '')

    def get_status_led_config(self):
        """
        Returns the configuration as set by :func:`Set Status LED Config`
        """
        self.check_validity()

        return self.ipcon.send_request(self, BrickletDCV2.FUNCTION_GET_STATUS_LED_CONFIG, (), '', 9, 'B')

    def get_chip_temperature(self):
        """
        Returns the temperature as measured inside the microcontroller. The
        value returned is not the ambient temperature!

        The temperature is only proportional to the real temperature and it has bad
        accuracy. Practically it is only useful as an indicator for
        temperature changes.
        """
        self.check_validity()

        return self.ipcon.send_request(self, BrickletDCV2.FUNCTION_GET_CHIP_TEMPERATURE, (), '', 10, 'h')

    def reset(self):
        """
        Calling this function will reset the Bricklet. All configurations
        will be lost.

        After a reset you have to create new device objects,
        calling functions on the existing ones will result in
        undefined behavior!
        """
        self.check_validity()

        self.ipcon.send_request(self, BrickletDCV2.FUNCTION_RESET, (), '', 0, '')

    def write_uid(self, uid):
        """
        Writes a new UID into flash. If you want to set a new UID
        you have to decode the Base58 encoded UID string into an
        integer first.

        We recommend that you use Brick Viewer to change the UID.
        """
        self.check_validity()

        uid = int(uid)

        self.ipcon.send_request(self, BrickletDCV2.FUNCTION_WRITE_UID, (uid,), 'I', 0, '')

    def read_uid(self):
        """
        Returns the current UID as an integer. Encode as
        Base58 to get the usual string version.
        """
        self.check_validity()

        return self.ipcon.send_request(self, BrickletDCV2.FUNCTION_READ_UID, (), '', 12, 'I')

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
        return GetIdentity(*self.ipcon.send_request(self, BrickletDCV2.FUNCTION_GET_IDENTITY, (), '', 33, '8s 8s c 3B 3B H'))

DCV2 = BrickletDCV2 # for backward compatibility
