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
import posixpath
from collections import namedtuple
from PyQt4 import QtCore

from brickv.async_call import async_call
from brickv.object_creator import create_object_in_qt_main_thread

SCRIPT_FOLDER = '/usr/local/scripts'

script_data_set = set()

class ScriptData(QtCore.QObject):
    qtcb_result = QtCore.pyqtSignal(object)

    def __init__(self):
        QtCore.QObject.__init__(self)

        self.process                   = None
        self.stdout                    = None
        self.stderr                    = None
        self.script_name               = None
        self.result_callback           = None
        self.params                    = None
        self.max_length                = None
        self.decode_output_as_utf8     = True
        self.redirect_stderr_to_stdout = False
        self.script_instance           = None
        self.abort                     = False
        self.execute_as_user           = False

class ScriptManager:
    ScriptResult = namedtuple('ScriptResult', 'stdout stderr exit_code')

    @staticmethod
    def _call(script, sd, data):
        if data == None:
            script.copied = False

        sd.qtcb_result.emit(data)
        sd.qtcb_result.disconnect(sd.result_callback)

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
    # The stdout and stderr from the script will be given back to result_callback.
    # If there is an error, result_callback will report None.
    def execute_script(self, script_name, result_callback, params=None, max_length=65536,
                       decode_output_as_utf8=True, redirect_stderr_to_stdout=False,
                       execute_as_user=False):
        if not script_name in self.scripts:
            if result_callback != None:
                result_callback(None) # We are still in GUI thread, use result_callback instead of signal
                return

        if params == None:
            params = []

        sd                           = ScriptData()
        sd.script_name               = script_name
        sd.result_callback           = result_callback
        sd.params                    = params
        sd.max_length                = max_length
        sd.decode_output_as_utf8     = decode_output_as_utf8
        sd.redirect_stderr_to_stdout = redirect_stderr_to_stdout
        sd.execute_as_user           = execute_as_user

        script_data_set.add(sd)

        if sd.result_callback != None:
            sd.qtcb_result.connect(sd.result_callback)

        # We just let all exceptions fall through to here and give up.
        # There is nothing we can do anyway.
        try:
            self._init_script(sd)
            return sd
        except:
            print 'ScriptManager.execute_script: _init_script failed'
            traceback.print_exc()

            if sd.result_callback != None:
                sd.qtcb_result.disconnect(sd.result_callback)

            self.scripts[sd.script_name].copied = False

            if sd.result_callback != None:
                sd.result_callback(None) # We are still in GUI thread, use result_callback instead of signal

            script_data_set.remove(sd)

        return None

    def abort_script(self, sd):
        if sd.abort:
            return

        sd.abort = True

        if sd.process != None:
            try:
                sd.process.kill(REDProcess.SIGNAL_KILL)
            except:
                print 'ScriptManager.abort_script: sd.process.kill failed'
                traceback.print_exc()

    def _init_script(self, sd):
        if self.scripts[sd.script_name].copied:
            return self._execute_after_init(sd)

        async_call(self._init_script_async, sd, lambda execute: self._init_script_done(execute, sd), lambda: self._init_script_error(sd))

    def _init_script_async(self, sd):
        script = self.scripts[sd.script_name]

        script.copy_lock.acquire()

        # recheck the copied flag, maybe someone else managed to
        # copy the script in the meantime. if not it's our turn to copy it
        if script.copied:
            script.copy_lock.release()
            return True

        try:
            script.file = create_object_in_qt_main_thread(REDFile, (self.session,))
            script.file.open(posixpath.join(SCRIPT_FOLDER, sd.script_name + script.file_ending),
                             REDFile.FLAG_WRITE_ONLY | REDFile.FLAG_CREATE | REDFile.FLAG_NON_BLOCKING | REDFile.FLAG_TRUNCATE, 0755, 0, 0)
            script.file.write_async(script.script, lambda error: self._init_script_async_write_done(error, sd))
        except:
            try:
                self.scripts[sd.script_name].copy_lock.release()
            except:
                pass

            print 'ScriptManager._init_script_async: copy_lock.release failed'
            traceback.print_exc()
            raise
        finally:
            return False

    def _init_script_async_write_done(self, error, sd):
        script = self.scripts[sd.script_name]

        script.file.release()
        script.file = None
        script.copied = True
        script.copy_lock.release()

        if error == None:
            self._execute_after_init(sd)
        else:
            print 'ScriptManager._init_script_async_write_done', unicode(error)
            ScriptManager._call(script, sd, None)
            script_data_set.remove(sd)

    def _init_script_done(self, execute, sd):
        if execute:
            self._execute_after_init(sd)

    def _init_script_error(self, sd):
        ScriptManager._call(self.scripts[sd.script_name], sd, None)
        script_data_set.remove(sd)

    def _release_script_data(self, sd):
        try:
            sd.process.release()
            sd.stdout.release()

            if not sd.redirect_stderr_to_stdout:
                sd.stderr.release()
        except:
            print 'ScriptManager._release_script_data: release failed'
            traceback.print_exc()

        sd.process = None
        sd.stdout  = None
        sd.stderr  = None

    def _execute_after_init(self, sd):
        if sd.abort:
            ScriptManager._call(self.scripts[sd.script_name], sd, None)
            script_data_set.remove(sd)
            return

        try:
            sd.stdout = REDPipe(self.session).create(REDPipe.FLAG_NON_BLOCKING_READ, sd.max_length)

            if sd.redirect_stderr_to_stdout:
                sd.stderr = sd.stdout
            else:
                sd.stderr = REDPipe(self.session).create(REDPipe.FLAG_NON_BLOCKING_READ, sd.max_length)
        except:
            print 'ScriptManager._execute_after_init: REDPipe.create failed'
            traceback.print_exc()

            ScriptManager._call(self.scripts[sd.script_name], sd, None)
            script_data_set.remove(sd)
            return

        # NOTE: this function will be called on the UI thread
        def cb_process_state_changed(sd):
            # TODO: If we want to support returns > 1MB we need to do more work here,
            #       but it may not be necessary.
            if not sd.abort and sd.process.state == REDProcess.STATE_EXITED:
                def cb_stdout_read(result, sd):
                    if result.error != None:
                        self._release_script_data(sd)
                        ScriptManager._call(self.scripts[sd.script_name], sd, None)
                        script_data_set.remove(sd)
                        return

                    if sd.decode_output_as_utf8:
                        out = result.data.decode('utf-8') # NOTE: assuming scripts return UTF-8
                    else:
                        out = result.data

                    if sd.redirect_stderr_to_stdout:
                        exit_code = sd.process.exit_code

                        self._release_script_data(sd)
                        ScriptManager._call(self.scripts[sd.script_name], sd, self.ScriptResult(out, None, exit_code))
                        script_data_set.remove(sd)
                    else:
                        def cb_stderr_read(result, sd):
                            if result.error != None:
                                self._release_script_data(sd)
                                ScriptManager._call(self.scripts[sd.script_name], sd, None)
                                script_data_set.remove(sd)
                                return

                            if sd.decode_output_as_utf8:
                                err = result.data.decode('utf-8') # NOTE: assuming scripts return UTF-8
                            else:
                                err = result.data

                            exit_code = sd.process.exit_code

                            self._release_script_data(sd)
                            ScriptManager._call(self.scripts[sd.script_name], sd, self.ScriptResult(out, err, exit_code))
                            script_data_set.remove(sd)

                        sd.stderr.read_async(sd.max_length, lambda result: cb_stderr_read(result, sd))

                sd.stdout.read_async(sd.max_length, lambda result: cb_stdout_read(result, sd))
            else:
                self._release_script_data(sd)
                ScriptManager._call(self.scripts[sd.script_name], sd, None)
                script_data_set.remove(sd)

        sd.process                        = REDProcess(self.session)
        sd.process.state_changed_callback = lambda x: cb_process_state_changed(sd)

        # FIXME: do incremental reads on the output
        """
        # NOTE: this function will be called on the UI thread
        def cb_stdout_events_occurred(sd):
            print 'cb_stdout_events_occurred', sd.script_name

        # NOTE: this function will be called on the UI thread
        def cb_stderr_events_occurred(sd):
            print 'cb_stderr_events_occurred', sd.script_name

        sd.stdout.events_occurred_callback = lambda x: cb_stdout_events_occurred(sd)
        sd.stderr.events_occurred_callback = lambda x: cb_stderr_events_occurred(sd)

        try:
            sd.stdout.set_events(REDFile.EVENT_READABLE)
        except:
            print 'ScriptManager._execute_after_init: sd.stdout.set_events failed'
            traceback.print_exc() # ignore error

        try:
            sd.stderr.set_events(REDFile.EVENT_READABLE)
        except:
            print 'ScriptManager._execute_after_init: sd.stderr.set_events failed'
            traceback.print_exc() # ignore error
        """

        # need to set LANG otherwise python will not correctly handle non-ASCII filenames
        env = ['LANG=en_US.UTF-8']

        if sd.execute_as_user:
            uid = 1000
            gid = 1000
        else:
            uid = 0
            gid = 0

        try:
            # FIXME: Do we need a timeout here in case that the state_changed callback never comes?
            sd.process.spawn(posixpath.join(SCRIPT_FOLDER, sd.script_name + self.scripts[sd.script_name].file_ending),
                             sd.params, env, '/', uid, gid, self.devnull, sd.stdout, sd.stderr)
        except:
            print 'ScriptManager._execute_after_init: sd.process.spawn failed'
            traceback.print_exc()

            self._release_script_data(sd)
            ScriptManager._call(self.scripts[sd.script_name], sd, None)
            script_data_set.remove(sd)
