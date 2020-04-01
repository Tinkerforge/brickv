# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2020-04-01.      #
#                                                           #
# Python Bindings Version 2.1.24                            #
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


class TNGUnknown(Device):
    """

    """

    DEVICE_IDENTIFIER = -201
    DEVICE_DISPLAY_NAME = 'TNG Unknown'
    DEVICE_URL_PART = 'unknown' # internal



    FUNCTION_GET_TIMESTAMP = 234
    FUNCTION_COPY_FIRMWARE = 235
    FUNCTION_SET_WRITE_FIRMWARE_POINTER = 237
    FUNCTION_WRITE_FIRMWARE = 238
    FUNCTION_RESET = 243

    COPY_STATUS_OK = 0
    COPY_STATUS_DEVICE_IDENTIFIER_INCORRECT = 1
    COPY_STATUS_MAGIC_NUMBER_INCORRECT = 2
    COPY_STATUS_LENGTH_MALFORMED = 3
    COPY_STATUS_CRC_MISMATCH = 4

    def __init__(self, uid, ipcon):
        """
        Creates an object with the unique device ID *uid* and adds it to
        the IP Connection *ipcon*.
        """
        Device.__init__(self, uid, ipcon, TNGUnknown.DEVICE_IDENTIFIER, TNGUnknown.DEVICE_DISPLAY_NAME)

        self.api_version = (2, 0, 0)

        self.response_expected[TNGUnknown.FUNCTION_GET_TIMESTAMP] = TNGUnknown.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[TNGUnknown.FUNCTION_COPY_FIRMWARE] = TNGUnknown.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[TNGUnknown.FUNCTION_SET_WRITE_FIRMWARE_POINTER] = TNGUnknown.RESPONSE_EXPECTED_FALSE
        self.response_expected[TNGUnknown.FUNCTION_WRITE_FIRMWARE] = TNGUnknown.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[TNGUnknown.FUNCTION_RESET] = TNGUnknown.RESPONSE_EXPECTED_FALSE


        ipcon.add_device(self)

    def get_timestamp(self):
        """
        TODO
        """
        self.check_validity()

        return self.ipcon.send_request(self, TNGUnknown.FUNCTION_GET_TIMESTAMP, (), '', 16, 'Q')

    def copy_firmware(self):
        """
        TODO
        """
        self.check_validity()

        return self.ipcon.send_request(self, TNGUnknown.FUNCTION_COPY_FIRMWARE, (), '', 9, 'B')

    def set_write_firmware_pointer(self, pointer):
        """
        TODO
        """
        self.check_validity()

        pointer = int(pointer)

        self.ipcon.send_request(self, TNGUnknown.FUNCTION_SET_WRITE_FIRMWARE_POINTER, (pointer,), 'I', 0, '')

    def write_firmware(self, data):
        """
        TODO
        """
        self.check_validity()

        data = list(map(int, data))

        return self.ipcon.send_request(self, TNGUnknown.FUNCTION_WRITE_FIRMWARE, (data,), '64B', 9, 'B')

    def reset(self):
        """
        Calling this function will reset the TNG module. All configurations
        will be lost.

        After a reset you have to create new device objects,
        calling functions on the existing ones will result in
        undefined behavior!
        """
        self.check_validity()

        self.ipcon.send_request(self, TNGUnknown.FUNCTION_RESET, (), '', 0, '')
