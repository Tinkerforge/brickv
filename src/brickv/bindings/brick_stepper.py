# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2012-05-18.      #
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

GetSpeedRamping = namedtuple('SpeedRamping', ['acceleration', 'deacceleration'])

class Stepper(Device):
    """
    Device for controlling stepper motors
    """

    CALLBACK_UNDER_VOLTAGE = 31
    CALLBACK_POSITION_REACHED = 32

    FUNCTION_SET_MAX_VELOCITY = 1
    FUNCTION_GET_MAX_VELOCITY = 2
    FUNCTION_GET_CURRENT_VELOCITY = 3
    FUNCTION_SET_SPEED_RAMPING = 4
    FUNCTION_GET_SPEED_RAMPING = 5
    FUNCTION_FULL_BRAKE = 6
    FUNCTION_SET_CURRENT_POSITION = 7
    FUNCTION_GET_CURRENT_POSITION = 8
    FUNCTION_SET_TARGET_POSITION = 9
    FUNCTION_GET_TARGET_POSITION = 10
    FUNCTION_SET_STEPS = 11
    FUNCTION_GET_STEPS = 12
    FUNCTION_GET_REMAINING_STEPS = 13
    FUNCTION_SET_STEP_MODE = 14
    FUNCTION_GET_STEP_MODE = 15
    FUNCTION_DRIVE_FORWARD = 16
    FUNCTION_DRIVE_BACKWARD = 17
    FUNCTION_STOP = 18
    FUNCTION_GET_STACK_INPUT_VOLTAGE = 19
    FUNCTION_GET_EXTERNAL_INPUT_VOLTAGE = 20
    FUNCTION_GET_CURRENT_CONSUMPTION = 21
    FUNCTION_SET_MOTOR_CURRENT = 22
    FUNCTION_GET_MOTOR_CURRENT = 23
    FUNCTION_ENABLE = 24
    FUNCTION_DISABLE = 25
    FUNCTION_IS_ENABLED = 26
    FUNCTION_SET_DECAY = 27
    FUNCTION_GET_DECAY = 28
    FUNCTION_SET_MINIMUM_VOLTAGE = 29
    FUNCTION_GET_MINIMUM_VOLTAGE = 30
    FUNCTION_SET_SYNC_RECT = 33
    FUNCTION_IS_SYNC_RECT = 34

    def __init__(self, uid):
        """
        Creates an object with the unique device ID *uid*. This object can
        then be added to the IP connection.
        """
        Device.__init__(self, uid)

        self.expected_name = 'Stepper Brick';

        self.binding_version = [1, 0, 0]

        self.callbacks_format[Stepper.CALLBACK_UNDER_VOLTAGE] = 'H'
        self.callbacks_format[Stepper.CALLBACK_POSITION_REACHED] = 'i'

    def set_max_velocity(self, velocity):
        """
        Sets the maximum velocity of the stepper motor in steps per second.
        This function does *not* start the motor, it merely sets the maximum
        velocity the stepper motor is accelerated to. To get the motor running use
        either :func:`SetTargetPosition`, :func:`SetSteps`, :func:`DriveForward` or
        :func:`DriveBackward`.
        """
        self.ipcon.write(self, Stepper.FUNCTION_SET_MAX_VELOCITY, (velocity,), 'H', '')

    def get_max_velocity(self):
        """
        Returns the velocity as set by :func:`SetMaxVelocity`.
        """
        return self.ipcon.write(self, Stepper.FUNCTION_GET_MAX_VELOCITY, (), '', 'H')

    def get_current_velocity(self):
        """
        Returns the *current* velocity of the stepper motor in steps per second.
        """
        return self.ipcon.write(self, Stepper.FUNCTION_GET_CURRENT_VELOCITY, (), '', 'H')

    def set_speed_ramping(self, acceleration, deacceleration):
        """
        Sets the acceleration and deacceleration of the stepper motor. The values
        are given in *steps/s²*. An acceleration of 1000 means, that
        every second the velocity is increased by 1000 *steps/s*.
        
        For example: If the current velocity is 0 and you want to accelerate to a
        velocity of 8000 *steps/s* in 10 seconds, you should set an acceleration
        of 800 *steps/s²*.
        
        An acceleration/deacceleration of 0 means instantaneous 
        acceleration/deacceleration (not recommended)
        
        The default value is 1000 for both
        """
        self.ipcon.write(self, Stepper.FUNCTION_SET_SPEED_RAMPING, (acceleration, deacceleration), 'H H', '')

    def get_speed_ramping(self):
        """
        Returns the acceleration and deacceleration as set by 
        :func:`SetSpeedRamping`.
        """
        return GetSpeedRamping(*self.ipcon.write(self, Stepper.FUNCTION_GET_SPEED_RAMPING, (), '', 'H H'))

    def full_brake(self):
        """
        Executes an active full brake. 
         
         .. warning::
          This function is for emergency purposes,
          where an immediate brake is necessary. Depending on the current velocity and
          the strength of the motor, a full brake can be quite violent.
        
        Call :func:`Stop` if you just want to stop the motor.
        """
        self.ipcon.write(self, Stepper.FUNCTION_FULL_BRAKE, (), '', '')

    def set_current_position(self, position):
        """
        Sets the current steps of the internal step counter. This can be used to
        set the current position to 0 when some kind of starting position
        is reached (e.g. when a CNC machine reaches a corner).
        """
        self.ipcon.write(self, Stepper.FUNCTION_SET_CURRENT_POSITION, (position,), 'i', '')

    def get_current_position(self):
        """
        Returns the current position of the stepper motor in steps. On startup
        the position is 0. The steps are counted with all possible driving
        functions (:func:`SetTargetPosition`, :func:`SetSteps`, :func:`DriveForward` or
        :func:`DriveBackward`). It also is possible to reset the steps to 0 or
        set them to any other desired value with :func:`SetCurrentPosition`.
        """
        return self.ipcon.write(self, Stepper.FUNCTION_GET_CURRENT_POSITION, (), '', 'i')

    def set_target_position(self, position):
        """
        Sets the target position of the stepper motor in steps. For example,
        if the current position of the motor is 500 and :func:`SetTargetPosition` is
        called with 1000, the stepper motor will drive 500 steps forward. It will
        use the velocity, acceleration and deacceleration as set by
        :func:`SetMaxVelocity` and :func:`SetSpeedRamping`.
        
        A call of :func:`SetTargetPosition` with the parameter *x* is equivalent to
        a call of :func:`SetSteps` with the parameter 
        (*x* - :func:`GetCurrentPosition`).
        """
        self.ipcon.write(self, Stepper.FUNCTION_SET_TARGET_POSITION, (position,), 'i', '')

    def get_target_position(self):
        """
        Returns the last target position as set by :func:`SetTargetPosition`.
        """
        return self.ipcon.write(self, Stepper.FUNCTION_GET_TARGET_POSITION, (), '', 'i')

    def set_steps(self, steps):
        """
        Sets the number of steps the stepper motor should run. Positive values
        will drive the motor forward and negative values backward. 
        The velocity, acceleration and deacceleration as set by
        :func:`SetMaxVelocity` and :func:`SetSpeedRamping` will be used.
        """
        self.ipcon.write(self, Stepper.FUNCTION_SET_STEPS, (steps,), 'i', '')

    def get_steps(self):
        """
        Returns the last steps as set by :func:`SetSteps`.
        """
        return self.ipcon.write(self, Stepper.FUNCTION_GET_STEPS, (), '', 'i')

    def get_remaining_steps(self):
        """
        Returns the remaining steps of the last call of :func:`SetSteps`.
        For example, if :func:`SetSteps` is called with 2000 and 
        :func:`GetRemainingSteps` is called after the motor has run for 500 steps,
        it will return 1500.
        """
        return self.ipcon.write(self, Stepper.FUNCTION_GET_REMAINING_STEPS, (), '', 'i')

    def set_step_mode(self, mode):
        """
        Sets the step mode of the stepper motor. Possible values are:
        
        * Full Step = 1
        * Half Step = 2
        * Quarter Step = 4
        * Eighth Step = 8
        
        A higher value will increase the resolution and
        decrease the torque of the stepper motor.
        
        The default value is 8 (Eighth Step).
        """
        self.ipcon.write(self, Stepper.FUNCTION_SET_STEP_MODE, (mode,), 'B', '')

    def get_step_mode(self):
        """
        Returns the step mode as set by :func:`SetStepMode`.
        """
        return self.ipcon.write(self, Stepper.FUNCTION_GET_STEP_MODE, (), '', 'B')

    def drive_forward(self):
        """
        Drives the stepper motor forward until :func:`DriveBackward` or
        :func:`Stop` is called. The velocity, acceleration and deacceleration as 
        set by :func:`SetMaxVelocity` and :func:`SetSpeedRamping` will be used.
        """
        self.ipcon.write(self, Stepper.FUNCTION_DRIVE_FORWARD, (), '', '')

    def drive_backward(self):
        """
        Drives the stepper motor backward until :func:`DriveForward` or
        :func:`Stop` is triggered. The velocity, acceleration and deacceleration as
        set by :func:`SetMaxVelocity` and :func:`SetSpeedRamping` will be used.
        """
        self.ipcon.write(self, Stepper.FUNCTION_DRIVE_BACKWARD, (), '', '')

    def stop(self):
        """
        Stops the stepper motor with the deacceleration as set by 
        :func:`SetSpeedRamping`.
        """
        self.ipcon.write(self, Stepper.FUNCTION_STOP, (), '', '')

    def get_stack_input_voltage(self):
        """
        Returns the stack input voltage in mV. The stack input voltage is the
        voltage that is supplied via the stack, i.e. it is given by a 
        Step-Down or Step-Up Power Supply.
        """
        return self.ipcon.write(self, Stepper.FUNCTION_GET_STACK_INPUT_VOLTAGE, (), '', 'H')

    def get_external_input_voltage(self):
        """
        Returns the external input voltage in mV. The external input voltage is
        given via the black power input connector on the Stepper Brick. 
         
        If there is an external input voltage and a stack input voltage, the motor
        will be driven by the external input voltage. If there is only a stack 
        voltage present, the motor will be driven by this voltage.
        
         .. warning:: 
          This means, if you have a high stack voltage and a low external voltage,
          the motor will be driven with the low external voltage. If you then remove
          the external connection, it will immediately be driven by the high
          stack voltage
        """
        return self.ipcon.write(self, Stepper.FUNCTION_GET_EXTERNAL_INPUT_VOLTAGE, (), '', 'H')

    def get_current_consumption(self):
        """
        Returns the current consumption of the motor in mA.
        """
        return self.ipcon.write(self, Stepper.FUNCTION_GET_CURRENT_CONSUMPTION, (), '', 'H')

    def set_motor_current(self, current):
        """
        Sets the current in mA with which the motor will be driven.
        The minimum value is 100mA, the maximum value 2291mA and the 
        default value is 800mA.
        
         .. warning::
          Do not set this value above the specifications of your stepper motor.
          Otherwise it may damage your motor.
        """
        self.ipcon.write(self, Stepper.FUNCTION_SET_MOTOR_CURRENT, (current,), 'H', '')

    def get_motor_current(self):
        """
        Returns the current as set by :func:`SetMotorCurrent`.
        """
        return self.ipcon.write(self, Stepper.FUNCTION_GET_MOTOR_CURRENT, (), '', 'H')

    def enable(self):
        """
        Enables the motor. The motor can be configured (maximum velocity, 
        acceleration, etc) before it is enabled.
        """
        self.ipcon.write(self, Stepper.FUNCTION_ENABLE, (), '', '')

    def disable(self):
        """
        Disables the motor. The configurations are kept (maximum velocity, 
        acceleration, etc) but the motor is not driven until it is enabled again.
        """
        self.ipcon.write(self, Stepper.FUNCTION_DISABLE, (), '', '')

    def is_enabled(self):
        """
        Returns true if the motor is enabled, false otherwise.
        """
        return self.ipcon.write(self, Stepper.FUNCTION_IS_ENABLED, (), '', '?')

    def set_decay(self, decay):
        """
        Sets the decay mode of the stepper motor. The possible value range is
        between 0 and 65535. A value of 0 sets the fast decay mode, a value of
        65535 sets the slow decay mode and a value in between sets the mixed
        decay mode.
        
        Changing the decay mode is only possible if synchronous rectification
        is enabled (see :func:`SetSyncRect`).
        
        For a good explanation of the different decay modes see 
        `this <http://robot.avayanex.com/?p=86/>`_ blog post by Avayan.
        
        A good decay mode is unfortunately different for every motor. The best
        way to work out a good decay mode for your stepper motor, if you can't
        measure the current with an oscilloscope, is to listen to the sound of
        the motor. If the value is too low, you often hear a high pitched 
        sound and if it is too high you can often hear a humming sound.
        
        Generally, fast decay mode (small value) will be noisier but also
        allow higher motor speeds.
        
        The default value is 10000.
         .. note::
          There is unfortunately no formula to calculate a perfect decay
          mode for a given stepper motor. If you have problems with loud noises
          or the maximum motor speed is too slow, you should try to tinker with
          the decay value
        """
        self.ipcon.write(self, Stepper.FUNCTION_SET_DECAY, (decay,), 'H', '')

    def get_decay(self):
        """
        Returns the decay mode as set by :func:`SetDecay`
        """
        return self.ipcon.write(self, Stepper.FUNCTION_GET_DECAY, (), '', 'H')

    def set_minimum_voltage(self, voltage):
        """
        Sets the minimum voltage in mV, below which the :func:`UnderVoltage` callback
        is triggered. The minimum possible value that works with the Stepper Brick is 8V.
        You can use this function to detect the discharge of a battery that is used
        to drive the stepper motor. If you have a fixed power supply, you likely do 
        not need this functionality.
        
        The default value is 8V.
        """
        self.ipcon.write(self, Stepper.FUNCTION_SET_MINIMUM_VOLTAGE, (voltage,), 'H', '')

    def get_minimum_voltage(self):
        """
        Returns the minimum voltage as set by :func:`SetMinimumVoltage`.
        """
        return self.ipcon.write(self, Stepper.FUNCTION_GET_MINIMUM_VOLTAGE, (), '', 'H')

    def set_sync_rect(self, sync_rect):
        """
        Turns synchronous rectification on or off (true/false).
        
        With synchronous rectification on, the decay can be changed
        (see :func:`SetDecay`). Without synchronous rectification fast
        decay is used.
        
        For an explanation of synchronous rectification see 
        `here <http://en.wikipedia.org/wiki/Active_rectification>`__.
        
        .. warning::
         If you want to use high speeds (> 10000 steps/s) for a large 
         stepper motor with a large inductivity we strongly
         suggest that you disable synchronous rectification. Otherwise the
         Brick may not be able to cope with the load and overheat.
        
        The default value is false.
        """
        self.ipcon.write(self, Stepper.FUNCTION_SET_SYNC_RECT, (sync_rect,), '?', '')

    def is_sync_rect(self):
        """
        Returns true if synchronous rectification is enabled, false otherwise.
        """
        return self.ipcon.write(self, Stepper.FUNCTION_IS_SYNC_RECT, (), '', '?')

    def register_callback(self, cb, func):
        """
        Registers a callback with ID cb to the function func.
        """
        self.callbacks[cb] = func
