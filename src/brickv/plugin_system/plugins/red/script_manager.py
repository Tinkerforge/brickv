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

SCRIPT_FOLDER = '/usr/local/scripts'

class ScriptManager:
    ScriptResult = namedtuple('ReturnValue', 'stdout stderr')
    red = None
    devnull = None
    scripts = None
    
    def __init__(self, red):
        self.red = red
        self.devnull = REDFile(self.red).open('/dev/null', REDFile.FLAG_READ_ONLY, 0, 0, 0)

        from brickv.plugin_system.plugins.red._scripts import scripts
        self.scripts = scripts.copy()
    
    # Call with a script name from the scripts/ folder.
    # The stdout and stderr from the script will be given back to callback.
    # If there is an error, callback will return None.
    def execute_script(self, script_name, callback, params = [], max_len = 10000):
        if not script_name in self.scripts:
            callback(None)
            
        # We just let all exceptions fall through to here and give up.
        # There is nothing we can do anyway.
        try:
            self._init_script(script_name, callback, params, max_len)
        except:
            traceback.print_exc()
            self.scripts[script_name].copied = False
            callback(None)


    def _init_script(self, script_name, callback, params, max_len):
        if self.scripts[script_name].copied:
            return self._execute_after_init(script_name, callback, params, max_len)
        
        red_file = REDFile(self.red).open(os.path.join(SCRIPT_FOLDER, script_name + self.scripts[script_name].file_ending), REDFile.FLAG_WRITE_ONLY | REDFile.FLAG_CREATE | REDFile.FLAG_NON_BLOCKING | REDFile.FLAG_TRUNCATE, 0755, 0, 0)
        red_file.write_async(self.scripts[script_name].script, lambda async_write_error: self._init_script_done(async_write_error, red_file, script_name, callback, params, max_len))

    def _init_script_done(self, async_write_error, red_file, script_name, callback, params, max_len):
        red_file.release()
        
        if async_write_error == None:
            try:
                self.scripts[script_name].stdout = REDPipe(self.red).create(REDPipe.FLAG_NON_BLOCKING_READ)
                self.scripts[script_name].stderr = REDPipe(self.red).create(REDPipe.FLAG_NON_BLOCKING_READ)
            except:
                traceback.print_exc()
                self.scripts[script_name].copied = False
                callback(None)
            else:
                self.scripts[script_name].copied = True
                self._execute_after_init(script_name, callback, params, max_len)
        else:
            print str(async_write_error)
            self.scripts[script_name].copied = False
            callback(None)
            
    def _execute_after_init(self, script_name, callback, params, max_len):
        def state_changed(p):
            # TODO: If we want to support returns > 4kb we need to do more work here,
            #       but it may not be necessary.
            if p.state == REDProcess.STATE_EXITED:
                try:
                    try:
                        out = self.scripts[script_name].stdout.read(max_len)
                    except REDError as e:
                        if e.error_code == REDError.E_WOULD_BLOCK:
                            out = ''
                        else:
                            raise e
                            
                    try:
                        err = self.scripts[script_name].stderr.read(max_len)
                    except REDError as e:
                        if e.error_code == REDError.E_WOULD_BLOCK:
                            err = ''
                        else:
                            raise e
                        
                except REDError:
                    traceback.print_exc()
                    self.scripts[script_name].copied = False
                    callback(None)
                else:
                    callback(self.ScriptResult(out, err))
                finally:
                    red_process.release()
    
                
        red_process = REDProcess(self.red)
        red_process.state_changed_callback = state_changed

        script_params = [os.path.join(SCRIPT_FOLDER, script_name + self.scripts[script_name].file_ending)]
        script_params.extend(params)

        # FIXME: Do we need a timeout here in case that the state_changed callback never comes?
        red_process.spawn(os.path.join(SCRIPT_FOLDER, script_name + self.scripts[script_name].file_ending), params, [], '/', 0, 0, self.devnull, self.scripts[script_name].stdout, self.scripts[script_name].stderr)