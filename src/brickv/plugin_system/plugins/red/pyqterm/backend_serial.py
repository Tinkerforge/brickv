# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014 Olaf Lüke <olaf@tinkerforge.com>

backend_serial.py: Rewrite of the pyqterm backend for serial 
                   communication with RED Brick. We use the
                   same API, so we can use the rest of the
                   pyqterm code as is.

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public
License along with this program; if not, write to the
Free Software Foundation, Inc., 59 Temple Place - Suite 330,
Boston, MA 02111-1307, USA.
"""

import sys
import os
import fcntl
import array
import threading
import time
import pty
import signal
import struct
import select
import subprocess
import serial
import traceback

from .backend import Terminal


def synchronized(func):
    def wrapper(self, *args, **kwargs):
        try:
            self.lock.acquire()
        except AttributeError:
            self.lock = threading.RLock()
            self.lock.acquire()
        try:
            result = func(self, *args, **kwargs)
        finally:
            self.lock.release()
        return result
    return wrapper

class SerialMultiplexer(object):
    def __init__(self, cmd="/dev/ttyACM0", env_term="xterm-color", timeout=60 * 60 * 24):
        # Set Linux signal handler
        if sys.platform in ("linux2", "linux3"):
            self.sigchldhandler = signal.signal(signal.SIGCHLD, signal.SIG_IGN)
        # Session
        self.session = {}
        self.cmd = cmd
        self.env_term = env_term
        self.timeout = timeout
        self.signal = None

        # Supervisor thread
        self.signal_stop = 0
        self.thread = threading.Thread(target=self.proc_thread)
        self.thread.start()

    def stop(self):
        # Stop supervisor thread
        self.signal_stop = 1
        self.thread.join()

    def proc_resize(self, sid, w, h):
        # TODO: implementme
        pass

    @synchronized
    def proc_keepalive(self, sid, w, h, cmd=None):
        if not sid in self.session:
            # Start a new session
            self.session[sid] = {
                'state': 'unborn',
                'term':    Terminal(w, h),
                'time':    time.time(),
                'w':    w,
                'h':    h}
            return self.proc_spawn(sid, cmd)
        elif self.session[sid]['state'] == 'alive':
            self.session[sid]['time'] = time.time()
            # Update terminal size
            if self.session[sid]['w'] != w or self.session[sid]['h'] != h:
                self.proc_resize(sid, w, h)
            return True
        else:
            return False

    def proc_spawn(self, sid, cmd=None):
        # Session
        self.session[sid]['state'] = 'alive'
        w, h = self.session[sid]['w'], self.session[sid]['h']
        # Fork new process
        
        try:
            self.serial = serial.Serial(cmd, timeout=0)
            return True
        except:
            self.serial = None
            traceback.print_exc()
            self.session[sid]['state'] = 'dead'
            return False

    def proc_waitfordeath(self, sid):
        try:
            self.serial.close()
        except:
            pass

        self.session[sid]['state'] = 'dead'
        return True

    def proc_bury(self, sid):
        self.proc_waitfordeath(sid)
        if sid in self.session:
            del self.session[sid]
        return True

    @synchronized
    def proc_buryall(self):
        for sid in self.session.keys():
            self.proc_bury(sid)

    @synchronized
    def proc_read(self, sid):
        """
        Read from process
        """
        if sid not in self.session:
            return False
        elif self.session[sid]['state'] != 'alive':
            return False
        try:
            d = self.serial.read(65000)
            if not d:
                # Process finished, BSD
                self.proc_waitfordeath(sid)
                return False
        except (IOError, OSError):
            # Process finished, Linux
            self.proc_waitfordeath(sid)
            return False
        term = self.session[sid]['term']
        term.write(d)
        # Read terminal response
        d = term.read()
        if d:
            try:
                self.serial.write(d)
            except (IOError, OSError):
                return False
        return True

    @synchronized
    def proc_write(self, sid, d):
        """
        Write to process
        """
        if sid not in self.session:
            return False
        elif self.session[sid]['state'] != 'alive':
            return False
        try:
            term = self.session[sid]['term']
            d = term.pipe(d)
            self.serial.write(d)
        except (IOError, OSError):
            return False
        return True

    @synchronized
    def proc_dump(self, sid):
        """
        Dump terminal output
        """
        if sid not in self.session:
            return False
        return self.session[sid]['term'].dump()

    @synchronized
    def proc_getalive(self):
        """
        Get alive sessions, bury timed out ones
        """
        fds = []
        fd2sid = {}
        now = time.time()
        for sid in self.session.keys():
            then = self.session[sid]['time']
            if (now - then) > self.timeout:
                self.proc_bury(sid)
            else:
                if self.session[sid]['state'] == 'alive':
                    fds.append(self.session[sid]['fd'])
                    fd2sid[self.session[sid]['fd']] = sid
        return (fds, fd2sid)

    def proc_thread(self):
        """
        Supervisor thread
        """
        while not self.signal_stop:
            # TODO: FIXME
            sid = self.session.keys()[0]
            self.proc_read(sid)
            self.session[sid]["changed"] = time.time()
        self.proc_buryall()