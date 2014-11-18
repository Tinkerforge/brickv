# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014 Matthias Bolte <matthias@tinkerforge.com>

program_info_c_compile.py: Program C/C++ Compile Info Widget

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

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QDialog
from brickv.plugin_system.plugins.red.ui_program_info_c_compile import Ui_ProgramInfoCCompile
import os
import traceback

class ProgramInfoCCompile(QDialog, Ui_ProgramInfoCCompile):
    def __init__(self, script_manager, program, *args, **kwargs):
        QDialog.__init__(self, *args, **kwargs)

        self.setupUi(self)
        self.setWindowFlags(self.windowFlags() | Qt.Tool)

        self.script_manager = script_manager
        self.program        = program
        self.script_data    = None

        self.rejected.connect(self.cancel_make_execution)
        self.button_make.clicked.connect(lambda: self.execute_make())
        self.button_clean.clicked.connect(lambda: self.execute_make('clean'))
        self.button_cancel.clicked.connect(self.reject)

    def log(self, message):
        self.edit_log.appendPlainText(message)
        self.edit_log.verticalScrollBar().setValue(self.edit_log.verticalScrollBar().maximum())

    def execute_make(self, target=None):
        self.button_make.setEnabled(False)
        self.button_clean.setEnabled(False)

        # FIXME: it would be better to read the output incremental instead of
        #        waiting for make to exit and then display it in a burst
        def cb_make_helper(result):
            self.script_data = None

            if result != None and len(result.stderr) == 0:
                for s in result.stdout.rstrip().split('\n'):
                    self.log(s)

                self.log('...done')
            else:
                if result != None:
                    for s in result.stderr.rstrip().split('\n'):
                        self.log(s)

                self.log('...error')

            self.button_make.setEnabled(True)
            self.button_clean.setEnabled(True)

        if target != None:
            self.log('Executing make {0}...'.format(target))
        else:
            self.log('Executing make...')

        make_options      = self.program.cast_custom_option_value_list('c.options', unicode, [])
        working_directory = os.path.join(unicode(self.program.root_directory), 'bin', unicode(self.program.working_directory))

        if target != None:
            make_options.append(target)

        self.script_data = self.script_manager.execute_script('make_helper', cb_make_helper, [working_directory] + make_options, max_length=1024*1024)

    def cancel_make_execution(self):
        if self.script_data != None:
            try:
                self.script_manager.abort_script(self.script_data)
            except:
                traceback.print_exc()
