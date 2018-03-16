# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2014-2015, 2017 Matthias Bolte <matthias@tinkerforge.com>

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

import posixpath
from collections import namedtuple
from threading import Lock

from PyQt4.QtCore import QObject, pyqtSignal
from PyQt4.QtGui import QMessageBox

from brickv.plugin_system.plugins.red.api import REDFile, REDPipe, REDProcess
from brickv.async_call import async_call
from brickv.object_creator import create_object_in_qt_main_thread
from brickv.plugin_system.plugins.red.script_data import script_data
from brickv.utils import get_main_window

SCRIPT_FOLDER = '/usr/local/scripts'

script_instances = set()

class Script(object):
    def __init__(self, name, extension, content):
        self.name        = name
        self.extension   = extension
        self.content     = content
        self.uploaded    = False
        self.upload_lock = Lock()
        self.red_file    = None

class ScriptInstance(QObject):
    qtcb_result = pyqtSignal(object)

    def __init__(self):
        QObject.__init__(self)

        self.name                      = None
        self.script                    = None
        self.process                   = None
        self.stdout                    = None
        self.stderr                    = None
        self.result_callback           = None
        self.params                    = None
        self.max_length                = None
        self.decode_output_as_utf8     = True
        self.redirect_stderr_to_stdout = False
        self.abort                     = False
        self.execute_as_user           = False

    def release(self):
        if self.process != None:
            try:
                self.process.release()
            except:
                pass

            self.process = None

        if self.stdout != None:
            try:
                self.stdout.release()
            except:
                pass

            self.stdout = None

        if self.stderr != None and not self.redirect_stderr_to_stdout:
            try:
                self.stderr.release()
            except:
                pass

            self.stderr = None

    def report_result(self, result):
        # if result is None then the and error during script upload
        # occurred and the upload has to be done again
        if result == None:
            self.script.uploaded = False

        self.qtcb_result.emit(result)
        self.qtcb_result.disconnect(self.result_callback)

# stdout and stderr are either strings or None (UTF-8 decode error)
ScriptResult = namedtuple('ScriptResult', 'error stdout stderr exit_code')

class ScriptManager(object):
    def __init__(self, session):
        self.session = session
        self.devnull = REDFile(self.session).open('/dev/null', REDFile.FLAG_READ_ONLY, 0, 0, 0) # FIXME: This is blocking the GUI!
        self.scripts = {}

        for sd in script_data:
            name, extension, content = sd
            self.scripts[name] = Script(name, extension, content)

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
                result_callback(ScriptResult('Script "{0}" is unknown'.format(script_name), None, None, None)) # We are still in GUI thread, use result_callback instead of signal
                return

        if params == None:
            params = []

        si                           = ScriptInstance()
        si.name                      = script_name
        si.script                    = self.scripts[script_name]
        si.result_callback           = result_callback
        si.params                    = params
        si.max_length                = max_length
        si.decode_output_as_utf8     = decode_output_as_utf8
        si.redirect_stderr_to_stdout = redirect_stderr_to_stdout
        si.execute_as_user           = execute_as_user

        script_instances.add(si)

        if si.result_callback != None:
            si.qtcb_result.connect(si.result_callback)

        # We just let all exceptions fall through to here and give up.
        # There is nothing we can do anyway.
        try:
            self._init_script(si)
            return si
        except Exception as e:
            if si.result_callback != None:
                si.qtcb_result.disconnect(si.result_callback)

            si.script.uploaded = False

            if si.result_callback != None:
                si.result_callback(ScriptResult('Could not initialize script "{0}": {1}'.format(si.name, e), None, None, None)) # We are still in GUI thread, use result_callback instead of signal

            script_instances.remove(si)

        return None

    def abort_script(self, si):
        if si.abort:
            return

        si.abort = True

        if si.process != None:
            try:
                si.process.kill(REDProcess.SIGNAL_KILL)
            except:
                pass

    def _init_script(self, si):
        if si.script.uploaded:
            return self._execute_after_init(si)

        def cb_success(execute):
            if execute:
                self._execute_after_init(si)

        def cb_error(exception):
            si.report_result(ScriptResult('Could not async-initialize script "{0}": {1}'.format(si.name, exception), None, None, None))
            script_instances.remove(si)

        async_call(self._init_script_async, si, cb_success, cb_error, report_exception=True)

    def _init_script_async(self, si):
        si.script.upload_lock.acquire()

        # recheck the uploaded flag, maybe someone else managed to upload
        # the script in the meantime. if not it's our turn to upload it
        if si.script.uploaded:
            si.script.upload_lock.release()
            return True

        try:
            si.script.red_file = create_object_in_qt_main_thread(REDFile, (self.session,))
            si.script.red_file.open(posixpath.join(SCRIPT_FOLDER, si.script.name + si.script.extension),
                                    REDFile.FLAG_WRITE_ONLY | REDFile.FLAG_CREATE | REDFile.FLAG_NON_BLOCKING | REDFile.FLAG_TRUNCATE, 0o755, 0, 0)
            si.script.red_file.write_async(si.script.content, lambda error: self._init_script_async_write_done(error, si))
            return False
        except:
            try:
                si.script.upload_lock.release()
            except:
                pass

            raise

    def _init_script_async_write_done(self, error, si):
        si.script.red_file.release()
        si.script.red_file = None
        si.script.uploaded = True
        si.script.upload_lock.release()

        if error == None:
            self._execute_after_init(si)
        else:
            si.report_result(ScriptResult('Could not async-write script "{0}": {1}'.format(si.name, error), None, None, None))
            script_instances.remove(si)

    def _report_result_and_cleanup(self, si, result):
        si.release()
        si.report_result(result)
        script_instances.remove(si)

    def _execute_after_init(self, si):
        if si.abort:
            self._report_result_and_cleanup(si, ScriptResult('Script "{0}" aborted'.format(si.name), None, None, None))
            return

        try:
            si.stdout = REDPipe(self.session).create(REDPipe.FLAG_NON_BLOCKING_READ, si.max_length)

            if si.redirect_stderr_to_stdout:
                si.stderr = si.stdout
            else:
                si.stderr = REDPipe(self.session).create(REDPipe.FLAG_NON_BLOCKING_READ, si.max_length)
        except Exception as e:
            self._report_result_and_cleanup(si, ScriptResult('Could not create pipes for script "{0}": {1}'.format(si.name, e), None, None, None))
            return

        # NOTE: this function will be called on the UI thread
        def cb_process_state_changed(si):
            # TODO: If we want to support returns > 1MB we need to do more work here,
            #       but it may not be necessary.
            if si.abort:
                self._report_result_and_cleanup(si, ScriptResult('Script "{0}" aborted'.format(si.name), None, None, None))
            elif si.process.state == REDProcess.STATE_RUNNING:
                pass # still running ignore it
            elif si.process.state != REDProcess.STATE_EXITED:
                self._report_result_and_cleanup(si, ScriptResult('Script "{0}" in wrong state: {1} (exit-code {2})'
                                                                 .format(si.name, si.process.state, si.process.exit_code), None, None, None))
            else:
                def cb_stdout_read(result):
                    if result.error != None:
                        self._report_result_and_cleanup(si, ScriptResult('Could not read stdout for script "{0}": {1}'.format(si.name, result.error), None, None, None))
                        return

                    if si.decode_output_as_utf8:
                        try:
                            out = result.data.decode('utf-8')
                        except UnicodeDecodeError:
                            out = None
                    else:
                        out = result.data

                    if si.redirect_stderr_to_stdout:
                        exit_code = si.process.exit_code

                        self._report_result_and_cleanup(si, ScriptResult(None, out, u'', exit_code))
                    else:
                        def cb_stderr_read(result):
                            if result.error != None:
                                self._report_result_and_cleanup(si, ScriptResult('Could not read stderr for script "{0}": {1}'.format(si.name, result.error), None, None, None))
                                return

                            if si.decode_output_as_utf8:
                                try:
                                    err = result.data.decode('utf-8')
                                except UnicodeDecodeError:
                                    err = None
                            else:
                                err = result.data

                            exit_code = si.process.exit_code

                            self._report_result_and_cleanup(si, ScriptResult(None, out, err, exit_code))

                        si.stderr.read_async(si.max_length, cb_stderr_read)

                si.stdout.read_async(si.max_length, cb_stdout_read)

        si.process                        = REDProcess(self.session)
        si.process.state_changed_callback = lambda x: cb_process_state_changed(si)

        # FIXME: do incremental reads on the output
        """
        # NOTE: this function will be called on the UI thread
        def cb_stdout_events_occurred(si):
            print 'cb_stdout_events_occurred', si.script.name

        # NOTE: this function will be called on the UI thread
        def cb_stderr_events_occurred(si):
            print 'cb_stderr_events_occurred', si.script.name

        si.stdout.events_occurred_callback = lambda x: cb_stdout_events_occurred(si)
        si.stderr.events_occurred_callback = lambda x: cb_stderr_events_occurred(si)

        try:
            si.stdout.set_events(REDFile.EVENT_READABLE)
        except:
            pass

        try:
            si.stderr.set_events(REDFile.EVENT_READABLE)
        except:
            pass
        """

        # need to set LANG otherwise python will not correctly handle non-ASCII filenames
        # also set a sensible PATH so scripts can find basic command without an absolute path
        env = ['LANG=en_US.UTF-8', 'PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin']

        if si.execute_as_user:
            uid = 1000
            gid = 1000
        else:
            uid = 0
            gid = 0

        try:
            # FIXME: Do we need a timeout here in case that the state_changed callback never comes?
            si.process.spawn(posixpath.join(SCRIPT_FOLDER, si.script.name + si.script.extension),
                             si.params, env, '/', uid, gid, self.devnull, si.stdout, si.stderr)
        except Exception as e:
            self._report_result_and_cleanup(si, ScriptResult('Could not execute script "{0}": {1}'.format(si.name, e), None, None, None))

def check_script_result(result, decode_stderr=False):
    if result == None:
        return (False, u'Script error 1001: Unexpected internal error')
    elif result.error != None:
        return (False, u'Script error 100X: {0}'.format(result.error))
    elif result.stdout == None:
        return (False, u'Script error 1002: Stdout not UTF-8 encoded')
    elif result.stderr == None:
        return (False, u'Script error 1003: Stderr not UTF-8 encoded')
    elif result.exit_code != 0:
        if decode_stderr:
            try:
                stderr = result.stderr.decode('utf-8').strip()
            except UnicodeDecodeError:
                stderr = u'<error message not UTF-8 encoded>'
        else:
            stderr = result.stderr.strip()

        if len(stderr) == 0:
            stderr = u'<empty error message>'

        return (False, u'Script error {0}: {1}'.format(result.exit_code, stderr))
    else:
        return (True, None)

def report_script_result(result, title, message_header, decode_stderr=False, before_message_box=None):
    okay, message = check_script_result(result, decode_stderr)

    if okay:
        return True

    if before_message_box != None:
        before_message_box()

    QMessageBox.critical(get_main_window(), title, message_header + u':\n\n' + message)
    return False
