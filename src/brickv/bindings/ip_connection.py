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

def get_stack_id_from_data(data):
    return ord(data[0:0 + 1])

def get_function_id_from_data(data):
    return ord(data[1:1 + 1])

def get_length_from_data(data):
    return struct.unpack('<H', data[2:4])[0]

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
    NOT_ADDED = -6

    def __init__(self, value, description):
        self.value = value
        self.description = description

    def __str__(self):
        return str(self.value) + ': ' + str(self.description)

def decorator_ipcon_check(f):
    def func(self, *args, **kwargs):
        if self.ipcon is None:
            msg = 'Device ' + base58encode(self.uid) + ' not yet added to IPConnection'
            raise Error(Error.NOT_ADDED, msg)
        return f(self, *args, **kwargs)

    return func

class DeviceConChecker(type):
    def __new__(mcs, name, bases, dct):
        if bases[0].__name__ != 'Device':
            return type.__new__(mcs, name, bases, dct)

        dct_new = {}
        for elem in dct:
            if type(dct[elem]) is types.FunctionType and \
               not elem in ('__init__', 'register_callback'):
                dct_new[elem] = decorator_ipcon_check(dct[elem])
            else:
                dct_new[elem] = dct[elem]
        return type.__new__(mcs, name, bases, dct_new)

DeviceConCheckerMeta = DeviceConChecker('DeviceConCheckerMeta', (object, ), {})

GetVersion = namedtuple('Version', ['name', 'firmware_version', 'binding_version'])

class Device(DeviceConCheckerMeta):
    def __init__(self, uid):
        self.uid = base58decode(uid)
        self.ipcon = None
        self.stack_id = 0
        self.expected_name = ''
        self.name = ''
        self.firmware_version = [0, 0, 0]
        self.binding_version = [0, 0, 0]
        self.registered_callbacks = {}
        self.callback_formats = {}
        self.expected_response_function_id = -1
        self.response_queue = Queue()
        self.write_lock = Lock()

    def get_version(self):
        """
        Returns the name (including the hardware version), the firmware version
        and the binding version of the device. The firmware and binding versions are
        given in arrays of size 3 with the syntax [major, minor, revision].
        """
        return GetVersion(self.name, self.firmware_version, self.binding_version)

class IPConnection:
    FUNCTION_GET_STACK_ID = 255
    FUNCTION_ENUMERATE = 254
    FUNCTION_ENUMERATE_CALLBACK = 253
    FUNCTION_STACK_ENUMERATE = 252
    FUNCTION_ADC_CALIBRATE = 251
    FUNCTION_GET_ADC_CALIBRATION = 250

    FUNCTION_READ_BRICKLET_UID = 249
    FUNCTION_WRITE_BRICKLET_UID = 248
    FUNCTION_READ_BRICKLET_PLUGIN = 247
    FUNCTION_WRITE_BRICKLET_PLUGIN = 246
    FUNCTION_READ_BRICKLET_NAME = 245
    FUNCTION_WRITE_BRICKLET_NAME = 244

    BROADCAST_ADDRESS = 0
    ENUMERATE_LENGTH = 4
    GET_STACK_ID_LENGTH = 12

    RESPONSE_TIMEOUT = 2.5

    PLUGIN_CHUNK_SIZE = 32


    def __init__(self, host, port):
        """
        Creates an IP connection to the Brick Daemon with the given *host*
        and *port*. With the IP connection itself it is possible to enumerate the
        available devices. Other then that it is only used to add Bricks and
        Bricklets to the connection.
        """

        self.callback_queue = Queue()
        self.pending_add_device = None
        self.pending_add_device_handled = False
        self.add_device_lock = Lock()
        self.devices = {}
        self.enumerate_callback = None
        self.host = host
        self.port = port

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))

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
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.connect((self.host, self.port))
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
                data = self.sock.recv(8192)
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
                if len(pending_data) < 4:
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
            data = self.callback_queue.get()

            if not self.thread_callback_flag:
                return

            if data is None:
                continue

            stack_id = get_stack_id_from_data(data)
            function_id = get_function_id_from_data(data)
            length = get_length_from_data(data)
            
            if function_id == IPConnection.FUNCTION_ENUMERATE_CALLBACK:
                data = data[:length]
                data = data[4:]
                uid, name, stack_id, new = self.deserialize_data(data, 'Q 40s B ?')

                self.enumerate_callback(base58encode(uid), name, stack_id, new)
                continue

            device = self.devices[stack_id]
            if function_id in device.registered_callbacks:
                form = device.callback_formats[function_id]
                if len(form) == 0:
                    device.registered_callbacks[function_id]()
                elif len(form) == 1:
                    device.registered_callbacks[function_id](self.deserialize_data(data[4:], form))
                else:
                    device.registered_callbacks[function_id](*self.deserialize_data(data[4:], form))

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
            self.sock.shutdown(socket.SHUT_RDWR)
        except socket.error:
            pass
        self.sock.close()

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
       
        length = struct.pack('<H', struct.calcsize('<' + form) + 4)
        if sys.hexversion < 0x03000000:
            request = chr(device.stack_id) + chr(function_id) + length
        else:
            request = bytes([device.stack_id, function_id]) + length

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
            self.sock.send(request)
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

        return self.deserialize_data(response, form_ret)

    def handle_response(self, packet):
        function_id = get_function_id_from_data(packet)
        if function_id == IPConnection.FUNCTION_GET_STACK_ID:
            self.handle_add_device(packet)
            return
        if function_id == IPConnection.FUNCTION_ENUMERATE_CALLBACK:
            self.handle_enumerate(packet)
            return

        stack_id = get_stack_id_from_data(packet)
        if not stack_id in self.devices:
            # Response from an unknown device, ignoring it
            return

        device = self.devices[stack_id]
        if device.expected_response_function_id == function_id:
            device.response_queue.put(packet[4:])
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
        * *name* - str: The name of the device (includes "Brick" or "Bricklet" and a version number).
        * *stack_id* - int: The stack ID of the device (you can find out the position in a stack with this).
        * *is_new* - bool: True if the device is added, false if it is removed.

        There are three different possibilities for the callback to be called.
        Firstly, the callback is called with all currently available devices in the
        IP connection (with *is_new* true). Secondly, the callback is called if
        a new Brick is plugged in via USB (with *is_new* true) and lastly it is
        called if a Brick is unplugged (with *is_new* false).

        It should be possible to implement "plug 'n play" functionality with this
        (as is done in Brick Viewer).
        """

        self.enumerate_callback = callback
        if sys.hexversion < 0x03000000:
            request = chr(IPConnection.BROADCAST_ADDRESS) + \
                      chr(IPConnection.FUNCTION_ENUMERATE) + \
                      struct.pack('<H', IPConnection.ENUMERATE_LENGTH)
        else:
            request = bytes([IPConnection.BROADCAST_ADDRESS,
                             IPConnection.FUNCTION_ENUMERATE]) + \
                      struct.pack('<H', IPConnection.ENUMERATE_LENGTH)

        self.sock.send(request)

    def handle_add_device(self, packet):
        if self.pending_add_device is None or self.pending_add_device_handled:
            return

        _, _, _, uid, firmware_version, name, stack_id = self.deserialize_data(packet, 'B B H Q 3B 40s B')

        if self.pending_add_device.uid == uid:
            # Check device name (replace '-' with ' ' for backward compatibility)
            i = name.rfind(' ')
            if i < 0 or name[0:i].replace('-', ' ') != self.pending_add_device.expected_name.replace('-', ' '):
                return

            self.pending_add_device.firmware_version = firmware_version
            self.pending_add_device.name = name
            self.pending_add_device.stack_id = stack_id
            self.devices[stack_id] = self.pending_add_device
            self.pending_add_device_handled = True
            self.pending_add_device.response_queue.put(None)

    def add_device(self, device):
        """
        Adds a device (Brick or Bricklet) to the IP connection. Every device
        has to be added to an IP connection before it can be used. Examples for
        this can be found in the API documentation for every Brick and Bricklet.
        """

        if sys.hexversion < 0x03000000:
            request = chr(IPConnection.BROADCAST_ADDRESS) + \
                      chr(IPConnection.FUNCTION_GET_STACK_ID) + \
                      struct.pack('<H', IPConnection.GET_STACK_ID_LENGTH) + \
                      struct.pack('<Q', device.uid)
        else:
            request = bytes([IPConnection.BROADCAST_ADDRESS,
                             IPConnection.FUNCTION_GET_STACK_ID]) + \
                      struct.pack('<H', IPConnection.GET_STACK_ID_LENGTH) + \
                      struct.pack('<Q', device.uid)

        self.add_device_lock.acquire()
        try:
            self.pending_add_device_handled = False
            self.pending_add_device = device
            self.sock.send(request)

            try:
                device.response_queue.get(True, IPConnection.RESPONSE_TIMEOUT)
            except Empty:
                msg = 'Could not add device ' + \
                      str(base58encode(device.uid)) + \
                      ', timeout'
                raise Error(Error.TIMEOUT, msg)

            device.ipcon = self
        finally:
            self.pending_add_device = None
            self.add_device_lock.release()

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
                          'c Q',
                          '')

    def read_bricklet_uid(self, device, port):
        uid_int = self.send_request(device,
                                    IPConnection.FUNCTION_READ_BRICKLET_UID,
                                    (port,),
                                    'c',
                                    'Q')

        return base58encode(uid_int)
