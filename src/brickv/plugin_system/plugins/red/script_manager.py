# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014 Olaf Lüke <olaf@tinkerforge.com>

script_manager.py: Manage RED Brick scripts

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

from brickv.plugin_system.plugins.red.api import REDFile, REDPipe, REDProcess

import traceback
import os
from collections import namedtuple
from PyQt4 import QtCore

from brickv.async_call import async_call
from brickv.object_creator import create_object_in_qt_main_thread

SCRIPT_FOLDER = '/usr/local/scripts'

script_data_set = set()

class ScriptData(QtCore.QObject):
    script_signal = QtCore.pyqtSignal(object)

    def __init__(self):
        QtCore.QObject.__init__(self)
        self.process = None
        self.stdout = None
        self.stderr = None
        self.script_name = None
        self.callback = None
        self.params = None
        self.max_len = None
        self.decode_output_as_utf8 = True
        self.script_instance = None

class ScriptManager:
    ScriptResult = namedtuple('ScriptResult', 'stdout stderr')

    @staticmethod
    def _call(script, sd, data):
        if data == None:
            script.copied = False

        sd.script_signal.emit(data)
        sd.script_signal.disconnect(sd.callback)

    def __init__(self, session):
        self.session = session
        # FIXME: This is blocking the GUI!
        self.devnull = REDFile(self.session).open('/dev/null', REDFile.FLAG_READ_ONLY, 0, 0, 0)
        self.scripts = {}

        # We can't use copy.deepycopy directly on scripts, since deep-copy does not work on QObject.
        # Instead we create a new Script/QObjects here.
        # This is way more efficient anyway, since we can shallow-copy script and file_ending
        # while just reinitializing the rest
        from brickv.plugin_system.plugins.red._scripts import scripts, Script
        for key, value in scripts.items():
            self.scripts[key] = Script(value.script, value.file_ending)

    def destroy(self):
        # ensure to release all REDObjects
        self.devnull.release()
        self.scripts = {}

    # Call with a script name from the scripts/ folder.
    # The stdout and stderr from the script will be given back to callback.
    # If there is an error, callback will return None.
    def execute_script(self, script_name, callback, params = [], max_len = 65536, decode_output_as_utf8=True):
        if not script_name in self.scripts:
            if callback is not None:
                callback(None) # We are still in GUI thread, use callback instead of signal
                return

        sd = ScriptData()
        script_data_set.add(sd)
        sd.script_name = script_name
        sd.callback = callback
        sd.params = params
        sd.max_len = max_len
        sd.decode_output_as_utf8 = decode_output_as_utf8

        if callback is not None:
            sd.script_signal.connect(callback)

        # We just let all exceptions fall through to here and give up.
        # There is nothing we can do anyway.
        try:
            self._init_script(sd)
        except:
            traceback.print_exc()
            if sd.callback is not None:
                sd.script_signal.disconnect(sd.callback)
            self.scripts[sd.script_name].copied = False
            if sd.callback is not None:
                sd.callback(None) # We are still in GUI thread, use callback instead of signal
            script_data_set.remove(sd)

    def _init_script(self, sd):
        if self.scripts[sd.script_name].copied:
            return self._execute_after_init(sd)

        async_call(self._init_script_async, sd, lambda: self._init_script_done(sd), lambda: self._init_script_error(sd))

    def _init_script_async(self, sd):
        script = self.scripts[sd.script_name]

        script.copy_lock.acquire()

        # recheck the copied flag, maybe someone else managed to
        # copy the script in the meantime. if not it's our turn to copy it
        if script.copied:
            script.copy_lock.release()
            return

        try:
            script.file = create_object_in_qt_main_thread(REDFile, (self.session,))
            script.file.open(os.path.join(SCRIPT_FOLDER, sd.script_name + script.file_ending),
                             REDFile.FLAG_WRITE_ONLY | REDFile.FLAG_CREATE | REDFile.FLAG_NON_BLOCKING | REDFile.FLAG_TRUNCATE, 0755, 0, 0)
            script.file.write_async(script.script, lambda error: self._init_script_async_write_done(error, sd))
        except:
            self.scripts[sd.script_name].copy_lock.release()
            traceback.print_exc()
            raise

    def _init_script_async_write_done(self, error, sd):
        script = self.scripts[sd.script_name]

        script.file.release()
        script.file = None
        script.copied = True
        script.copy_lock.release()

        if error == None:
            self._execute_after_init(sd)
        else:
            print '_init_script_async_write_done', unicode(error)
            ScriptManager._call(script, sd, None)
            script_data_set.remove(sd)

    def _init_script_done(self, sd):
        self._execute_after_init(sd)

    def _init_script_error(self, sd):
        ScriptManager._call(self.scripts[sd.script_name], sd, None)
        script_data_set.remove(sd)

    def _execute_after_init(self, sd):
        try:
            sd.stdout = REDPipe(self.session).create(REDPipe.FLAG_NON_BLOCKING_READ, 1024*1024)
            sd.stderr = REDPipe(self.session).create(REDPipe.FLAG_NON_BLOCKING_READ, 1024*1024)
        except:
            traceback.print_exc()
            ScriptManager._call(self.scripts[sd.script_name], sd, None)
            script_data_set.remove(sd)
            return

        def state_changed(red_process, sd):
            # TODO: If we want to support returns > 1MB we need to do more work here,
            #       but it may not be necessary.
            if red_process.state == REDProcess.STATE_ERROR:
                ScriptManager._call(self.scripts[sd.script_name], sd, None)
                try:
                    sd.process.release()
                    sd.stdout.release()
                    sd.stderr.release()
                except:
                    traceback.print_exc()

                script_data_set.remove(sd)
            elif red_process.state == REDProcess.STATE_EXITED:
                def cb_stdout_data(result, sd):
                    if result.error != None:
                        ScriptManager._call(self.scripts[sd.script_name], sd, None)

                        try:
                            sd.process.release()
                            sd.stdout.release()
                            sd.stderr.release()
                        except:
                            traceback.print_exc()

                        script_data_set.remove(sd)

                    if sd.decode_output_as_utf8:
                        out = result.data.decode('utf-8') # NOTE: assuming scripts return UTF-8
                    else:
                        out = result.data

                    def cb_stderr_data(result, sd):
                        if result.error != None:
                            ScriptManager._call(self.scripts[sd.script_name], sd, None)

                        try:
                            sd.process.release()
                            sd.stdout.release()
                            sd.stderr.release()
                        except:
                            traceback.print_exc()


                        if sd.decode_output_as_utf8:
                            err = result.data.decode('utf-8') # NOTE: assuming scripts return UTF-8
                        else:
                            err = result.data

                        ScriptManager._call(self.scripts[sd.script_name], sd, self.ScriptResult(out, err))
                        script_data_set.remove(sd)

                    sd.stderr.read_async(sd.max_len, lambda result: cb_stderr_data(result, sd))

                sd.stdout.read_async(sd.max_len, lambda result: cb_stdout_data(result, sd))

        sd.process = REDProcess(self.session)
        sd.process.state_changed_callback = lambda red_process: state_changed(red_process, sd)

        # need to set LANG otherwise python will not correctly handle non-ASCII filenames
        env = ['LANG=en_US.UTF-8']

        # FIXME: Do we need a timeout here in case that the state_changed callback never comes?
        sd.process.spawn(os.path.join(SCRIPT_FOLDER, sd.script_name + self.scripts[sd.script_name].file_ending),
                         sd.params, env, '/', 0, 0, self.devnull, sd.stdout, sd.stderr)
