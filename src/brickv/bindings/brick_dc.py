# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2012-05-23.      #
#                                                           #
# If you have a bugfix for this file and want to commit it, #
# please fix the bug in the generator. You can find a link  #
# to the generator git on tinkerforge.com                   #
#############################################################

try:
    from collections import namedtuple
except ImportError:
    from .ip_connection import namedtuple
from .ip_connection import Device, IPConnection, Error


class DC(Device):
    """
    Device for controlling DC motors
    """

    CALLBACK_UNDER_VOLTAGE = 21
    CALLBACK_EMERGENCY_SHUTDOWN = 22
    CALLBACK_VELOCITY_REACHED = 23
    CALLBACK_CURRENT_VELOCITY = 24

    FUNCTION_SET_VELOCITY = 1
    FUNCTION_GET_VELOCITY = 2
    FUNCTION_GET_CURRENT_VELOCITY = 3
    FUNCTION_SET_ACCELERATION = 4
    FUNCTION_GET_ACCELERATION = 5
    FUNCTION_SET_PWM_FREQUENCY = 6
    FUNCTION_GET_PWM_FREQUENCY = 7
    FUNCTION_FULL_BRAKE = 8
    FUNCTION_GET_STACK_INPUT_VOLTAGE = 9
    FUNCTION_GET_EXTERNAL_INPUT_VOLTAGE = 10
    FUNCTION_GET_CURRENT_CONSUMPTION = 11
    FUNCTION_ENABLE = 12
    FUNCTION_DISABLE = 13
    FUNCTION_IS_ENABLED = 14
    FUNCTION_SET_MINIMUM_VOLTAGE = 15
    FUNCTION_GET_MINIMUM_VOLTAGE = 16
    FUNCTION_SET_DRIVE_MODE = 17
    FUNCTION_GET_DRIVE_MODE = 18
    FUNCTION_SET_CURRENT_VELOCITY_PERIOD = 19
    FUNCTION_GET_CURRENT_VELOCITY_PERIOD = 20

    def __init__(self, uid):
        """
        Creates an object with the unique device ID *uid*. This object can
        then be added to the IP connection.
        """
        Device.__init__(self, uid)

        self.expected_name = 'DC Brick'

        self.binding_version = [1, 0, 0]

        self.callbacks_format[DC.CALLBACK_UNDER_VOLTAGE] = 'H'
        self.callbacks_format[DC.CALLBACK_EMERGENCY_SHUTDOWN] = ''
        self.callbacks_format[DC.CALLBACK_VELOCITY_REACHED] = 'h'
        self.callbacks_format[DC.CALLBACK_CURRENT_VELOCITY] = 'h'

    def set_velocity(self, velocity):
        """
        Sets the velocity of the motor. Whereas -32767 is full speed backward,
        0 is stop and 32767 is full speed forward. Depending on the 
        acceleration (see :func:`SetAcceleration`), the motor is not immediately 
        brought to the velocity but smoothly accelerated.
        
        The velocity describes the duty cycle of the PWM with which the motor is
        controlled, e.g. a velocity of 3277 sets a PWM with a 10% duty cycle.
        You can not only control the duty cycle of the PWM but also the frequency,
        see :func:`SetPWMFrequency`.
        
        The default velocity is 0.
        """
        self.ipcon.write(self, DC.FUNCTION_SET_VELOCITY, (velocity,), 'h', '')

    def get_velocity(self):
        """
        Returns the velocity as set by :func:`SetVelocity`.
        """
        return self.ipcon.write(self, DC.FUNCTION_GET_VELOCITY, (), '', 'h')

    def get_current_velocity(self):
        """
        Returns the *current* velocity of the motor. This value is different
        from :func:`GetVelocity` whenever the motor is currently accelerating
        to a goal set by :func:`SetVelocity`.
        """
        return self.ipcon.write(self, DC.FUNCTION_GET_CURRENT_VELOCITY, (), '', 'h')

    def set_acceleration(self, acceleration):
        """
        Sets the acceleration of the motor. It is given in *velocity/s*. An
        acceleration of 10000 means, that every second the velocity is increased
        by 10000 (or about 30% duty cycle).
        
        For example: If the current velocity is 0 and you want to accelerate to a
        velocity of 16000 (about 50% duty cycle) in 10 seconds, you should set
        an acceleration of 1600.
        
        If acceleration is set to 0, there is no speed ramping, i.e. a new velocity
        is immediately given to the motor.
        
        The default acceleration is 10000.
        """
        self.ipcon.write(self, DC.FUNCTION_SET_ACCELERATION, (acceleration,), 'H', '')

    def get_acceleration(self):
        """
        Returns the acceleration as set by :func:`SetAcceleration`.
        """
        return self.ipcon.write(self, DC.FUNCTION_GET_ACCELERATION, (), '', 'H')

    def set_pwm_frequency(self, frequency):
        """
        Sets the frequency (in Hz) of the PWM with which the motor is driven.
        The possible range of the frequency is 1-20000Hz. Often a high frequency
        is less noisy and the motor runs smoother. However, with a low frequency
        there are less switches and therefore fewer switching losses. Also with
        most motors lower frequencies enable higher torque.
        
        If you have no idea what all this means, just ignore this function and use
        the default frequency, it will very likely work fine.
        
        The default frequency is 15 kHz.
        """
        self.ipcon.write(self, DC.FUNCTION_SET_PWM_FREQUENCY, (frequency,), 'H', '')

    def get_pwm_frequency(self):
        """
        Returns the PWM frequency (in Hz) as set by :func:`SetPWMFrequency`.
        """
        return self.ipcon.write(self, DC.FUNCTION_GET_PWM_FREQUENCY, (), '', 'H')

    def full_brake(self):
        """
        Executes an active full brake. 
         
         .. warning::
          This function is for emergency purposes,
          where an immediate brake is necessary. Depending on the current velocity and
          the strength of the motor, a full brake can be quite violent.
        
        Call :func:`SetVelocity` with 0 if you just want to stop the motor.
        """
        self.ipcon.write(self, DC.FUNCTION_FULL_BRAKE, (), '', '')

    def get_stack_input_voltage(self):
        """
        Returns the stack input voltage in mV. The stack input voltage is the
        voltage that is supplied via the stack, i.e. it is given by a 
        Step-Down or Step-Up Power Supply.
        """
        return self.ipcon.write(self, DC.FUNCTION_GET_STACK_INPUT_VOLTAGE, (), '', 'H')

    def get_external_input_voltage(self):
        """
        Returns the external input voltage in mV. The external input voltage is
        given via the black power input connector on the DC Brick. 
         
        If there is an external input voltage and a stack input voltage, the motor
        will be driven by the external input voltage. If there is only a stack 
        voltage present, the motor will be driven by this voltage.
        
         .. warning:: 
          This means, if you have a high stack voltage and a low external voltage,
          the motor will be driven with the low external voltage. If you then remove
          the external connection, it will immediately be driven by the high
          stack voltage.
        """
        return self.ipcon.write(self, DC.FUNCTION_GET_EXTERNAL_INPUT_VOLTAGE, (), '', 'H')

    def get_current_consumption(self):
        """
        Returns the current consumption of the motor in mA.
        """
        return self.ipcon.write(self, DC.FUNCTION_GET_CURRENT_CONSUMPTION, (), '', 'H')

    def enable(self):
        """
        Enables the motor. The motor can be configured (velocity, 
        acceleration, etc) before it is enabled.
        """
        self.ipcon.write(self, DC.FUNCTION_ENABLE, (), '', '')

    def disable(self):
        """
        Disables the motor. The configurations are kept (velocity, 
        acceleration, etc) but the motor is not driven until it is enabled again.
        """
        self.ipcon.write(self, DC.FUNCTION_DISABLE, (), '', '')

    def is_enabled(self):
        """
        Returns true if the motor is enabled, false otherwise.
        """
        return self.ipcon.write(self, DC.FUNCTION_IS_ENABLED, (), '', '?')

    def set_minimum_voltage(self, voltage):
        """
        Sets the minimum voltage in mV, below which the :func:`UnderVoltage` callback
        is triggered. The minimum possible value that works with the DC Brick is 5V.
        You can use this function to detect the discharge of a battery that is used
        to drive the motor. If you have a fixed power supply, you likely do not need 
        this functionality.
        
        The default value is 5V.
        """
        self.ipcon.write(self, DC.FUNCTION_SET_MINIMUM_VOLTAGE, (voltage,), 'H', '')

    def get_minimum_voltage(self):
        """
        Returns the minimum voltage as set by :func:`SetMinimumVoltage`
        """
        return self.ipcon.write(self, DC.FUNCTION_GET_MINIMUM_VOLTAGE, (), '', 'H')

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
        Advantages are: Less current consumption and less demands on the motor/driver.
        
        The default value is 0 = Drive/Brake.
        """
        self.ipcon.write(self, DC.FUNCTION_SET_DRIVE_MODE, (mode,), 'B', '')

    def get_drive_mode(self):
        """
        Returns the drive mode, as set by :func:`SetDriveMode`.
        """
        return self.ipcon.write(self, DC.FUNCTION_GET_DRIVE_MODE, (), '', 'B')

    def set_current_velocity_period(self, period):
        """
        Sets a period in ms with which the :func:`CurrentVelocity` callback is triggered.
        A period of 0 turns the callback off.
        
        The default value is 0.
        """
        self.ipcon.write(self, DC.FUNCTION_SET_CURRENT_VELOCITY_PERIOD, (period,), 'H', '')

    def get_current_velocity_period(self):
        """
        Returns the period as set by :func:`SetCurrentVelocityPeriod`.
        """
        return self.ipcon.write(self, DC.FUNCTION_GET_CURRENT_VELOCITY_PERIOD, (), '', 'H')

    def register_callback(self, cb, func):
        """
        Registers a callback with ID cb to the function func.
        """
        self.callbacks[cb] = func
