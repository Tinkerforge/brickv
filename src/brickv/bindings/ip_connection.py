# -*- coding: utf-8 -*-
# Copyright (C) 2012-2015 Matthias Bolte <matthias@tinkerforge.com>
# Copyright (C) 2011-2012 Olaf Lüke <olaf@tinkerforge.com>
#
# Redistribution and use in source and binary forms of this file,
# with or without modification, are permitted. See the Creative
# Commons Zero (CC0 1.0) License for more details.

from threading import Thread, Lock, Semaphore

try:
    from threading import current_thread # Python 2.6
except ImportError:
    from threading import currentThread as current_thread # Python 2.5

try:
    from queue import Queue, Empty # Python 3
except ImportError:
    from Queue import Queue, Empty # Python 2

import struct
import socket
import sys
import time
import os
import math
import hmac
import hashlib
import errno

try:
    from collections import namedtuple
except ImportError:
    def namedtuple(typename, field_names, verbose=False, rename=False):
        def ntuple(*args):
            return args

        return ntuple

def get_uid_from_data(data):
    return struct.unpack('<I', data[0:4])[0]

def get_length_from_data(data):
    return struct.unpack('<B', data[4:5])[0]

def get_function_id_from_data(data):
    return struct.unpack('<B', data[5:6])[0]

def get_sequence_number_from_data(data):
    return (struct.unpack('<B', data[6:7])[0] >> 4) & 0x0F

def get_error_code_from_data(data):
    return (struct.unpack('<B', data[7:8])[0] >> 6) & 0x03

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

def uid64_to_uid32(uid64):
    value1 = uid64 & 0xFFFFFFFF
    value2 = (uid64 >> 32) & 0xFFFFFFFF

    uid32  = (value1 & 0x00000FFF)
    uid32 |= (value1 & 0x0F000000) >> 12
    uid32 |= (value2 & 0x0000003F) << 16
    uid32 |= (value2 & 0x000F0000) << 6
    uid32 |= (value2 & 0x3F000000) << 2

    return uid32

class Error(Exception):
    TIMEOUT = -1
    NOT_ADDED = -6 # obsolete since v2.0
    ALREADY_CONNECTED = -7
    NOT_CONNECTED = -8
    INVALID_PARAMETER = -9
    NOT_SUPPORTED = -10
    UNKNOWN_ERROR_CODE = -11
    STREAM_NO_DATA = -12
    STREAM_OUT_OF_SYNC = -13

    def __init__(self, value, description):
        self.value = value
        self.description = description

    def __str__(self):
        return str(self.description) + ' (' + str(self.value) + ')'

class Device:
    RESPONSE_EXPECTED_INVALID_FUNCTION_ID = 0
    RESPONSE_EXPECTED_ALWAYS_TRUE = 1 # getter
    RESPONSE_EXPECTED_ALWAYS_FALSE = 2 # callback
    RESPONSE_EXPECTED_TRUE = 3 # setter
    RESPONSE_EXPECTED_FALSE = 4 # setter, default

    STREAM_STATUS_COMPLETE = 0
    STREAM_STATUS_OUT_OF_SYNC = 1

    def __init__(self, uid, ipcon):
        """
        Creates the device object with the unique device ID *uid* and adds
        it to the IPConnection *ipcon*.
        """

        uid_ = base58decode(uid)

        if uid_ > 0xFFFFFFFF:
            uid_ = uid64_to_uid32(uid_)

        self.uid = uid_
        self.ipcon = ipcon
        self.api_version = (0, 0, 0)
        self.registered_callbacks = {}
        self.callback_formats = {}
        self.low_level_callbacks = {}
        self.expected_response_function_id = None # protected by request_lock
        self.expected_response_sequence_number = None # protected by request_lock
        self.response_queue = Queue()
        self.request_lock = Lock()
        self.stream_lock = Lock()

        self.response_expected = [Device.RESPONSE_EXPECTED_INVALID_FUNCTION_ID] * 256
        self.response_expected[IPConnection.FUNCTION_ENUMERATE] = Device.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[IPConnection.FUNCTION_ADC_CALIBRATE] = Device.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[IPConnection.FUNCTION_GET_ADC_CALIBRATION] = Device.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[IPConnection.FUNCTION_READ_BRICKLET_UID] = Device.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[IPConnection.FUNCTION_WRITE_BRICKLET_UID] = Device.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[IPConnection.FUNCTION_READ_BRICKLET_PLUGIN] = Device.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[IPConnection.FUNCTION_WRITE_BRICKLET_PLUGIN] = Device.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[IPConnection.CALLBACK_ENUMERATE] = Device.RESPONSE_EXPECTED_ALWAYS_FALSE

        ipcon.devices[self.uid] = self # FIXME: maybe use a weakref here

    def get_api_version(self):
        """
        Returns the API version (major, minor, revision) of the bindings for
        this device.
        """

        return self.api_version

    def get_response_expected(self, function_id):
        """
        Returns the response expected flag for the function specified by the
        *function_id* parameter. It is *true* if the function is expected to
        send a response, *false* otherwise.

        For getter functions this is enabled by default and cannot be disabled,
        because those functions will always send a response. For callback
        configuration functions it is enabled by default too, but can be
        disabled via the set_response_expected function. For setter functions
        it is disabled by default and can be enabled.

        Enabling the response expected flag for a setter function allows to
        detect timeouts and other error conditions calls of this setter as
        well. The device will then send a response for this purpose. If this
        flag is disabled for a setter function then no response is send and
        errors are silently ignored, because they cannot be detected.
        """

        if function_id < 0 or function_id >= len(self.response_expected):
            raise ValueError('Function ID {0} out of range'.format(function_id))

        flag = self.response_expected[function_id]

        if flag == Device.RESPONSE_EXPECTED_INVALID_FUNCTION_ID:
            raise ValueError('Invalid function ID {0}'.format(function_id))

        return flag in [Device.RESPONSE_EXPECTED_ALWAYS_TRUE, Device.RESPONSE_EXPECTED_TRUE]

    def set_response_expected(self, function_id, response_expected):
        """
        Changes the response expected flag of the function specified by the
        *function_id* parameter. This flag can only be changed for setter
        (default value: *false*) and callback configuration functions
        (default value: *true*). For getter functions it is always enabled
        and callbacks it is always disabled.

        Enabling the response expected flag for a setter function allows to
        detect timeouts and other error conditions calls of this setter as
        well. The device will then send a response for this purpose. If this
        flag is disabled for a setter function then no response is send and
        errors are silently ignored, because they cannot be detected.
        """

        if function_id < 0 or function_id >= len(self.response_expected):
            raise ValueError('Function ID {0} out of range'.format(function_id))

        flag = self.response_expected[function_id]

        if flag == Device.RESPONSE_EXPECTED_INVALID_FUNCTION_ID:
            raise ValueError('Invalid function ID {0}'.format(function_id))

        if flag in [Device.RESPONSE_EXPECTED_ALWAYS_TRUE, Device.RESPONSE_EXPECTED_ALWAYS_FALSE]:
            raise ValueError('Response Expected flag cannot be changed for function ID {0}'.format(function_id))

        if bool(response_expected):
            self.response_expected[function_id] = Device.RESPONSE_EXPECTED_TRUE
        else:
            self.response_expected[function_id] = Device.RESPONSE_EXPECTED_FALSE

    def set_response_expected_all(self, response_expected):
        """
        Changes the response expected flag for all setter and callback
        configuration functions of this device at once.
        """

        if bool(response_expected):
            flag = Device.RESPONSE_EXPECTED_TRUE
        else:
            flag = Device.RESPONSE_EXPECTED_FALSE

        for i in range(len(self.response_expected)):
            if self.response_expected[i] in [Device.RESPONSE_EXPECTED_TRUE, Device.RESPONSE_EXPECTED_FALSE]:
                self.response_expected[i] = flag

class BrickDaemon(Device):
    FUNCTION_GET_AUTHENTICATION_NONCE = 1
    FUNCTION_AUTHENTICATE = 2

    def __init__(self, uid, ipcon):
        Device.__init__(self, uid, ipcon)

        self.api_version = (2, 0, 0)

        self.response_expected[BrickDaemon.FUNCTION_GET_AUTHENTICATION_NONCE] = BrickDaemon.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickDaemon.FUNCTION_AUTHENTICATE] = BrickDaemon.RESPONSE_EXPECTED_TRUE

    def get_authentication_nonce(self):
        return self.ipcon.send_request(self, BrickDaemon.FUNCTION_GET_AUTHENTICATION_NONCE, (), '', '4B')

    def authenticate(self, client_nonce, digest):
        self.ipcon.send_request(self, BrickDaemon.FUNCTION_AUTHENTICATE, (client_nonce, digest), '4B 20B', '')

class IPConnection:
    FUNCTION_ENUMERATE = 254
    FUNCTION_ADC_CALIBRATE = 251
    FUNCTION_GET_ADC_CALIBRATION = 250
    FUNCTION_READ_BRICKLET_UID = 249
    FUNCTION_WRITE_BRICKLET_UID = 248
    FUNCTION_READ_BRICKLET_PLUGIN = 247
    FUNCTION_WRITE_BRICKLET_PLUGIN = 246
    FUNCTION_DISCONNECT_PROBE = 128

    CALLBACK_ENUMERATE = 253
    CALLBACK_CONNECTED = 0
    CALLBACK_DISCONNECTED = 1

    BROADCAST_UID = 0

    PLUGIN_CHUNK_SIZE = 32

    # enumeration_type parameter to the enumerate callback
    ENUMERATION_TYPE_AVAILABLE = 0
    ENUMERATION_TYPE_CONNECTED = 1
    ENUMERATION_TYPE_DISCONNECTED = 2

    # connect_reason parameter to the connected callback
    CONNECT_REASON_REQUEST = 0
    CONNECT_REASON_AUTO_RECONNECT = 1

    # disconnect_reason parameter to the disconnected callback
    DISCONNECT_REASON_REQUEST = 0
    DISCONNECT_REASON_ERROR = 1
    DISCONNECT_REASON_SHUTDOWN = 2

    # returned by get_connection_state
    CONNECTION_STATE_DISCONNECTED = 0
    CONNECTION_STATE_CONNECTED = 1
    CONNECTION_STATE_PENDING = 2 # auto-reconnect in process

    QUEUE_EXIT = 0
    QUEUE_META = 1
    QUEUE_PACKET = 2

    DISCONNECT_PROBE_INTERVAL = 5

    class CallbackContext:
        def __init__(self):
            self.queue = None
            self.thread = None
            self.packet_dispatch_allowed = False
            self.lock = None

    def __init__(self):
        """
        Creates an IP Connection object that can be used to enumerate the available
        devices. It is also required for the constructor of Bricks and Bricklets.
        """

        self.host = None
        self.port = None
        self.timeout = 2.5
        self.auto_reconnect = True
        self.auto_reconnect_allowed = False
        self.auto_reconnect_pending = False
        self.sequence_number_lock = Lock()
        self.next_sequence_number = 0 # protected by sequence_number_lock
        self.authentication_lock = Lock() # protects authentication handshake
        self.next_authentication_nonce = 0 # protected by authentication_lock
        self.devices = {}
        self.registered_callbacks = {}
        self.socket = None # protected by socket_lock
        self.socket_id = 0 # protected by socket_lock
        self.socket_lock = Lock()
        self.socket_send_lock = Lock()
        self.receive_flag = False
        self.receive_thread = None
        self.callback = None
        self.disconnect_probe_flag = False
        self.disconnect_probe_queue = None
        self.disconnect_probe_thread = None
        self.waiter = Semaphore()
        self.brickd = BrickDaemon("2", self)

    def connect(self, host, port):
        """
        Creates a TCP/IP connection to the given *host* and *port*. The host
        and port can point to a Brick Daemon or to a WIFI/Ethernet Extension.

        Devices can only be controlled when the connection was established
        successfully.

        Blocks until the connection is established and throws an exception if
        there is no Brick Daemon or WIFI/Ethernet Extension listening at the
        given host and port.
        """

        with self.socket_lock:
            if self.socket is not None:
                raise Error(Error.ALREADY_CONNECTED,
                            'Already connected to {0}:{1}'.format(self.host, self.port))

            self.host = host
            self.port = port

            self.connect_unlocked(False)

    def disconnect(self):
        """
        Disconnects the TCP/IP connection from the Brick Daemon or the
        WIFI/Ethernet Extension.
        """

        with self.socket_lock:
            self.auto_reconnect_allowed = False

            if self.auto_reconnect_pending:
                # abort potentially pending auto reconnect
                self.auto_reconnect_pending = False
            else:
                if self.socket is None:
                    raise Error(Error.NOT_CONNECTED, 'Not connected')

                self.disconnect_unlocked()

            # end callback thread
            callback = self.callback
            self.callback = None

        # do this outside of socket_lock to allow calling (dis-)connect from
        # the callbacks while blocking on the join call here
        callback.queue.put((IPConnection.QUEUE_META,
                            (IPConnection.CALLBACK_DISCONNECTED,
                             IPConnection.DISCONNECT_REASON_REQUEST, None)))
        callback.queue.put((IPConnection.QUEUE_EXIT, None))

        if current_thread() is not callback.thread:
            callback.thread.join()

    def authenticate(self, secret):
        """
        Performs an authentication handshake with the connected Brick Daemon or
        WIFI/Ethernet Extension. If the handshake succeeds the connection switches
        from non-authenticated to authenticated state and communication can
        continue as normal. If the handshake fails then the connection gets closed.
        Authentication can fail if the wrong secret was used or if authentication
        is not enabled at all on the Brick Daemon or the WIFI/Ethernet Extension.

        For more information about authentication see
        http://www.tinkerforge.com/en/doc/Tutorials/Tutorial_Authentication/Tutorial.html
        """

        secret_bytes = secret.encode('ascii')

        with self.authentication_lock:
            if self.next_authentication_nonce == 0:
                try:
                    self.next_authentication_nonce = struct.unpack('<I', os.urandom(4))[0]
                except NotImplementedError:
                    subseconds, seconds = math.modf(time.time())
                    seconds = int(seconds)
                    subseconds = int(subseconds * 1000000)
                    self.next_authentication_nonce = ((seconds << 26 | seconds >> 6) & 0xFFFFFFFF) + subseconds + os.getpid()

            server_nonce = self.brickd.get_authentication_nonce()
            client_nonce = struct.unpack('<4B', struct.pack('<I', self.next_authentication_nonce))
            self.next_authentication_nonce = (self.next_authentication_nonce + 1) % (1 << 32)

            h = hmac.new(secret_bytes, digestmod=hashlib.sha1)

            h.update(struct.pack('<4B', *server_nonce))
            h.update(struct.pack('<4B', *client_nonce))

            digest = struct.unpack('<20B', h.digest())
            h = None

            self.brickd.authenticate(client_nonce, digest)

    def get_connection_state(self):
        """
        Can return the following states:

        - CONNECTION_STATE_DISCONNECTED: No connection is established.
        - CONNECTION_STATE_CONNECTED: A connection to the Brick Daemon or
          the WIFI/Ethernet Extension is established.
        - CONNECTION_STATE_PENDING: IP Connection is currently trying to
          connect.
        """

        if self.socket is not None:
            return IPConnection.CONNECTION_STATE_CONNECTED
        elif self.auto_reconnect_pending:
            return IPConnection.CONNECTION_STATE_PENDING
        else:
            return IPConnection.CONNECTION_STATE_DISCONNECTED

    def set_auto_reconnect(self, auto_reconnect):
        """
        Enables or disables auto-reconnect. If auto-reconnect is enabled,
        the IP Connection will try to reconnect to the previously given
        host and port, if the connection is lost.

        Default value is *True*.
        """

        self.auto_reconnect = bool(auto_reconnect)

        if not self.auto_reconnect:
            # abort potentially pending auto reconnect
            self.auto_reconnect_allowed = False

    def get_auto_reconnect(self):
        """
        Returns *true* if auto-reconnect is enabled, *false* otherwise.
        """

        return self.auto_reconnect

    def set_timeout(self, timeout):
        """
        Sets the timeout in seconds for getters and for setters for which the
        response expected flag is activated.

        Default timeout is 2.5.
        """

        timeout = float(timeout)

        if timeout < 0:
            raise ValueError('Timeout cannot be negative')

        self.timeout = timeout

    def get_timeout(self):
        """
        Returns the timeout as set by set_timeout.
        """

        return self.timeout

    def enumerate(self):
        """
        Broadcasts an enumerate request. All devices will respond with an
        enumerate callback.
        """

        request, _, _ = self.create_packet_header(None, 8, IPConnection.FUNCTION_ENUMERATE)

        self.send(request)

    def wait(self):
        """
        Stops the current thread until unwait is called.

        This is useful if you rely solely on callbacks for events, if you want
        to wait for a specific callback or if the IP Connection was created in
        a thread.

        Wait and unwait act in the same way as "acquire" and "release" of a
        semaphore.
        """
        self.waiter.acquire()

    def unwait(self):
        """
        Unwaits the thread previously stopped by wait.

        Wait and unwait act in the same way as "acquire" and "release" of
        a semaphore.
        """
        self.waiter.release()

    def register_callback(self, id_, callback):
        """
        Registers a callback with ID *id* to the function *callback*.
        """
        if callback is None:
            self.registered_callbacks.pop(id_, None)
        else:
            self.registered_callbacks[id_] = callback

    def connect_unlocked(self, is_auto_reconnect):
        # NOTE: assumes that socket is None and socket_lock is locked

        # create callback thread and queue
        if self.callback is None:
            try:
                self.callback = IPConnection.CallbackContext()
                self.callback.queue = Queue()
                self.callback.packet_dispatch_allowed = False
                self.callback.lock = Lock()
                self.callback.thread = Thread(name='Callback-Processor',
                                              target=self.callback_loop,
                                              args=(self.callback, ))
                self.callback.thread.daemon = True
                self.callback.thread.start()
            except:
                self.callback = None
                raise

        # create and connect socket
        try:
            tmp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tmp.settimeout(5)
            tmp.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            tmp.connect((self.host, self.port))

            if sys.platform == 'win32':
                # for some unknown reason the socket recv() call does not
                # immediate return on Windows if the socket gets shut down on
                # disconnect. the socket recv() call will still block for
                # several seconds before it returns. this in turn blocks the
                # disconnect. to workaround this use a 100ms timeout for
                # blocking socket operations.
                tmp.settimeout(0.1)
            else:
                tmp.settimeout(None)
        except:
            def cleanup1():
                # end callback thread
                if not is_auto_reconnect:
                    self.callback.queue.put((IPConnection.QUEUE_EXIT, None))

                    if current_thread() is not self.callback.thread:
                        self.callback.thread.join()

                    self.callback = None

            cleanup1()
            raise

        self.socket = tmp
        self.socket_id += 1

        # create disconnect probe thread
        try:
            self.disconnect_probe_flag = True
            self.disconnect_probe_queue = Queue()
            self.disconnect_probe_thread = Thread(name='Disconnect-Prober',
                                                  target=self.disconnect_probe_loop,
                                                  args=(self.disconnect_probe_queue, ))
            self.disconnect_probe_thread.daemon = True
            self.disconnect_probe_thread.start()
        except:
            def cleanup2():
                self.disconnect_probe_thread = None

                # close socket
                self.socket.close()
                self.socket = None

                # end callback thread
                if not is_auto_reconnect:
                    self.callback.queue.put((IPConnection.QUEUE_EXIT, None))

                    if current_thread() is not self.callback.thread:
                        self.callback.thread.join()

                    self.callback = None

            cleanup2()
            raise

        # create receive thread
        self.callback.packet_dispatch_allowed = True

        try:
            self.receive_flag = True
            self.receive_thread = Thread(name='Brickd-Receiver',
                                         target=self.receive_loop,
                                         args=(self.socket_id, ))
            self.receive_thread.daemon = True
            self.receive_thread.start()
        except:
            def cleanup3():
                # close socket
                self.disconnect_unlocked()

                # end callback thread
                if not is_auto_reconnect:
                    self.callback.queue.put((IPConnection.QUEUE_EXIT, None))

                    if current_thread() is not self.callback.thread:
                        self.callback.thread.join()

                    self.callback = None

            cleanup3()
            raise

        self.auto_reconnect_allowed = False
        self.auto_reconnect_pending = False

        if is_auto_reconnect:
            connect_reason = IPConnection.CONNECT_REASON_AUTO_RECONNECT
        else:
            connect_reason = IPConnection.CONNECT_REASON_REQUEST

        self.callback.queue.put((IPConnection.QUEUE_META,
                                (IPConnection.CALLBACK_CONNECTED,
                                 connect_reason, None)))

    def disconnect_unlocked(self):
        # NOTE: assumes that socket is not None and socket_lock is locked

        # end disconnect probe thread
        self.disconnect_probe_queue.put(True)
        self.disconnect_probe_thread.join() # FIXME: use a timeout?
        self.disconnect_probe_thread = None

        # stop dispatching packet callbacks before ending the receive
        # thread to avoid timeout exceptions due to callback functions
        # trying to call getters
        if current_thread() is not self.callback.thread:
            # FIXME: cannot hold callback lock here because this can
            #        deadlock due to an ordering problem with the socket lock
            #with self.callback.lock:
            if True:
                self.callback.packet_dispatch_allowed = False
        else:
            self.callback.packet_dispatch_allowed = False

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

    def receive_loop(self, socket_id):
        if sys.hexversion < 0x03000000:
            pending_data = ''
        else:
            pending_data = bytes()

        while self.receive_flag:
            try:
                data = self.socket.recv(8192)
            except socket.timeout:
                continue
            except socket.error:
                if self.receive_flag:
                    e = sys.exc_info()[1]
                    if e.errno == errno.EINTR:
                        continue

                    self.handle_disconnect_by_peer(IPConnection.DISCONNECT_REASON_ERROR, socket_id, False)
                break

            if len(data) == 0:
                if self.receive_flag:
                    self.handle_disconnect_by_peer(IPConnection.DISCONNECT_REASON_SHUTDOWN, socket_id, False)
                break

            pending_data += data

            while self.receive_flag:
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

    def dispatch_meta(self, function_id, parameter, socket_id):
        if function_id == IPConnection.CALLBACK_CONNECTED:
            if IPConnection.CALLBACK_CONNECTED in self.registered_callbacks:
                self.registered_callbacks[IPConnection.CALLBACK_CONNECTED](parameter)
        elif function_id == IPConnection.CALLBACK_DISCONNECTED:
            if parameter != IPConnection.DISCONNECT_REASON_REQUEST:
                # need to do this here, the receive_loop is not allowed to
                # hold the socket_lock because this could cause a deadlock
                # with a concurrent call to the (dis-)connect function
                with self.socket_lock:
                    # don't close the socket if it got disconnected or
                    # reconnected in the meantime
                    if self.socket is not None and self.socket_id == socket_id:
                        # end disconnect probe thread
                        self.disconnect_probe_queue.put(True)
                        self.disconnect_probe_thread.join() # FIXME: use a timeout?
                        self.disconnect_probe_thread = None

                        # close socket
                        self.socket.close()
                        self.socket = None

            # FIXME: wait a moment here, otherwise the next connect
            # attempt will succeed, even if there is no open server
            # socket. the first receive will then fail directly
            time.sleep(0.1)

            if IPConnection.CALLBACK_DISCONNECTED in self.registered_callbacks:
                self.registered_callbacks[IPConnection.CALLBACK_DISCONNECTED](parameter)

            if parameter != IPConnection.DISCONNECT_REASON_REQUEST and \
               self.auto_reconnect and self.auto_reconnect_allowed:
                self.auto_reconnect_pending = True
                retry = True

                # block here until reconnect. this is okay, there is no
                # callback to deliver when there is no connection
                while retry:
                    retry = False

                    with self.socket_lock:
                        if self.auto_reconnect_allowed and self.socket is None:
                            try:
                                self.connect_unlocked(True)
                            except:
                                retry = True
                        else:
                            self.auto_reconnect_pending = False

                    if retry:
                        time.sleep(0.1)

    def dispatch_packet(self, packet):
        uid = get_uid_from_data(packet)
        length = get_length_from_data(packet)
        function_id = get_function_id_from_data(packet)
        payload = packet[8:]

        if function_id == IPConnection.CALLBACK_ENUMERATE and \
           IPConnection.CALLBACK_ENUMERATE in self.registered_callbacks:
            uid, connected_uid, position, hardware_version, \
                firmware_version, device_identifier, enumeration_type = \
                self.deserialize_data(payload, '8s 8s c 3B 3B H B')

            cb = self.registered_callbacks[IPConnection.CALLBACK_ENUMERATE]
            cb(uid, connected_uid, position, hardware_version,
               firmware_version, device_identifier, enumeration_type)
            return

        if uid not in self.devices:
            return

        device = self.devices[uid]

        if function_id in device.registered_callbacks:
            cb = device.registered_callbacks[function_id]
            form = device.callback_formats[function_id]

            if len(form) == 0:
                cb()
            elif len(form) == 1:
                cb(self.deserialize_data(payload, form))
            else:
                cb(*self.deserialize_data(payload, form))

        if function_id in device.low_level_callbacks:
            llcb = device.low_level_callbacks[function_id] # [hlfid, options, state]
            llform = device.callback_formats[function_id] # FIXME: currently assuming that llform is longer than 1
            values = self.deserialize_data(payload, llform)
            stream = llcb[1].get('stream', None)

            if stream != None:
                result = None
                fixed_total_length = stream.get('fixed_total_length', None)

                if fixed_total_length == None:
                    extra = tuple(values[:-3])
                    total_length = values[-3]
                else:
                    extra = tuple(values[:-2])
                    total_length = fixed_total_length

                # FIXME: validate that extra parameters are identical for all low-level callback of a stream
                # FIXME: validate that total length is identical for all low-level callback of a stream

                chunk_offset = values[-2] # FIXME: validate chunk offset < total length
                chunk_data = values[-1]

                if llcb[2] == None: # no stream in-progress
                    if chunk_offset == 0: # stream starts
                        llcb[2] = chunk_data

                        if len(llcb[2]) >= total_length: # stream complete
                            result = extra + (Device.STREAM_STATUS_COMPLETE,) + (llcb[2][:total_length],)
                            llcb[2] = None
                    else: # ignore tail of current stream, wait for next stream start
                        pass
                else: # stream in-progress
                    if chunk_offset != len(llcb[2]): # stream out-of-sync
                        result = extra + (Device.STREAM_STATUS_OUT_OF_SYNC,) + (None,)
                        llcb[2] = None
                    else: # stream in-sync
                        llcb[2] += chunk_data

                        if len(llcb[2]) >= total_length: # stream complete
                            result = extra + (Device.STREAM_STATUS_COMPLETE,) + (llcb[2][:total_length],)
                            llcb[2] = None

                if result != None and llcb[0] in device.registered_callbacks:
                    device.registered_callbacks[llcb[0]](*result)

    def callback_loop(self, callback):
        while True:
            kind, data = callback.queue.get()

            # FIXME: cannot hold callback lock here because this can
            #        deadlock due to an ordering problem with the socket lock
            #with callback.lock:
            if True:
                if kind == IPConnection.QUEUE_EXIT:
                    break
                elif kind == IPConnection.QUEUE_META:
                    self.dispatch_meta(*data)
                elif kind == IPConnection.QUEUE_PACKET:
                    # don't dispatch callbacks when the receive thread isn't running
                    if callback.packet_dispatch_allowed:
                        self.dispatch_packet(data)

    # NOTE: the disconnect probe thread is not allowed to hold the socket_lock at any
    #       time because it is created and joined while the socket_lock is locked
    def disconnect_probe_loop(self, disconnect_probe_queue):
        request, _, _ = self.create_packet_header(None, 8, IPConnection.FUNCTION_DISCONNECT_PROBE)

        while True:
            try:
                disconnect_probe_queue.get(True, IPConnection.DISCONNECT_PROBE_INTERVAL)
                break
            except Empty:
                pass

            if self.disconnect_probe_flag:
                try:
                    with self.socket_send_lock:
                        while True:
                            try:
                                self.socket.send(request)
                                break
                            except socket.timeout:
                                continue
                except socket.error:
                    self.handle_disconnect_by_peer(IPConnection.DISCONNECT_REASON_ERROR,
                                                   self.socket_id, False)
                    break
            else:
                self.disconnect_probe_flag = True

    def deserialize_data(self, data, form):
        ret = []

        for f in form.split(' '):
            o = f

            if '!' in f:
                if len(f) > 1:
                    f = '{0}B'.format(int(math.ceil(int(f.replace('!', '')) / 8.0)))
                else:
                    f = 'B'

            f = '<' + f
            length = struct.calcsize(f)
            x = struct.unpack(f, data[:length])

            if '!' in o:
                y = []

                if len(o) > 1:
                    for i in range(int(o.replace('!', ''))):
                        y.append(x[i // 8] & (1 << (i % 8)) != 0)
                else:
                    y.append(x[0] != 0)

                x = y

            if len(x) > 1:
                if 'c' in f:
                    x = tuple([self.handle_deserialized_char(c) for c in x])

                ret.append(x)
            elif 'c' in f:
                ret.append(self.handle_deserialized_char(x[0]))
            elif 's' in f:
                ret.append(self.handle_deserialized_string(x[0]))
            else:
                ret.append(x[0])

            data = data[length:]

        if len(ret) == 1:
            return ret[0]
        else:
            return ret

    def handle_deserialized_char(self, c):
        if sys.hexversion >= 0x03000000:
            try:
                # c is a bytes object, try to decode it as ASCII. if it is
                # not decodable keep it as a bytes object because there is no
                # other option for this in Python 3
                c = c.decode('ascii')
            except:
                pass

        return c

    def handle_deserialized_string(self, s):
        nul = b'\x00'

        if sys.hexversion >= 0x03000000:
            try:
                # s is a bytes object, try to decode it as ASCII. if it is
                # not decodable keep it as a bytes object because there is no
                # other option for this in Python 3
                s = s.decode('ascii')
                nul = '\x00'
            except:
                pass

        i = s.find(nul)
        if i >= 0:
            s = s[:i]

        return s

    def send(self, packet):
        with self.socket_lock:
            if self.socket is None:
                raise Error(Error.NOT_CONNECTED, 'Not connected')

            try:
                with self.socket_send_lock:
                    while True:
                        try:
                            self.socket.send(packet)
                            break
                        except socket.timeout:
                            continue
            except socket.error:
                self.handle_disconnect_by_peer(IPConnection.DISCONNECT_REASON_ERROR, None, True)
                raise Error(Error.NOT_CONNECTED, 'Not connected')

            self.disconnect_probe_flag = False

    def send_request(self, device, function_id, data, form, form_ret):
        patched_from = []

        for f in form.split(' '):
            if '!' in f:
                if len(f) > 1:
                    patched_from.append('{0}B'.format(int(math.ceil(int(f.replace('!', '')) / 8.0))))
                else:
                    patched_from.append('?')
            else:
                patched_from.append(f)

        patched_from = '<' + ' '.join(patched_from)
        length = 8 + struct.calcsize(patched_from)
        request, response_expected, sequence_number = \
            self.create_packet_header(device, length, function_id)

        def pack_string(f, d):
            if sys.hexversion < 0x03000000:
                if isinstance(d, unicode):
                    f = f.replace('s', 'B').replace('c', 'B')
                    l = map(ord, d)
                    p = f.replace('B', '')

                    if len(p) == 0:
                        p = '1'

                    l += [0] * (int(p) - len(l))

                    return struct.pack('<' + f, *l)
                else:
                    return struct.pack('<' + f, d)
            else:
                if isinstance(d, str):
                    return struct.pack('<' + f, bytes(map(ord, d)))
                else:
                    return struct.pack('<' + f, d)

        for f, d in zip(form.split(' '), data):
            if '!' in f:
                if len(f) > 1:
                    if int(f.replace('!', '')) != len(d):
                        raise ValueError('Incorrect bool list length')

                    p = [0]*int(math.ceil(len(d) / 8.0))

                    for i, b in enumerate(d):
                        if b:
                            p[i // 8] |= 1 << (i % 8)

                    request += struct.pack('<{0}B'.format(len(p)), *p)
                else:
                    request += struct.pack('<?', d)
            elif len(f) > 1 and not 's' in f and not 'c' in f:
                request += struct.pack('<' + f, *d)
            elif 's' in f:
                request += pack_string(f, d)
            elif 'c' in f:
                if len(f) > 1:
                    if int(f.replace('c', '')) != len(d):
                        raise ValueError('Incorrect char list length')

                    for k in d:
                        request += pack_string('c', k)
                else:
                    request += pack_string(f, d)
            else:
                request += struct.pack('<' + f, d)

        if response_expected:
            with device.request_lock:
                device.expected_response_function_id = function_id
                device.expected_response_sequence_number = sequence_number

                try:
                    self.send(request)

                    while True:
                        response = device.response_queue.get(True, self.timeout)

                        if function_id == get_function_id_from_data(response) and \
                           sequence_number == get_sequence_number_from_data(response):
                            # ignore old responses that arrived after the timeout expired, but before setting
                            # expected_response_function_id and expected_response_sequence_number back to None
                            break
                except Empty:
                    msg = 'Did not receive response for function {0} in time'.format(function_id)
                    raise Error(Error.TIMEOUT, msg)
                finally:
                    device.expected_response_function_id = None
                    device.expected_response_sequence_number = None

            error_code = get_error_code_from_data(response)

            if error_code == 0:
                # no error
                pass
            elif error_code == 1:
                msg = 'Got invalid parameter for function {0}'.format(function_id)
                raise Error(Error.INVALID_PARAMETER, msg)
            elif error_code == 2:
                msg = 'Function {0} is not supported'.format(function_id)
                raise Error(Error.NOT_SUPPORTED, msg)
            else:
                msg = 'Function {0} returned an unknown error'.format(function_id)
                raise Error(Error.UNKNOWN_ERROR_CODE, msg)

            if len(form_ret) > 0:
                return self.deserialize_data(response[8:], form_ret)
        else:
            self.send(request)

    def get_next_sequence_number(self):
        with self.sequence_number_lock:
            sequence_number = self.next_sequence_number + 1
            self.next_sequence_number = sequence_number % 15
            return sequence_number

    def handle_response(self, packet):
        self.disconnect_probe_flag = False

        function_id = get_function_id_from_data(packet)
        sequence_number = get_sequence_number_from_data(packet)

        if sequence_number == 0 and function_id == IPConnection.CALLBACK_ENUMERATE:
            if IPConnection.CALLBACK_ENUMERATE in self.registered_callbacks:
                self.callback.queue.put((IPConnection.QUEUE_PACKET, packet))
            return

        uid = get_uid_from_data(packet)

        if not uid in self.devices:
            # Response from an unknown device, ignoring it
            return

        device = self.devices[uid]

        if sequence_number == 0:
            if function_id in device.registered_callbacks or \
               function_id in device.low_level_callbacks: # FIXME: better lookup
                self.callback.queue.put((IPConnection.QUEUE_PACKET, packet))
            return

        if device.expected_response_function_id == function_id and \
           device.expected_response_sequence_number == sequence_number:
            device.response_queue.put(packet)
            return

        # Response seems to be OK, but can't be handled

    def handle_disconnect_by_peer(self, disconnect_reason, socket_id, disconnect_immediately):
        # NOTE: assumes that socket_lock is locked if disconnect_immediately is true

        self.auto_reconnect_allowed = True

        if disconnect_immediately:
            self.disconnect_unlocked()

        self.callback.queue.put((IPConnection.QUEUE_META,
                                 (IPConnection.CALLBACK_DISCONNECTED,
                                  disconnect_reason, socket_id)))

    def create_packet_header(self, device, length, function_id):
        uid = IPConnection.BROADCAST_UID
        sequence_number = self.get_next_sequence_number()
        r_bit = 0

        if device is not None:
            uid = device.uid

            if device.get_response_expected(function_id):
                r_bit = 1

        sequence_number_and_options = (sequence_number << 4) | (r_bit << 3)

        return (struct.pack('<IBBBB', uid, length, function_id,
                            sequence_number_and_options, 0),
                bool(r_bit),
                sequence_number)

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
