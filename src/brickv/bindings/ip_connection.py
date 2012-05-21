# -*- coding: utf-8 -*-
# Copyright (C) 2012 Matthias Bolte <matthias@tinkerforge.com>
# Copyright (C) 2011 Olaf Lüke <olaf@tinkerforge.com>
#
# Redistribution and use in source and binary forms of this file, 
# with or without modification, are permitted. 

from threading import Thread, BoundedSemaphore
# Queue for python 2, queue for python 3
try:
    from Queue import Queue
    from Queue import Empty
except ImportError:
    from queue import Queue
    from queue import Empty
import struct
import socket
import types
import sys

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
    column_multiplier = 1;
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
        return str(self.value) + ": " + str(self.description)

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
        self.callbacks = {}
        self.callbacks_format = {}
        self.answer_function_id = -1
        self.answer = None
        self.answer_queue = Queue()
        self.sem_write = BoundedSemaphore(value=1)

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

    TIMEOUT_ADD_DEVICE = 2.5
    TIMEOUT_ANSWER = 2.5

    PLUGIN_CHUNK_SIZE = 32

    callback_queue = Queue()

    def __init__(self, host, port):
        self.add_dev = None
        self.devices = {}
        self.enumerate_callback = None
        self.recv_loop_flag = True

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))

        self.thread_recv = Thread(target=self.recv_loop)
        self.thread_recv.daemon = True
        self.thread_recv.start()

        self.thread_callback = Thread(target=self.callback_loop)
        self.thread_callback.daemon = True
        self.thread_callback.start()

    def recv_loop(self):
        while self.recv_loop_flag:
            data = self.sock.recv(8192)
            if len(data) == 0:
                if self.recv_loop_flag:
                    sys.stderr.write("Socket disconnected by Server, destroying ipcon\n")
                    self.destroy()
                return

            while len(data) != 0:
                handled = self.handle_message(data)
                data = data[handled:]

    def callback_loop(self):
        while self.recv_loop_flag:
            try:
                data = self.callback_queue.get(True, 1.0)
            except:
                if self.recv_loop_flag:
                    continue
                else:
                    return

            stack_id = get_stack_id_from_data(data)
            function_id = get_function_id_from_data(data)
            length = get_length_from_data(data)
            
            if function_id == IPConnection.FUNCTION_ENUMERATE_CALLBACK:
                data = data[:length]
                data = data[4:]

                uid, name, stack_id, new = self.data_to_return(data, 'Q 40s B ?')

                # Remove \0 from end of string
                name = name.replace(chr(0), '')

                self.enumerate_callback(base58encode(uid), name.decode(), stack_id, new)
                continue

            device = self.devices[stack_id]
            if function_id in device.callbacks:
                form = device.callbacks_format[function_id]
                if len(form) == 0:
                    device.callbacks[function_id]()
                elif len(form) == 1:
                    device.callbacks[function_id](self.data_to_return(data[4:], form))
                else:
                    device.callbacks[function_id](*self.data_to_return(data[4:], form))

    def destroy(self):
        self.recv_loop_flag = False
        try:
            self.sock.shutdown(socket.SHUT_RDWR)
        except socket.error:
            pass
        self.sock.close()

        self.join_thread()

    def data_to_return(self, data, form):
        ret = []
        for f in form.split(' '):
            f = '<' + f
            length = struct.calcsize(f)

            x = struct.unpack(f, data[:length])
            if len(x) > 1:
                ret.append(x)
            else:
                ret.append(x[0])

            data = data[length:]
       
        if len(ret) == 1:
            return ret[0] 

        return ret

    def join_thread(self):
        self.thread_recv.join()
        self.thread_callback.join()

    def write(self, device, function_id, data, form, form_ret):
        device.sem_write.acquire()
       
        length = struct.pack('<H', struct.calcsize('<' + form) + 4)
        if sys.hexversion < 0x03000000:
            write_data = chr(device.stack_id) + chr(function_id) + length
        else:
            write_data = bytes([device.stack_id, function_id]) + length

        for f, d in zip(form.split(' '), data):
            if len(f) > 1 and not 's' in f:
                write_data += struct.pack('<' + f, *d)
            elif 's' in f:
                if sys.hexversion < 0x03000000:
                    if type(d) == types.UnicodeType:
                        write_data += struct.pack('<' + f, d.encode('ascii'))
                    else:
                        write_data += struct.pack('<' + f, d)
                else:
                    if isinstance(d, str):
                        write_data += struct.pack('<' + f, bytes(d, 'ascii'))
                    else:
                        write_data += struct.pack('<' + f, d)
            else:
                write_data += struct.pack('<' + f, d)

        if len(form_ret) != 0:
            device.answer_function_id = function_id

        try:
            self.sock.send(write_data)
        except socket.error:
            self.destroy()

        if len(form_ret) == 0:
            device.sem_write.release()
            return
        
        try:
            answer = device.answer_queue.get(True, IPConnection.TIMEOUT_ANSWER)
        except Empty:
            device.sem_write.release()
            msg = 'Did not receive answer for message' + str(data) +  'in time'
            raise Error(Error.TIMEOUT, msg)

        try:
            device.sem_write.release()
        except ValueError:
            self.recv_loop_flag = False

        return self.data_to_return(answer, form_ret)

    def handle_message(self, data):
        function_id = get_function_id_from_data(data)
        if function_id == IPConnection.FUNCTION_GET_STACK_ID:
            return self.handle_add_device(data)
        if function_id == IPConnection.FUNCTION_ENUMERATE_CALLBACK:
            return self.handle_enumerate(data)

        stack_id = get_stack_id_from_data(data)
        length = get_length_from_data(data)

        if not stack_id in self.devices:
            # Message for an unknown device, ignoring it
            return length

        device = self.devices[stack_id]
        if device.answer_function_id == function_id:
            device.answer_queue.put(data[4:])
            return length
    
        if function_id in device.callbacks:
            self.callback_queue.put(data)
            return length

        # Message seems to be OK, but can't be handled, most likely
        # a callback without registered function
        return length;

    def handle_enumerate(self, data):
        length = get_length_from_data(data)

        if self.enumerate_callback == None:
            return length

        self.callback_queue.put(data) 
        return length


    def enumerate(self, func):
        self.enumerate_callback = func
        if sys.hexversion < 0x03000000:
            msg = chr(IPConnection.BROADCAST_ADDRESS) + \
                  chr(IPConnection.FUNCTION_ENUMERATE) + \
                  struct.pack('<H', IPConnection.ENUMERATE_LENGTH)
        else:
            msg = bytes([IPConnection.BROADCAST_ADDRESS, 
                         IPConnection.FUNCTION_ENUMERATE]) + \
                  struct.pack('<H', IPConnection.ENUMERATE_LENGTH)

        self.sock.send(msg)

    def handle_add_device(self, data):
        length = get_length_from_data(data)

        if self.add_dev == None:
            return length

        value = struct.unpack('<BBHQ 3B 40s B', data[:length])

        if self.add_dev.uid == value[3]:
            if sys.hexversion < 0x03000000:
                name = value[7].replace(chr(0), '').decode()
            else:
                name = value[7].decode('ascii').replace(chr(0), '')

            i = name.rfind(' ')
            if i < 0 or name[0:i] != self.add_dev.expected_name:
                return length;

            self.add_dev.firmware_version = [value[4], value[5], value[6]]
            self.add_dev.name = name
            self.add_dev.stack_id = value[8]
            self.devices[value[8]] = self.add_dev
            self.add_dev.answer_queue.put(None)
            self.add_dev = None

        return length

    def add_device(self, device):
        if sys.hexversion < 0x03000000:
            msg = chr(IPConnection.BROADCAST_ADDRESS) + \
                  chr(IPConnection.FUNCTION_GET_STACK_ID) + \
                  struct.pack('<H', IPConnection.GET_STACK_ID_LENGTH) + \
                  struct.pack('<Q', device.uid)
        else:
            msg = bytes([IPConnection.BROADCAST_ADDRESS,
                         IPConnection.FUNCTION_GET_STACK_ID]) + \
                  struct.pack('<H', IPConnection.GET_STACK_ID_LENGTH) + \
                  struct.pack('<Q', device.uid)
  
        self.add_dev = device
        self.sock.send(msg)
    
        try:
            device.answer_queue.get(True, IPConnection.TIMEOUT_ADD_DEVICE)
        except Empty:
            msg = 'Could not add device ' + \
                  str(base58encode(device.uid)) + \
                  ', timeout'
            raise Error(Error.TIMEOUT, msg)

        device.ipcon = self

    def write_bricklet_plugin(self, device, port, plugin):
        position = 0

        # Fill last chunk with zeros
        length = len(plugin)
        mod = length % IPConnection.PLUGIN_CHUNK_SIZE
        if mod != 0:
            plugin += '\x00'*(IPConnection.PLUGIN_CHUNK_SIZE-mod)

        while len(plugin) != 0:
            plugin_chunk = plugin[:IPConnection.PLUGIN_CHUNK_SIZE]
            plugin = plugin[IPConnection.PLUGIN_CHUNK_SIZE:]

            self.write(device,
                       IPConnection.FUNCTION_WRITE_BRICKLET_PLUGIN,
                       (port, position, plugin_chunk),
                       'c B 32s',
                       '')

            position += 1

    def read_bricklet_plugin(self, device, port, length):
        plugin = ''
        position = 0
        while len(plugin) < length:
            plugin += self.write(device, 
                                 IPConnection.FUNCTION_READ_BRICKLET_PLUGIN,
                                 (port, position), 
                                 'c B', 
                                 '32s')
            position += 1

        # Remove unnecessary bytes at end
        return plugin[:length]
        
    def get_adc_calibration(self, device):
        return self.write(device, 
                          IPConnection.FUNCTION_GET_ADC_CALIBRATION,
                          (), 
                          '', 
                          'h h')


    def adc_calibrate(self, device, port):
        self.write(device,
                   IPConnection.FUNCTION_ADC_CALIBRATE,
                   (port,),
                   'c',
                   '')

    def write_bricklet_uid(self, device, port, uid):
        uid_int = base58decode(uid)

        self.write(device,
                   IPConnection.FUNCTION_WRITE_BRICKLET_UID,
                   (port, uid_int),
                   'c Q',
                   '')

    def read_bricklet_uid(self, device, port):
        uid_int = self.write(device, 
                             IPConnection.FUNCTION_READ_BRICKLET_UID,
                             (port,), 
                             'c', 
                             'Q')

        return base58encode(uid_int)
