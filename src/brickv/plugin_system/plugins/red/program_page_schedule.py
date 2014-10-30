# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014 Matthias Bolte <matthias@tinkerforge.com>

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

from PyQt4.QtCore import QDateTime, QDate, QTime
from brickv.plugin_system.plugins.red.program_page import ProgramPage
from brickv.plugin_system.plugins.red.program_wizard_utils import *
from brickv.plugin_system.plugins.red.ui_program_page_schedule import Ui_ProgramPageSchedule
import os

class ProgramPageSchedule(ProgramPage, Ui_ProgramPageSchedule):
    def __init__(self, title_prefix='', *args, **kwargs):
        ProgramPage.__init__(self, *args, **kwargs)

        self.setupUi(self)

        self.setTitle(title_prefix + 'Schedule')

        self.registerField('start_condition', self.combo_start_condition)
        self.registerField('start_time', self.date_start_time)
        self.registerField('start_delay', self.spin_start_delay)
        self.registerField('repeat_mode', self.combo_repeat_mode)
        self.registerField('repeat_interval', self.spin_repeat_interval)
        self.registerField('repeat_fields', self.edit_repeat_fields)

        self.combo_start_condition.currentIndexChanged.connect(self.update_ui_state)
        self.combo_repeat_mode.currentIndexChanged.connect(self.update_ui_state)
        self.combo_repeat_mode.currentIndexChanged.connect(lambda: self.completeChanged.emit())

        self.edit_repeat_fields_checker = MandatoryLineEditChecker(self, self.edit_repeat_fields, self.label_repeat_fields,
                                                                   '^ *' + ' +'.join(['[a-zA-Z0-9,*/-]+']*5) + ' *$')

    # overrides QWizardPage.initializePage
    def initializePage(self):
        now = QDateTime.currentDateTime().addSecs(5 * 60) # set default start time to 5 minutes from now

        self.set_formatted_sub_title(u'Specify the execution schedule for the {language} program [{name}].')
        self.combo_start_condition.setCurrentIndex(Constants.DEFAULT_START_CONDITION)
        self.date_start_time.setDateTime(now)
        self.combo_repeat_mode.setCurrentIndex(Constants.DEFAULT_REPEAT_MODE)

        # if a program exists then this page is used in an edit wizard
        if self.wizard().program != None:
            program = self.wizard().program

            start_condition = Constants.get_start_condition(program.start_condition)
            repeat_mode     = Constants.get_repeat_mode(program.repeat_mode)

            self.combo_start_condition.setCurrentIndex(start_condition)
            self.date_start_time.setDateTime(QDateTime.fromTime_t(program.start_timestamp))
            self.spin_start_delay.setValue(program.start_delay)
            self.combo_repeat_mode.setCurrentIndex(repeat_mode)
            self.spin_repeat_interval.setValue(program.repeat_interval)

            if program.repeat_mode == REDProgram.REPEAT_MODE_CRON:
                self.edit_repeat_fields.setText(unicode(program.repeat_fields))

        self.update_ui_state()

    # overrides QWizardPage.isComplete
    def isComplete(self):
        repeat_mode = self.get_field('repeat_mode').toInt()[0]

        if repeat_mode == Constants.REPEAT_MODE_CRON and \
           not self.edit_repeat_fields_checker.complete:
                return False

        return ProgramPage.isComplete(self)

    def update_ui_state(self):
        start_condition        = self.get_field('start_condition').toInt()[0]
        start_condition_never  = start_condition == Constants.START_CONDITION_NEVER
        start_condition_now    = start_condition == Constants.START_CONDITION_NOW
        start_condition_reboot = start_condition == Constants.START_CONDITION_REBOOT
        start_condition_time   = start_condition == Constants.START_CONDITION_TIME

        self.label_start_time.setVisible(start_condition_time)
        self.date_start_time.setVisible(start_condition_time)
        self.label_start_delay.setVisible(start_condition_now or start_condition_reboot)
        self.spin_start_delay.setVisible(start_condition_now or start_condition_reboot)
        self.label_start_condition_never_help.setVisible(start_condition_never)
        self.label_start_condition_now_help.setVisible(start_condition_now)
        self.label_start_condition_reboot_help.setVisible(start_condition_reboot)
        self.label_start_condition_time_help.setVisible(start_condition_time)

        repeat_mode          = self.get_field('repeat_mode').toInt()[0]
        repeat_mode_never    = repeat_mode == Constants.REPEAT_MODE_NEVER
        repeat_mode_interval = repeat_mode == Constants.REPEAT_MODE_INTERVAL
        repeat_mode_cron     = repeat_mode == Constants.REPEAT_MODE_CRON

        self.label_repeat_interval.setVisible(repeat_mode_interval)
        self.spin_repeat_interval.setVisible(repeat_mode_interval)
        self.label_repeat_fields.setVisible(repeat_mode_cron)
        self.edit_repeat_fields.setVisible(repeat_mode_cron)
        self.label_repeat_mode_never_help.setVisible(repeat_mode_never)
        self.label_repeat_mode_interval_help.setVisible(repeat_mode_interval)
        self.label_repeat_mode_cron_help.setVisible(repeat_mode_cron)

    def apply_program_changes(self):
        program = self.wizard().program

        if program == None:
            return

        start_condition = Constants.api_start_conditions[self.get_field('start_condition').toInt()[0]]
        start_time      = self.get_field('start_time').toDateTime().toMSecsSinceEpoch() / 1000
        start_delay     = self.get_field('start_delay').toUInt()[0]
        repeat_mode     = Constants.api_repeat_modes[self.get_field('repeat_mode').toInt()[0]]
        repeat_interval = self.get_field('repeat_interval').toInt()[0]
        repeat_fields   = ' '.join(unicode(self.get_field('repeat_fields').toString()).split())

        try:
            program.set_schedule(start_condition, start_time, start_delay,
                                 repeat_mode, repeat_interval, repeat_fields) # FIXME: async_call
        except REDError as e:
            QMessageBox.critical(self, 'Edit Error',
                                 u'Could not update stdio redirection of program [{0}]:\n\n{1}'
                                 .format(program.cast_custom_option_value(Constants.FIELD_NAME, unicode, '<unknown>')))
