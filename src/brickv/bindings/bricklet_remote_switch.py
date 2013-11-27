# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2013-11-27.      #
#                                                           #
# Bindings Version 2.0.12                                    #
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

GetIdentity = namedtuple('Identity', ['uid', 'connected_uid', 'position', 'hardware_version', 'firmware_version', 'device_identifier'])

class BrickletRemoteSwitch(Device):
    """
    Device that controls mains switches remotely
    """

    DEVICE_IDENTIFIER = 235

    CALLBACK_SWITCHING_DONE = 3

    FUNCTION_SWITCH_SOCKET = 1
    FUNCTION_GET_SWITCHING_STATE = 2
    FUNCTION_SET_REPEATS = 4
    FUNCTION_GET_REPEATS = 5
    FUNCTION_GET_IDENTITY = 255

    SWITCH_TO_OFF = 0
    SWITCH_TO_ON = 1
    SWITCHING_STATE_READY = 0
    SWITCHING_STATE_BUSY = 1

    def __init__(self, uid, ipcon):
        """
        Creates an object with the unique device ID *uid* and adds it to
        the IP Connection *ipcon*.
        """
        Device.__init__(self, uid, ipcon)

        self.api_version = (2, 0, 0)

        self.response_expected[BrickletRemoteSwitch.FUNCTION_SWITCH_SOCKET] = BrickletRemoteSwitch.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletRemoteSwitch.FUNCTION_GET_SWITCHING_STATE] = BrickletRemoteSwitch.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletRemoteSwitch.CALLBACK_SWITCHING_DONE] = BrickletRemoteSwitch.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletRemoteSwitch.FUNCTION_SET_REPEATS] = BrickletRemoteSwitch.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletRemoteSwitch.FUNCTION_GET_REPEATS] = BrickletRemoteSwitch.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletRemoteSwitch.FUNCTION_GET_IDENTITY] = BrickletRemoteSwitch.RESPONSE_EXPECTED_ALWAYS_TRUE

        self.callback_formats[BrickletRemoteSwitch.CALLBACK_SWITCHING_DONE] = ''

    def switch_socket(self, house_code, receiver_code, switch_to):
        """
        To switch a socket you have to give the house code, receiver code and the
        state (on or off) you want to switch to.
        
        A detailed description on how you can find the house and receiver code
        can be found :ref:`here <remote_switch_bricklet_house_and_receiver_code>`.
        """
        self.ipcon.send_request(self, BrickletRemoteSwitch.FUNCTION_SWITCH_SOCKET, (house_code, receiver_code, switch_to), 'B B B', '')

    def get_switching_state(self):
        """
        Returns the current switching state. If the current state is busy, the
        Bricklet is currently sending a code to switch a socket. It will not
        accept any calls of :func:`SwitchSocket` until the state changes to ready.
        
        How long the switching takes is dependent on the number of repeats, see
        :func:`SetRepeats`.
        """
        return self.ipcon.send_request(self, BrickletRemoteSwitch.FUNCTION_GET_SWITCHING_STATE, (), '', 'B')

    def set_repeats(self, repeats):
        """
        Sets the number of times the code is send when :func:`SwitchSocket` is called.
        The repeats basically correspond to the amount of time that a button of the
        remote is pressed. 
        
        Some dimmers are controlled by the length of a button pressed,
        this can be simulated by increasing the repeats.
        
        The default value is 5.
        """
        self.ipcon.send_request(self, BrickletRemoteSwitch.FUNCTION_SET_REPEATS, (repeats,), 'B', '')

    def get_repeats(self):
        """
        Returns the number of repeats as set by :func:`SetRepeats`.
        """
        return self.ipcon.send_request(self, BrickletRemoteSwitch.FUNCTION_GET_REPEATS, (), '', 'B')

    def get_identity(self):
        """
        Returns the UID, the UID where the Bricklet is connected to, 
        the position, the hardware and firmware version as well as the
        device identifier.
        
        The position can be 'a', 'b', 'c' or 'd'.
        
        The device identifiers can be found :ref:`here <device_identifier>`.
        
        .. versionadded:: 2.0.0~(Plugin)
        """
        return GetIdentity(*self.ipcon.send_request(self, BrickletRemoteSwitch.FUNCTION_GET_IDENTITY, (), '', '8s 8s c 3B 3B H'))

    def register_callback(self, id, callback):
        """
        Registers a callback with ID *id* to the function *callback*.
        """
        self.registered_callbacks[id] = callback

RemoteSwitch = BrickletRemoteSwitch # for backward compatibility
