# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2016-02-10.      #
#                                                           #
# Python Bindings Version 2.1.8                             #
#                                                           #
# If you have a bugfix for this file and want to commit it, #
# please fix the bug in the generator. You can find a link  #
# to the generators git repository on tinkerforge.com       #
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

class BrickletTilt(Device):
    """
    Detects inclination of Bricklet (tilt switch open/closed)
    """

    DEVICE_IDENTIFIER = 239
    DEVICE_DISPLAY_NAME = 'Tilt Bricklet'

    CALLBACK_TILT_STATE = 5

    FUNCTION_GET_TILT_STATE = 1
    FUNCTION_ENABLE_TILT_STATE_CALLBACK = 2
    FUNCTION_DISABLE_TILT_STATE_CALLBACK = 3
    FUNCTION_IS_TILT_STATE_CALLBACK_ENABLED = 4
    FUNCTION_GET_IDENTITY = 255

    TILT_STATE_CLOSED = 0
    TILT_STATE_OPEN = 1
    TILT_STATE_CLOSED_VIBRATING = 2

    def __init__(self, uid, ipcon):
        """
        Creates an object with the unique device ID *uid* and adds it to
        the IP Connection *ipcon*.
        """
        Device.__init__(self, uid, ipcon)

        self.api_version = (2, 0, 0)

        self.response_expected[BrickletTilt.FUNCTION_GET_TILT_STATE] = BrickletTilt.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletTilt.FUNCTION_ENABLE_TILT_STATE_CALLBACK] = BrickletTilt.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletTilt.FUNCTION_DISABLE_TILT_STATE_CALLBACK] = BrickletTilt.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletTilt.FUNCTION_IS_TILT_STATE_CALLBACK_ENABLED] = BrickletTilt.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletTilt.CALLBACK_TILT_STATE] = BrickletTilt.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletTilt.FUNCTION_GET_IDENTITY] = BrickletTilt.RESPONSE_EXPECTED_ALWAYS_TRUE

        self.callback_formats[BrickletTilt.CALLBACK_TILT_STATE] = 'B'

    def get_tilt_state(self):
        """
        Returns the current tilt state. The state can either be
        
        * 0 = Closed: The ball in the tilt switch closes the circuit.
        * 1 = Open: The ball in the tilt switch does not close the circuit.
        * 2 = Closed Vibrating: The tilt switch is in motion (rapid change between open and close).
        
        .. image:: /Images/Bricklets/bricklet_tilt_mechanics.jpg
           :scale: 100 %
           :alt: Tilt states
           :align: center
           :target: ../../_images/Bricklets/bricklet_tilt_mechanics.jpg
        """
        return self.ipcon.send_request(self, BrickletTilt.FUNCTION_GET_TILT_STATE, (), '', 'B')

    def enable_tilt_state_callback(self):
        """
        Enables the :func:`TiltState` callback.
        """
        self.ipcon.send_request(self, BrickletTilt.FUNCTION_ENABLE_TILT_STATE_CALLBACK, (), '', '')

    def disable_tilt_state_callback(self):
        """
        Disables the :func:`TiltState` callback.
        """
        self.ipcon.send_request(self, BrickletTilt.FUNCTION_DISABLE_TILT_STATE_CALLBACK, (), '', '')

    def is_tilt_state_callback_enabled(self):
        """
        Returns *true* if the :func:`TiltState` callback is enabled.
        """
        return self.ipcon.send_request(self, BrickletTilt.FUNCTION_IS_TILT_STATE_CALLBACK_ENABLED, (), '', '?')

    def get_identity(self):
        """
        Returns the UID, the UID where the Bricklet is connected to, 
        the position, the hardware and firmware version as well as the
        device identifier.
        
        The position can be 'a', 'b', 'c' or 'd'.
        
        The device identifier numbers can be found :ref:`here <device_identifier>`.
        |device_identifier_constant|
        """
        return GetIdentity(*self.ipcon.send_request(self, BrickletTilt.FUNCTION_GET_IDENTITY, (), '', '8s 8s c 3B 3B H'))

    def register_callback(self, id, callback):
        """
        Registers a callback with ID *id* to the function *callback*.
        """
        self.registered_callbacks[id] = callback

Tilt = BrickletTilt # for backward compatibility
