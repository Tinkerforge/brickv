# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014-2015 Matthias Bolte <matthias@tinkerforge.com>

program_page_schedule.py: Program Wizard Schedule Page

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

from PyQt5.QtWidgets import QMessageBox

from brickv.plugin_system.plugins.red.api import *
from brickv.plugin_system.plugins.red.program_page import ProgramPage
from brickv.plugin_system.plugins.red.program_utils import *
from brickv.plugin_system.plugins.red.ui_program_page_schedule import Ui_ProgramPageSchedule
from brickv.utils import get_main_window

class ProgramPageSchedule(ProgramPage, Ui_ProgramPageSchedule):
    def __init__(self, title_prefix=''):
        ProgramPage.__init__(self)

        self.setupUi(self)

        self.interval_help_template = self.label_start_mode_interval_help.text()

        self.setTitle(title_prefix + 'Schedule')

        self.registerField('start_mode', self.combo_start_mode)
        self.registerField('continue_after_error', self.check_continue_after_error)
        self.registerField('start_interval', self.spin_start_interval)
        self.registerField('start_fields', self.edit_start_fields)

        self.combo_start_mode.currentIndexChanged.connect(self.update_ui_state)
        self.spin_start_interval.valueChanged.connect(self.update_interval_help)

        self.edit_start_fields_checker = MandatoryLineEditChecker(self, self.label_start_fields, self.edit_start_fields,
                                                                  r'^ *(@\S+|\S+ +\S+ +\S+ +\S+ +\S+) *$')

    # overrides QWizardPage.initializePage
    def initializePage(self):
        self.set_formatted_sub_title('Specify when the {language} program [{name}] should be executed.')
        self.combo_start_mode.setCurrentIndex(Constants.DEFAULT_START_MODE)

        # if a program exists then this page is used in an edit wizard
        program = self.wizard().program

        if program != None:
            self.combo_start_mode.setCurrentIndex(Constants.get_start_mode(program.start_mode))
            self.check_continue_after_error.setChecked(program.continue_after_error)
            self.spin_start_interval.setValue(program.start_interval)

            if program.start_mode == REDProgram.START_MODE_CRON:
                self.edit_start_fields.setText(program.start_fields)
        elif self.combo_start_mode.count() <= Constants.START_MODE_SEPARATOR:
            self.combo_start_mode.insertSeparator(Constants.START_MODE_SEPARATOR)
            self.combo_start_mode.insertItem(Constants.START_MODE_ONCE, 'Once After Upload')

        self.update_ui_state()
        self.update_interval_help()

    # overrides QWizardPage.isComplete
    def isComplete(self):
        start_mode = self.get_field('start_mode')

        if start_mode == Constants.START_MODE_CRON and \
           not self.edit_start_fields_checker.complete:
            return False

        return ProgramPage.isComplete(self)

    # overrides ProgramPage.update_ui_state
    def update_ui_state(self):
        start_mode          = self.get_field('start_mode')
        start_mode_never    = start_mode == Constants.START_MODE_NEVER
        start_mode_always   = start_mode == Constants.START_MODE_ALWAYS
        start_mode_interval = start_mode == Constants.START_MODE_INTERVAL
        start_mode_cron     = start_mode == Constants.START_MODE_CRON
        start_mode_once     = start_mode == Constants.START_MODE_ONCE

        self.label_start_interval.setVisible(start_mode_interval)
        self.spin_start_interval.setVisible(start_mode_interval)
        self.label_start_fields.setVisible(start_mode_cron)
        self.edit_start_fields.setVisible(start_mode_cron)
        self.label_start_mode_never_help.setVisible(start_mode_never)
        self.label_start_mode_always_help.setVisible(start_mode_always)
        self.label_start_mode_interval_help.setVisible(start_mode_interval)
        self.label_start_mode_cron_help.setVisible(start_mode_cron)
        self.label_start_mode_once_help.setVisible(start_mode_once)
        self.line.setVisible(not start_mode_never and not start_mode_once)
        self.check_continue_after_error.setVisible(not start_mode_never and not start_mode_once)
        self.label_continue_after_error_help.setVisible(not start_mode_never and not start_mode_once)

    def update_interval_help(self):
        text = self.interval_help_template.replace('<INTERVAL>', str(self.spin_start_interval.value()))
        self.label_start_mode_interval_help.setText(text)

    def apply_program_changes(self):
        program = self.wizard().program

        if program == None:
            return

        start_mode           = Constants.api_start_modes[self.get_field('start_mode')]
        continue_after_error = self.get_field('continue_after_error')
        start_interval       = self.get_field('start_interval')
        start_fields         = self.get_field('start_fields')

        try:
            program.set_schedule(start_mode, continue_after_error, start_interval, start_fields) # FIXME: async_call
        except (Error, REDError) as e:
            QMessageBox.critical(get_main_window(), 'Edit Program Error',
                                 'Could not update stdio redirection of program [{0}]:\n\n{1}'
                                 .format(program.cast_custom_option_value('name', str, '<unknown>'), e))
            return

        try:
            program.set_custom_option_value('started_once_after_upload', False) # FIXME: async_call
        except (Error, REDError) as e:
            QMessageBox.critical(get_main_window(), 'Edit Program Error',
                                 'Could not update custom options of program [{0}]:\n\n{1}'
                                 .format(program.cast_custom_option_value('name', str, '<unknown>'), e))
            return

        self.set_last_edit_timestamp()
