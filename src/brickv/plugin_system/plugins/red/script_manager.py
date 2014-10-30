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

from brickv.plugin_system.plugins.red.api import REDFile, REDPipe, REDError, REDProcess

import traceback
import os

from collections import namedtuple

from brickv.async_call import async_call

SCRIPT_FOLDER = '/usr/local/scripts'

class ScriptManager:
    ScriptResult = namedtuple('ReturnValue', 'stdout stderr')

    @staticmethod
    def _call(script, callback, data):
        script.is_executing = False
        if data == None:
            script.copied = False

        script.script_signal.emit(data)
        script.script_signal.disconnect(callback)

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
    def execute_script(self, script_name, callback, params = [], max_len = 65536):
        if not script_name in self.scripts:
            if callback is not None:
                callback(None) # We are still in GUI thread, use callback instead of signal

        # The script is currently being executed, this should be the only case
        # were we don't call the callback
        if self.scripts[script_name].is_executing:
            return

        if callback is not None:
            self.scripts[script_name].script_signal.connect(callback)

        # We just let all exceptions fall through to here and give up.
        # There is nothing we can do anyway.
        try:
            self.scripts[script_name].is_executing = True
            self._init_script(script_name, callback, params, max_len)
        except:
            traceback.print_exc()
            if callback is not None:
                self.scripts[script_name].script_signal.disconnect(callback)
            self.scripts[script_name].copied = False
            self.scripts[script_name].is_executing = False
            if callback is not None:
                callback(None) # We are still in GUI thread, use callback instead of signal

    def _init_script(self, script_name, callback, params, max_len):
        if self.scripts[script_name].copied:
            return self._execute_after_init(script_name, callback, params, max_len)

        self.scripts[script_name].file = REDFile(self.session)
        async_call(self.scripts[script_name].file.open,
                   (os.path.join(SCRIPT_FOLDER, script_name + self.scripts[script_name].file_ending),
                    REDFile.FLAG_WRITE_ONLY | REDFile.FLAG_CREATE | REDFile.FLAG_NON_BLOCKING | REDFile.FLAG_TRUNCATE, 0755, 0, 0),
                   lambda x: self._init_script_open_file(script_name, callback, params, max_len, x),
                   lambda: self._init_script_open_file_error(script_name, callback, params, max_len))

    def _init_script_open_file_error(self, script_name, callback, params, max_len):
        ScriptManager._call(self.scripts[script_name], callback, None)

    def _init_script_open_file(self, script_name, callback, params, max_len, red_file):
        self.scripts[script_name].file.write_async(self.scripts[script_name].script,
                                                   lambda async_write_error: self._init_script_done(async_write_error, script_name, callback, params, max_len))

    def _init_script_done(self, async_write_error, script_name, callback, params, max_len):
        self.scripts[script_name].file.release()

        if async_write_error == None:
            try:
                self.scripts[script_name].stdout = REDPipe(self.session).create(REDPipe.FLAG_NON_BLOCKING_READ, 1024*1024)
                self.scripts[script_name].stderr = REDPipe(self.session).create(REDPipe.FLAG_NON_BLOCKING_READ, 1024*1024)
            except:
                traceback.print_exc()
                ScriptManager._call(self.scripts[script_name], callback, None)
            else:
                self._execute_after_init(script_name, callback, params, max_len)
        else:
            print str(async_write_error)
            ScriptManager._call(self.scripts[script_name], callback, None)

    def _execute_after_init(self, script_name, callback, params, max_len):
        def state_changed(red_process):
            # TODO: If we want to support returns > 1MB we need to do more work here,
            #       but it may not be necessary.
            if red_process.state == REDProcess.STATE_ERROR:
                ScriptManager._call(self.scripts[script_name], callback, None)
                try:
                    self.scripts[script_name].process.release()
                    self.scripts[script_name].stdout.release()
                    self.scripts[script_name].stderr.release()
                except:
                    traceback.print_exc()
            elif red_process.state == REDProcess.STATE_EXITED:
                def cb_stdout_data(result):
                    if result.error != None:
                        ScriptManager._call(self.scripts[script_name], callback, None)

                        try:
                            self.scripts[script_name].process.release()
                            self.scripts[script_name].stdout.release()
                            self.scripts[script_name].stderr.release()
                        except:
                            traceback.print_exc()

                    out = result.data.decode('utf-8') # NOTE: assuming scripts return UTF-8

                    def cb_stderr_data(result):
                        if result.error != None:
                            ScriptManager._call(self.scripts[script_name], callback, None)

                        try:
                            self.scripts[script_name].process.release()
                            self.scripts[script_name].stdout.release()
                            self.scripts[script_name].stderr.release()
                        except:
                            traceback.print_exc()

                        err = result.data.decode('utf-8') # NOTE: assuming scripts return UTF-8

                        ScriptManager._call(self.scripts[script_name], callback, self.ScriptResult(out, err))

                    self.scripts[script_name].stderr.read_async(max_len, cb_stderr_data)

                self.scripts[script_name].stdout.read_async(max_len, cb_stdout_data)

        self.scripts[script_name].process = REDProcess(self.session)
        self.scripts[script_name].process.state_changed_callback = state_changed

        # FIXME: Do we need a timeout here in case that the state_changed callback never comes?
        self.scripts[script_name].process.spawn(os.path.join(SCRIPT_FOLDER, script_name + self.scripts[script_name].file_ending),
                                                params, [], '/', 0, 0, self.devnull, self.scripts[script_name].stdout, self.scripts[script_name].stderr)
