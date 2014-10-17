# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014 Matthias Bolte <matthias@tinkerforge.com>

new_program_schedule.py: New Program Wizard Schedule Page

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
from PyQt4.QtGui import QWizardPage
from brickv.plugin_system.plugins.red.new_program_constants import Constants
from brickv.plugin_system.plugins.red.ui_new_program_schedule import Ui_NewProgramSchedule
import os

class NewProgramSchedule(QWizardPage, Ui_NewProgramSchedule):
    def __init__(self, *args, **kwargs):
        QWizardPage.__init__(self, *args, **kwargs)

        self.setupUi(self)

        self.setTitle('Schedule')

        self.registerField('schedule.start_condition', self.combo_start_condition)
        self.registerField('schedule.start_time', self.date_start_time)
        self.registerField('schedule.start_delay', self.spin_start_delay)
        self.registerField('schedule.repeat_mode', self.combo_repeat_mode)
        self.registerField('schedule.repeat_interval', self.spin_repeat_interval)
        self.registerField('schedule.repeat_seconds', self.edit_repeat_seconds)
        self.registerField('schedule.repeat_minutes', self.edit_repeat_minutes)
        self.registerField('schedule.repeat_hours', self.edit_repeat_hours)
        self.registerField('schedule.repeat_days', self.edit_repeat_days)
        self.registerField('schedule.repeat_months', self.edit_repeat_months)
        self.registerField('schedule.repeat_weekdays', self.edit_repeat_weekdays)

        self.combo_start_condition.currentIndexChanged.connect(self.update_ui_state)
        self.combo_repeat_mode.currentIndexChanged.connect(self.update_ui_state)

    # overrides QWizardPage.initializePage
    def initializePage(self):
        now = QDateTime.currentDateTime()
        now.addSecs(5 * 60) # set default start time to 5 minutes from now

        self.setSubTitle('Specify the execution schedule for the new {0} program [{1}].'
                         .format(Constants.language_names[self.field('language').toInt()[0]],
                                 str(self.field('name').toString())))
        self.combo_start_condition.setCurrentIndex(Constants.SCHEDULE_START_CONDITION_NOW)
        self.date_start_time.setDateTime(now)
        self.combo_repeat_mode.setCurrentIndex(0)
        self.update_ui_state()

    # overrides QWizardPage.nextId
    def nextId(self):
        return -1

    def update_ui_state(self):
        start_condition = self.field('schedule.start_condition').toInt()[0]
        start_condition_time = start_condition == Constants.SCHEDULE_START_CONDITION_TIME
        start_condition_now = start_condition == Constants.SCHEDULE_START_CONDITION_NOW
        start_condition_reboot = start_condition == Constants.SCHEDULE_START_CONDITION_REBOOT

        self.label_start_time.setVisible(start_condition_time)
        self.date_start_time.setVisible(start_condition_time)
        self.label_start_delay.setVisible(start_condition_now or start_condition_reboot)
        self.spin_start_delay.setVisible(start_condition_now or start_condition_reboot)

        repeat_mode = self.field('schedule.repeat_mode').toInt()[0]
        repeat_mode_interval = repeat_mode == Constants.SCHEDULE_REPEAT_MODE_INTERVAL
        repeat_mode_selection = repeat_mode == Constants.SCHEDULE_REPEAT_MODE_SELECTION

        self.label_repeat_interval.setVisible(repeat_mode_interval)
        self.spin_repeat_interval.setVisible(repeat_mode_interval)
        self.label_repeat_seconds.setVisible(repeat_mode_selection)
        self.edit_repeat_seconds.setVisible(repeat_mode_selection)
        self.label_repeat_minutes.setVisible(repeat_mode_selection)
        self.edit_repeat_minutes.setVisible(repeat_mode_selection)
        self.label_repeat_hours.setVisible(repeat_mode_selection)
        self.edit_repeat_hours.setVisible(repeat_mode_selection)
        self.label_repeat_days.setVisible(repeat_mode_selection)
        self.edit_repeat_days.setVisible(repeat_mode_selection)
        self.label_repeat_months.setVisible(repeat_mode_selection)
        self.edit_repeat_months.setVisible(repeat_mode_selection)
        self.label_repeat_weekdays.setVisible(repeat_mode_selection)
        self.edit_repeat_weekdays.setVisible(repeat_mode_selection)
