# -*- coding: utf-8 -*-
# Copyright (C) 2012 Matthias Bolte <matthias@tinkerforge.com>
# Copyright (C) 2011 Olaf Lüke <olaf@tinkerforge.com>
#
# Redistribution and use in source and binary forms of this file,
# with or without modification, are permitted.

from threading import Thread, Lock

# current_thread for python 2.6, currentThread for python 2.5
try:
    from threading import current_thread
except ImportError:
    from threading import currentThread as current_thread

# Queue for python 2, queue for python 3
try:
    from Queue import Queue, Empty
except ImportError:
    from queue import Queue, Empty

import struct
import socket
import types
import sys
import time

# use normal tuples instead of namedtuples in python version below 2.6
if sys.hexversion < 0x02060000:
    def namedtuple(typename, field_names, verbose=False, rename=False):
        def ntuple(*args):
            return args

        return ntuple
else:
    from collections import namedtuple

def get_uid_from_data(data):
    return struct.unpack('<I', data[0:4])[0]

def get_length_from_data(data):
    return struct.unpack('<B', data[4:5])[0]

def get_function_id_from_data(data):
    return struct.unpack('<B', data[5:6])[0]

def get_seqnum_and_options_from_data(data):
    return struct.unpack('<B', data[6:7])[0]

BASE58 = '123456789abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ'
def base58encode(value):
    encoded = ''
    while value >= 58:
        div, mod = divmod(value, 58)
        encoded = BASE58[mod] + encoded
        value = div
    encoded = BASE58[value] + encoded
    return encoded

def base58decode(encoded):
    value = 0
    column_multiplier = 1
    for c in encoded[::-1]:
        column = BASE58.index(c)
        value += column * column_multiplier
        column_multiplier *= 58
    return value

class Error(Exception):
    TIMEOUT = -1
    NO_CONNECT = -4
    NOT_ADDED = -6 # obsolete since v2.0

    def __init__(self, value, description):
        self.value = value
        self.description = description

    def __str__(self):
        return str(self.value) + ': ' + str(self.description)

class Device:
    def __init__(self, uid, ipcon):
        self.uid = base58decode(uid)
        self.ipcon = ipcon
        self.api_version = (0, 0, 0)
        self.registered_callbacks = {}
        self.callback_formats = {}
        self.expected_response_function_id = -1
        self.response_queue = Queue()
        self.write_lock = Lock()

        ipcon.devices[self.uid] = self

    def get_api_version(self):
        """
        Returns API version [major, minor, revision] used for this device.
        """
        return self.api_version

class IPConnection:
    FUNCTION_GET_IDENTITY = 255
    FUNCTION_ENUMERATE = 254
    CALLBACK_ENUMERATE = 253
    FUNCTION_ADC_CALIBRATE = 251
    FUNCTION_GET_ADC_CALIBRATION = 250
    FUNCTION_READ_BRICKLET_UID = 249
    FUNCTION_WRITE_BRICKLET_UID = 248
    FUNCTION_READ_BRICKLET_PLUGIN = 247
    FUNCTION_WRITE_BRICKLET_PLUGIN = 246
    CALLBACK_AUTHENTICATION_ERROR = 241

    BROADCAST_UID = 0

    RESPONSE_TIMEOUT = 2.5

    PLUGIN_CHUNK_SIZE = 32

    ENUMERATION_AVAILABLE = 0
    ENUMERATION_CONNECTED = 1
    ENUMERATION_DISCONNECTED = 2

    def __init__(self, host, port):
        """
        Creates an IP connection to the Brick Daemon with the given *host*
        and *port*. With the IP connection itself it is possible to enumerate the
        available devices. Other then that it is only used to add Bricks and
        Bricklets to the connection.
        """

        self.next_seqnum = 0
        self.auth_key = None
        self.callback_queue = Queue()
        self.devices = {}
        self.enumerate_callback = None
        self.host = host
        self.port = port

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))

        self.thread_receive_flag = True
        self.thread_receive = Thread(target=self.receive_loop)
        self.thread_receive.daemon = True
        self.thread_receive.start()

        self.thread_callback_flag = True
        self.thread_callback = Thread(target=self.callback_loop)
        self.thread_callback.daemon = True
        self.thread_callback.start()

    def reconnect(self):
        while self.thread_receive_flag:
            try:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.connect((self.host, self.port))
                return True
            except:
                time.sleep(0.1)
        return False

    def receive_loop(self):
        if sys.hexversion < 0x03000000:
            pending_data = ''
        else:
            pending_data = bytes()

        while self.thread_receive_flag:
            try:
                data = self.socket.recv(8192)
            except socket.error:
                data = ''
                if self.reconnect():
                    continue
                else:
                    return

            if len(data) == 0:
                if self.thread_receive_flag:
                    sys.stderr.write('Socket disconnected by Server, destroying IPConnection\n')
                    self.destroy()
                return

            pending_data += data

            while True:
                if len(pending_data) < 8:
                    # Wait for complete header
                    break

                length = get_length_from_data(pending_data)

                if len(pending_data) < length:
                    # Wait for complete packet
                    break

                packet = pending_data[0:length]
                pending_data = pending_data[length:]

                self.handle_response(packet)

    def callback_loop(self):
        while self.thread_callback_flag:
            packet = self.callback_queue.get()

            if not self.thread_callback_flag:
                return

            if packet is None:
                continue

            uid = get_uid_from_data(packet)
            length = get_length_from_data(packet)
            function_id = get_function_id_from_data(packet)
            payload = packet[8:]

            if function_id == IPConnection.CALLBACK_ENUMERATE:
                uid, connected_uid, position, hardware_version, \
                    firmware_version, device_identifier, enumeration_type = \
                    self.deserialize_data(payload, '8s 8s c 3B 3B H B')

                self.enumerate_callback(uid, connected_uid, position, hardware_version,
                                        firmware_version, device_identifier, enumeration_type)
                continue

            if uid not in self.devices:
                continue

            device = self.devices[uid]
            if function_id in device.registered_callbacks:
                form = device.callback_formats[function_id]
                if len(form) == 0:
                    device.registered_callbacks[function_id]()
                elif len(form) == 1:
                    device.registered_callbacks[function_id](self.deserialize_data(payload, form))
                else:
                    device.registered_callbacks[function_id](*self.deserialize_data(payload, form))

    def destroy(self):
        """
        Destroys the IP connection. The socket to the Brick Daemon will be closed
        and the threads of the IP connection terminated.
        """

        # End callback thread
        self.thread_callback_flag = False
        self.callback_queue.put(None) # unblock callback_loop

        if current_thread() is not self.thread_callback:
            self.thread_callback.join()

        # End receive thread
        self.thread_receive_flag = False
        try:
            self.socket.shutdown(socket.SHUT_RDWR)
        except socket.error:
            pass
        self.socket.close()

        if current_thread() is not self.thread_receive:
            self.thread_receive.join()

    def deserialize_data(self, data, form):
        ret = []
        for f in form.split(' '):
            f = '<' + f
            length = struct.calcsize(f)

            x = struct.unpack(f, data[:length])
            if len(x) > 1:
                ret.append(x)
            elif 's' in f:
                ret.append(self.trim_deserialized_string(x[0]))
            else:
                ret.append(x[0])

            data = data[length:]

        if len(ret) == 1:
            return ret[0]

        return ret

    def trim_deserialized_string(self, s):
        if sys.hexversion >= 0x03000000:
            s = s.decode('ascii')

        i = s.find(chr(0))
        if i >= 0:
            s = s[:i]

        return s

    def join_thread(self):
        """
        Joins the threads of the IP connection. The call will block until the
        IP connection is :py:func:`destroyed <IPConnection.destroy>`.

        This makes sense if you relies solely on callbacks for events or if
        the IP connection was created in a threads.
        """

        self.thread_callback.join()
        self.thread_receive.join()

    def send_request(self, device, function_id, data, form, form_ret):
        device.write_lock.acquire()

        length = 8 + struct.calcsize('<' + form)
        request = self.create_packet_header(device.uid, length, function_id)

        for f, d in zip(form.split(' '), data):
            if len(f) > 1 and not 's' in f:
                request += struct.pack('<' + f, *d)
            elif 's' in f:
                if sys.hexversion < 0x03000000:
                    if type(d) == types.UnicodeType:
                        request += struct.pack('<' + f, d.encode('ascii'))
                    else:
                        request += struct.pack('<' + f, d)
                else:
                    if isinstance(d, str):
                        request += struct.pack('<' + f, bytes(d, 'ascii'))
                    else:
                        request += struct.pack('<' + f, d)
            else:
                request += struct.pack('<' + f, d)

        if len(form_ret) != 0:
            device.expected_response_function_id = function_id

        try:
            self.socket.send(request)
        except socket.error:
            self.destroy()

        if len(form_ret) == 0:
            device.write_lock.release()
            return

        try:
            response = device.response_queue.get(True, IPConnection.RESPONSE_TIMEOUT)
        except Empty:
            device.write_lock.release()
            msg = 'Did not receive response for function ' + str(function_id) +  ' in time'
            raise Error(Error.TIMEOUT, msg)

        try:
            device.write_lock.release()
        except ValueError:
            self.destroy()

        return self.deserialize_data(response[8:], form_ret)

    def get_next_seqnum(self):
        seqnum = self.next_seqnum
        self.next_seqnum = (self.next_seqnum + 1) % 16

        return seqnum

    def handle_response(self, packet):
        function_id = get_function_id_from_data(packet)
        if function_id == IPConnection.CALLBACK_ENUMERATE:
            self.handle_enumerate(packet)
            return

        uid = get_uid_from_data(packet)
        if not uid in self.devices:
            # Response from an unknown device, ignoring it
            return

        device = self.devices[uid]
        if device.expected_response_function_id == function_id:
            device.response_queue.put(packet)
            return

        if function_id in device.registered_callbacks:
            self.callback_queue.put(packet)
            return

        # Response seems to be OK, but can't be handled, most likely
        # a callback without registered function

    def handle_enumerate(self, packet):
        if self.enumerate_callback is not None:
            self.callback_queue.put(packet)

    def enumerate(self, callback):
        """
        This method registers a callback that receives four parameters:

        * *uid* - str: The UID of the device.
        * *connected_uid* - str: UID where the device is connected to. For a Bricklet this will be a UID of
        the Brick where it is connected to. For a Brick it will be the UID of the bottom Master Brick in the
        stack. For the bottom Master Brick in a Stack this will be '1'. With this information it is possible
        to reconstruct the complete network topology.
        * *position* - str: Position in stack. For Bricks: '0' - '8' (position in stack). For Bricklets: 'A' - 'D' (position on Brick).
        * *hardware_version* - (int, int, int): Major, minor and release number for hardware version.
        * *firmware_version* - (int, int, int): Major, minor and release number for firmware version.
        * *device_identifier* - int: A number that represents the Brick, instead of the name of the Brick (easier to parse).
        * *enumeration_type - int: Type of enumeration:
          * AVAILABLE (0): If device is available (enumeration triggered by user).
          * CONNECTED (1): If device is newly added.
          * DISCONNECTED (2): If device is removed (only possible for USB connection).

        There are three different possibilities for the callback to be called.
        Firstly, the callback is called with all currently available devices in the
        IP connection (with *enumeration_type* AVAILABLE). Secondly, the callback is called if
        a new Brick is plugged in via USB (with *enumeration_type* ADDED) and lastly it is
        called if a Brick is unplugged (with *enumeration_type* REMOVED).

        It should be possible to implement "plug 'n play" functionality with this
        (as is done in Brick Viewer).
        """

        self.enumerate_callback = callback
        request = self.create_packet_header(IPConnection.BROADCAST_UID, 8,
                                            IPConnection.FUNCTION_ENUMERATE)

        self.socket.send(request)

    def create_packet_header(self, uid, length, function_id):
        seqnum = self.get_next_seqnum()
        auth_bit = 0

        if self.auth_key is not None:
            auth_bit = 1

        seqnum_and_options = seqnum << 4 | auth_bit << 2

        return struct.pack('<IBBBB', uid, length, function_id, seqnum_and_options, 0)

    def write_bricklet_plugin(self, device, port, position, plugin_chunk):
        self.send_request(device,
                          IPConnection.FUNCTION_WRITE_BRICKLET_PLUGIN,
                          (port, position, plugin_chunk),
                          'c B 32B',
                          '')

    def read_bricklet_plugin(self, device, port, position):
        return self.send_request(device,
                                 IPConnection.FUNCTION_READ_BRICKLET_PLUGIN,
                                 (port, position),
                                 'c B',
                                 '32B')

    def get_adc_calibration(self, device):
        return self.send_request(device,
                                 IPConnection.FUNCTION_GET_ADC_CALIBRATION,
                                 (),
                                 '',
                                 'h h')

    def adc_calibrate(self, device, port):
        self.send_request(device,
                          IPConnection.FUNCTION_ADC_CALIBRATE,
                          (port,),
                          'c',
                          '')

    def write_bricklet_uid(self, device, port, uid):
        uid_int = base58decode(uid)

        self.send_request(device,
                          IPConnection.FUNCTION_WRITE_BRICKLET_UID,
                          (port, uid_int),
                          'c I',
                          '')

    def read_bricklet_uid(self, device, port):
        uid_int = self.send_request(device,
                                    IPConnection.FUNCTION_READ_BRICKLET_UID,
                                    (port,),
                                    'c',
                                    'I')

        return base58encode(uid_int)
