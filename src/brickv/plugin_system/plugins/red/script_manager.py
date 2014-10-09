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
from brickv.plugin_system.plugins.red._scripts import scripts

import traceback
import os

from collections import namedtuple

SCRIPT_FOLDER = '/usr/local/scripts'

class ScriptManager:
    ScriptResult = namedtuple('ReturnValue', 'stdout stderr')
    red = None
    devnull = None
    
    # Call with a script name from the scripts/ folder.
    # The stdout and stderr from the script will be given back to callback.
    # If there is an error, callback will return None.
    @staticmethod
    def execute_script(script_name, callback, params = [], max_len = 10000):
        if not script_name in scripts:
            callback(None)
            
        # We just let all exceptions fall through to here and give up.
        # There is nothing we can do anyway.
        try:
            ScriptManager._init_script(script_name, callback, params, max_len)
        except:
            traceback.print_exc()
            scripts[script_name].copied = False
            callback(None)


    @staticmethod
    def _init_script(script_name, callback, params, max_len):
        if scripts[script_name].copied:
            return ScriptManager._execute_after_init(script_name, callback, params, max_len)
        
        red_file = REDFile(ScriptManager.red).open(os.path.join(SCRIPT_FOLDER, script_name + '.py'), REDFile.FLAG_WRITE_ONLY | REDFile.FLAG_CREATE | REDFile.FLAG_NON_BLOCKING | REDFile.FLAG_TRUNCATE, 0755, 0, 0)
        red_file.write_async(scripts[script_name].script, lambda async_write_error: ScriptManager._init_script_done(async_write_error, red_file, script_name, callback, params, max_len))

    @staticmethod
    def _init_script_done(async_write_error, red_file, script_name, callback, params, max_len):
        red_file.release()
        
        if async_write_error == None:
            try:
                scripts[script_name].stdout = REDPipe(ScriptManager.red).create(REDPipe.FLAG_NON_BLOCKING_READ)
                scripts[script_name].stderr = REDPipe(ScriptManager.red).create(REDPipe.FLAG_NON_BLOCKING_READ)
            except:
                traceback.print_exc()
                scripts[script_name].copied = False
                callback(None)
            else:
                scripts[script_name].copied = True
                ScriptManager._execute_after_init(script_name, callback, params, max_len)
        else:
            print str(async_write_error)
            scripts[script_name].copied = False
            callback(None)
            
    @staticmethod
    def _execute_after_init(script_name, callback, params, max_len):
        if ScriptManager.devnull == None:
            ScriptManager.devnull = REDFile(ScriptManager.red).open('/dev/null', REDFile.FLAG_READ_ONLY, 0, 0, 0)
            
        def state_changed(p):
            # TODO: If we want to support returns > 4kb we need to do more work here,
            #       but it may not be necessary.
            if p.state == REDProcess.STATE_EXITED:
                try:
                    try:
                        out = scripts[script_name].stdout.read(max_len)
                    except REDError as e:
                        if e.error_code == REDError.E_WOULD_BLOCK:
                            out = ''
                        else:
                            raise e
                            
                    try:
                        err = scripts[script_name].stderr.read(max_len)
                    except REDError as e:
                        if e.error_code == REDError.E_WOULD_BLOCK:
                            err = ''
                        else:
                            raise e
                        
                except REDError:
                    traceback.print_exc()
                    scripts[script_name].copied = False
                    callback(None)
                else:
                    callback(ScriptManager.ScriptResult(out, err))
                finally:
                    red_process.release()
    
                
        red_process = REDProcess(ScriptManager.red)
        red_process.state_changed_callback = state_changed

        script_params = [os.path.join(SCRIPT_FOLDER, script_name + '.py')]
        script_params.extend(params)

        # FIXME: Do we need a timeout here in case that the state_changed callback never comes?
        red_process.spawn('/usr/bin/python', script_params, [], '/', 0, 0, ScriptManager.devnull, scripts[script_name].stdout, scripts[script_name].stderr)