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
    NOT_ADDED = -6 # obsolete since v2.0
    ALREADY_CONNECTED = -7
    NOT_CONNECTED = -8

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
    FUNCTION_ADC_CALIBRATE = 251
    FUNCTION_GET_ADC_CALIBRATION = 250
    FUNCTION_READ_BRICKLET_UID = 249
    FUNCTION_WRITE_BRICKLET_UID = 248
    FUNCTION_READ_BRICKLET_PLUGIN = 247
    FUNCTION_WRITE_BRICKLET_PLUGIN = 246

    CALLBACK_ENUMERATE = 253
    CALLBACK_AUTHENTICATION_ERROR = 241
    CALLBACK_CONNECTED = -1
    CALLBACK_DISCONNECTED = -2

    BROADCAST_UID = 0

    RESPONSE_TIMEOUT = 2.5

    PLUGIN_CHUNK_SIZE = 32

    ENUMERATION_AVAILABLE = 0
    ENUMERATION_CONNECTED = 1
    ENUMERATION_DISCONNECTED = 2

    DISCONNECT_ERROR = 0
    DISCONNECT_REQUEST = 1
    DISCONNECT_SHUTDOWN = 2

    QUEUE_EXIT = 0
    QUEUE_META = 1
    QUEUE_PACKET = 2

    def __init__(self, host, port):
        """
        Creates an IP connection to the Brick Daemon with the given *host*
        and *port*. With the IP connection itself it is possible to enumerate
        the available devices. Other then that it is only used to add Bricks
        and Bricklets to the connection.
        """

        self.host = host
        self.port = port
        self.next_seqnum = 0
        self.auth_key = None
        self.devices = {}
        self.registered_callbacks = {}
        self.socket = None
        self.socket_lock = Lock()
        self.receive_flag = False
        self.receive_thread = None
        self.callback_queue = None
        self.callback_thread = None

    def connect(self):
        with self.socket_lock:
            if self.socket is not None:
                raise Error(Error.ALREADY_CONNECTED,
                            'Already connected to {0}:{1}'.format(self.host, self.port))

            if self.callback_thread is None:
                try:
                    self.callback_queue = Queue()
                    self.callback_thread = Thread(target=self.callback_loop, args=(self.callback_queue, ))
                    self.callback_thread.daemon = True
                    self.callback_thread.start()
                except:
                    self.callback_queue = None
                    self.callback_thread = None
                    raise

            try:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.connect((self.host, self.port))
            except:
                self.socket = None
                raise

            try:
                self.receive_flag = True
                self.receive_thread = Thread(target=self.receive_loop)
                self.receive_thread.daemon = True
                self.receive_thread.start()
            except:
                def cleanup():
                    # end receive thread
                    self.receive_flag = False

                    try:
                        self.socket.shutdown(socket.SHUT_RDWR)
                    except socket.error:
                        pass

                    if self.receive_thread is not None:
                        self.receive_thread.join() # FIXME: use a timeout?

                    self.receive_thread = None

                    # close socket
                    self.socket.close()
                    self.socket = None

                    # end callback thread
                    self.callback_queue.put((IPConnection.QUEUE_EXIT, None))

                    if current_thread() is not self.callback_thread:
                        self.callback_thread.join()

                    self.callback_queue = None
                    self.callback_thread = None

                cleanup()
                raise

        # do this outside the socket_lock to ensure that the callback will
        # not be executed while the socket_lock is held
        self.callback_queue.put((IPConnection.QUEUE_META, (IPConnection.CALLBACK_CONNECTED, None)))

    def disconnect(self):
        with self.socket_lock:
            if self.socket is None:
                raise Error(Error.NOT_CONNECTED,
                            'Not connected to {0}:{1}'.format(self.host, self.port))

            # end receive thread
            self.receive_flag = False

            try:
                self.socket.shutdown(socket.SHUT_RDWR)
            except socket.error:
                pass

            if self.receive_thread is not None:
                self.receive_thread.join() # FIXME: use a timeout?

            self.receive_thread = None

            # close socket
            self.socket.close()
            self.socket = None

            # end callback thread
            callback_queue = self.callback_queue
            callback_thread = self.callback_thread

            self.callback_queue = None
            self.callback_thread = None

        # do this outside of socket_lock to allow calling connect from the callback
        callback_queue.put((IPConnection.QUEUE_META,
                            (IPConnection.CALLBACK_DISCONNECTED,
                             IPConnection.DISCONNECT_REQUEST)))
        callback_queue.put((IPConnection.QUEUE_EXIT, None))

        if current_thread() is not callback_thread:
            callback_thread.join()

    def is_connected(self):
        return self.socket is not None

    def enumerate(self):
        with self.socket_lock:
            if self.socket is None:
                raise Error(Error.NOT_CONNECTED,
                            'Not connected to {0}:{1}'.format(self.host, self.port))

            request = self.create_packet_header(IPConnection.BROADCAST_UID, 8,
                                                IPConnection.FUNCTION_ENUMERATE,
                                                False)

            self.socket.send(request)

    def register_callback(self, id, callback):
        """
        Registers a callback with ID *id* to the function *callback*.
        """
        self.registered_callbacks[id] = callback

    def receive_loop(self):
        if sys.hexversion < 0x03000000:
            pending_data = ''
        else:
            pending_data = bytes()

        while self.receive_flag:
            try:
                data = self.socket.recv(8192)
            except socket.error:
                self.callback_queue.put((IPConnection.QUEUE_META,
                                         (IPConnection.CALLBACK_DISCONNECTED,
                                          IPConnection.DISCONNECT_ERROR)))
                return

            if len(data) == 0:
                if self.receive_flag:
                    self.callback_queue.put((IPConnection.QUEUE_META,
                                             (IPConnection.CALLBACK_DISCONNECTED,
                                              IPConnection.DISCONNECT_SHUTDOWN)))
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

    def callback_loop(self, callback_queue):
        while True:
            kind, data = callback_queue.get()

            if kind == IPConnection.QUEUE_EXIT:
                return
            elif kind == IPConnection.QUEUE_META:
                function_id, parameter = data

                if function_id == IPConnection.CALLBACK_CONNECTED:
                    if IPConnection.CALLBACK_CONNECTED in self.registered_callbacks and \
                       self.registered_callbacks[IPConnection.CALLBACK_CONNECTED] is not None:
                        self.registered_callbacks[IPConnection.CALLBACK_CONNECTED]()
                elif function_id == IPConnection.CALLBACK_DISCONNECTED:
                    if IPConnection.CALLBACK_DISCONNECTED in self.registered_callbacks and \
                       self.registered_callbacks[IPConnection.CALLBACK_DISCONNECTED] is not None:
                        self.registered_callbacks[IPConnection.CALLBACK_DISCONNECTED](parameter)
            elif kind == IPConnection.QUEUE_PACKET:
                packet = data
                uid = get_uid_from_data(packet)
                length = get_length_from_data(packet)
                function_id = get_function_id_from_data(packet)
                payload = packet[8:]

                if function_id == IPConnection.CALLBACK_ENUMERATE and \
                   IPConnection.CALLBACK_ENUMERATE in self.registered_callbacks:
                    uid, connected_uid, position, hardware_version, \
                        firmware_version, device_identifier, enumeration_type = \
                        self.deserialize_data(payload, '8s 8s c 3B 3B H B')

                    self.registered_callbacks[IPConnection.CALLBACK_ENUMERATE](uid, connected_uid, position, hardware_version,
                                                                               firmware_version, device_identifier, enumeration_type)
                    continue

                if uid not in self.devices:
                    continue

                device = self.devices[uid]
                if function_id in device.registered_callbacks and \
                   device.registered_callbacks[function_id] is not None:
                    form = device.callback_formats[function_id]
                    if len(form) == 0:
                        device.registered_callbacks[function_id]()
                    elif len(form) == 1:
                        device.registered_callbacks[function_id](self.deserialize_data(payload, form))
                    else:
                        device.registered_callbacks[function_id](*self.deserialize_data(payload, form))

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

    def send_request(self, device, function_id, data, form, form_ret):
        with self.socket_lock:
            if self.socket is None:
                raise Error(Error.NOT_CONNECTED,
                            'Not connected to {0}:{1}'.format(self.host, self.port))

            device.write_lock.acquire()

            length = 8 + struct.calcsize('<' + form)
            request = self.create_packet_header(device.uid, length, function_id,
                                                len(form_ret) != 0)

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
            pass

        if len(form_ret) == 0:
            device.write_lock.release()
            return

        try:
            response = device.response_queue.get(True, IPConnection.RESPONSE_TIMEOUT)
        except Empty:
            device.write_lock.release()
            msg = 'Did not receive response for function ' + str(function_id) +  ' in time'
            raise Error(Error.TIMEOUT, msg)

        device.write_lock.release()

        return self.deserialize_data(response[8:], form_ret)

    def get_next_seqnum(self):
        seqnum = self.next_seqnum
        self.next_seqnum = (self.next_seqnum + 1) % 15
        seqnum += 1

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
            self.callback_queue.put((IPConnection.QUEUE_PACKET, packet))
            return

        # Response seems to be OK, but can't be handled, most likely
        # a callback without registered function

    def handle_enumerate(self, packet):
        if IPConnection.CALLBACK_ENUMERATE in self.registered_callbacks:
            self.callback_queue.put((IPConnection.QUEUE_PACKET, packet))

    def create_packet_header(self, uid, length, function_id, response_expected):
        seqnum = self.get_next_seqnum()
        r_bit = 0
        a_bit = 0

        if response_expected:
            r_bit = 1

        if self.auth_key is not None:
            a_bit = 1

        seqnum_and_options = (seqnum << 4) | (r_bit << 3) | (a_bit << 2)

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
