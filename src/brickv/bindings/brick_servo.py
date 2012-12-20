# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2012-12-20.      #
#                                                           #
# If you have a bugfix for this file and want to commit it, #
# please fix the bug in the generator. You can find a link  #
# to the generator git on tinkerforge.com                   #
#############################################################

try:
    from collections import namedtuple
except ImportError:
    try:
        from .ip_connection import namedtuple
    except ValueError:
        from ip_connection import namedtuple

try:
    from .ip_connection import Device, IPConnection, Error
except ValueError:
    from ip_connection import Device, IPConnection, Error

GetPulseWidth = namedtuple('PulseWidth', ['min', 'max'])
GetDegree = namedtuple('Degree', ['min', 'max'])

class Servo(Device):
    """
    Device for controlling up to seven servos
    """

    CALLBACK_UNDER_VOLTAGE = 26
    CALLBACK_POSITION_REACHED = 27
    CALLBACK_VELOCITY_REACHED = 28

    FUNCTION_ENABLE = 1
    FUNCTION_DISABLE = 2
    FUNCTION_IS_ENABLED = 3
    FUNCTION_SET_POSITION = 4
    FUNCTION_GET_POSITION = 5
    FUNCTION_GET_CURRENT_POSITION = 6
    FUNCTION_SET_VELOCITY = 7
    FUNCTION_GET_VELOCITY = 8
    FUNCTION_GET_CURRENT_VELOCITY = 9
    FUNCTION_SET_ACCELERATION = 10
    FUNCTION_GET_ACCELERATION = 11
    FUNCTION_SET_OUTPUT_VOLTAGE = 12
    FUNCTION_GET_OUTPUT_VOLTAGE = 13
    FUNCTION_SET_PULSE_WIDTH = 14
    FUNCTION_GET_PULSE_WIDTH = 15
    FUNCTION_SET_DEGREE = 16
    FUNCTION_GET_DEGREE = 17
    FUNCTION_SET_PERIOD = 18
    FUNCTION_GET_PERIOD = 19
    FUNCTION_GET_SERVO_CURRENT = 20
    FUNCTION_GET_OVERALL_CURRENT = 21
    FUNCTION_GET_STACK_INPUT_VOLTAGE = 22
    FUNCTION_GET_EXTERNAL_INPUT_VOLTAGE = 23
    FUNCTION_SET_MINIMUM_VOLTAGE = 24
    FUNCTION_GET_MINIMUM_VOLTAGE = 25
    FUNCTION_RESET = 243
    FUNCTION_GET_CHIP_TEMPERATURE = 242

    def __init__(self, uid):
        """
        Creates an object with the unique device ID *uid*. This object can
        then be added to the IP connection.
        """
        Device.__init__(self, uid)

        self.expected_name = 'Servo Brick'

        self.binding_version = [1, 0, 1]

        self.callback_formats[Servo.CALLBACK_UNDER_VOLTAGE] = 'H'
        self.callback_formats[Servo.CALLBACK_POSITION_REACHED] = 'B h'
        self.callback_formats[Servo.CALLBACK_VELOCITY_REACHED] = 'B h'

    def enable(self, servo_num):
        """
        Enables a servo (0 to 6). If a servo is enabled, the configured position,
        velocity, acceleration, etc. are applied immediately.
        """
        self.ipcon.send_request(self, Servo.FUNCTION_ENABLE, (servo_num,), 'B', '')

    def disable(self, servo_num):
        """
        Disables a servo (0 to 6). Disabled servos are not driven at all, i.e. a
        disabled servo will not hold its position if a load is applied.
        """
        self.ipcon.send_request(self, Servo.FUNCTION_DISABLE, (servo_num,), 'B', '')

    def is_enabled(self, servo_num):
        """
        Returns *true* if the specified servo is enabled, *false* otherwise.
        """
        return self.ipcon.send_request(self, Servo.FUNCTION_IS_ENABLED, (servo_num,), 'B', '?')

    def set_position(self, servo_num, position):
        """
        Sets the position in °/100 for the specified servo. 
        
        The default range of the position is -9000 to 9000, but it can be specified
        according to your servo with :func:`SetDegree`.
        
        If you want to control a linear servo or RC brushless motor controller or
        similar with the Servo Brick, you can also define lengths or speeds with
        :func:`SetDegree`.
        """
        self.ipcon.send_request(self, Servo.FUNCTION_SET_POSITION, (servo_num, position), 'B h', '')

    def get_position(self, servo_num):
        """
        Returns the position of the specified servo as set by :func:`SetPosition`.
        """
        return self.ipcon.send_request(self, Servo.FUNCTION_GET_POSITION, (servo_num,), 'B', 'h')

    def get_current_position(self, servo_num):
        """
        Returns the *current* position of the specified servo. This may not be the
        value of :func:`SetPosition` if the servo is currently approaching a
        position goal.
        """
        return self.ipcon.send_request(self, Servo.FUNCTION_GET_CURRENT_POSITION, (servo_num,), 'B', 'h')

    def set_velocity(self, servo_num, velocity):
        """
        Sets the maximum velocity of the specified servo in °/100s. The velocity
        is accelerated according to the value set by :func:`SetAcceleration`.
        
        The minimum velocity is 0 (no movement) and the maximum velocity is 65535.
        With a value of 65535 the position will be set immediately (no velocity).
        
        The default value is 65535.
        """
        self.ipcon.send_request(self, Servo.FUNCTION_SET_VELOCITY, (servo_num, velocity), 'B H', '')

    def get_velocity(self, servo_num):
        """
        Returns the velocity of the specified servo as set by :func:`SetVelocity`.
        """
        return self.ipcon.send_request(self, Servo.FUNCTION_GET_VELOCITY, (servo_num,), 'B', 'H')

    def get_current_velocity(self, servo_num):
        """
        Returns the *current* velocity of the specified servo. This may not be the
        value of :func:`SetVelocity` if the servo is currently approaching a
        velocity goal.
        """
        return self.ipcon.send_request(self, Servo.FUNCTION_GET_CURRENT_VELOCITY, (servo_num,), 'B', 'H')

    def set_acceleration(self, servo_num, acceleration):
        """
        Sets the acceleration of the specified servo in °/100s².
        
        The minimum acceleration is 1 and the maximum acceleration is 65535.
        With a value of 65535 the velocity will be set immediately (no acceleration).
        
        The default value is 65535.
        """
        self.ipcon.send_request(self, Servo.FUNCTION_SET_ACCELERATION, (servo_num, acceleration), 'B H', '')

    def get_acceleration(self, servo_num):
        """
        Returns the acceleration for the specified servo as set by 
        :func:`SetAcceleration`.
        """
        return self.ipcon.send_request(self, Servo.FUNCTION_GET_ACCELERATION, (servo_num,), 'B', 'H')

    def set_output_voltage(self, voltage):
        """
        Sets the output voltages with which the servos are driven in mV.
        The minimum output voltage is 5000mV and the maximum output voltage is 
        9000mV.
        
        .. note::
         We recommend that you set this value to the maximum voltage that is
         specified for your servo, most servos achieve their maximum force only
         with high voltages.
        
        The default value is 5000.
        """
        self.ipcon.send_request(self, Servo.FUNCTION_SET_OUTPUT_VOLTAGE, (voltage,), 'H', '')

    def get_output_voltage(self):
        """
        Returns the output voltage as specified by :func:`SetOutputVoltage`.
        """
        return self.ipcon.send_request(self, Servo.FUNCTION_GET_OUTPUT_VOLTAGE, (), '', 'H')

    def set_pulse_width(self, servo_num, min, max):
        """
        Sets the minimum and maximum pulse width of the specified servo in µs.
        
        Usually, servos are controlled with a 
        `PWM <http://en.wikipedia.org/wiki/Pulse-width_modulation>`__, whereby the
        length of the pulse controls the position of the servo. Every servo has
        different minimum and maximum pulse widths, these can be specified with
        this function.
        
        If you have a datasheet for your servo that specifies the minimum and
        maximum pulse width, you should set the values accordingly. If your servo
        comes without any datasheet you have to find the values via trial and error.
        
        Both values have a range from 1 to 65535 (unsigned 16-bit integer). The
        minimum must be smaller than the maximum.
        
        The default values are 1000µs (1ms) and 2000µs (2ms) for minimum and 
        maximum pulse width.
        """
        self.ipcon.send_request(self, Servo.FUNCTION_SET_PULSE_WIDTH, (servo_num, min, max), 'B H H', '')

    def get_pulse_width(self, servo_num):
        """
        Returns the minimum and maximum pulse width for the specified servo as set by
        :func:`SetPulseWidth`.
        """
        return GetPulseWidth(*self.ipcon.send_request(self, Servo.FUNCTION_GET_PULSE_WIDTH, (servo_num,), 'B', 'H H'))

    def set_degree(self, servo_num, min, max):
        """
        Sets the minimum and maximum degree for the specified servo (by default
        given as °/100).
        
        This only specifies the abstract values between which the minimum and maximum
        pulse width is scaled. For example: If you specify a pulse width of 1000µs
        to 2000µs and a degree range of -90° to 90°, a call of :func:`SetPosition`
        with 0 will result in a pulse width of 1500µs 
        (-90° = 1000µs, 90° = 2000µs, etc.).
        
        Possible usage:
        
        * The datasheet of your servo specifies a range of 200° with the middle position
          at 110°. In this case you can set the minimum to -9000 and the maximum to 11000.
        * You measure a range of 220° on your servo and you don't have or need a middle
          position. In this case you can set the minimum to 0 and the maximum to 22000.
        * You have a linear servo with a drive length of 20cm, In this case you could
          set the minimum to 0 and the maximum to 20000. Now you can set the Position
          with :func:`SetPosition` with a resolution of cm/100. Also the velocity will
          have a resolution of cm/100s and the acceleration will have a resolution of
          cm/100s².
        * You don't care about units and just want the highest possible resolution. In
          this case you should set the minimum to -32767 and the maximum to 32767.
        * You have a brushless motor with a maximum speed of 10000 rpm and want to
          control it with a RC brushless motor controller. In this case you can set the
          minimum to 0 and the maximum to 10000. :func:`SetPosition` now controls the rpm.
        
        Both values have a possible range from -32767 to 32767 
        (signed 16-bit integer). The minimum must be smaller than the maximum.
        
        The default values are -9000 and 9000 for the minimum and maximum degree.
        """
        self.ipcon.send_request(self, Servo.FUNCTION_SET_DEGREE, (servo_num, min, max), 'B h h', '')

    def get_degree(self, servo_num):
        """
        Returns the minimum and maximum degree for the specified servo as set by
        :func:`SetDegree`.
        """
        return GetDegree(*self.ipcon.send_request(self, Servo.FUNCTION_GET_DEGREE, (servo_num,), 'B', 'h h'))

    def set_period(self, servo_num, period):
        """
        Sets the period of the specified servo in µs.
        
        Usually, servos are controlled with a 
        `PWM <http://en.wikipedia.org/wiki/Pulse-width_modulation>`__. Different
        servos expect PWMs with different periods. Most servos run well with a 
        period of about 20ms.
        
        If your servo comes with a datasheet that specifies a period, you should
        set it accordingly. If you don't have a datasheet and you have no idea
        what the correct period is, the default value (19.5ms) will most likely
        work fine. 
        
        The minimum possible period is 2000µs and the maximum is 65535µs.
        
        The default value is 19.5ms (19500µs).
        """
        self.ipcon.send_request(self, Servo.FUNCTION_SET_PERIOD, (servo_num, period), 'B H', '')

    def get_period(self, servo_num):
        """
        Returns the period for the specified servo as set by :func:`SetPeriod`.
        """
        return self.ipcon.send_request(self, Servo.FUNCTION_GET_PERIOD, (servo_num,), 'B', 'H')

    def get_servo_current(self, servo_num):
        """
        Returns the current consumption of the specified servo in mA.
        """
        return self.ipcon.send_request(self, Servo.FUNCTION_GET_SERVO_CURRENT, (servo_num,), 'B', 'H')

    def get_overall_current(self):
        """
        Returns the current consumption of all servos together in mA.
        """
        return self.ipcon.send_request(self, Servo.FUNCTION_GET_OVERALL_CURRENT, (), '', 'H')

    def get_stack_input_voltage(self):
        """
        Returns the stack input voltage in mV. The stack input voltage is the
        voltage that is supplied via the stack, i.e. it is given by a 
        Step-Down or Step-Up Power Supply.
        """
        return self.ipcon.send_request(self, Servo.FUNCTION_GET_STACK_INPUT_VOLTAGE, (), '', 'H')

    def get_external_input_voltage(self):
        """
        Returns the external input voltage in mV. The external input voltage is
        given via the black power input connector on the Servo Brick. 
         
        If there is an external input voltage and a stack input voltage, the motors
        will be driven by the external input voltage. If there is only a stack 
        voltage present, the motors will be driven by this voltage.
        
        .. warning::
         This means, if you have a high stack voltage and a low external voltage,
         the motors will be driven with the low external voltage. If you then remove
         the external connection, it will immediately be driven by the high
         stack voltage
        """
        return self.ipcon.send_request(self, Servo.FUNCTION_GET_EXTERNAL_INPUT_VOLTAGE, (), '', 'H')

    def set_minimum_voltage(self, voltage):
        """
        Sets the minimum voltage in mV, below which the :func:`UnderVoltage` callback
        is triggered. The minimum possible value that works with the Servo Brick is 5V.
        You can use this function to detect the discharge of a battery that is used
        to drive the stepper motor. If you have a fixed power supply, you likely do 
        not need this functionality.
        
        The default value is 5V (5000mV).
        """
        self.ipcon.send_request(self, Servo.FUNCTION_SET_MINIMUM_VOLTAGE, (voltage,), 'H', '')

    def get_minimum_voltage(self):
        """
        Returns the minimum voltage as set by :func:`SetMinimumVoltage`
        """
        return self.ipcon.send_request(self, Servo.FUNCTION_GET_MINIMUM_VOLTAGE, (), '', 'H')

    def reset(self):
        """
        Calling this function will reset the Brick. Calling this function
        on a Brick inside of a stack will reset the whole stack.
        
        After a reset you have to create new device objects,
        calling functions on the existing ones will result in
        undefined behavior!
        
        .. versionadded:: 1.1.3~(Firmware)
        """
        self.ipcon.send_request(self, Servo.FUNCTION_RESET, (), '', '')

    def get_chip_temperature(self):
        """
        Returns the temperature in °C/10 as measured inside the microcontroller. The
        value returned is not the ambient temperature!
        
        The temperature is only proportional to the real temperature and it has an
        accuracy of +-15%. Practically it is only useful as an indicator for
        temperature changes.
        
        .. versionadded:: 1.1.3~(Firmware)
        """
        return self.ipcon.send_request(self, Servo.FUNCTION_GET_CHIP_TEMPERATURE, (), '', 'h')

    def register_callback(self, id, callback):
        """
        Registers a callback with ID id to the function callback.
        """
        self.registered_callbacks[id] = callback
