# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2018-09-28.      #
#                                                           #
# Python Bindings Version 2.1.18                            #
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

GetIdentity = namedtuple('Identity', ['uid', 'connected_uid', 'position', 'hardware_version', 'firmware_version', 'device_identifier'])

class BrickletRemoteSwitch(Device):
    """
    Controls remote mains switches
    """

    DEVICE_IDENTIFIER = 235
    DEVICE_DISPLAY_NAME = 'Remote Switch Bricklet'
    DEVICE_URL_PART = 'remote_switch' # internal

    CALLBACK_SWITCHING_DONE = 3


    FUNCTION_SWITCH_SOCKET = 1
    FUNCTION_GET_SWITCHING_STATE = 2
    FUNCTION_SET_REPEATS = 4
    FUNCTION_GET_REPEATS = 5
    FUNCTION_SWITCH_SOCKET_A = 6
    FUNCTION_SWITCH_SOCKET_B = 7
    FUNCTION_DIM_SOCKET_B = 8
    FUNCTION_SWITCH_SOCKET_C = 9
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

        self.api_version = (2, 0, 1)

        self.response_expected[BrickletRemoteSwitch.FUNCTION_SWITCH_SOCKET] = BrickletRemoteSwitch.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletRemoteSwitch.FUNCTION_GET_SWITCHING_STATE] = BrickletRemoteSwitch.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletRemoteSwitch.FUNCTION_SET_REPEATS] = BrickletRemoteSwitch.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletRemoteSwitch.FUNCTION_GET_REPEATS] = BrickletRemoteSwitch.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletRemoteSwitch.FUNCTION_SWITCH_SOCKET_A] = BrickletRemoteSwitch.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletRemoteSwitch.FUNCTION_SWITCH_SOCKET_B] = BrickletRemoteSwitch.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletRemoteSwitch.FUNCTION_DIM_SOCKET_B] = BrickletRemoteSwitch.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletRemoteSwitch.FUNCTION_SWITCH_SOCKET_C] = BrickletRemoteSwitch.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletRemoteSwitch.FUNCTION_GET_IDENTITY] = BrickletRemoteSwitch.RESPONSE_EXPECTED_ALWAYS_TRUE

        self.callback_formats[BrickletRemoteSwitch.CALLBACK_SWITCHING_DONE] = ''


    def switch_socket(self, house_code, receiver_code, switch_to):
        """
        This function is deprecated, use :func:`Switch Socket A` instead.
        """
        house_code = int(house_code)
        receiver_code = int(receiver_code)
        switch_to = int(switch_to)

        self.ipcon.send_request(self, BrickletRemoteSwitch.FUNCTION_SWITCH_SOCKET, (house_code, receiver_code, switch_to), 'B B B', '')

    def get_switching_state(self):
        """
        Returns the current switching state. If the current state is busy, the
        Bricklet is currently sending a code to switch a socket. It will not
        accept any calls of :func:`Switch Socket` until the state changes to ready.

        How long the switching takes is dependent on the number of repeats, see
        :func:`Set Repeats`.
        """
        return self.ipcon.send_request(self, BrickletRemoteSwitch.FUNCTION_GET_SWITCHING_STATE, (), '', 'B')

    def set_repeats(self, repeats):
        """
        Sets the number of times the code is send when of the :func:`Switch Socket`
        functions is called. The repeats basically correspond to the amount of time
        that a button of the remote is pressed.

        Some dimmers are controlled by the length of a button pressed,
        this can be simulated by increasing the repeats.

        The default value is 5.
        """
        repeats = int(repeats)

        self.ipcon.send_request(self, BrickletRemoteSwitch.FUNCTION_SET_REPEATS, (repeats,), 'B', '')

    def get_repeats(self):
        """
        Returns the number of repeats as set by :func:`Set Repeats`.
        """
        return self.ipcon.send_request(self, BrickletRemoteSwitch.FUNCTION_GET_REPEATS, (), '', 'B')

    def switch_socket_a(self, house_code, receiver_code, switch_to):
        """
        To switch a type A socket you have to give the house code, receiver code and the
        state (on or off) you want to switch to.

        The house code and receiver code have a range of 0 to 31 (5bit).

        A detailed description on how you can figure out the house and receiver code
        can be found :ref:`here <remote_switch_bricklet_type_a_house_and_receiver_code>`.

        .. versionadded:: 2.0.1$nbsp;(Plugin)
        """
        house_code = int(house_code)
        receiver_code = int(receiver_code)
        switch_to = int(switch_to)

        self.ipcon.send_request(self, BrickletRemoteSwitch.FUNCTION_SWITCH_SOCKET_A, (house_code, receiver_code, switch_to), 'B B B', '')

    def switch_socket_b(self, address, unit, switch_to):
        """
        To switch a type B socket you have to give the address, unit and the state
        (on or off) you want to switch to.

        The address has a range of 0 to 67108863 (26bit) and the unit has a range
        of 0 to 15 (4bit). To switch all devices with the same address use 255 for
        the unit.

        A detailed description on how you can teach a socket the address and unit can
        be found :ref:`here <remote_switch_bricklet_type_b_address_and_unit>`.

        .. versionadded:: 2.0.1$nbsp;(Plugin)
        """
        address = int(address)
        unit = int(unit)
        switch_to = int(switch_to)

        self.ipcon.send_request(self, BrickletRemoteSwitch.FUNCTION_SWITCH_SOCKET_B, (address, unit, switch_to), 'I B B', '')

    def dim_socket_b(self, address, unit, dim_value):
        """
        To control a type B dimmer you have to give the address, unit and the
        dim value you want to set the dimmer to.

        The address has a range of 0 to 67108863 (26bit), the unit and the dim value
        has a range of 0 to 15 (4bit).

        A detailed description on how you can teach a dimmer the address and unit can
        be found :ref:`here <remote_switch_bricklet_type_b_address_and_unit>`.

        .. versionadded:: 2.0.1$nbsp;(Plugin)
        """
        address = int(address)
        unit = int(unit)
        dim_value = int(dim_value)

        self.ipcon.send_request(self, BrickletRemoteSwitch.FUNCTION_DIM_SOCKET_B, (address, unit, dim_value), 'I B B', '')

    def switch_socket_c(self, system_code, device_code, switch_to):
        """
        To switch a type C socket you have to give the system code, device code and the
        state (on or off) you want to switch to.

        The system code has a range of 'A' to 'P' (4bit) and the device code has a
        range of 1 to 16 (4bit).

        A detailed description on how you can figure out the system and device code
        can be found :ref:`here <remote_switch_bricklet_type_c_system_and_device_code>`.

        .. versionadded:: 2.0.1$nbsp;(Plugin)
        """
        system_code = create_char(system_code)
        device_code = int(device_code)
        switch_to = int(switch_to)

        self.ipcon.send_request(self, BrickletRemoteSwitch.FUNCTION_SWITCH_SOCKET_C, (system_code, device_code, switch_to), 'c B B', '')

    def get_identity(self):
        """
        Returns the UID, the UID where the Bricklet is connected to,
        the position, the hardware and firmware version as well as the
        device identifier.

        The position can be 'a', 'b', 'c' or 'd'.

        The device identifier numbers can be found :ref:`here <device_identifier>`.
        |device_identifier_constant|
        """
        return GetIdentity(*self.ipcon.send_request(self, BrickletRemoteSwitch.FUNCTION_GET_IDENTITY, (), '', '8s 8s c 3B 3B H'))

    def register_callback(self, callback_id, function):
        """
        Registers the given *function* with the given *callback_id*.
        """
        if function is None:
            self.registered_callbacks.pop(callback_id, None)
        else:
            self.registered_callbacks[callback_id] = function

RemoteSwitch = BrickletRemoteSwitch # for backward compatibility
