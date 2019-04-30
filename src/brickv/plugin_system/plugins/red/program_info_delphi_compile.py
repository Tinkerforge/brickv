# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014-2015, 2017 Matthias Bolte <matthias@tinkerforge.com>

program_info_delphi_compile.py: Program Delphi Compile Info Widget

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

import html
import posixpath

from PyQt5.QtWidgets import QDialog

from brickv.plugin_system.plugins.red.program_utils import *
from brickv.plugin_system.plugins.red.ui_program_info_delphi_compile import Ui_ProgramInfoDelphiCompile
from brickv.plugin_system.plugins.red.script_manager import check_script_result

class ProgramInfoDelphiCompile(QDialog, Ui_ProgramInfoDelphiCompile):
    def __init__(self, parent, script_manager, program):
        QDialog.__init__(self, parent)

        self.setupUi(self)
        self.setModal(True)

        self.script_manager  = script_manager
        self.program         = program
        self.script_instance = None

        self.rejected.connect(self.cancel_script_execution)
        self.button_make.clicked.connect(lambda: self.execute_fpcmake(None))
        self.button_clean.clicked.connect(lambda: self.execute_fpcmake('clean'))
        self.button_compile.clicked.connect(lambda: self.execute_lazbuild([]))
        self.button_recompile_all.clicked.connect(lambda: self.execute_lazbuild(['-B']))
        self.button_cancel.clicked.connect(self.cancel_script_execution)
        self.button_close.clicked.connect(self.reject)

        build_system_api_name = program.cast_custom_option_value('delphi.build_system', str, '<unknown>')
        build_system          = Constants.get_delphi_build_system(build_system_api_name)
        build_system_fpcmake  = build_system == Constants.DELPHI_BUILD_SYSTEM_FPCMAKE
        build_system_lazbuild = build_system == Constants.DELPHI_BUILD_SYSTEM_LAZBUILD

        self.button_make.setVisible(build_system_fpcmake)
        self.button_clean.setVisible(build_system_fpcmake)
        self.button_compile.setVisible(build_system_lazbuild)
        self.button_recompile_all.setVisible(build_system_lazbuild)
        self.button_cancel.setEnabled(False)

    def log(self, message, bold=False, pre=False):
        if bold:
            self.edit_log.appendHtml('<b>{0}</b>'.format(html.escape(message)))
        elif pre:
            self.edit_log.appendHtml('<pre>{0}</pre>'.format(message))
        else:
            self.edit_log.appendPlainText(message)

        self.edit_log.verticalScrollBar().setValue(self.edit_log.verticalScrollBar().maximum())

    def execute_fpcmake(self, target): # target = None for default
        self.button_make.setEnabled(False)
        self.button_clean.setEnabled(False)
        self.button_cancel.setEnabled(True)

        # FIXME: it would be better to read the output incremental instead of
        #        waiting for make to exit and then display it in a burst
        def cb_fpcmake_helper(result):
            self.button_make.setEnabled(True)
            self.button_clean.setEnabled(True)
            self.button_cancel.setEnabled(False)

            aborted = self.script_instance.abort
            self.script_instance = None

            okay, message = check_script_result(result, stderr_is_redirected=True)
            if not okay:
                self.log(message, pre=True)
                self.log('...error' if not aborted else '...canceled', bold=True)
                return

            for s in result.stdout.rstrip().split('\n'):
                self.log(s, pre=True)

            if aborted:
                self.log('...canceled', bold=True)
            elif result.exit_code != 0:
                self.log('...error', bold=True)
            else:
                self.log('...done')

        if target != None:
            self.log('Executing fpcmake and make {0}...'.format(target))
        else:
            self.log('Executing fpcmake and make...')

        make_options      = self.program.cast_custom_option_value_list('delphi.make_options', str, [])
        working_directory = posixpath.join(self.program.root_directory, 'bin', self.program.working_directory)

        if target != None:
            make_options.append(target)

        self.script_instance = self.script_manager.execute_script('fpcmake_helper', cb_fpcmake_helper, [working_directory] + make_options,
                                                                  max_length=1024*1024, redirect_stderr_to_stdout=True,
                                                                  execute_as_user=True)

    def execute_lazbuild(self, additional_options):
        self.button_compile.setEnabled(False)
        self.button_recompile_all.setEnabled(False)
        self.button_cancel.setEnabled(True)

        # FIXME: it would be better to read the output incremental instead of
        #        waiting for make to exit and then display it in a burst
        def cb_lazbuild_helper(result):
            def remove_whitespace(message):
                message_old = message
                message_new = message_old.replace('\n\n\n', '\n')

                while message_old != message_new:
                    message_old = message_new
                    message_new = message_old.replace('\n\n\n', '\n')
                return message_new

            self.button_compile.setEnabled(True)
            self.button_recompile_all.setEnabled(True)
            self.button_cancel.setEnabled(False)

            aborted = self.script_instance.abort
            self.script_instance = None

            okay, message = check_script_result(result, stderr_is_redirected=True)
            if not okay:
                self.log(remove_whitespace(message), pre=True)
                self.log('...error' if not aborted else '...canceled', bold=True)
                return

            for s in remove_whitespace(result.stdout.rstrip()).split('\n'):
                self.log(s, pre=True)

            if aborted:
                self.log('...canceled', bold=True)
            elif result.exit_code != 0:
                self.log('...error', bold=True)
            else:
                self.log('...done')

        if len(additional_options):
            self.log('Executing lazbuild {0}...'.format(' '.join(additional_options)))
        else:
            self.log('Executing lazbuild...')

        lazbuild_options  = self.program.cast_custom_option_value_list('delphi.lazbuild_options', str, []) + additional_options
        working_directory = posixpath.join(self.program.root_directory, 'bin', self.program.working_directory)

        self.script_instance = self.script_manager.execute_script('lazbuild_helper', cb_lazbuild_helper, [working_directory] + lazbuild_options,
                                                                  max_length=1024*1024, redirect_stderr_to_stdout=True,
                                                                  execute_as_user=True)

    def cancel_script_execution(self):
        script_instance = self.script_instance

        if script_instance == None:
            return

        self.button_make.setEnabled(True)
        self.button_clean.setEnabled(True)
        self.button_compile.setEnabled(True)
        self.button_recompile_all.setEnabled(True)
        self.button_cancel.setEnabled(False)

        self.script_manager.abort_script(script_instance)
