# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2016-05-31.      #
#                                                           #
# Python Bindings Version 2.1.9                             #
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

GetRGBValues = namedtuple('RGBValues', ['r', 'g', 'b'])
GetIdentity = namedtuple('Identity', ['uid', 'connected_uid', 'position', 'hardware_version', 'firmware_version', 'device_identifier'])

class BrickletLEDStrip(Device):
    """
    Controls up to 320 RGB LEDs
    """

    DEVICE_IDENTIFIER = 231
    DEVICE_DISPLAY_NAME = 'LED Strip Bricklet'

    CALLBACK_FRAME_RENDERED = 6

    FUNCTION_SET_RGB_VALUES = 1
    FUNCTION_GET_RGB_VALUES = 2
    FUNCTION_SET_FRAME_DURATION = 3
    FUNCTION_GET_FRAME_DURATION = 4
    FUNCTION_GET_SUPPLY_VOLTAGE = 5
    FUNCTION_SET_CLOCK_FREQUENCY = 7
    FUNCTION_GET_CLOCK_FREQUENCY = 8
    FUNCTION_SET_CHIP_TYPE = 9
    FUNCTION_GET_CHIP_TYPE = 10
    FUNCTION_GET_IDENTITY = 255

    CHIP_TYPE_WS2801 = 2801
    CHIP_TYPE_WS2811 = 2811
    CHIP_TYPE_WS2812 = 2812

    def __init__(self, uid, ipcon):
        """
        Creates an object with the unique device ID *uid* and adds it to
        the IP Connection *ipcon*.
        """
        Device.__init__(self, uid, ipcon)

        self.api_version = (2, 0, 2)

        self.response_expected[BrickletLEDStrip.FUNCTION_SET_RGB_VALUES] = BrickletLEDStrip.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletLEDStrip.FUNCTION_GET_RGB_VALUES] = BrickletLEDStrip.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletLEDStrip.FUNCTION_SET_FRAME_DURATION] = BrickletLEDStrip.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletLEDStrip.FUNCTION_GET_FRAME_DURATION] = BrickletLEDStrip.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletLEDStrip.FUNCTION_GET_SUPPLY_VOLTAGE] = BrickletLEDStrip.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletLEDStrip.CALLBACK_FRAME_RENDERED] = BrickletLEDStrip.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletLEDStrip.FUNCTION_SET_CLOCK_FREQUENCY] = BrickletLEDStrip.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletLEDStrip.FUNCTION_GET_CLOCK_FREQUENCY] = BrickletLEDStrip.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletLEDStrip.FUNCTION_SET_CHIP_TYPE] = BrickletLEDStrip.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletLEDStrip.FUNCTION_GET_CHIP_TYPE] = BrickletLEDStrip.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletLEDStrip.FUNCTION_GET_IDENTITY] = BrickletLEDStrip.RESPONSE_EXPECTED_ALWAYS_TRUE

        self.callback_formats[BrickletLEDStrip.CALLBACK_FRAME_RENDERED] = 'H'

    def set_rgb_values(self, index, length, r, g, b):
        """
        Sets the *rgb* values for the LEDs with the given *length* starting 
        from *index*.
        
        The maximum length is 16, the index goes from 0 to 319 and the rgb values
        have 8 bits each.
        
        Example: If you set
        
        * index to 5,
        * length to 3,
        * r to [255, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        * g to [0, 255, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] and
        * b to [0, 0, 255, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        
        the LED with index 5 will be red, 6 will be green and 7 will be blue.
        
        .. note:: Depending on the LED circuitry colors can be permuted.
        
        The colors will be transfered to actual LEDs when the next
        frame duration ends, see :func:`SetFrameDuration`.
        
        Generic approach: 
        
        * Set the frame duration to a value that represents
          the number of frames per second you want to achieve. 
        * Set all of the LED colors for one frame.
        * Wait for the :func:`FrameRendered` callback.
        * Set all of the LED colors for next frame.
        * Wait for the :func:`FrameRendered` callback.
        * and so on.
        
        This approach ensures that you can change the LED colors with
        a fixed frame rate.
        
        The actual number of controllable LEDs depends on the number of free
        Bricklet ports. See :ref:`here <led_strip_bricklet_ram_constraints>` for more
        information. A call of :func:`SetRGBValues` with index + length above the
        bounds is ignored completely.
        """
        self.ipcon.send_request(self, BrickletLEDStrip.FUNCTION_SET_RGB_VALUES, (index, length, r, g, b), 'H B 16B 16B 16B', '')

    def get_rgb_values(self, index, length):
        """
        Returns the rgb with the given *length* starting from the
        given *index*.
        
        The values are the last values that were set by :func:`SetRGBValues`.
        """
        return GetRGBValues(*self.ipcon.send_request(self, BrickletLEDStrip.FUNCTION_GET_RGB_VALUES, (index, length), 'H B', '16B 16B 16B'))

    def set_frame_duration(self, duration):
        """
        Sets the frame duration in ms.
        
        Example: If you want to achieve 20 frames per second, you should
        set the frame duration to 50ms (50ms * 20 = 1 second). 
        
        For an explanation of the general approach see :func:`SetRGBValues`.
        
        Default value: 100ms (10 frames per second).
        """
        self.ipcon.send_request(self, BrickletLEDStrip.FUNCTION_SET_FRAME_DURATION, (duration,), 'H', '')

    def get_frame_duration(self):
        """
        Returns the frame duration in ms as set by :func:`SetFrameDuration`.
        """
        return self.ipcon.send_request(self, BrickletLEDStrip.FUNCTION_GET_FRAME_DURATION, (), '', 'H')

    def get_supply_voltage(self):
        """
        Returns the current supply voltage of the LEDs. The voltage is given in mV.
        """
        return self.ipcon.send_request(self, BrickletLEDStrip.FUNCTION_GET_SUPPLY_VOLTAGE, (), '', 'H')

    def set_clock_frequency(self, frequency):
        """
        Sets the frequency of the clock in Hz. The range is 10000Hz (10kHz) up to
        2000000Hz (2MHz).
        
        The Bricklet will choose the nearest achievable frequency, which may
        be off by a few Hz. You can get the exact frequency that is used by
        calling :func:`GetClockFrequency`.
        
        If you have problems with flickering LEDs, they may be bits flipping. You
        can fix this by either making the connection between the LEDs and the
        Bricklet shorter or by reducing the frequency.
        
        With a decreasing frequency your maximum frames per second will decrease
        too.
        
        The default value is 1.66MHz.
        
        .. note::
         The frequency in firmware version 2.0.0 is fixed at 2MHz.
        
        .. versionadded:: 2.0.1$nbsp;(Plugin)
        """
        self.ipcon.send_request(self, BrickletLEDStrip.FUNCTION_SET_CLOCK_FREQUENCY, (frequency,), 'I', '')

    def get_clock_frequency(self):
        """
        Returns the currently used clock frequency as set by :func:`SetClockFrequency`.
        
        .. versionadded:: 2.0.1$nbsp;(Plugin)
        """
        return self.ipcon.send_request(self, BrickletLEDStrip.FUNCTION_GET_CLOCK_FREQUENCY, (), '', 'I')

    def set_chip_type(self, chip):
        """
        Sets the type of the led driver chip. We currently support
        the chips
        
        * WS2801 (``chip`` = 2801),
        * WS2811 (``chip`` = 2811) and
        * WS2812 (``chip`` = 2812).
        
        The WS2812 is sometimes also called "NeoPixel", a name coined by
        Adafruit.
        
        The default value is WS2801 (``chip`` = 2801).
        
        .. versionadded:: 2.0.2$nbsp;(Plugin)
        """
        self.ipcon.send_request(self, BrickletLEDStrip.FUNCTION_SET_CHIP_TYPE, (chip,), 'H', '')

    def get_chip_type(self):
        """
        Returns the currently used chip type as set by :func:`SetChipType`.
        
        .. versionadded:: 2.0.2$nbsp;(Plugin)
        """
        return self.ipcon.send_request(self, BrickletLEDStrip.FUNCTION_GET_CHIP_TYPE, (), '', 'H')

    def get_identity(self):
        """
        Returns the UID, the UID where the Bricklet is connected to, 
        the position, the hardware and firmware version as well as the
        device identifier.
        
        The position can be 'a', 'b', 'c' or 'd'.
        
        The device identifier numbers can be found :ref:`here <device_identifier>`.
        |device_identifier_constant|
        """
        return GetIdentity(*self.ipcon.send_request(self, BrickletLEDStrip.FUNCTION_GET_IDENTITY, (), '', '8s 8s c 3B 3B H'))

    def register_callback(self, id, callback):
        """
        Registers a callback with ID *id* to the function *callback*.
        """
        self.registered_callbacks[id] = callback

LEDStrip = BrickletLEDStrip # for backward compatibility
