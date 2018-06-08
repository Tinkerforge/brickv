# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2018-06-08.      #
#                                                           #
# Python Bindings Version 2.1.17                            #
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

NormalWriteExtraOut2LowLevel = namedtuple('NormalWriteExtraOut2LowLevel', ['extra_1', 'extra_2'])
FixedWriteExtraOut2LowLevel = namedtuple('FixedWriteExtraOut2LowLevel', ['extra_1', 'extra_2'])
ShortWriteExtraOutPrefix1LowLevel = namedtuple('ShortWriteExtraOutPrefix1LowLevel', ['extra', 'message_chunk_written'])
ShortWriteExtraOutPrefix2LowLevel = namedtuple('ShortWriteExtraOutPrefix2LowLevel', ['extra_1', 'extra_2', 'message_chunk_written'])
ShortWriteExtraOutSuffix1LowLevel = namedtuple('ShortWriteExtraOutSuffix1LowLevel', ['message_chunk_written', 'extra'])
ShortWriteExtraOutSuffix2LowLevel = namedtuple('ShortWriteExtraOutSuffix2LowLevel', ['message_chunk_written', 'extra_1', 'extra_2'])
ShortWriteExtraFullLowLevel = namedtuple('ShortWriteExtraFullLowLevel', ['extra_5', 'message_chunk_written', 'extra_6'])
SingleWriteExtraOut2LowLevel = namedtuple('SingleWriteExtraOut2LowLevel', ['extra_1', 'extra_2'])
ShortSingleWriteExtraOutPrefix1LowLevel = namedtuple('ShortSingleWriteExtraOutPrefix1LowLevel', ['extra', 'message_written'])
ShortSingleWriteExtraOutPrefix2LowLevel = namedtuple('ShortSingleWriteExtraOutPrefix2LowLevel', ['extra_1', 'extra_2', 'message_written'])
ShortSingleWriteExtraOutSuffix1LowLevel = namedtuple('ShortSingleWriteExtraOutSuffix1LowLevel', ['message_written', 'extra'])
ShortSingleWriteExtraOutSuffix2LowLevel = namedtuple('ShortSingleWriteExtraOutSuffix2LowLevel', ['message_written', 'extra_1', 'extra_2'])
ShortSingleWriteExtraFullLowLevel = namedtuple('ShortSingleWriteExtraFullLowLevel', ['extra_4', 'message_written', 'extra_5'])
NormalReadLowLevel = namedtuple('NormalReadLowLevel', ['message_length', 'message_chunk_offset', 'message_chunk_data'])
NormalReadExtraIn1LowLevel = namedtuple('NormalReadExtraIn1LowLevel', ['message_length', 'message_chunk_offset', 'message_chunk_data'])
NormalReadExtraIn2LowLevel = namedtuple('NormalReadExtraIn2LowLevel', ['message_length', 'message_chunk_offset', 'message_chunk_data'])
NormalReadExtraOutPrefix1LowLevel = namedtuple('NormalReadExtraOutPrefix1LowLevel', ['extra', 'message_length', 'message_chunk_offset', 'message_chunk_data'])
NormalReadExtraOutPrefix2LowLevel = namedtuple('NormalReadExtraOutPrefix2LowLevel', ['extra_1', 'extra_2', 'message_length', 'message_chunk_offset', 'message_chunk_data'])
NormalReadExtraOutSuffix1LowLevel = namedtuple('NormalReadExtraOutSuffix1LowLevel', ['message_length', 'message_chunk_offset', 'message_chunk_data', 'extra'])
NormalReadExtraOutSuffix2LowLevel = namedtuple('NormalReadExtraOutSuffix2LowLevel', ['message_length', 'message_chunk_offset', 'message_chunk_data', 'extra_1', 'extra_2'])
NormalReadExtraOutFullLowLevel = namedtuple('NormalReadExtraOutFullLowLevel', ['extra_1', 'message_length', 'extra_2', 'message_chunk_offset', 'extra_3', 'message_chunk_data', 'extra_4'])
FixedReadLowLevel = namedtuple('FixedReadLowLevel', ['message_chunk_offset', 'message_chunk_data'])
FixedReadExtraIn1LowLevel = namedtuple('FixedReadExtraIn1LowLevel', ['message_chunk_offset', 'message_chunk_data'])
FixedReadExtraIn2LowLevel = namedtuple('FixedReadExtraIn2LowLevel', ['message_chunk_offset', 'message_chunk_data'])
FixedReadExtraOutPrefix1LowLevel = namedtuple('FixedReadExtraOutPrefix1LowLevel', ['extra', 'message_chunk_offset', 'message_chunk_data'])
FixedReadExtraOutPrefix2LowLevel = namedtuple('FixedReadExtraOutPrefix2LowLevel', ['extra_1', 'extra_2', 'message_chunk_offset', 'message_chunk_data'])
FixedReadExtraOutSuffix1LowLevel = namedtuple('FixedReadExtraOutSuffix1LowLevel', ['message_chunk_offset', 'message_chunk_data', 'extra'])
FixedReadExtraOutSuffix2LowLevel = namedtuple('FixedReadExtraOutSuffix2LowLevel', ['message_chunk_offset', 'message_chunk_data', 'extra_1', 'extra_2'])
FixedReadExtraOutFullLowLevel = namedtuple('FixedReadExtraOutFullLowLevel', ['extra_1', 'message_chunk_offset', 'extra_2', 'message_chunk_data', 'extra_3'])
SingleReadLowLevel = namedtuple('SingleReadLowLevel', ['message_length', 'message_data'])
SingleReadExtraIn1LowLevel = namedtuple('SingleReadExtraIn1LowLevel', ['message_length', 'message_data'])
SingleReadExtraIn2LowLevel = namedtuple('SingleReadExtraIn2LowLevel', ['message_length', 'message_data'])
SingleReadExtraOutPrefix1LowLevel = namedtuple('SingleReadExtraOutPrefix1LowLevel', ['extra', 'message_length', 'message_data'])
SingleReadExtraOutPrefix2LowLevel = namedtuple('SingleReadExtraOutPrefix2LowLevel', ['extra_1', 'extra_2', 'message_length', 'message_data'])
SingleReadExtraOutSuffix1LowLevel = namedtuple('SingleReadExtraOutSuffix1LowLevel', ['message_length', 'message_data', 'extra'])
SingleReadExtraOutSuffix2LowLevel = namedtuple('SingleReadExtraOutSuffix2LowLevel', ['message_length', 'message_data', 'extra_1', 'extra_2'])
SingleReadExtraOutFullLowLevel = namedtuple('SingleReadExtraOutFullLowLevel', ['extra_1', 'message_length', 'extra_2', 'message_data', 'extra_3'])
GetIdentity = namedtuple('Identity', ['uid', 'connected_uid', 'position', 'hardware_version', 'firmware_version', 'device_identifier'])
NormalWriteExtraOut2 = namedtuple('NormalWriteExtraOut2', ['extra_1', 'extra_2'])
FixedWriteExtraOut2 = namedtuple('FixedWriteExtraOut2', ['extra_1', 'extra_2'])
ShortWriteExtraOutPrefix1 = namedtuple('ShortWriteExtraOutPrefix1', ['extra', 'message_written'])
ShortWriteExtraOutPrefix2 = namedtuple('ShortWriteExtraOutPrefix2', ['extra_1', 'extra_2', 'message_written'])
ShortWriteExtraOutSuffix1 = namedtuple('ShortWriteExtraOutSuffix1', ['message_written', 'extra'])
ShortWriteExtraOutSuffix2 = namedtuple('ShortWriteExtraOutSuffix2', ['message_written', 'extra_1', 'extra_2'])
ShortWriteExtraFull = namedtuple('ShortWriteExtraFull', ['extra_5', 'message_written', 'extra_6'])
SingleWriteExtraOut2 = namedtuple('SingleWriteExtraOut2', ['extra_1', 'extra_2'])
ShortSingleWriteExtraOutPrefix1 = namedtuple('ShortSingleWriteExtraOutPrefix1', ['extra', 'message_written'])
ShortSingleWriteExtraOutPrefix2 = namedtuple('ShortSingleWriteExtraOutPrefix2', ['extra_1', 'extra_2', 'message_written'])
ShortSingleWriteExtraOutSuffix1 = namedtuple('ShortSingleWriteExtraOutSuffix1', ['message_written', 'extra'])
ShortSingleWriteExtraOutSuffix2 = namedtuple('ShortSingleWriteExtraOutSuffix2', ['message_written', 'extra_1', 'extra_2'])
ShortSingleWriteExtraFull = namedtuple('ShortSingleWriteExtraFull', ['extra_4', 'message_written', 'extra_5'])
NormalReadExtraOutPrefix1 = namedtuple('NormalReadExtraOutPrefix1', ['extra', 'message'])
NormalReadExtraOutPrefix2 = namedtuple('NormalReadExtraOutPrefix2', ['extra_1', 'extra_2', 'message'])
NormalReadExtraOutSuffix1 = namedtuple('NormalReadExtraOutSuffix1', ['message', 'extra'])
NormalReadExtraOutSuffix2 = namedtuple('NormalReadExtraOutSuffix2', ['message', 'extra_1', 'extra_2'])
NormalReadExtraOutFull = namedtuple('NormalReadExtraOutFull', ['extra_1', 'extra_2', 'extra_3', 'message', 'extra_4'])
FixedReadExtraOutPrefix1 = namedtuple('FixedReadExtraOutPrefix1', ['extra', 'message'])
FixedReadExtraOutPrefix2 = namedtuple('FixedReadExtraOutPrefix2', ['extra_1', 'extra_2', 'message'])
FixedReadExtraOutSuffix1 = namedtuple('FixedReadExtraOutSuffix1', ['message', 'extra'])
FixedReadExtraOutSuffix2 = namedtuple('FixedReadExtraOutSuffix2', ['message', 'extra_1', 'extra_2'])
FixedReadExtraOutFull = namedtuple('FixedReadExtraOutFull', ['extra_1', 'extra_2', 'message', 'extra_3'])
SingleReadExtraOutPrefix1 = namedtuple('SingleReadExtraOutPrefix1', ['extra', 'message'])
SingleReadExtraOutPrefix2 = namedtuple('SingleReadExtraOutPrefix2', ['extra_1', 'extra_2', 'message'])
SingleReadExtraOutSuffix1 = namedtuple('SingleReadExtraOutSuffix1', ['message', 'extra'])
SingleReadExtraOutSuffix2 = namedtuple('SingleReadExtraOutSuffix2', ['message', 'extra_1', 'extra_2'])
SingleReadExtraOutFull = namedtuple('SingleReadExtraOutFull', ['extra_1', 'extra_2', 'message', 'extra_3'])

class BrickletStreamTest(Device):
    """

    """

    DEVICE_IDENTIFIER = 21111
    DEVICE_DISPLAY_NAME = 'Stream Test Bricklet'
    DEVICE_URL_PART = 'stream_test' # internal

    CALLBACK_NORMAL_READ_LOW_LEVEL = 69
    CALLBACK_NORMAL_READ_EXTRA_PREFIX_1_LOW_LEVEL = 70
    CALLBACK_NORMAL_READ_EXTRA_PREFIX_2_LOW_LEVEL = 71
    CALLBACK_NORMAL_READ_EXTRA_SUFFIX_1_LOW_LEVEL = 72
    CALLBACK_NORMAL_READ_EXTRA_SUFFIX_2_LOW_LEVEL = 73
    CALLBACK_NORMAL_READ_EXTRA_FULL_LOW_LEVEL = 74
    CALLBACK_FIXED_READ_LOW_LEVEL = 75
    CALLBACK_FIXED_READ_EXTRA_PREFIX_1_LOW_LEVEL = 76
    CALLBACK_FIXED_READ_EXTRA_PREFIX_2_LOW_LEVEL = 77
    CALLBACK_FIXED_READ_EXTRA_SUFFIX_1_LOW_LEVEL = 78
    CALLBACK_FIXED_READ_EXTRA_SUFFIX_2_LOW_LEVEL = 79
    CALLBACK_FIXED_READ_EXTRA_FULL_LOW_LEVEL = 80
    CALLBACK_SINGLE_READ_LOW_LEVEL = 81
    CALLBACK_SINGLE_READ_EXTRA_PREFIX_1_LOW_LEVEL = 82
    CALLBACK_SINGLE_READ_EXTRA_PREFIX_2_LOW_LEVEL = 83
    CALLBACK_SINGLE_READ_EXTRA_SUFFIX_1_LOW_LEVEL = 84
    CALLBACK_SINGLE_READ_EXTRA_SUFFIX_2_LOW_LEVEL = 85
    CALLBACK_SINGLE_READ_EXTRA_FULL_LOW_LEVEL = 86

    CALLBACK_NORMAL_READ = -69
    CALLBACK_NORMAL_READ_EXTRA_PREFIX_1 = -70
    CALLBACK_NORMAL_READ_EXTRA_PREFIX_2 = -71
    CALLBACK_NORMAL_READ_EXTRA_SUFFIX_1 = -72
    CALLBACK_NORMAL_READ_EXTRA_SUFFIX_2 = -73
    CALLBACK_NORMAL_READ_EXTRA_FULL = -74
    CALLBACK_FIXED_READ = -75
    CALLBACK_FIXED_READ_EXTRA_PREFIX_1 = -76
    CALLBACK_FIXED_READ_EXTRA_PREFIX_2 = -77
    CALLBACK_FIXED_READ_EXTRA_SUFFIX_1 = -78
    CALLBACK_FIXED_READ_EXTRA_SUFFIX_2 = -79
    CALLBACK_FIXED_READ_EXTRA_FULL = -80
    CALLBACK_SINGLE_READ = -81
    CALLBACK_SINGLE_READ_EXTRA_PREFIX_1 = -82
    CALLBACK_SINGLE_READ_EXTRA_PREFIX_2 = -83
    CALLBACK_SINGLE_READ_EXTRA_SUFFIX_1 = -84
    CALLBACK_SINGLE_READ_EXTRA_SUFFIX_2 = -85
    CALLBACK_SINGLE_READ_EXTRA_FULL = -86

    FUNCTION_NORMAL_WRITE_LOW_LEVEL = 1
    FUNCTION_NORMAL_WRITE_EXTRA_IN_PREFIX_1_LOW_LEVEL = 2
    FUNCTION_NORMAL_WRITE_EXTRA_IN_PREFIX_2_LOW_LEVEL = 3
    FUNCTION_NORMAL_WRITE_EXTRA_IN_SUFFIX_1_LOW_LEVEL = 4
    FUNCTION_NORMAL_WRITE_EXTRA_IN_SUFFIX_2_LOW_LEVEL = 5
    FUNCTION_NORMAL_WRITE_EXTRA_IN_FULL_LOW_LEVEL = 6
    FUNCTION_NORMAL_WRITE_EXTRA_OUT_1_LOW_LEVEL = 7
    FUNCTION_NORMAL_WRITE_EXTRA_OUT_2_LOW_LEVEL = 8
    FUNCTION_FIXED_WRITE_LOW_LEVEL = 9
    FUNCTION_FIXED_WRITE_EXTRA_IN_PREFIX_1_LOW_LEVEL = 10
    FUNCTION_FIXED_WRITE_EXTRA_IN_PREFIX_2_LOW_LEVEL = 11
    FUNCTION_FIXED_WRITE_EXTRA_IN_SUFFIX_1_LOW_LEVEL = 12
    FUNCTION_FIXED_WRITE_EXTRA_IN_SUFFIX_2_LOW_LEVEL = 13
    FUNCTION_FIXED_WRITE_EXTRA_IN_FULL_LOW_LEVEL = 14
    FUNCTION_FIXED_WRITE_EXTRA_OUT_1_LOW_LEVEL = 15
    FUNCTION_FIXED_WRITE_EXTRA_OUT_2_LOW_LEVEL = 16
    FUNCTION_SHORT_WRITE_LOW_LEVEL = 17
    FUNCTION_SHORT_WRITE_EXTRA_IN_PREFIX_1_LOW_LEVEL = 18
    FUNCTION_SHORT_WRITE_EXTRA_IN_PREFIX_2_LOW_LEVEL = 19
    FUNCTION_SHORT_WRITE_EXTRA_IN_SUFFIX_1_LOW_LEVEL = 20
    FUNCTION_SHORT_WRITE_EXTRA_IN_SUFFIX_2_LOW_LEVEL = 21
    FUNCTION_SHORT_WRITE_EXTRA_OUT_PREFIX_1_LOW_LEVEL = 22
    FUNCTION_SHORT_WRITE_EXTRA_OUT_PREFIX_2_LOW_LEVEL = 23
    FUNCTION_SHORT_WRITE_EXTRA_OUT_SUFFIX_1_LOW_LEVEL = 24
    FUNCTION_SHORT_WRITE_EXTRA_OUT_SUFFIX_2_LOW_LEVEL = 25
    FUNCTION_SHORT_WRITE_EXTRA_FULL_LOW_LEVEL = 26
    FUNCTION_SINGLE_WRITE_LOW_LEVEL = 27
    FUNCTION_SINGLE_WRITE_EXTRA_IN_PREFIX_1_LOW_LEVEL = 28
    FUNCTION_SINGLE_WRITE_EXTRA_IN_PREFIX_2_LOW_LEVEL = 29
    FUNCTION_SINGLE_WRITE_EXTRA_IN_SUFFIX_1_LOW_LEVEL = 30
    FUNCTION_SINGLE_WRITE_EXTRA_IN_SUFFIX_2_LOW_LEVEL = 31
    FUNCTION_SINGLE_WRITE_EXTRA_IN_FULL_LOW_LEVEL = 32
    FUNCTION_SINGLE_WRITE_EXTRA_OUT_1_LOW_LEVEL = 33
    FUNCTION_SINGLE_WRITE_EXTRA_OUT_2_LOW_LEVEL = 34
    FUNCTION_SHORT_SINGLE_WRITE_LOW_LEVEL = 35
    FUNCTION_SHORT_SINGLE_WRITE_EXTRA_IN_PREFIX_1_LOW_LEVEL = 36
    FUNCTION_SHORT_SINGLE_WRITE_EXTRA_IN_PREFIX_2_LOW_LEVEL = 37
    FUNCTION_SHORT_SINGLE_WRITE_EXTRA_IN_SUFFIX_1_LOW_LEVEL = 38
    FUNCTION_SHORT_SINGLE_WRITE_EXTRA_IN_SUFFIX_2_LOW_LEVEL = 39
    FUNCTION_SHORT_SINGLE_WRITE_EXTRA_OUT_PREFIX_1_LOW_LEVEL = 40
    FUNCTION_SHORT_SINGLE_WRITE_EXTRA_OUT_PREFIX_2_LOW_LEVEL = 41
    FUNCTION_SHORT_SINGLE_WRITE_EXTRA_OUT_SUFFIX_1_LOW_LEVEL = 42
    FUNCTION_SHORT_SINGLE_WRITE_EXTRA_OUT_SUFFIX_2_LOW_LEVEL = 43
    FUNCTION_SHORT_SINGLE_WRITE_EXTRA_FULL_LOW_LEVEL = 44
    FUNCTION_NORMAL_READ_LOW_LEVEL = 45
    FUNCTION_NORMAL_READ_EXTRA_IN_1_LOW_LEVEL = 46
    FUNCTION_NORMAL_READ_EXTRA_IN_2_LOW_LEVEL = 47
    FUNCTION_NORMAL_READ_EXTRA_OUT_PREFIX_1_LOW_LEVEL = 48
    FUNCTION_NORMAL_READ_EXTRA_OUT_PREFIX_2_LOW_LEVEL = 49
    FUNCTION_NORMAL_READ_EXTRA_OUT_SUFFIX_1_LOW_LEVEL = 50
    FUNCTION_NORMAL_READ_EXTRA_OUT_SUFFIX_2_LOW_LEVEL = 51
    FUNCTION_NORMAL_READ_EXTRA_OUT_FULL_LOW_LEVEL = 52
    FUNCTION_FIXED_READ_LOW_LEVEL = 53
    FUNCTION_FIXED_READ_EXTRA_IN_1_LOW_LEVEL = 54
    FUNCTION_FIXED_READ_EXTRA_IN_2_LOW_LEVEL = 55
    FUNCTION_FIXED_READ_EXTRA_OUT_PREFIX_1_LOW_LEVEL = 56
    FUNCTION_FIXED_READ_EXTRA_OUT_PREFIX_2_LOW_LEVEL = 57
    FUNCTION_FIXED_READ_EXTRA_OUT_SUFFIX_1_LOW_LEVEL = 58
    FUNCTION_FIXED_READ_EXTRA_OUT_SUFFIX_2_LOW_LEVEL = 59
    FUNCTION_FIXED_READ_EXTRA_OUT_FULL_LOW_LEVEL = 60
    FUNCTION_SINGLE_READ_LOW_LEVEL = 61
    FUNCTION_SINGLE_READ_EXTRA_IN_1_LOW_LEVEL = 62
    FUNCTION_SINGLE_READ_EXTRA_IN_2_LOW_LEVEL = 63
    FUNCTION_SINGLE_READ_EXTRA_OUT_PREFIX_1_LOW_LEVEL = 64
    FUNCTION_SINGLE_READ_EXTRA_OUT_PREFIX_2_LOW_LEVEL = 65
    FUNCTION_SINGLE_READ_EXTRA_OUT_SUFFIX_1_LOW_LEVEL = 66
    FUNCTION_SINGLE_READ_EXTRA_OUT_SUFFIX_2_LOW_LEVEL = 67
    FUNCTION_SINGLE_READ_EXTRA_OUT_FULL_LOW_LEVEL = 68
    FUNCTION_GET_IDENTITY = 255


    def __init__(self, uid, ipcon):
        """
        Creates an object with the unique device ID *uid* and adds it to
        the IP Connection *ipcon*.
        """
        Device.__init__(self, uid, ipcon)

        self.api_version = (2, 0, 0)

        self.response_expected[BrickletStreamTest.FUNCTION_NORMAL_WRITE_LOW_LEVEL] = BrickletStreamTest.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletStreamTest.FUNCTION_NORMAL_WRITE_EXTRA_IN_PREFIX_1_LOW_LEVEL] = BrickletStreamTest.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletStreamTest.FUNCTION_NORMAL_WRITE_EXTRA_IN_PREFIX_2_LOW_LEVEL] = BrickletStreamTest.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletStreamTest.FUNCTION_NORMAL_WRITE_EXTRA_IN_SUFFIX_1_LOW_LEVEL] = BrickletStreamTest.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletStreamTest.FUNCTION_NORMAL_WRITE_EXTRA_IN_SUFFIX_2_LOW_LEVEL] = BrickletStreamTest.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletStreamTest.FUNCTION_NORMAL_WRITE_EXTRA_IN_FULL_LOW_LEVEL] = BrickletStreamTest.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletStreamTest.FUNCTION_NORMAL_WRITE_EXTRA_OUT_1_LOW_LEVEL] = BrickletStreamTest.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletStreamTest.FUNCTION_NORMAL_WRITE_EXTRA_OUT_2_LOW_LEVEL] = BrickletStreamTest.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletStreamTest.FUNCTION_FIXED_WRITE_LOW_LEVEL] = BrickletStreamTest.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletStreamTest.FUNCTION_FIXED_WRITE_EXTRA_IN_PREFIX_1_LOW_LEVEL] = BrickletStreamTest.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletStreamTest.FUNCTION_FIXED_WRITE_EXTRA_IN_PREFIX_2_LOW_LEVEL] = BrickletStreamTest.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletStreamTest.FUNCTION_FIXED_WRITE_EXTRA_IN_SUFFIX_1_LOW_LEVEL] = BrickletStreamTest.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletStreamTest.FUNCTION_FIXED_WRITE_EXTRA_IN_SUFFIX_2_LOW_LEVEL] = BrickletStreamTest.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletStreamTest.FUNCTION_FIXED_WRITE_EXTRA_IN_FULL_LOW_LEVEL] = BrickletStreamTest.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletStreamTest.FUNCTION_FIXED_WRITE_EXTRA_OUT_1_LOW_LEVEL] = BrickletStreamTest.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletStreamTest.FUNCTION_FIXED_WRITE_EXTRA_OUT_2_LOW_LEVEL] = BrickletStreamTest.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletStreamTest.FUNCTION_SHORT_WRITE_LOW_LEVEL] = BrickletStreamTest.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletStreamTest.FUNCTION_SHORT_WRITE_EXTRA_IN_PREFIX_1_LOW_LEVEL] = BrickletStreamTest.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletStreamTest.FUNCTION_SHORT_WRITE_EXTRA_IN_PREFIX_2_LOW_LEVEL] = BrickletStreamTest.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletStreamTest.FUNCTION_SHORT_WRITE_EXTRA_IN_SUFFIX_1_LOW_LEVEL] = BrickletStreamTest.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletStreamTest.FUNCTION_SHORT_WRITE_EXTRA_IN_SUFFIX_2_LOW_LEVEL] = BrickletStreamTest.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletStreamTest.FUNCTION_SHORT_WRITE_EXTRA_OUT_PREFIX_1_LOW_LEVEL] = BrickletStreamTest.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletStreamTest.FUNCTION_SHORT_WRITE_EXTRA_OUT_PREFIX_2_LOW_LEVEL] = BrickletStreamTest.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletStreamTest.FUNCTION_SHORT_WRITE_EXTRA_OUT_SUFFIX_1_LOW_LEVEL] = BrickletStreamTest.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletStreamTest.FUNCTION_SHORT_WRITE_EXTRA_OUT_SUFFIX_2_LOW_LEVEL] = BrickletStreamTest.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletStreamTest.FUNCTION_SHORT_WRITE_EXTRA_FULL_LOW_LEVEL] = BrickletStreamTest.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletStreamTest.FUNCTION_SINGLE_WRITE_LOW_LEVEL] = BrickletStreamTest.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletStreamTest.FUNCTION_SINGLE_WRITE_EXTRA_IN_PREFIX_1_LOW_LEVEL] = BrickletStreamTest.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletStreamTest.FUNCTION_SINGLE_WRITE_EXTRA_IN_PREFIX_2_LOW_LEVEL] = BrickletStreamTest.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletStreamTest.FUNCTION_SINGLE_WRITE_EXTRA_IN_SUFFIX_1_LOW_LEVEL] = BrickletStreamTest.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletStreamTest.FUNCTION_SINGLE_WRITE_EXTRA_IN_SUFFIX_2_LOW_LEVEL] = BrickletStreamTest.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletStreamTest.FUNCTION_SINGLE_WRITE_EXTRA_IN_FULL_LOW_LEVEL] = BrickletStreamTest.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletStreamTest.FUNCTION_SINGLE_WRITE_EXTRA_OUT_1_LOW_LEVEL] = BrickletStreamTest.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletStreamTest.FUNCTION_SINGLE_WRITE_EXTRA_OUT_2_LOW_LEVEL] = BrickletStreamTest.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletStreamTest.FUNCTION_SHORT_SINGLE_WRITE_LOW_LEVEL] = BrickletStreamTest.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletStreamTest.FUNCTION_SHORT_SINGLE_WRITE_EXTRA_IN_PREFIX_1_LOW_LEVEL] = BrickletStreamTest.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletStreamTest.FUNCTION_SHORT_SINGLE_WRITE_EXTRA_IN_PREFIX_2_LOW_LEVEL] = BrickletStreamTest.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletStreamTest.FUNCTION_SHORT_SINGLE_WRITE_EXTRA_IN_SUFFIX_1_LOW_LEVEL] = BrickletStreamTest.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletStreamTest.FUNCTION_SHORT_SINGLE_WRITE_EXTRA_IN_SUFFIX_2_LOW_LEVEL] = BrickletStreamTest.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletStreamTest.FUNCTION_SHORT_SINGLE_WRITE_EXTRA_OUT_PREFIX_1_LOW_LEVEL] = BrickletStreamTest.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletStreamTest.FUNCTION_SHORT_SINGLE_WRITE_EXTRA_OUT_PREFIX_2_LOW_LEVEL] = BrickletStreamTest.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletStreamTest.FUNCTION_SHORT_SINGLE_WRITE_EXTRA_OUT_SUFFIX_1_LOW_LEVEL] = BrickletStreamTest.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletStreamTest.FUNCTION_SHORT_SINGLE_WRITE_EXTRA_OUT_SUFFIX_2_LOW_LEVEL] = BrickletStreamTest.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletStreamTest.FUNCTION_SHORT_SINGLE_WRITE_EXTRA_FULL_LOW_LEVEL] = BrickletStreamTest.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletStreamTest.FUNCTION_NORMAL_READ_LOW_LEVEL] = BrickletStreamTest.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletStreamTest.FUNCTION_NORMAL_READ_EXTRA_IN_1_LOW_LEVEL] = BrickletStreamTest.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletStreamTest.FUNCTION_NORMAL_READ_EXTRA_IN_2_LOW_LEVEL] = BrickletStreamTest.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletStreamTest.FUNCTION_NORMAL_READ_EXTRA_OUT_PREFIX_1_LOW_LEVEL] = BrickletStreamTest.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletStreamTest.FUNCTION_NORMAL_READ_EXTRA_OUT_PREFIX_2_LOW_LEVEL] = BrickletStreamTest.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletStreamTest.FUNCTION_NORMAL_READ_EXTRA_OUT_SUFFIX_1_LOW_LEVEL] = BrickletStreamTest.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletStreamTest.FUNCTION_NORMAL_READ_EXTRA_OUT_SUFFIX_2_LOW_LEVEL] = BrickletStreamTest.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletStreamTest.FUNCTION_NORMAL_READ_EXTRA_OUT_FULL_LOW_LEVEL] = BrickletStreamTest.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletStreamTest.FUNCTION_FIXED_READ_LOW_LEVEL] = BrickletStreamTest.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletStreamTest.FUNCTION_FIXED_READ_EXTRA_IN_1_LOW_LEVEL] = BrickletStreamTest.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletStreamTest.FUNCTION_FIXED_READ_EXTRA_IN_2_LOW_LEVEL] = BrickletStreamTest.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletStreamTest.FUNCTION_FIXED_READ_EXTRA_OUT_PREFIX_1_LOW_LEVEL] = BrickletStreamTest.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletStreamTest.FUNCTION_FIXED_READ_EXTRA_OUT_PREFIX_2_LOW_LEVEL] = BrickletStreamTest.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletStreamTest.FUNCTION_FIXED_READ_EXTRA_OUT_SUFFIX_1_LOW_LEVEL] = BrickletStreamTest.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletStreamTest.FUNCTION_FIXED_READ_EXTRA_OUT_SUFFIX_2_LOW_LEVEL] = BrickletStreamTest.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletStreamTest.FUNCTION_FIXED_READ_EXTRA_OUT_FULL_LOW_LEVEL] = BrickletStreamTest.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletStreamTest.FUNCTION_SINGLE_READ_LOW_LEVEL] = BrickletStreamTest.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletStreamTest.FUNCTION_SINGLE_READ_EXTRA_IN_1_LOW_LEVEL] = BrickletStreamTest.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletStreamTest.FUNCTION_SINGLE_READ_EXTRA_IN_2_LOW_LEVEL] = BrickletStreamTest.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletStreamTest.FUNCTION_SINGLE_READ_EXTRA_OUT_PREFIX_1_LOW_LEVEL] = BrickletStreamTest.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletStreamTest.FUNCTION_SINGLE_READ_EXTRA_OUT_PREFIX_2_LOW_LEVEL] = BrickletStreamTest.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletStreamTest.FUNCTION_SINGLE_READ_EXTRA_OUT_SUFFIX_1_LOW_LEVEL] = BrickletStreamTest.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletStreamTest.FUNCTION_SINGLE_READ_EXTRA_OUT_SUFFIX_2_LOW_LEVEL] = BrickletStreamTest.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletStreamTest.FUNCTION_SINGLE_READ_EXTRA_OUT_FULL_LOW_LEVEL] = BrickletStreamTest.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletStreamTest.FUNCTION_GET_IDENTITY] = BrickletStreamTest.RESPONSE_EXPECTED_ALWAYS_TRUE

        self.callback_formats[BrickletStreamTest.CALLBACK_NORMAL_READ_LOW_LEVEL] = 'H H 60c'
        self.callback_formats[BrickletStreamTest.CALLBACK_NORMAL_READ_EXTRA_PREFIX_1_LOW_LEVEL] = 'B H H 59c'
        self.callback_formats[BrickletStreamTest.CALLBACK_NORMAL_READ_EXTRA_PREFIX_2_LOW_LEVEL] = 'B B H H 58c'
        self.callback_formats[BrickletStreamTest.CALLBACK_NORMAL_READ_EXTRA_SUFFIX_1_LOW_LEVEL] = 'H H 59c B'
        self.callback_formats[BrickletStreamTest.CALLBACK_NORMAL_READ_EXTRA_SUFFIX_2_LOW_LEVEL] = 'H H 58c B B'
        self.callback_formats[BrickletStreamTest.CALLBACK_NORMAL_READ_EXTRA_FULL_LOW_LEVEL] = 'B H B H B 56c B'
        self.callback_formats[BrickletStreamTest.CALLBACK_FIXED_READ_LOW_LEVEL] = 'H 62c'
        self.callback_formats[BrickletStreamTest.CALLBACK_FIXED_READ_EXTRA_PREFIX_1_LOW_LEVEL] = 'B H 61c'
        self.callback_formats[BrickletStreamTest.CALLBACK_FIXED_READ_EXTRA_PREFIX_2_LOW_LEVEL] = 'B B H 60c'
        self.callback_formats[BrickletStreamTest.CALLBACK_FIXED_READ_EXTRA_SUFFIX_1_LOW_LEVEL] = 'H 61c B'
        self.callback_formats[BrickletStreamTest.CALLBACK_FIXED_READ_EXTRA_SUFFIX_2_LOW_LEVEL] = 'H 60c B B'
        self.callback_formats[BrickletStreamTest.CALLBACK_FIXED_READ_EXTRA_FULL_LOW_LEVEL] = 'B H B 59c B'
        self.callback_formats[BrickletStreamTest.CALLBACK_SINGLE_READ_LOW_LEVEL] = 'B 63c'
        self.callback_formats[BrickletStreamTest.CALLBACK_SINGLE_READ_EXTRA_PREFIX_1_LOW_LEVEL] = 'B B 62c'
        self.callback_formats[BrickletStreamTest.CALLBACK_SINGLE_READ_EXTRA_PREFIX_2_LOW_LEVEL] = 'B B B 61c'
        self.callback_formats[BrickletStreamTest.CALLBACK_SINGLE_READ_EXTRA_SUFFIX_1_LOW_LEVEL] = 'B 62c B'
        self.callback_formats[BrickletStreamTest.CALLBACK_SINGLE_READ_EXTRA_SUFFIX_2_LOW_LEVEL] = 'B 61c B B'
        self.callback_formats[BrickletStreamTest.CALLBACK_SINGLE_READ_EXTRA_FULL_LOW_LEVEL] = 'B B B 60c B'

        self.high_level_callbacks[BrickletStreamTest.CALLBACK_NORMAL_READ] = [('stream_length', 'stream_chunk_offset', 'stream_chunk_data'), {'fixed_length': None, 'single_chunk': False}, None]
        self.high_level_callbacks[BrickletStreamTest.CALLBACK_NORMAL_READ_EXTRA_PREFIX_1] = [(None, 'stream_length', 'stream_chunk_offset', 'stream_chunk_data'), {'fixed_length': None, 'single_chunk': False}, None]
        self.high_level_callbacks[BrickletStreamTest.CALLBACK_NORMAL_READ_EXTRA_PREFIX_2] = [(None, None, 'stream_length', 'stream_chunk_offset', 'stream_chunk_data'), {'fixed_length': None, 'single_chunk': False}, None]
        self.high_level_callbacks[BrickletStreamTest.CALLBACK_NORMAL_READ_EXTRA_SUFFIX_1] = [('stream_length', 'stream_chunk_offset', 'stream_chunk_data', None), {'fixed_length': None, 'single_chunk': False}, None]
        self.high_level_callbacks[BrickletStreamTest.CALLBACK_NORMAL_READ_EXTRA_SUFFIX_2] = [('stream_length', 'stream_chunk_offset', 'stream_chunk_data', None, None), {'fixed_length': None, 'single_chunk': False}, None]
        self.high_level_callbacks[BrickletStreamTest.CALLBACK_NORMAL_READ_EXTRA_FULL] = [(None, 'stream_length', None, 'stream_chunk_offset', None, 'stream_chunk_data', None), {'fixed_length': None, 'single_chunk': False}, None]
        self.high_level_callbacks[BrickletStreamTest.CALLBACK_FIXED_READ] = [('stream_chunk_offset', 'stream_chunk_data'), {'fixed_length': 1000, 'single_chunk': False}, None]
        self.high_level_callbacks[BrickletStreamTest.CALLBACK_FIXED_READ_EXTRA_PREFIX_1] = [(None, 'stream_chunk_offset', 'stream_chunk_data'), {'fixed_length': 1000, 'single_chunk': False}, None]
        self.high_level_callbacks[BrickletStreamTest.CALLBACK_FIXED_READ_EXTRA_PREFIX_2] = [(None, None, 'stream_chunk_offset', 'stream_chunk_data'), {'fixed_length': 1000, 'single_chunk': False}, None]
        self.high_level_callbacks[BrickletStreamTest.CALLBACK_FIXED_READ_EXTRA_SUFFIX_1] = [('stream_chunk_offset', 'stream_chunk_data', None), {'fixed_length': 1000, 'single_chunk': False}, None]
        self.high_level_callbacks[BrickletStreamTest.CALLBACK_FIXED_READ_EXTRA_SUFFIX_2] = [('stream_chunk_offset', 'stream_chunk_data', None, None), {'fixed_length': 1000, 'single_chunk': False}, None]
        self.high_level_callbacks[BrickletStreamTest.CALLBACK_FIXED_READ_EXTRA_FULL] = [(None, 'stream_chunk_offset', None, 'stream_chunk_data', None), {'fixed_length': 1000, 'single_chunk': False}, None]
        self.high_level_callbacks[BrickletStreamTest.CALLBACK_SINGLE_READ] = [('stream_length', 'stream_chunk_data'), {'fixed_length': None, 'single_chunk': True}, None]
        self.high_level_callbacks[BrickletStreamTest.CALLBACK_SINGLE_READ_EXTRA_PREFIX_1] = [(None, 'stream_length', 'stream_chunk_data'), {'fixed_length': None, 'single_chunk': True}, None]
        self.high_level_callbacks[BrickletStreamTest.CALLBACK_SINGLE_READ_EXTRA_PREFIX_2] = [(None, None, 'stream_length', 'stream_chunk_data'), {'fixed_length': None, 'single_chunk': True}, None]
        self.high_level_callbacks[BrickletStreamTest.CALLBACK_SINGLE_READ_EXTRA_SUFFIX_1] = [('stream_length', 'stream_chunk_data', None), {'fixed_length': None, 'single_chunk': True}, None]
        self.high_level_callbacks[BrickletStreamTest.CALLBACK_SINGLE_READ_EXTRA_SUFFIX_2] = [('stream_length', 'stream_chunk_data', None, None), {'fixed_length': None, 'single_chunk': True}, None]
        self.high_level_callbacks[BrickletStreamTest.CALLBACK_SINGLE_READ_EXTRA_FULL] = [(None, 'stream_length', None, 'stream_chunk_data', None), {'fixed_length': None, 'single_chunk': True}, None]

    def normal_write_low_level(self, message_length, message_chunk_offset, message_chunk_data):
        """

        """
        message_length = int(message_length)
        message_chunk_offset = int(message_chunk_offset)
        message_chunk_data = create_char_list(message_chunk_data)

        self.ipcon.send_request(self, BrickletStreamTest.FUNCTION_NORMAL_WRITE_LOW_LEVEL, (message_length, message_chunk_offset, message_chunk_data), 'H H 60c', '')

    def normal_write_extra_in_prefix_1_low_level(self, extra, message_length, message_chunk_offset, message_chunk_data):
        """

        """
        extra = int(extra)
        message_length = int(message_length)
        message_chunk_offset = int(message_chunk_offset)
        message_chunk_data = create_char_list(message_chunk_data)

        self.ipcon.send_request(self, BrickletStreamTest.FUNCTION_NORMAL_WRITE_EXTRA_IN_PREFIX_1_LOW_LEVEL, (extra, message_length, message_chunk_offset, message_chunk_data), 'B H H 59c', '')

    def normal_write_extra_in_prefix_2_low_level(self, extra_1, extra_2, message_length, message_chunk_offset, message_chunk_data):
        """

        """
        extra_1 = int(extra_1)
        extra_2 = int(extra_2)
        message_length = int(message_length)
        message_chunk_offset = int(message_chunk_offset)
        message_chunk_data = create_char_list(message_chunk_data)

        self.ipcon.send_request(self, BrickletStreamTest.FUNCTION_NORMAL_WRITE_EXTRA_IN_PREFIX_2_LOW_LEVEL, (extra_1, extra_2, message_length, message_chunk_offset, message_chunk_data), 'B B H H 58c', '')

    def normal_write_extra_in_suffix_1_low_level(self, message_length, message_chunk_offset, message_chunk_data, extra):
        """

        """
        message_length = int(message_length)
        message_chunk_offset = int(message_chunk_offset)
        message_chunk_data = create_char_list(message_chunk_data)
        extra = int(extra)

        self.ipcon.send_request(self, BrickletStreamTest.FUNCTION_NORMAL_WRITE_EXTRA_IN_SUFFIX_1_LOW_LEVEL, (message_length, message_chunk_offset, message_chunk_data, extra), 'H H 59c B', '')

    def normal_write_extra_in_suffix_2_low_level(self, message_length, message_chunk_offset, message_chunk_data, extra_1, extra_2):
        """

        """
        message_length = int(message_length)
        message_chunk_offset = int(message_chunk_offset)
        message_chunk_data = create_char_list(message_chunk_data)
        extra_1 = int(extra_1)
        extra_2 = int(extra_2)

        self.ipcon.send_request(self, BrickletStreamTest.FUNCTION_NORMAL_WRITE_EXTRA_IN_SUFFIX_2_LOW_LEVEL, (message_length, message_chunk_offset, message_chunk_data, extra_1, extra_2), 'H H 58c B B', '')

    def normal_write_extra_in_full_low_level(self, extra_1, message_length, extra_2, message_chunk_offset, extra_3, message_chunk_data, extra_4):
        """

        """
        extra_1 = int(extra_1)
        message_length = int(message_length)
        extra_2 = int(extra_2)
        message_chunk_offset = int(message_chunk_offset)
        extra_3 = int(extra_3)
        message_chunk_data = create_char_list(message_chunk_data)
        extra_4 = int(extra_4)

        self.ipcon.send_request(self, BrickletStreamTest.FUNCTION_NORMAL_WRITE_EXTRA_IN_FULL_LOW_LEVEL, (extra_1, message_length, extra_2, message_chunk_offset, extra_3, message_chunk_data, extra_4), 'B H B H B 56c B', '')

    def normal_write_extra_out_1_low_level(self, message_length, message_chunk_offset, message_chunk_data):
        """

        """
        message_length = int(message_length)
        message_chunk_offset = int(message_chunk_offset)
        message_chunk_data = create_char_list(message_chunk_data)

        return self.ipcon.send_request(self, BrickletStreamTest.FUNCTION_NORMAL_WRITE_EXTRA_OUT_1_LOW_LEVEL, (message_length, message_chunk_offset, message_chunk_data), 'H H 60c', 'B')

    def normal_write_extra_out_2_low_level(self, message_length, message_chunk_offset, message_chunk_data):
        """

        """
        message_length = int(message_length)
        message_chunk_offset = int(message_chunk_offset)
        message_chunk_data = create_char_list(message_chunk_data)

        return NormalWriteExtraOut2LowLevel(*self.ipcon.send_request(self, BrickletStreamTest.FUNCTION_NORMAL_WRITE_EXTRA_OUT_2_LOW_LEVEL, (message_length, message_chunk_offset, message_chunk_data), 'H H 60c', 'B B'))

    def fixed_write_low_level(self, message_chunk_offset, message_chunk_data):
        """

        """
        message_chunk_offset = int(message_chunk_offset)
        message_chunk_data = create_char_list(message_chunk_data)

        self.ipcon.send_request(self, BrickletStreamTest.FUNCTION_FIXED_WRITE_LOW_LEVEL, (message_chunk_offset, message_chunk_data), 'H 62c', '')

    def fixed_write_extra_in_prefix_1_low_level(self, extra, message_chunk_offset, message_chunk_data):
        """

        """
        extra = int(extra)
        message_chunk_offset = int(message_chunk_offset)
        message_chunk_data = create_char_list(message_chunk_data)

        self.ipcon.send_request(self, BrickletStreamTest.FUNCTION_FIXED_WRITE_EXTRA_IN_PREFIX_1_LOW_LEVEL, (extra, message_chunk_offset, message_chunk_data), 'B H 61c', '')

    def fixed_write_extra_in_prefix_2_low_level(self, extra_1, extra_2, message_chunk_offset, message_chunk_data):
        """

        """
        extra_1 = int(extra_1)
        extra_2 = int(extra_2)
        message_chunk_offset = int(message_chunk_offset)
        message_chunk_data = create_char_list(message_chunk_data)

        self.ipcon.send_request(self, BrickletStreamTest.FUNCTION_FIXED_WRITE_EXTRA_IN_PREFIX_2_LOW_LEVEL, (extra_1, extra_2, message_chunk_offset, message_chunk_data), 'B B H 60c', '')

    def fixed_write_extra_in_suffix_1_low_level(self, message_chunk_offset, message_chunk_data, extra):
        """

        """
        message_chunk_offset = int(message_chunk_offset)
        message_chunk_data = create_char_list(message_chunk_data)
        extra = int(extra)

        self.ipcon.send_request(self, BrickletStreamTest.FUNCTION_FIXED_WRITE_EXTRA_IN_SUFFIX_1_LOW_LEVEL, (message_chunk_offset, message_chunk_data, extra), 'H 61c B', '')

    def fixed_write_extra_in_suffix_2_low_level(self, message_chunk_offset, message_chunk_data, extra_1, extra_2):
        """

        """
        message_chunk_offset = int(message_chunk_offset)
        message_chunk_data = create_char_list(message_chunk_data)
        extra_1 = int(extra_1)
        extra_2 = int(extra_2)

        self.ipcon.send_request(self, BrickletStreamTest.FUNCTION_FIXED_WRITE_EXTRA_IN_SUFFIX_2_LOW_LEVEL, (message_chunk_offset, message_chunk_data, extra_1, extra_2), 'H 60c B B', '')

    def fixed_write_extra_in_full_low_level(self, extra_1, message_chunk_offset, extra_2, message_chunk_data, extra_3):
        """

        """
        extra_1 = int(extra_1)
        message_chunk_offset = int(message_chunk_offset)
        extra_2 = int(extra_2)
        message_chunk_data = create_char_list(message_chunk_data)
        extra_3 = int(extra_3)

        self.ipcon.send_request(self, BrickletStreamTest.FUNCTION_FIXED_WRITE_EXTRA_IN_FULL_LOW_LEVEL, (extra_1, message_chunk_offset, extra_2, message_chunk_data, extra_3), 'B H B 59c B', '')

    def fixed_write_extra_out_1_low_level(self, message_chunk_offset, message_chunk_data):
        """

        """
        message_chunk_offset = int(message_chunk_offset)
        message_chunk_data = create_char_list(message_chunk_data)

        return self.ipcon.send_request(self, BrickletStreamTest.FUNCTION_FIXED_WRITE_EXTRA_OUT_1_LOW_LEVEL, (message_chunk_offset, message_chunk_data), 'H 62c', 'B')

    def fixed_write_extra_out_2_low_level(self, message_chunk_offset, message_chunk_data):
        """

        """
        message_chunk_offset = int(message_chunk_offset)
        message_chunk_data = create_char_list(message_chunk_data)

        return FixedWriteExtraOut2LowLevel(*self.ipcon.send_request(self, BrickletStreamTest.FUNCTION_FIXED_WRITE_EXTRA_OUT_2_LOW_LEVEL, (message_chunk_offset, message_chunk_data), 'H 62c', 'B B'))

    def short_write_low_level(self, message_length, message_chunk_offset, message_chunk_data):
        """

        """
        message_length = int(message_length)
        message_chunk_offset = int(message_chunk_offset)
        message_chunk_data = create_char_list(message_chunk_data)

        return self.ipcon.send_request(self, BrickletStreamTest.FUNCTION_SHORT_WRITE_LOW_LEVEL, (message_length, message_chunk_offset, message_chunk_data), 'H H 60c', 'B')

    def short_write_extra_in_prefix_1_low_level(self, extra, message_length, message_chunk_offset, message_chunk_data):
        """

        """
        extra = int(extra)
        message_length = int(message_length)
        message_chunk_offset = int(message_chunk_offset)
        message_chunk_data = create_char_list(message_chunk_data)

        return self.ipcon.send_request(self, BrickletStreamTest.FUNCTION_SHORT_WRITE_EXTRA_IN_PREFIX_1_LOW_LEVEL, (extra, message_length, message_chunk_offset, message_chunk_data), 'B H H 59c', 'B')

    def short_write_extra_in_prefix_2_low_level(self, extra_1, extra_2, message_length, message_chunk_offset, message_chunk_data):
        """

        """
        extra_1 = int(extra_1)
        extra_2 = int(extra_2)
        message_length = int(message_length)
        message_chunk_offset = int(message_chunk_offset)
        message_chunk_data = create_char_list(message_chunk_data)

        return self.ipcon.send_request(self, BrickletStreamTest.FUNCTION_SHORT_WRITE_EXTRA_IN_PREFIX_2_LOW_LEVEL, (extra_1, extra_2, message_length, message_chunk_offset, message_chunk_data), 'B B H H 58c', 'B')

    def short_write_extra_in_suffix_1_low_level(self, message_length, message_chunk_offset, message_chunk_data, extra):
        """

        """
        message_length = int(message_length)
        message_chunk_offset = int(message_chunk_offset)
        message_chunk_data = create_char_list(message_chunk_data)
        extra = int(extra)

        return self.ipcon.send_request(self, BrickletStreamTest.FUNCTION_SHORT_WRITE_EXTRA_IN_SUFFIX_1_LOW_LEVEL, (message_length, message_chunk_offset, message_chunk_data, extra), 'H H 59c B', 'B')

    def short_write_extra_in_suffix_2_low_level(self, message_length, message_chunk_offset, message_chunk_data, extra_1, extra_2):
        """

        """
        message_length = int(message_length)
        message_chunk_offset = int(message_chunk_offset)
        message_chunk_data = create_char_list(message_chunk_data)
        extra_1 = int(extra_1)
        extra_2 = int(extra_2)

        return self.ipcon.send_request(self, BrickletStreamTest.FUNCTION_SHORT_WRITE_EXTRA_IN_SUFFIX_2_LOW_LEVEL, (message_length, message_chunk_offset, message_chunk_data, extra_1, extra_2), 'H H 58c B B', 'B')

    def short_write_extra_out_prefix_1_low_level(self, message_length, message_chunk_offset, message_chunk_data):
        """

        """
        message_length = int(message_length)
        message_chunk_offset = int(message_chunk_offset)
        message_chunk_data = create_char_list(message_chunk_data)

        return ShortWriteExtraOutPrefix1LowLevel(*self.ipcon.send_request(self, BrickletStreamTest.FUNCTION_SHORT_WRITE_EXTRA_OUT_PREFIX_1_LOW_LEVEL, (message_length, message_chunk_offset, message_chunk_data), 'H H 60c', 'B B'))

    def short_write_extra_out_prefix_2_low_level(self, message_length, message_chunk_offset, message_chunk_data):
        """

        """
        message_length = int(message_length)
        message_chunk_offset = int(message_chunk_offset)
        message_chunk_data = create_char_list(message_chunk_data)

        return ShortWriteExtraOutPrefix2LowLevel(*self.ipcon.send_request(self, BrickletStreamTest.FUNCTION_SHORT_WRITE_EXTRA_OUT_PREFIX_2_LOW_LEVEL, (message_length, message_chunk_offset, message_chunk_data), 'H H 60c', 'B B B'))

    def short_write_extra_out_suffix_1_low_level(self, message_length, message_chunk_offset, message_chunk_data):
        """

        """
        message_length = int(message_length)
        message_chunk_offset = int(message_chunk_offset)
        message_chunk_data = create_char_list(message_chunk_data)

        return ShortWriteExtraOutSuffix1LowLevel(*self.ipcon.send_request(self, BrickletStreamTest.FUNCTION_SHORT_WRITE_EXTRA_OUT_SUFFIX_1_LOW_LEVEL, (message_length, message_chunk_offset, message_chunk_data), 'H H 60c', 'B B'))

    def short_write_extra_out_suffix_2_low_level(self, message_length, message_chunk_offset, message_chunk_data):
        """

        """
        message_length = int(message_length)
        message_chunk_offset = int(message_chunk_offset)
        message_chunk_data = create_char_list(message_chunk_data)

        return ShortWriteExtraOutSuffix2LowLevel(*self.ipcon.send_request(self, BrickletStreamTest.FUNCTION_SHORT_WRITE_EXTRA_OUT_SUFFIX_2_LOW_LEVEL, (message_length, message_chunk_offset, message_chunk_data), 'H H 60c', 'B B B'))

    def short_write_extra_full_low_level(self, extra_1, message_length, extra_2, message_chunk_offset, extra_3, message_chunk_data, extra_4):
        """

        """
        extra_1 = int(extra_1)
        message_length = int(message_length)
        extra_2 = int(extra_2)
        message_chunk_offset = int(message_chunk_offset)
        extra_3 = int(extra_3)
        message_chunk_data = create_char_list(message_chunk_data)
        extra_4 = int(extra_4)

        return ShortWriteExtraFullLowLevel(*self.ipcon.send_request(self, BrickletStreamTest.FUNCTION_SHORT_WRITE_EXTRA_FULL_LOW_LEVEL, (extra_1, message_length, extra_2, message_chunk_offset, extra_3, message_chunk_data, extra_4), 'B H B H B 56c B', 'B B B'))

    def single_write_low_level(self, message_length, message_data):
        """

        """
        message_length = int(message_length)
        message_data = create_char_list(message_data)

        self.ipcon.send_request(self, BrickletStreamTest.FUNCTION_SINGLE_WRITE_LOW_LEVEL, (message_length, message_data), 'B 63c', '')

    def single_write_extra_in_prefix_1_low_level(self, extra, message_length, message_data):
        """

        """
        extra = int(extra)
        message_length = int(message_length)
        message_data = create_char_list(message_data)

        self.ipcon.send_request(self, BrickletStreamTest.FUNCTION_SINGLE_WRITE_EXTRA_IN_PREFIX_1_LOW_LEVEL, (extra, message_length, message_data), 'B B 62c', '')

    def single_write_extra_in_prefix_2_low_level(self, extra_1, extra_2, message_length, message_data):
        """

        """
        extra_1 = int(extra_1)
        extra_2 = int(extra_2)
        message_length = int(message_length)
        message_data = create_char_list(message_data)

        self.ipcon.send_request(self, BrickletStreamTest.FUNCTION_SINGLE_WRITE_EXTRA_IN_PREFIX_2_LOW_LEVEL, (extra_1, extra_2, message_length, message_data), 'B B B 61c', '')

    def single_write_extra_in_suffix_1_low_level(self, message_length, message_data, extra):
        """

        """
        message_length = int(message_length)
        message_data = create_char_list(message_data)
        extra = int(extra)

        self.ipcon.send_request(self, BrickletStreamTest.FUNCTION_SINGLE_WRITE_EXTRA_IN_SUFFIX_1_LOW_LEVEL, (message_length, message_data, extra), 'B 62c B', '')

    def single_write_extra_in_suffix_2_low_level(self, message_length, message_data, extra_1, extra_2):
        """

        """
        message_length = int(message_length)
        message_data = create_char_list(message_data)
        extra_1 = int(extra_1)
        extra_2 = int(extra_2)

        self.ipcon.send_request(self, BrickletStreamTest.FUNCTION_SINGLE_WRITE_EXTRA_IN_SUFFIX_2_LOW_LEVEL, (message_length, message_data, extra_1, extra_2), 'B 61c B B', '')

    def single_write_extra_in_full_low_level(self, extra_1, message_length, extra_2, message_data, extra_3):
        """

        """
        extra_1 = int(extra_1)
        message_length = int(message_length)
        extra_2 = int(extra_2)
        message_data = create_char_list(message_data)
        extra_3 = int(extra_3)

        self.ipcon.send_request(self, BrickletStreamTest.FUNCTION_SINGLE_WRITE_EXTRA_IN_FULL_LOW_LEVEL, (extra_1, message_length, extra_2, message_data, extra_3), 'B B B 60c B', '')

    def single_write_extra_out_1_low_level(self, message_length, message_data):
        """

        """
        message_length = int(message_length)
        message_data = create_char_list(message_data)

        return self.ipcon.send_request(self, BrickletStreamTest.FUNCTION_SINGLE_WRITE_EXTRA_OUT_1_LOW_LEVEL, (message_length, message_data), 'B 63c', 'B')

    def single_write_extra_out_2_low_level(self, message_length, message_data):
        """

        """
        message_length = int(message_length)
        message_data = create_char_list(message_data)

        return SingleWriteExtraOut2LowLevel(*self.ipcon.send_request(self, BrickletStreamTest.FUNCTION_SINGLE_WRITE_EXTRA_OUT_2_LOW_LEVEL, (message_length, message_data), 'B 63c', 'B B'))

    def short_single_write_low_level(self, message_length, message_data):
        """

        """
        message_length = int(message_length)
        message_data = create_char_list(message_data)

        return self.ipcon.send_request(self, BrickletStreamTest.FUNCTION_SHORT_SINGLE_WRITE_LOW_LEVEL, (message_length, message_data), 'B 63c', 'B')

    def short_single_write_extra_in_prefix_1_low_level(self, extra, message_length, message_data):
        """

        """
        extra = int(extra)
        message_length = int(message_length)
        message_data = create_char_list(message_data)

        return self.ipcon.send_request(self, BrickletStreamTest.FUNCTION_SHORT_SINGLE_WRITE_EXTRA_IN_PREFIX_1_LOW_LEVEL, (extra, message_length, message_data), 'B B 62c', 'B')

    def short_single_write_extra_in_prefix_2_low_level(self, extra_1, extra_2, message_length, message_data):
        """

        """
        extra_1 = int(extra_1)
        extra_2 = int(extra_2)
        message_length = int(message_length)
        message_data = create_char_list(message_data)

        return self.ipcon.send_request(self, BrickletStreamTest.FUNCTION_SHORT_SINGLE_WRITE_EXTRA_IN_PREFIX_2_LOW_LEVEL, (extra_1, extra_2, message_length, message_data), 'B B B 61c', 'B')

    def short_single_write_extra_in_suffix_1_low_level(self, message_length, message_data, extra):
        """

        """
        message_length = int(message_length)
        message_data = create_char_list(message_data)
        extra = int(extra)

        return self.ipcon.send_request(self, BrickletStreamTest.FUNCTION_SHORT_SINGLE_WRITE_EXTRA_IN_SUFFIX_1_LOW_LEVEL, (message_length, message_data, extra), 'B 62c B', 'B')

    def short_single_write_extra_in_suffix_2_low_level(self, message_length, message_data, extra_1, extra_2):
        """

        """
        message_length = int(message_length)
        message_data = create_char_list(message_data)
        extra_1 = int(extra_1)
        extra_2 = int(extra_2)

        return self.ipcon.send_request(self, BrickletStreamTest.FUNCTION_SHORT_SINGLE_WRITE_EXTRA_IN_SUFFIX_2_LOW_LEVEL, (message_length, message_data, extra_1, extra_2), 'B 61c B B', 'B')

    def short_single_write_extra_out_prefix_1_low_level(self, message_length, message_data):
        """

        """
        message_length = int(message_length)
        message_data = create_char_list(message_data)

        return ShortSingleWriteExtraOutPrefix1LowLevel(*self.ipcon.send_request(self, BrickletStreamTest.FUNCTION_SHORT_SINGLE_WRITE_EXTRA_OUT_PREFIX_1_LOW_LEVEL, (message_length, message_data), 'B 62c', 'B B'))

    def short_single_write_extra_out_prefix_2_low_level(self, message_length, message_data):
        """

        """
        message_length = int(message_length)
        message_data = create_char_list(message_data)

        return ShortSingleWriteExtraOutPrefix2LowLevel(*self.ipcon.send_request(self, BrickletStreamTest.FUNCTION_SHORT_SINGLE_WRITE_EXTRA_OUT_PREFIX_2_LOW_LEVEL, (message_length, message_data), 'B 62c', 'B B B'))

    def short_single_write_extra_out_suffix_1_low_level(self, message_length, message_data):
        """

        """
        message_length = int(message_length)
        message_data = create_char_list(message_data)

        return ShortSingleWriteExtraOutSuffix1LowLevel(*self.ipcon.send_request(self, BrickletStreamTest.FUNCTION_SHORT_SINGLE_WRITE_EXTRA_OUT_SUFFIX_1_LOW_LEVEL, (message_length, message_data), 'B 63c', 'B B'))

    def short_single_write_extra_out_suffix_2_low_level(self, message_length, message_data):
        """

        """
        message_length = int(message_length)
        message_data = create_char_list(message_data)

        return ShortSingleWriteExtraOutSuffix2LowLevel(*self.ipcon.send_request(self, BrickletStreamTest.FUNCTION_SHORT_SINGLE_WRITE_EXTRA_OUT_SUFFIX_2_LOW_LEVEL, (message_length, message_data), 'B 63c', 'B B B'))

    def short_single_write_extra_full_low_level(self, extra_1, message_length, extra_2, message_data, extra_3):
        """

        """
        extra_1 = int(extra_1)
        message_length = int(message_length)
        extra_2 = int(extra_2)
        message_data = create_char_list(message_data)
        extra_3 = int(extra_3)

        return ShortSingleWriteExtraFullLowLevel(*self.ipcon.send_request(self, BrickletStreamTest.FUNCTION_SHORT_SINGLE_WRITE_EXTRA_FULL_LOW_LEVEL, (extra_1, message_length, extra_2, message_data, extra_3), 'B B B 60c B', 'B B B'))

    def normal_read_low_level(self):
        """

        """
        return NormalReadLowLevel(*self.ipcon.send_request(self, BrickletStreamTest.FUNCTION_NORMAL_READ_LOW_LEVEL, (), '', 'H H 60c'))

    def normal_read_extra_in_1_low_level(self, extra):
        """

        """
        extra = int(extra)

        return NormalReadExtraIn1LowLevel(*self.ipcon.send_request(self, BrickletStreamTest.FUNCTION_NORMAL_READ_EXTRA_IN_1_LOW_LEVEL, (extra,), 'B', 'H H 60c'))

    def normal_read_extra_in_2_low_level(self, extra_1, extra_2):
        """

        """
        extra_1 = int(extra_1)
        extra_2 = int(extra_2)

        return NormalReadExtraIn2LowLevel(*self.ipcon.send_request(self, BrickletStreamTest.FUNCTION_NORMAL_READ_EXTRA_IN_2_LOW_LEVEL, (extra_1, extra_2), 'B B', 'H H 60c'))

    def normal_read_extra_out_prefix_1_low_level(self):
        """

        """
        return NormalReadExtraOutPrefix1LowLevel(*self.ipcon.send_request(self, BrickletStreamTest.FUNCTION_NORMAL_READ_EXTRA_OUT_PREFIX_1_LOW_LEVEL, (), '', 'B H H 59c'))

    def normal_read_extra_out_prefix_2_low_level(self):
        """

        """
        return NormalReadExtraOutPrefix2LowLevel(*self.ipcon.send_request(self, BrickletStreamTest.FUNCTION_NORMAL_READ_EXTRA_OUT_PREFIX_2_LOW_LEVEL, (), '', 'B B H H 58c'))

    def normal_read_extra_out_suffix_1_low_level(self):
        """

        """
        return NormalReadExtraOutSuffix1LowLevel(*self.ipcon.send_request(self, BrickletStreamTest.FUNCTION_NORMAL_READ_EXTRA_OUT_SUFFIX_1_LOW_LEVEL, (), '', 'H H 59c B'))

    def normal_read_extra_out_suffix_2_low_level(self):
        """

        """
        return NormalReadExtraOutSuffix2LowLevel(*self.ipcon.send_request(self, BrickletStreamTest.FUNCTION_NORMAL_READ_EXTRA_OUT_SUFFIX_2_LOW_LEVEL, (), '', 'H H 58c B B'))

    def normal_read_extra_out_full_low_level(self):
        """

        """
        return NormalReadExtraOutFullLowLevel(*self.ipcon.send_request(self, BrickletStreamTest.FUNCTION_NORMAL_READ_EXTRA_OUT_FULL_LOW_LEVEL, (), '', 'B H B H B 56c B'))

    def fixed_read_low_level(self):
        """

        """
        return FixedReadLowLevel(*self.ipcon.send_request(self, BrickletStreamTest.FUNCTION_FIXED_READ_LOW_LEVEL, (), '', 'H 62c'))

    def fixed_read_extra_in_1_low_level(self, extra):
        """

        """
        extra = int(extra)

        return FixedReadExtraIn1LowLevel(*self.ipcon.send_request(self, BrickletStreamTest.FUNCTION_FIXED_READ_EXTRA_IN_1_LOW_LEVEL, (extra,), 'B', 'H 62c'))

    def fixed_read_extra_in_2_low_level(self, extra_1, extra_2):
        """

        """
        extra_1 = int(extra_1)
        extra_2 = int(extra_2)

        return FixedReadExtraIn2LowLevel(*self.ipcon.send_request(self, BrickletStreamTest.FUNCTION_FIXED_READ_EXTRA_IN_2_LOW_LEVEL, (extra_1, extra_2), 'B B', 'H 62c'))

    def fixed_read_extra_out_prefix_1_low_level(self):
        """

        """
        return FixedReadExtraOutPrefix1LowLevel(*self.ipcon.send_request(self, BrickletStreamTest.FUNCTION_FIXED_READ_EXTRA_OUT_PREFIX_1_LOW_LEVEL, (), '', 'B H 61c'))

    def fixed_read_extra_out_prefix_2_low_level(self):
        """

        """
        return FixedReadExtraOutPrefix2LowLevel(*self.ipcon.send_request(self, BrickletStreamTest.FUNCTION_FIXED_READ_EXTRA_OUT_PREFIX_2_LOW_LEVEL, (), '', 'B B H 60c'))

    def fixed_read_extra_out_suffix_1_low_level(self):
        """

        """
        return FixedReadExtraOutSuffix1LowLevel(*self.ipcon.send_request(self, BrickletStreamTest.FUNCTION_FIXED_READ_EXTRA_OUT_SUFFIX_1_LOW_LEVEL, (), '', 'H 61c B'))

    def fixed_read_extra_out_suffix_2_low_level(self):
        """

        """
        return FixedReadExtraOutSuffix2LowLevel(*self.ipcon.send_request(self, BrickletStreamTest.FUNCTION_FIXED_READ_EXTRA_OUT_SUFFIX_2_LOW_LEVEL, (), '', 'H 60c B B'))

    def fixed_read_extra_out_full_low_level(self):
        """

        """
        return FixedReadExtraOutFullLowLevel(*self.ipcon.send_request(self, BrickletStreamTest.FUNCTION_FIXED_READ_EXTRA_OUT_FULL_LOW_LEVEL, (), '', 'B H B 59c B'))

    def single_read_low_level(self):
        """

        """
        return SingleReadLowLevel(*self.ipcon.send_request(self, BrickletStreamTest.FUNCTION_SINGLE_READ_LOW_LEVEL, (), '', 'B 63c'))

    def single_read_extra_in_1_low_level(self, extra):
        """

        """
        extra = int(extra)

        return SingleReadExtraIn1LowLevel(*self.ipcon.send_request(self, BrickletStreamTest.FUNCTION_SINGLE_READ_EXTRA_IN_1_LOW_LEVEL, (extra,), 'B', 'B 62c'))

    def single_read_extra_in_2_low_level(self, extra_1, extra_2):
        """

        """
        extra_1 = int(extra_1)
        extra_2 = int(extra_2)

        return SingleReadExtraIn2LowLevel(*self.ipcon.send_request(self, BrickletStreamTest.FUNCTION_SINGLE_READ_EXTRA_IN_2_LOW_LEVEL, (extra_1, extra_2), 'B B', 'B 62c'))

    def single_read_extra_out_prefix_1_low_level(self):
        """

        """
        return SingleReadExtraOutPrefix1LowLevel(*self.ipcon.send_request(self, BrickletStreamTest.FUNCTION_SINGLE_READ_EXTRA_OUT_PREFIX_1_LOW_LEVEL, (), '', 'B B 62c'))

    def single_read_extra_out_prefix_2_low_level(self):
        """

        """
        return SingleReadExtraOutPrefix2LowLevel(*self.ipcon.send_request(self, BrickletStreamTest.FUNCTION_SINGLE_READ_EXTRA_OUT_PREFIX_2_LOW_LEVEL, (), '', 'B B B 61c'))

    def single_read_extra_out_suffix_1_low_level(self):
        """

        """
        return SingleReadExtraOutSuffix1LowLevel(*self.ipcon.send_request(self, BrickletStreamTest.FUNCTION_SINGLE_READ_EXTRA_OUT_SUFFIX_1_LOW_LEVEL, (), '', 'B 62c B'))

    def single_read_extra_out_suffix_2_low_level(self):
        """

        """
        return SingleReadExtraOutSuffix2LowLevel(*self.ipcon.send_request(self, BrickletStreamTest.FUNCTION_SINGLE_READ_EXTRA_OUT_SUFFIX_2_LOW_LEVEL, (), '', 'B 61c B B'))

    def single_read_extra_out_full_low_level(self):
        """

        """
        return SingleReadExtraOutFullLowLevel(*self.ipcon.send_request(self, BrickletStreamTest.FUNCTION_SINGLE_READ_EXTRA_OUT_FULL_LOW_LEVEL, (), '', 'B B B 60c B'))

    def get_identity(self):
        """
        Returns the UID, the UID where the Bricklet is connected to,
        the position, the hardware and firmware version as well as the
        device identifier.

        The position can be 'a', 'b', 'c' or 'd'.

        The device identifier numbers can be found :ref:`here <device_identifier>`.
        |device_identifier_constant|
        """
        return GetIdentity(*self.ipcon.send_request(self, BrickletStreamTest.FUNCTION_GET_IDENTITY, (), '', '8s 8s c 3B 3B H'))

    def normal_write(self, message):
        """

        """
        message = create_char_list(message)

        if len(message) > 65535:
            raise Error(Error.INVALID_PARAMETER, 'Message can be at most 65535 items long')

        message_length = len(message)
        message_chunk_offset = 0

        if message_length == 0:
            message_chunk_data = ['\0'] * 60
            ret = self.normal_write_low_level(message_length, message_chunk_offset, message_chunk_data)
        else:
            with self.stream_lock:
                while message_chunk_offset < message_length:
                    message_chunk_data = create_chunk_data(message, message_chunk_offset, 60, '\0')
                    ret = self.normal_write_low_level(message_length, message_chunk_offset, message_chunk_data)
                    message_chunk_offset += 60

        return ret

    def normal_write_extra_in_prefix_1(self, extra, message):
        """

        """
        extra = int(extra)
        message = create_char_list(message)

        if len(message) > 65535:
            raise Error(Error.INVALID_PARAMETER, 'Message can be at most 65535 items long')

        message_length = len(message)
        message_chunk_offset = 0

        if message_length == 0:
            message_chunk_data = ['\0'] * 59
            ret = self.normal_write_extra_in_prefix_1_low_level(extra, message_length, message_chunk_offset, message_chunk_data)
        else:
            with self.stream_lock:
                while message_chunk_offset < message_length:
                    message_chunk_data = create_chunk_data(message, message_chunk_offset, 59, '\0')
                    ret = self.normal_write_extra_in_prefix_1_low_level(extra, message_length, message_chunk_offset, message_chunk_data)
                    message_chunk_offset += 59

        return ret

    def normal_write_extra_in_prefix_2(self, extra_1, extra_2, message):
        """

        """
        extra_1 = int(extra_1)
        extra_2 = int(extra_2)
        message = create_char_list(message)

        if len(message) > 65535:
            raise Error(Error.INVALID_PARAMETER, 'Message can be at most 65535 items long')

        message_length = len(message)
        message_chunk_offset = 0

        if message_length == 0:
            message_chunk_data = ['\0'] * 58
            ret = self.normal_write_extra_in_prefix_2_low_level(extra_1, extra_2, message_length, message_chunk_offset, message_chunk_data)
        else:
            with self.stream_lock:
                while message_chunk_offset < message_length:
                    message_chunk_data = create_chunk_data(message, message_chunk_offset, 58, '\0')
                    ret = self.normal_write_extra_in_prefix_2_low_level(extra_1, extra_2, message_length, message_chunk_offset, message_chunk_data)
                    message_chunk_offset += 58

        return ret

    def normal_write_extra_in_suffix_1(self, message, extra):
        """

        """
        message = create_char_list(message)
        extra = int(extra)

        if len(message) > 65535:
            raise Error(Error.INVALID_PARAMETER, 'Message can be at most 65535 items long')

        message_length = len(message)
        message_chunk_offset = 0

        if message_length == 0:
            message_chunk_data = ['\0'] * 59
            ret = self.normal_write_extra_in_suffix_1_low_level(message_length, message_chunk_offset, message_chunk_data, extra)
        else:
            with self.stream_lock:
                while message_chunk_offset < message_length:
                    message_chunk_data = create_chunk_data(message, message_chunk_offset, 59, '\0')
                    ret = self.normal_write_extra_in_suffix_1_low_level(message_length, message_chunk_offset, message_chunk_data, extra)
                    message_chunk_offset += 59

        return ret

    def normal_write_extra_in_suffix_2(self, message, extra_1, extra_2):
        """

        """
        message = create_char_list(message)
        extra_1 = int(extra_1)
        extra_2 = int(extra_2)

        if len(message) > 65535:
            raise Error(Error.INVALID_PARAMETER, 'Message can be at most 65535 items long')

        message_length = len(message)
        message_chunk_offset = 0

        if message_length == 0:
            message_chunk_data = ['\0'] * 58
            ret = self.normal_write_extra_in_suffix_2_low_level(message_length, message_chunk_offset, message_chunk_data, extra_1, extra_2)
        else:
            with self.stream_lock:
                while message_chunk_offset < message_length:
                    message_chunk_data = create_chunk_data(message, message_chunk_offset, 58, '\0')
                    ret = self.normal_write_extra_in_suffix_2_low_level(message_length, message_chunk_offset, message_chunk_data, extra_1, extra_2)
                    message_chunk_offset += 58

        return ret

    def normal_write_extra_in_full(self, extra_1, extra_2, extra_3, message, extra_4):
        """

        """
        extra_1 = int(extra_1)
        extra_2 = int(extra_2)
        extra_3 = int(extra_3)
        message = create_char_list(message)
        extra_4 = int(extra_4)

        if len(message) > 65535:
            raise Error(Error.INVALID_PARAMETER, 'Message can be at most 65535 items long')

        message_length = len(message)
        message_chunk_offset = 0

        if message_length == 0:
            message_chunk_data = ['\0'] * 56
            ret = self.normal_write_extra_in_full_low_level(extra_1, message_length, extra_2, message_chunk_offset, extra_3, message_chunk_data, extra_4)
        else:
            with self.stream_lock:
                while message_chunk_offset < message_length:
                    message_chunk_data = create_chunk_data(message, message_chunk_offset, 56, '\0')
                    ret = self.normal_write_extra_in_full_low_level(extra_1, message_length, extra_2, message_chunk_offset, extra_3, message_chunk_data, extra_4)
                    message_chunk_offset += 56

        return ret

    def normal_write_extra_out_1(self, message):
        """

        """
        message = create_char_list(message)

        if len(message) > 65535:
            raise Error(Error.INVALID_PARAMETER, 'Message can be at most 65535 items long')

        message_length = len(message)
        message_chunk_offset = 0

        if message_length == 0:
            message_chunk_data = ['\0'] * 60
            ret = self.normal_write_extra_out_1_low_level(message_length, message_chunk_offset, message_chunk_data)
        else:
            with self.stream_lock:
                while message_chunk_offset < message_length:
                    message_chunk_data = create_chunk_data(message, message_chunk_offset, 60, '\0')
                    ret = self.normal_write_extra_out_1_low_level(message_length, message_chunk_offset, message_chunk_data)
                    message_chunk_offset += 60

        return ret

    def normal_write_extra_out_2(self, message):
        """

        """
        message = create_char_list(message)

        if len(message) > 65535:
            raise Error(Error.INVALID_PARAMETER, 'Message can be at most 65535 items long')

        message_length = len(message)
        message_chunk_offset = 0

        if message_length == 0:
            message_chunk_data = ['\0'] * 60
            ret = self.normal_write_extra_out_2_low_level(message_length, message_chunk_offset, message_chunk_data)
        else:
            with self.stream_lock:
                while message_chunk_offset < message_length:
                    message_chunk_data = create_chunk_data(message, message_chunk_offset, 60, '\0')
                    ret = self.normal_write_extra_out_2_low_level(message_length, message_chunk_offset, message_chunk_data)
                    message_chunk_offset += 60

        return NormalWriteExtraOut2(*ret)

    def fixed_write(self, message):
        """

        """
        message = create_char_list(message)

        message_length = 1000
        message_chunk_offset = 0

        if len(message) != message_length:
            raise Error(Error.INVALID_PARAMETER, 'Message has to be exactly {0} items long'.format(message_length))

        with self.stream_lock:
            while message_chunk_offset < message_length:
                message_chunk_data = create_chunk_data(message, message_chunk_offset, 62, '\0')
                ret = self.fixed_write_low_level(message_chunk_offset, message_chunk_data)
                message_chunk_offset += 62

        return ret

    def fixed_write_extra_in_prefix_1(self, extra, message):
        """

        """
        extra = int(extra)
        message = create_char_list(message)

        message_length = 1000
        message_chunk_offset = 0

        if len(message) != message_length:
            raise Error(Error.INVALID_PARAMETER, 'Message has to be exactly {0} items long'.format(message_length))

        with self.stream_lock:
            while message_chunk_offset < message_length:
                message_chunk_data = create_chunk_data(message, message_chunk_offset, 61, '\0')
                ret = self.fixed_write_extra_in_prefix_1_low_level(extra, message_chunk_offset, message_chunk_data)
                message_chunk_offset += 61

        return ret

    def fixed_write_extra_in_prefix_2(self, extra_1, extra_2, message):
        """

        """
        extra_1 = int(extra_1)
        extra_2 = int(extra_2)
        message = create_char_list(message)

        message_length = 1000
        message_chunk_offset = 0

        if len(message) != message_length:
            raise Error(Error.INVALID_PARAMETER, 'Message has to be exactly {0} items long'.format(message_length))

        with self.stream_lock:
            while message_chunk_offset < message_length:
                message_chunk_data = create_chunk_data(message, message_chunk_offset, 60, '\0')
                ret = self.fixed_write_extra_in_prefix_2_low_level(extra_1, extra_2, message_chunk_offset, message_chunk_data)
                message_chunk_offset += 60

        return ret

    def fixed_write_extra_in_suffix_1(self, message, extra):
        """

        """
        message = create_char_list(message)
        extra = int(extra)

        message_length = 1000
        message_chunk_offset = 0

        if len(message) != message_length:
            raise Error(Error.INVALID_PARAMETER, 'Message has to be exactly {0} items long'.format(message_length))

        with self.stream_lock:
            while message_chunk_offset < message_length:
                message_chunk_data = create_chunk_data(message, message_chunk_offset, 61, '\0')
                ret = self.fixed_write_extra_in_suffix_1_low_level(message_chunk_offset, message_chunk_data, extra)
                message_chunk_offset += 61

        return ret

    def fixed_write_extra_in_suffix_2(self, message, extra_1, extra_2):
        """

        """
        message = create_char_list(message)
        extra_1 = int(extra_1)
        extra_2 = int(extra_2)

        message_length = 1000
        message_chunk_offset = 0

        if len(message) != message_length:
            raise Error(Error.INVALID_PARAMETER, 'Message has to be exactly {0} items long'.format(message_length))

        with self.stream_lock:
            while message_chunk_offset < message_length:
                message_chunk_data = create_chunk_data(message, message_chunk_offset, 60, '\0')
                ret = self.fixed_write_extra_in_suffix_2_low_level(message_chunk_offset, message_chunk_data, extra_1, extra_2)
                message_chunk_offset += 60

        return ret

    def fixed_write_extra_in_full(self, extra_1, extra_2, message, extra_3):
        """

        """
        extra_1 = int(extra_1)
        extra_2 = int(extra_2)
        message = create_char_list(message)
        extra_3 = int(extra_3)

        message_length = 1000
        message_chunk_offset = 0

        if len(message) != message_length:
            raise Error(Error.INVALID_PARAMETER, 'Message has to be exactly {0} items long'.format(message_length))

        with self.stream_lock:
            while message_chunk_offset < message_length:
                message_chunk_data = create_chunk_data(message, message_chunk_offset, 59, '\0')
                ret = self.fixed_write_extra_in_full_low_level(extra_1, message_chunk_offset, extra_2, message_chunk_data, extra_3)
                message_chunk_offset += 59

        return ret

    def fixed_write_extra_out_1(self, message):
        """

        """
        message = create_char_list(message)

        message_length = 1000
        message_chunk_offset = 0

        if len(message) != message_length:
            raise Error(Error.INVALID_PARAMETER, 'Message has to be exactly {0} items long'.format(message_length))

        with self.stream_lock:
            while message_chunk_offset < message_length:
                message_chunk_data = create_chunk_data(message, message_chunk_offset, 62, '\0')
                ret = self.fixed_write_extra_out_1_low_level(message_chunk_offset, message_chunk_data)
                message_chunk_offset += 62

        return ret

    def fixed_write_extra_out_2(self, message):
        """

        """
        message = create_char_list(message)

        message_length = 1000
        message_chunk_offset = 0

        if len(message) != message_length:
            raise Error(Error.INVALID_PARAMETER, 'Message has to be exactly {0} items long'.format(message_length))

        with self.stream_lock:
            while message_chunk_offset < message_length:
                message_chunk_data = create_chunk_data(message, message_chunk_offset, 62, '\0')
                ret = self.fixed_write_extra_out_2_low_level(message_chunk_offset, message_chunk_data)
                message_chunk_offset += 62

        return FixedWriteExtraOut2(*ret)

    def short_write(self, message):
        """

        """
        message = create_char_list(message)

        if len(message) > 65535:
            raise Error(Error.INVALID_PARAMETER, 'Message can be at most 65535 items long')

        message_length = len(message)
        message_chunk_offset = 0

        if message_length == 0:
            message_chunk_data = ['\0'] * 60
            ret = self.short_write_low_level(message_length, message_chunk_offset, message_chunk_data)
            message_written = ret
        else:
            message_written = 0

            with self.stream_lock:
                while message_chunk_offset < message_length:
                    message_chunk_data = create_chunk_data(message, message_chunk_offset, 60, '\0')
                    ret = self.short_write_low_level(message_length, message_chunk_offset, message_chunk_data)
                    message_written += ret

                    if ret < 60:
                        break # either last chunk or short write

                    message_chunk_offset += 60

        return message_written

    def short_write_extra_in_prefix_1(self, extra, message):
        """

        """
        extra = int(extra)
        message = create_char_list(message)

        if len(message) > 65535:
            raise Error(Error.INVALID_PARAMETER, 'Message can be at most 65535 items long')

        message_length = len(message)
        message_chunk_offset = 0

        if message_length == 0:
            message_chunk_data = ['\0'] * 59
            ret = self.short_write_extra_in_prefix_1_low_level(extra, message_length, message_chunk_offset, message_chunk_data)
            message_written = ret
        else:
            message_written = 0

            with self.stream_lock:
                while message_chunk_offset < message_length:
                    message_chunk_data = create_chunk_data(message, message_chunk_offset, 59, '\0')
                    ret = self.short_write_extra_in_prefix_1_low_level(extra, message_length, message_chunk_offset, message_chunk_data)
                    message_written += ret

                    if ret < 59:
                        break # either last chunk or short write

                    message_chunk_offset += 59

        return message_written

    def short_write_extra_in_prefix_2(self, extra_1, extra_2, message):
        """

        """
        extra_1 = int(extra_1)
        extra_2 = int(extra_2)
        message = create_char_list(message)

        if len(message) > 65535:
            raise Error(Error.INVALID_PARAMETER, 'Message can be at most 65535 items long')

        message_length = len(message)
        message_chunk_offset = 0

        if message_length == 0:
            message_chunk_data = ['\0'] * 58
            ret = self.short_write_extra_in_prefix_2_low_level(extra_1, extra_2, message_length, message_chunk_offset, message_chunk_data)
            message_written = ret
        else:
            message_written = 0

            with self.stream_lock:
                while message_chunk_offset < message_length:
                    message_chunk_data = create_chunk_data(message, message_chunk_offset, 58, '\0')
                    ret = self.short_write_extra_in_prefix_2_low_level(extra_1, extra_2, message_length, message_chunk_offset, message_chunk_data)
                    message_written += ret

                    if ret < 58:
                        break # either last chunk or short write

                    message_chunk_offset += 58

        return message_written

    def short_write_extra_in_suffix_1(self, message, extra):
        """

        """
        message = create_char_list(message)
        extra = int(extra)

        if len(message) > 65535:
            raise Error(Error.INVALID_PARAMETER, 'Message can be at most 65535 items long')

        message_length = len(message)
        message_chunk_offset = 0

        if message_length == 0:
            message_chunk_data = ['\0'] * 59
            ret = self.short_write_extra_in_suffix_1_low_level(message_length, message_chunk_offset, message_chunk_data, extra)
            message_written = ret
        else:
            message_written = 0

            with self.stream_lock:
                while message_chunk_offset < message_length:
                    message_chunk_data = create_chunk_data(message, message_chunk_offset, 59, '\0')
                    ret = self.short_write_extra_in_suffix_1_low_level(message_length, message_chunk_offset, message_chunk_data, extra)
                    message_written += ret

                    if ret < 59:
                        break # either last chunk or short write

                    message_chunk_offset += 59

        return message_written

    def short_write_extra_in_suffix_2(self, message, extra_1, extra_2):
        """

        """
        message = create_char_list(message)
        extra_1 = int(extra_1)
        extra_2 = int(extra_2)

        if len(message) > 65535:
            raise Error(Error.INVALID_PARAMETER, 'Message can be at most 65535 items long')

        message_length = len(message)
        message_chunk_offset = 0

        if message_length == 0:
            message_chunk_data = ['\0'] * 58
            ret = self.short_write_extra_in_suffix_2_low_level(message_length, message_chunk_offset, message_chunk_data, extra_1, extra_2)
            message_written = ret
        else:
            message_written = 0

            with self.stream_lock:
                while message_chunk_offset < message_length:
                    message_chunk_data = create_chunk_data(message, message_chunk_offset, 58, '\0')
                    ret = self.short_write_extra_in_suffix_2_low_level(message_length, message_chunk_offset, message_chunk_data, extra_1, extra_2)
                    message_written += ret

                    if ret < 58:
                        break # either last chunk or short write

                    message_chunk_offset += 58

        return message_written

    def short_write_extra_out_prefix_1(self, message):
        """

        """
        message = create_char_list(message)

        if len(message) > 65535:
            raise Error(Error.INVALID_PARAMETER, 'Message can be at most 65535 items long')

        message_length = len(message)
        message_chunk_offset = 0

        if message_length == 0:
            message_chunk_data = ['\0'] * 60
            ret = self.short_write_extra_out_prefix_1_low_level(message_length, message_chunk_offset, message_chunk_data)
            message_written = ret.message_chunk_written
        else:
            message_written = 0

            with self.stream_lock:
                while message_chunk_offset < message_length:
                    message_chunk_data = create_chunk_data(message, message_chunk_offset, 60, '\0')
                    ret = self.short_write_extra_out_prefix_1_low_level(message_length, message_chunk_offset, message_chunk_data)
                    message_written += ret.message_chunk_written

                    if ret.message_chunk_written < 60:
                        break # either last chunk or short write

                    message_chunk_offset += 60

        return ShortWriteExtraOutPrefix1(ret.extra, message_written)

    def short_write_extra_out_prefix_2(self, message):
        """

        """
        message = create_char_list(message)

        if len(message) > 65535:
            raise Error(Error.INVALID_PARAMETER, 'Message can be at most 65535 items long')

        message_length = len(message)
        message_chunk_offset = 0

        if message_length == 0:
            message_chunk_data = ['\0'] * 60
            ret = self.short_write_extra_out_prefix_2_low_level(message_length, message_chunk_offset, message_chunk_data)
            message_written = ret.message_chunk_written
        else:
            message_written = 0

            with self.stream_lock:
                while message_chunk_offset < message_length:
                    message_chunk_data = create_chunk_data(message, message_chunk_offset, 60, '\0')
                    ret = self.short_write_extra_out_prefix_2_low_level(message_length, message_chunk_offset, message_chunk_data)
                    message_written += ret.message_chunk_written

                    if ret.message_chunk_written < 60:
                        break # either last chunk or short write

                    message_chunk_offset += 60

        return ShortWriteExtraOutPrefix2(ret.extra_1, ret.extra_2, message_written)

    def short_write_extra_out_suffix_1(self, message):
        """

        """
        message = create_char_list(message)

        if len(message) > 65535:
            raise Error(Error.INVALID_PARAMETER, 'Message can be at most 65535 items long')

        message_length = len(message)
        message_chunk_offset = 0

        if message_length == 0:
            message_chunk_data = ['\0'] * 60
            ret = self.short_write_extra_out_suffix_1_low_level(message_length, message_chunk_offset, message_chunk_data)
            message_written = ret.message_chunk_written
        else:
            message_written = 0

            with self.stream_lock:
                while message_chunk_offset < message_length:
                    message_chunk_data = create_chunk_data(message, message_chunk_offset, 60, '\0')
                    ret = self.short_write_extra_out_suffix_1_low_level(message_length, message_chunk_offset, message_chunk_data)
                    message_written += ret.message_chunk_written

                    if ret.message_chunk_written < 60:
                        break # either last chunk or short write

                    message_chunk_offset += 60

        return ShortWriteExtraOutSuffix1(message_written, ret.extra)

    def short_write_extra_out_suffix_2(self, message):
        """

        """
        message = create_char_list(message)

        if len(message) > 65535:
            raise Error(Error.INVALID_PARAMETER, 'Message can be at most 65535 items long')

        message_length = len(message)
        message_chunk_offset = 0

        if message_length == 0:
            message_chunk_data = ['\0'] * 60
            ret = self.short_write_extra_out_suffix_2_low_level(message_length, message_chunk_offset, message_chunk_data)
            message_written = ret.message_chunk_written
        else:
            message_written = 0

            with self.stream_lock:
                while message_chunk_offset < message_length:
                    message_chunk_data = create_chunk_data(message, message_chunk_offset, 60, '\0')
                    ret = self.short_write_extra_out_suffix_2_low_level(message_length, message_chunk_offset, message_chunk_data)
                    message_written += ret.message_chunk_written

                    if ret.message_chunk_written < 60:
                        break # either last chunk or short write

                    message_chunk_offset += 60

        return ShortWriteExtraOutSuffix2(message_written, ret.extra_1, ret.extra_2)

    def short_write_extra_full(self, extra_1, extra_2, extra_3, message, extra_4):
        """

        """
        extra_1 = int(extra_1)
        extra_2 = int(extra_2)
        extra_3 = int(extra_3)
        message = create_char_list(message)
        extra_4 = int(extra_4)

        if len(message) > 65535:
            raise Error(Error.INVALID_PARAMETER, 'Message can be at most 65535 items long')

        message_length = len(message)
        message_chunk_offset = 0

        if message_length == 0:
            message_chunk_data = ['\0'] * 56
            ret = self.short_write_extra_full_low_level(extra_1, message_length, extra_2, message_chunk_offset, extra_3, message_chunk_data, extra_4)
            message_written = ret.message_chunk_written
        else:
            message_written = 0

            with self.stream_lock:
                while message_chunk_offset < message_length:
                    message_chunk_data = create_chunk_data(message, message_chunk_offset, 56, '\0')
                    ret = self.short_write_extra_full_low_level(extra_1, message_length, extra_2, message_chunk_offset, extra_3, message_chunk_data, extra_4)
                    message_written += ret.message_chunk_written

                    if ret.message_chunk_written < 56:
                        break # either last chunk or short write

                    message_chunk_offset += 56

        return ShortWriteExtraFull(ret.extra_5, message_written, ret.extra_6)

    def single_write(self, message):
        """

        """
        message = create_char_list(message)

        message_length = len(message)
        message_data = list(message) # make a copy so we can potentially extend it

        if message_length > 63:
            raise Error(Error.INVALID_PARAMETER, 'Message can be at most 63 items long')

        if message_length < 63:
            message_data += ['\0'] * (63 - message_length)

        return self.single_write_low_level(message_length, message_data)

    def single_write_extra_in_prefix_1(self, extra, message):
        """

        """
        extra = int(extra)
        message = create_char_list(message)

        message_length = len(message)
        message_data = list(message) # make a copy so we can potentially extend it

        if message_length > 62:
            raise Error(Error.INVALID_PARAMETER, 'Message can be at most 62 items long')

        if message_length < 62:
            message_data += ['\0'] * (62 - message_length)

        return self.single_write_extra_in_prefix_1_low_level(extra, message_length, message_data)

    def single_write_extra_in_prefix_2(self, extra_1, extra_2, message):
        """

        """
        extra_1 = int(extra_1)
        extra_2 = int(extra_2)
        message = create_char_list(message)

        message_length = len(message)
        message_data = list(message) # make a copy so we can potentially extend it

        if message_length > 61:
            raise Error(Error.INVALID_PARAMETER, 'Message can be at most 61 items long')

        if message_length < 61:
            message_data += ['\0'] * (61 - message_length)

        return self.single_write_extra_in_prefix_2_low_level(extra_1, extra_2, message_length, message_data)

    def single_write_extra_in_suffix_1(self, message, extra):
        """

        """
        message = create_char_list(message)
        extra = int(extra)

        message_length = len(message)
        message_data = list(message) # make a copy so we can potentially extend it

        if message_length > 62:
            raise Error(Error.INVALID_PARAMETER, 'Message can be at most 62 items long')

        if message_length < 62:
            message_data += ['\0'] * (62 - message_length)

        return self.single_write_extra_in_suffix_1_low_level(message_length, message_data, extra)

    def single_write_extra_in_suffix_2(self, message, extra_1, extra_2):
        """

        """
        message = create_char_list(message)
        extra_1 = int(extra_1)
        extra_2 = int(extra_2)

        message_length = len(message)
        message_data = list(message) # make a copy so we can potentially extend it

        if message_length > 61:
            raise Error(Error.INVALID_PARAMETER, 'Message can be at most 61 items long')

        if message_length < 61:
            message_data += ['\0'] * (61 - message_length)

        return self.single_write_extra_in_suffix_2_low_level(message_length, message_data, extra_1, extra_2)

    def single_write_extra_in_full(self, extra_1, extra_2, message, extra_3):
        """

        """
        extra_1 = int(extra_1)
        extra_2 = int(extra_2)
        message = create_char_list(message)
        extra_3 = int(extra_3)

        message_length = len(message)
        message_data = list(message) # make a copy so we can potentially extend it

        if message_length > 60:
            raise Error(Error.INVALID_PARAMETER, 'Message can be at most 60 items long')

        if message_length < 60:
            message_data += ['\0'] * (60 - message_length)

        return self.single_write_extra_in_full_low_level(extra_1, message_length, extra_2, message_data, extra_3)

    def single_write_extra_out_1(self, message):
        """

        """
        message = create_char_list(message)

        message_length = len(message)
        message_data = list(message) # make a copy so we can potentially extend it

        if message_length > 63:
            raise Error(Error.INVALID_PARAMETER, 'Message can be at most 63 items long')

        if message_length < 63:
            message_data += ['\0'] * (63 - message_length)

        return self.single_write_extra_out_1_low_level(message_length, message_data)

    def single_write_extra_out_2(self, message):
        """

        """
        message = create_char_list(message)

        message_length = len(message)
        message_data = list(message) # make a copy so we can potentially extend it

        if message_length > 63:
            raise Error(Error.INVALID_PARAMETER, 'Message can be at most 63 items long')

        if message_length < 63:
            message_data += ['\0'] * (63 - message_length)

        return SingleWriteExtraOut2(*self.single_write_extra_out_2_low_level(message_length, message_data))

    def short_single_write(self, message):
        """

        """
        message = create_char_list(message)

        message_length = len(message)
        message_data = list(message) # make a copy so we can potentially extend it

        if message_length > 63:
            raise Error(Error.INVALID_PARAMETER, 'Message can be at most 63 items long')

        if message_length < 63:
            message_data += ['\0'] * (63 - message_length)

        return self.short_single_write_low_level(message_length, message_data)

    def short_single_write_extra_in_prefix_1(self, extra, message):
        """

        """
        extra = int(extra)
        message = create_char_list(message)

        message_length = len(message)
        message_data = list(message) # make a copy so we can potentially extend it

        if message_length > 62:
            raise Error(Error.INVALID_PARAMETER, 'Message can be at most 62 items long')

        if message_length < 62:
            message_data += ['\0'] * (62 - message_length)

        return self.short_single_write_extra_in_prefix_1_low_level(extra, message_length, message_data)

    def short_single_write_extra_in_prefix_2(self, extra_1, extra_2, message):
        """

        """
        extra_1 = int(extra_1)
        extra_2 = int(extra_2)
        message = create_char_list(message)

        message_length = len(message)
        message_data = list(message) # make a copy so we can potentially extend it

        if message_length > 61:
            raise Error(Error.INVALID_PARAMETER, 'Message can be at most 61 items long')

        if message_length < 61:
            message_data += ['\0'] * (61 - message_length)

        return self.short_single_write_extra_in_prefix_2_low_level(extra_1, extra_2, message_length, message_data)

    def short_single_write_extra_in_suffix_1(self, message, extra):
        """

        """
        message = create_char_list(message)
        extra = int(extra)

        message_length = len(message)
        message_data = list(message) # make a copy so we can potentially extend it

        if message_length > 62:
            raise Error(Error.INVALID_PARAMETER, 'Message can be at most 62 items long')

        if message_length < 62:
            message_data += ['\0'] * (62 - message_length)

        return self.short_single_write_extra_in_suffix_1_low_level(message_length, message_data, extra)

    def short_single_write_extra_in_suffix_2(self, message, extra_1, extra_2):
        """

        """
        message = create_char_list(message)
        extra_1 = int(extra_1)
        extra_2 = int(extra_2)

        message_length = len(message)
        message_data = list(message) # make a copy so we can potentially extend it

        if message_length > 61:
            raise Error(Error.INVALID_PARAMETER, 'Message can be at most 61 items long')

        if message_length < 61:
            message_data += ['\0'] * (61 - message_length)

        return self.short_single_write_extra_in_suffix_2_low_level(message_length, message_data, extra_1, extra_2)

    def short_single_write_extra_out_prefix_1(self, message):
        """

        """
        message = create_char_list(message)

        message_length = len(message)
        message_data = list(message) # make a copy so we can potentially extend it

        if message_length > 62:
            raise Error(Error.INVALID_PARAMETER, 'Message can be at most 62 items long')

        if message_length < 62:
            message_data += ['\0'] * (62 - message_length)

        return ShortSingleWriteExtraOutPrefix1(*self.short_single_write_extra_out_prefix_1_low_level(message_length, message_data))

    def short_single_write_extra_out_prefix_2(self, message):
        """

        """
        message = create_char_list(message)

        message_length = len(message)
        message_data = list(message) # make a copy so we can potentially extend it

        if message_length > 62:
            raise Error(Error.INVALID_PARAMETER, 'Message can be at most 62 items long')

        if message_length < 62:
            message_data += ['\0'] * (62 - message_length)

        return ShortSingleWriteExtraOutPrefix2(*self.short_single_write_extra_out_prefix_2_low_level(message_length, message_data))

    def short_single_write_extra_out_suffix_1(self, message):
        """

        """
        message = create_char_list(message)

        message_length = len(message)
        message_data = list(message) # make a copy so we can potentially extend it

        if message_length > 63:
            raise Error(Error.INVALID_PARAMETER, 'Message can be at most 63 items long')

        if message_length < 63:
            message_data += ['\0'] * (63 - message_length)

        return ShortSingleWriteExtraOutSuffix1(*self.short_single_write_extra_out_suffix_1_low_level(message_length, message_data))

    def short_single_write_extra_out_suffix_2(self, message):
        """

        """
        message = create_char_list(message)

        message_length = len(message)
        message_data = list(message) # make a copy so we can potentially extend it

        if message_length > 63:
            raise Error(Error.INVALID_PARAMETER, 'Message can be at most 63 items long')

        if message_length < 63:
            message_data += ['\0'] * (63 - message_length)

        return ShortSingleWriteExtraOutSuffix2(*self.short_single_write_extra_out_suffix_2_low_level(message_length, message_data))

    def short_single_write_extra_full(self, extra_1, extra_2, message, extra_3):
        """

        """
        extra_1 = int(extra_1)
        extra_2 = int(extra_2)
        message = create_char_list(message)
        extra_3 = int(extra_3)

        message_length = len(message)
        message_data = list(message) # make a copy so we can potentially extend it

        if message_length > 60:
            raise Error(Error.INVALID_PARAMETER, 'Message can be at most 60 items long')

        if message_length < 60:
            message_data += ['\0'] * (60 - message_length)

        return ShortSingleWriteExtraFull(*self.short_single_write_extra_full_low_level(extra_1, message_length, extra_2, message_data, extra_3))

    def normal_read(self):
        """

        """
        with self.stream_lock:
            ret = self.normal_read_low_level()
            message_length = ret.message_length
            message_out_of_sync = ret.message_chunk_offset != 0
            message_data = ret.message_chunk_data

            while not message_out_of_sync and len(message_data) < message_length:
                ret = self.normal_read_low_level()
                message_length = ret.message_length
                message_out_of_sync = ret.message_chunk_offset != len(message_data)
                message_data += ret.message_chunk_data

            if message_out_of_sync: # discard remaining stream to bring it back in-sync
                while ret.message_chunk_offset + 60 < message_length:
                    ret = self.normal_read_low_level()
                    message_length = ret.message_length

                raise Error(Error.STREAM_OUT_OF_SYNC, 'Message stream is out-of-sync')

        return message_data[:message_length]

    def normal_read_extra_in_1(self, extra):
        """

        """
        extra = int(extra)

        with self.stream_lock:
            ret = self.normal_read_extra_in_1_low_level(extra)
            message_length = ret.message_length
            message_out_of_sync = ret.message_chunk_offset != 0
            message_data = ret.message_chunk_data

            while not message_out_of_sync and len(message_data) < message_length:
                ret = self.normal_read_extra_in_1_low_level(extra)
                message_length = ret.message_length
                message_out_of_sync = ret.message_chunk_offset != len(message_data)
                message_data += ret.message_chunk_data

            if message_out_of_sync: # discard remaining stream to bring it back in-sync
                while ret.message_chunk_offset + 60 < message_length:
                    ret = self.normal_read_extra_in_1_low_level(extra)
                    message_length = ret.message_length

                raise Error(Error.STREAM_OUT_OF_SYNC, 'Message stream is out-of-sync')

        return message_data[:message_length]

    def normal_read_extra_in_2(self, extra_1, extra_2):
        """

        """
        extra_1 = int(extra_1)
        extra_2 = int(extra_2)

        with self.stream_lock:
            ret = self.normal_read_extra_in_2_low_level(extra_1, extra_2)
            message_length = ret.message_length
            message_out_of_sync = ret.message_chunk_offset != 0
            message_data = ret.message_chunk_data

            while not message_out_of_sync and len(message_data) < message_length:
                ret = self.normal_read_extra_in_2_low_level(extra_1, extra_2)
                message_length = ret.message_length
                message_out_of_sync = ret.message_chunk_offset != len(message_data)
                message_data += ret.message_chunk_data

            if message_out_of_sync: # discard remaining stream to bring it back in-sync
                while ret.message_chunk_offset + 60 < message_length:
                    ret = self.normal_read_extra_in_2_low_level(extra_1, extra_2)
                    message_length = ret.message_length

                raise Error(Error.STREAM_OUT_OF_SYNC, 'Message stream is out-of-sync')

        return message_data[:message_length]

    def normal_read_extra_out_prefix_1(self):
        """

        """
        with self.stream_lock:
            ret = self.normal_read_extra_out_prefix_1_low_level()
            message_length = ret.message_length
            message_out_of_sync = ret.message_chunk_offset != 0
            message_data = ret.message_chunk_data

            while not message_out_of_sync and len(message_data) < message_length:
                ret = self.normal_read_extra_out_prefix_1_low_level()
                message_length = ret.message_length
                message_out_of_sync = ret.message_chunk_offset != len(message_data)
                message_data += ret.message_chunk_data

            if message_out_of_sync: # discard remaining stream to bring it back in-sync
                while ret.message_chunk_offset + 59 < message_length:
                    ret = self.normal_read_extra_out_prefix_1_low_level()
                    message_length = ret.message_length

                raise Error(Error.STREAM_OUT_OF_SYNC, 'Message stream is out-of-sync')

        return NormalReadExtraOutPrefix1(ret.extra, message_data[:message_length])

    def normal_read_extra_out_prefix_2(self):
        """

        """
        with self.stream_lock:
            ret = self.normal_read_extra_out_prefix_2_low_level()
            message_length = ret.message_length
            message_out_of_sync = ret.message_chunk_offset != 0
            message_data = ret.message_chunk_data

            while not message_out_of_sync and len(message_data) < message_length:
                ret = self.normal_read_extra_out_prefix_2_low_level()
                message_length = ret.message_length
                message_out_of_sync = ret.message_chunk_offset != len(message_data)
                message_data += ret.message_chunk_data

            if message_out_of_sync: # discard remaining stream to bring it back in-sync
                while ret.message_chunk_offset + 58 < message_length:
                    ret = self.normal_read_extra_out_prefix_2_low_level()
                    message_length = ret.message_length

                raise Error(Error.STREAM_OUT_OF_SYNC, 'Message stream is out-of-sync')

        return NormalReadExtraOutPrefix2(ret.extra_1, ret.extra_2, message_data[:message_length])

    def normal_read_extra_out_suffix_1(self):
        """

        """
        with self.stream_lock:
            ret = self.normal_read_extra_out_suffix_1_low_level()
            message_length = ret.message_length
            message_out_of_sync = ret.message_chunk_offset != 0
            message_data = ret.message_chunk_data

            while not message_out_of_sync and len(message_data) < message_length:
                ret = self.normal_read_extra_out_suffix_1_low_level()
                message_length = ret.message_length
                message_out_of_sync = ret.message_chunk_offset != len(message_data)
                message_data += ret.message_chunk_data

            if message_out_of_sync: # discard remaining stream to bring it back in-sync
                while ret.message_chunk_offset + 59 < message_length:
                    ret = self.normal_read_extra_out_suffix_1_low_level()
                    message_length = ret.message_length

                raise Error(Error.STREAM_OUT_OF_SYNC, 'Message stream is out-of-sync')

        return NormalReadExtraOutSuffix1(message_data[:message_length], ret.extra)

    def normal_read_extra_out_suffix_2(self):
        """

        """
        with self.stream_lock:
            ret = self.normal_read_extra_out_suffix_2_low_level()
            message_length = ret.message_length
            message_out_of_sync = ret.message_chunk_offset != 0
            message_data = ret.message_chunk_data

            while not message_out_of_sync and len(message_data) < message_length:
                ret = self.normal_read_extra_out_suffix_2_low_level()
                message_length = ret.message_length
                message_out_of_sync = ret.message_chunk_offset != len(message_data)
                message_data += ret.message_chunk_data

            if message_out_of_sync: # discard remaining stream to bring it back in-sync
                while ret.message_chunk_offset + 58 < message_length:
                    ret = self.normal_read_extra_out_suffix_2_low_level()
                    message_length = ret.message_length

                raise Error(Error.STREAM_OUT_OF_SYNC, 'Message stream is out-of-sync')

        return NormalReadExtraOutSuffix2(message_data[:message_length], ret.extra_1, ret.extra_2)

    def normal_read_extra_out_full(self):
        """

        """
        with self.stream_lock:
            ret = self.normal_read_extra_out_full_low_level()
            message_length = ret.message_length
            message_out_of_sync = ret.message_chunk_offset != 0
            message_data = ret.message_chunk_data

            while not message_out_of_sync and len(message_data) < message_length:
                ret = self.normal_read_extra_out_full_low_level()
                message_length = ret.message_length
                message_out_of_sync = ret.message_chunk_offset != len(message_data)
                message_data += ret.message_chunk_data

            if message_out_of_sync: # discard remaining stream to bring it back in-sync
                while ret.message_chunk_offset + 56 < message_length:
                    ret = self.normal_read_extra_out_full_low_level()
                    message_length = ret.message_length

                raise Error(Error.STREAM_OUT_OF_SYNC, 'Message stream is out-of-sync')

        return NormalReadExtraOutFull(ret.extra_1, ret.extra_2, ret.extra_3, message_data[:message_length], ret.extra_4)

    def fixed_read(self):
        """

        """
        message_length = 1000

        with self.stream_lock:
            ret = self.fixed_read_low_level()

            if ret.message_chunk_offset == (1 << 16) - 1: # maximum chunk offset -> stream has no data
                message_length = 0
                message_out_of_sync = False
                message_data = ()
            else:
                message_out_of_sync = ret.message_chunk_offset != 0
                message_data = ret.message_chunk_data

            while not message_out_of_sync and len(message_data) < message_length:
                ret = self.fixed_read_low_level()
                message_out_of_sync = ret.message_chunk_offset != len(message_data)
                message_data += ret.message_chunk_data

            if message_out_of_sync: # discard remaining stream to bring it back in-sync
                while ret.message_chunk_offset + 62 < message_length:
                    ret = self.fixed_read_low_level()

                raise Error(Error.STREAM_OUT_OF_SYNC, 'Message stream is out-of-sync')

        return message_data[:message_length]

    def fixed_read_extra_in_1(self, extra):
        """

        """
        extra = int(extra)

        message_length = 1000

        with self.stream_lock:
            ret = self.fixed_read_extra_in_1_low_level(extra)

            if ret.message_chunk_offset == (1 << 16) - 1: # maximum chunk offset -> stream has no data
                message_length = 0
                message_out_of_sync = False
                message_data = ()
            else:
                message_out_of_sync = ret.message_chunk_offset != 0
                message_data = ret.message_chunk_data

            while not message_out_of_sync and len(message_data) < message_length:
                ret = self.fixed_read_extra_in_1_low_level(extra)
                message_out_of_sync = ret.message_chunk_offset != len(message_data)
                message_data += ret.message_chunk_data

            if message_out_of_sync: # discard remaining stream to bring it back in-sync
                while ret.message_chunk_offset + 62 < message_length:
                    ret = self.fixed_read_extra_in_1_low_level(extra)

                raise Error(Error.STREAM_OUT_OF_SYNC, 'Message stream is out-of-sync')

        return message_data[:message_length]

    def fixed_read_extra_in_2(self, extra_1, extra_2):
        """

        """
        extra_1 = int(extra_1)
        extra_2 = int(extra_2)

        message_length = 1000

        with self.stream_lock:
            ret = self.fixed_read_extra_in_2_low_level(extra_1, extra_2)

            if ret.message_chunk_offset == (1 << 16) - 1: # maximum chunk offset -> stream has no data
                message_length = 0
                message_out_of_sync = False
                message_data = ()
            else:
                message_out_of_sync = ret.message_chunk_offset != 0
                message_data = ret.message_chunk_data

            while not message_out_of_sync and len(message_data) < message_length:
                ret = self.fixed_read_extra_in_2_low_level(extra_1, extra_2)
                message_out_of_sync = ret.message_chunk_offset != len(message_data)
                message_data += ret.message_chunk_data

            if message_out_of_sync: # discard remaining stream to bring it back in-sync
                while ret.message_chunk_offset + 62 < message_length:
                    ret = self.fixed_read_extra_in_2_low_level(extra_1, extra_2)

                raise Error(Error.STREAM_OUT_OF_SYNC, 'Message stream is out-of-sync')

        return message_data[:message_length]

    def fixed_read_extra_out_prefix_1(self):
        """

        """
        message_length = 1000

        with self.stream_lock:
            ret = self.fixed_read_extra_out_prefix_1_low_level()

            if ret.message_chunk_offset == (1 << 16) - 1: # maximum chunk offset -> stream has no data
                message_length = 0
                message_out_of_sync = False
                message_data = ()
            else:
                message_out_of_sync = ret.message_chunk_offset != 0
                message_data = ret.message_chunk_data

            while not message_out_of_sync and len(message_data) < message_length:
                ret = self.fixed_read_extra_out_prefix_1_low_level()
                message_out_of_sync = ret.message_chunk_offset != len(message_data)
                message_data += ret.message_chunk_data

            if message_out_of_sync: # discard remaining stream to bring it back in-sync
                while ret.message_chunk_offset + 61 < message_length:
                    ret = self.fixed_read_extra_out_prefix_1_low_level()

                raise Error(Error.STREAM_OUT_OF_SYNC, 'Message stream is out-of-sync')

        return FixedReadExtraOutPrefix1(ret.extra, message_data[:message_length])

    def fixed_read_extra_out_prefix_2(self):
        """

        """
        message_length = 1000

        with self.stream_lock:
            ret = self.fixed_read_extra_out_prefix_2_low_level()

            if ret.message_chunk_offset == (1 << 16) - 1: # maximum chunk offset -> stream has no data
                message_length = 0
                message_out_of_sync = False
                message_data = ()
            else:
                message_out_of_sync = ret.message_chunk_offset != 0
                message_data = ret.message_chunk_data

            while not message_out_of_sync and len(message_data) < message_length:
                ret = self.fixed_read_extra_out_prefix_2_low_level()
                message_out_of_sync = ret.message_chunk_offset != len(message_data)
                message_data += ret.message_chunk_data

            if message_out_of_sync: # discard remaining stream to bring it back in-sync
                while ret.message_chunk_offset + 60 < message_length:
                    ret = self.fixed_read_extra_out_prefix_2_low_level()

                raise Error(Error.STREAM_OUT_OF_SYNC, 'Message stream is out-of-sync')

        return FixedReadExtraOutPrefix2(ret.extra_1, ret.extra_2, message_data[:message_length])

    def fixed_read_extra_out_suffix_1(self):
        """

        """
        message_length = 1000

        with self.stream_lock:
            ret = self.fixed_read_extra_out_suffix_1_low_level()

            if ret.message_chunk_offset == (1 << 16) - 1: # maximum chunk offset -> stream has no data
                message_length = 0
                message_out_of_sync = False
                message_data = ()
            else:
                message_out_of_sync = ret.message_chunk_offset != 0
                message_data = ret.message_chunk_data

            while not message_out_of_sync and len(message_data) < message_length:
                ret = self.fixed_read_extra_out_suffix_1_low_level()
                message_out_of_sync = ret.message_chunk_offset != len(message_data)
                message_data += ret.message_chunk_data

            if message_out_of_sync: # discard remaining stream to bring it back in-sync
                while ret.message_chunk_offset + 61 < message_length:
                    ret = self.fixed_read_extra_out_suffix_1_low_level()

                raise Error(Error.STREAM_OUT_OF_SYNC, 'Message stream is out-of-sync')

        return FixedReadExtraOutSuffix1(message_data[:message_length], ret.extra)

    def fixed_read_extra_out_suffix_2(self):
        """

        """
        message_length = 1000

        with self.stream_lock:
            ret = self.fixed_read_extra_out_suffix_2_low_level()

            if ret.message_chunk_offset == (1 << 16) - 1: # maximum chunk offset -> stream has no data
                message_length = 0
                message_out_of_sync = False
                message_data = ()
            else:
                message_out_of_sync = ret.message_chunk_offset != 0
                message_data = ret.message_chunk_data

            while not message_out_of_sync and len(message_data) < message_length:
                ret = self.fixed_read_extra_out_suffix_2_low_level()
                message_out_of_sync = ret.message_chunk_offset != len(message_data)
                message_data += ret.message_chunk_data

            if message_out_of_sync: # discard remaining stream to bring it back in-sync
                while ret.message_chunk_offset + 60 < message_length:
                    ret = self.fixed_read_extra_out_suffix_2_low_level()

                raise Error(Error.STREAM_OUT_OF_SYNC, 'Message stream is out-of-sync')

        return FixedReadExtraOutSuffix2(message_data[:message_length], ret.extra_1, ret.extra_2)

    def fixed_read_extra_out_full(self):
        """

        """
        message_length = 1000

        with self.stream_lock:
            ret = self.fixed_read_extra_out_full_low_level()

            if ret.message_chunk_offset == (1 << 16) - 1: # maximum chunk offset -> stream has no data
                message_length = 0
                message_out_of_sync = False
                message_data = ()
            else:
                message_out_of_sync = ret.message_chunk_offset != 0
                message_data = ret.message_chunk_data

            while not message_out_of_sync and len(message_data) < message_length:
                ret = self.fixed_read_extra_out_full_low_level()
                message_out_of_sync = ret.message_chunk_offset != len(message_data)
                message_data += ret.message_chunk_data

            if message_out_of_sync: # discard remaining stream to bring it back in-sync
                while ret.message_chunk_offset + 59 < message_length:
                    ret = self.fixed_read_extra_out_full_low_level()

                raise Error(Error.STREAM_OUT_OF_SYNC, 'Message stream is out-of-sync')

        return FixedReadExtraOutFull(ret.extra_1, ret.extra_2, message_data[:message_length], ret.extra_3)

    def single_read(self):
        """

        """
        ret = self.single_read_low_level()

        return ret.message_data[:ret.message_length]

    def single_read_extra_in_1(self, extra):
        """

        """
        extra = int(extra)

        ret = self.single_read_extra_in_1_low_level(extra)

        return ret.message_data[:ret.message_length]

    def single_read_extra_in_2(self, extra_1, extra_2):
        """

        """
        extra_1 = int(extra_1)
        extra_2 = int(extra_2)

        ret = self.single_read_extra_in_2_low_level(extra_1, extra_2)

        return ret.message_data[:ret.message_length]

    def single_read_extra_out_prefix_1(self):
        """

        """
        ret = self.single_read_extra_out_prefix_1_low_level()

        return SingleReadExtraOutPrefix1(ret.extra, ret.message_data[:ret.message_length])

    def single_read_extra_out_prefix_2(self):
        """

        """
        ret = self.single_read_extra_out_prefix_2_low_level()

        return SingleReadExtraOutPrefix2(ret.extra_1, ret.extra_2, ret.message_data[:ret.message_length])

    def single_read_extra_out_suffix_1(self):
        """

        """
        ret = self.single_read_extra_out_suffix_1_low_level()

        return SingleReadExtraOutSuffix1(ret.message_data[:ret.message_length], ret.extra)

    def single_read_extra_out_suffix_2(self):
        """

        """
        ret = self.single_read_extra_out_suffix_2_low_level()

        return SingleReadExtraOutSuffix2(ret.message_data[:ret.message_length], ret.extra_1, ret.extra_2)

    def single_read_extra_out_full(self):
        """

        """
        ret = self.single_read_extra_out_full_low_level()

        return SingleReadExtraOutFull(ret.extra_1, ret.extra_2, ret.message_data[:ret.message_length], ret.extra_3)

    def register_callback(self, callback_id, function):
        """
        Registers the given *function* with the given *callback_id*.
        """
        if function is None:
            self.registered_callbacks.pop(callback_id, None)
        else:
            self.registered_callbacks[callback_id] = function

StreamTest = BrickletStreamTest # for backward compatibility
