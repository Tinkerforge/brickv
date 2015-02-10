# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014 Ishraq Ibne Ashraf <ishraq@tinkerforge.com>

red_tab_settings_server_monitoring.py: RED settings server monitoring tab implementation

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

import json
from PyQt4 import QtCore, QtGui
from brickv.plugin_system.plugins.red.ui_red_tab_settings_server_monitoring import Ui_REDTabSettingsServerMonitoring
from brickv.plugin_system.plugins.red.api import *
from brickv.plugin_system.plugins.red.program_utils import TextFile
from brickv.async_call import async_call
from brickv.utils import get_main_window
from brickv.plugin_system.plugins.red.widget_spinbox_span_slider import widgetSpinBoxSpanSlider

# Constants

DEFAULT_COL_WIDTH_NAME     = 160
DEFAULT_COL_WIDTH_BRICKLET = 160
DEFAULT_COL_WIDTH_UID      = 160
DEFAULT_COL_WIDTH_WARNING  = 350
DEFAULT_COL_WIDTH_CRITICAL = 350
DEFAULT_COL_WIDTH_EMAIL    = 160
DEFAULT_COL_WIDTH_DELETE   = 100

COL_INDEX_NAME     = 0
COL_INDEX_BRICKLET = 1
COL_INDEX_UID      = 2
COL_INDEX_WARNING  = 3
COL_INDEX_CRITICAL = 4
COL_INDEX_EMAIL    = 5
COL_INDEX_DELETE   = 6

COUNT_COLUMNS_RULES_MODEL  = 7

COLUMN_EMAIL_ITEMS = ['No Notifications', 'Critical', 'Critical/Warning']
COLUMN_BRICKLET_ITEMS = ['PTC', 'Temperature', 'Humidity']

INITIAL_VALUE_LOWER = 30
INITIAL_VALUE_UPPER = 70

EVENT_CLICKED_ADD        = 1
EVENT_CLICKED_REMOVE_ALL = 2
EVENT_CLICKED_REFRESH    = 3
EVENT_CLICKED_SAVE       = 4
EVENT_INPUT_CHANGED      = 5

COLOR_WARNING   = QtGui.QColor(255, 255, 0)
COLOR_CRITICAL  = QtGui.QColor(255, 0, 0)

class REDTabSettingsServerMonitoring(QtGui.QWidget, Ui_REDTabSettingsServerMonitoring):
    def __init__(self):
        QtGui.QWidget.__init__(self)

        self.setupUi(self)

        self.session        = None # Set from REDTabSettings
        self.script_manager = None # Set from REDTabSettings
        self.image_version  = None # Set from REDTabSettings
        self.service_state  = None # Set from REDTabSettings

        self.is_tab_on_focus = False
        
        self.label_sm_unsupported.hide()
        self.label_sm_disabled.hide()
        self.show_working_wait(False)
        self.sarea_sm.hide()

        self.model_rules = QtGui.QStandardItemModel()

        headerRow = []
        headerRow.append('Name')
        headerRow.append('Bricklet')
        headerRow.append('UID')
        headerRow.append('Warning')
        headerRow.append('Critical')
        headerRow.append('Email')
        headerRow.append('Remove')
        self.model_rules.setHorizontalHeaderLabels(headerRow)
        self.tview_sm_rules.setModel(self.model_rules)
        self.tview_sm_rules.setColumnWidth(0, DEFAULT_COL_WIDTH_NAME)
        self.tview_sm_rules.setColumnWidth(1, DEFAULT_COL_WIDTH_BRICKLET)
        self.tview_sm_rules.setColumnWidth(2, DEFAULT_COL_WIDTH_UID)
        self.tview_sm_rules.setColumnWidth(3, DEFAULT_COL_WIDTH_WARNING)
        self.tview_sm_rules.setColumnWidth(4, DEFAULT_COL_WIDTH_CRITICAL)
        self.tview_sm_rules.setColumnWidth(5, DEFAULT_COL_WIDTH_EMAIL)
        self.tview_sm_rules.setColumnWidth(6, DEFAULT_COL_WIDTH_DELETE)

        # Connecting signals to slots
        self.pbutton_sm_add_rule.clicked.connect(self.slot_pbutton_sm_add_rule_clicked)
        self.pbutton_sm_remove_all_rules.clicked.connect(self.slot_pbutton_sm_remove_all_rules_clicked)
        self.pbutton_sm_refresh.clicked.connect(self.slot_pbutton_sm_refresh_clicked)
        self.pbutton_sm_save.clicked.connect(self.slot_pbutton_sm_save_clicked)
        self.chkbox_sm_email_enable.stateChanged.connect(self.slot_chkbox_sm_email_enable_state_changed)
        self.chkbox_sm_email_password_show.stateChanged.connect(self.slot_chkbox_sm_email_password_show_state_changed)
        
        self.chkbox_sm_email_enable.setCheckState(QtCore.Qt.Checked)
        self.chkbox_sm_email_enable.setCheckState(QtCore.Qt.Unchecked)
        self.chkbox_sm_email_password_show.setCheckState(QtCore.Qt.Checked)
        self.chkbox_sm_email_password_show.setCheckState(QtCore.Qt.Unchecked)

    def tab_on_focus(self):
        self.is_tab_on_focus = True

        if self.image_version.number < (1, 6):
            self.label_sm_unsupported.show()
        elif not self.service_state.servermonitoring:
            self.label_sm_disabled.show()
        else:
            self.sarea_sm.show()

    def tab_off_focus(self):
        self.is_tab_on_focus = False

    def tab_destroy(self):
        pass

    def show_working_wait(self, show):
        if show:
            self.label_sm_working_wait.show()
            self.pbar_sm_working_wait.show()
        else:
            self.label_sm_working_wait.hide()
            self.pbar_sm_working_wait.hide()

    def add_new_rule(self):
        rule = []
        rule.append(QtGui.QStandardItem(''))
        rule.append(QtGui.QStandardItem(''))
        rule.append(QtGui.QStandardItem(''))
        rule.append(QtGui.QStandardItem(''))
        rule.append(QtGui.QStandardItem(''))
        rule.append(QtGui.QStandardItem(''))
        rule.append(QtGui.QStandardItem(''))

        self.model_rules.appendRow(rule)

        r = self.model_rules.rowCount() - 1

        for c in range(0, COUNT_COLUMNS_RULES_MODEL):
            if c == COL_INDEX_NAME:
                item = self.model_rules.item(r, c)
                index = self.model_rules.indexFromItem(item)
                self.tview_sm_rules.setIndexWidget(index, QtGui.QLineEdit())

            elif c == COL_INDEX_BRICKLET:
                item = self.model_rules.item(r, c)
                index = self.model_rules.indexFromItem(item)
                cbox = QtGui.QComboBox(self.tview_sm_rules)
                cbox.addItems(COLUMN_BRICKLET_ITEMS)
                self.tview_sm_rules.setIndexWidget(index, cbox)

            elif c == COL_INDEX_UID:
                item = self.model_rules.item(r, c)
                index = self.model_rules.indexFromItem(item)
                self.tview_sm_rules.setIndexWidget(index, QtGui.QComboBox())

            elif c == COL_INDEX_WARNING:
                item = self.model_rules.item(r, c)
                index = self.model_rules.indexFromItem(item)
                widget_spin_span = widgetSpinBoxSpanSlider()
                widget_spin_span.sbox_upper.setValue(INITIAL_VALUE_UPPER)
                widget_spin_span.sbox_lower.setValue(INITIAL_VALUE_LOWER)
                widget_spin_span.span_slider.setColorOutsideRange(COLOR_WARNING)
                self.tview_sm_rules.setIndexWidget(index, widget_spin_span)

            elif c == COL_INDEX_CRITICAL:
                item = self.model_rules.item(r, c)
                index = self.model_rules.indexFromItem(item)
                widget_spin_span = widgetSpinBoxSpanSlider()
                widget_spin_span.sbox_upper.setValue(INITIAL_VALUE_UPPER)
                widget_spin_span.sbox_lower.setValue(INITIAL_VALUE_LOWER)
                widget_spin_span.span_slider.setColorOutsideRange(COLOR_CRITICAL)
                self.tview_sm_rules.setIndexWidget(index, widget_spin_span)

            elif c == COL_INDEX_EMAIL:
                item = self.model_rules.item(r, c)
                index = self.model_rules.indexFromItem(item)
                cbox = QtGui.QComboBox()
                cbox.addItems(COLUMN_EMAIL_ITEMS)

                if self.chkbox_sm_email_enable.isChecked():
                    cbox.setEnabled(True)
                else:
                    cbox.setEnabled(False)

                self.tview_sm_rules.setIndexWidget(index, cbox)

            elif c == COL_INDEX_DELETE:
                item = self.model_rules.item(r, c)
                index = self.model_rules.indexFromItem(item)
                btn = QtGui.QPushButton('X')
                btn.clicked.connect(self.slot_delete_rule_clicked)
                self.tview_sm_rules.setIndexWidget(index, btn)

    def update_gui(self, event):
        if event == EVENT_CLICKED_ADD:
            self.add_new_rule()

        elif event == EVENT_CLICKED_REMOVE_ALL:
            reply = QtGui.QMessageBox.question(get_main_window(),
                                               'Settings | Server Monitoring',
                                               'Are you sure you want to remove all rules?',
                                               QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)

            if (reply == QtGui.QMessageBox.Yes):
                self.model_rules.removeRows(0, self.model_rules.rowCount())

            if self.model_rules.rowCount() != 0:
                self.pbutton_sm_remove_all_rules.setEnabled(True)
            else:
                self.pbutton_sm_remove_all_rules.setEnabled(False)

        elif event == EVENT_CLICKED_REFRESH:
            self.show_working_wait(True)
            self.pbutton_sm_refresh.setText('Refreshing...')
            self.sarea_sm.setEnabled(False)

        elif event == EVENT_CLICKED_SAVE:
            self.show_working_wait(True)
            self.pbutton_sm_save.setText('Saving...')
            self.sarea_sm.setEnabled(False)

        elif event == EVENT_INPUT_CHANGED:
            self.pbutton_sm_save.setEnabled(True)

            if self.model_rules.rowCount() != 0:
                self.pbutton_sm_remove_all_rules.setEnabled(True)
            else:
                self.pbutton_sm_remove_all_rules.setEnabled(False)

    def update_gui_after_refresh(self):
        self.show_working_wait(False)
        self.sarea_sm.setEnabled(True)
        self.pbutton_sm_refresh.setText('Refresh')
        self.update_gui(EVENT_INPUT_CHANGED)

    def update_gui_after_save(self, result):
        self.show_working_wait(False)
        self.sarea_sm.setEnabled(True)
        self.pbutton_sm_save.setText('Save')

        if result:
            self.pbutton_sm_save.setEnabled(False)
        else:
            self.pbutton_sm_save.setEnabled(True)

    def slot_delete_rule_clicked(self):
        sender = self.sender()
        
        for r in range(self.model_rules.rowCount()):
            for c in range(0, COUNT_COLUMNS_RULES_MODEL):
                item = self.model_rules.item(r, c)
                index = self.model_rules.indexFromItem(item)
                if sender == self.tview_sm_rules.indexWidget(index):
                    self.model_rules.removeRows(r, 1)
                    break
        
        if self.model_rules.rowCount() == 0:
            self.pbutton_sm_remove_all_rules.setEnabled(False)
        else:
            self.pbutton_sm_remove_all_rules.setEnabled(True)

    def slot_pbutton_sm_add_rule_clicked(self):
        self.update_gui(EVENT_CLICKED_ADD)
        self.update_gui(EVENT_INPUT_CHANGED)

    def slot_pbutton_sm_remove_all_rules_clicked(self):
        self.update_gui(EVENT_CLICKED_REMOVE_ALL)
        self.update_gui(EVENT_INPUT_CHANGED)

    def slot_pbutton_sm_refresh_clicked(self):
        self.update_gui(EVENT_CLICKED_REFRESH)
        self.update_gui_after_refresh()

    def slot_pbutton_sm_save_clicked(self):
        self.update_gui(EVENT_CLICKED_SAVE)
        self.update_gui_after_save(True)
    
    def slot_chkbox_sm_email_enable_state_changed(self, state):        
        if state == QtCore.Qt.Checked:
            for r in range(self.model_rules.rowCount()):
                item = self.model_rules.item(r, 5)
                index = self.model_rules.indexFromItem(item)
                widget = self.tview_sm_rules.indexWidget(index)
                widget.setEnabled(True)

            self.label_sm_email_from.show()
            self.ledit_sm_email_from.show()
            self.label_sm_email_to.show()
            self.ledit_sm_email_to.show()
            self.label_sm_email_server.show()
            self.ledit_sm_email_server.show()
            self.label_sm_email_port.show()
            self.sbox_sm_email_port.show()
            self.label_sm_email_username.show()
            self.ledit_sm_email_username.show()
            self.label_sm_email_password.show()
            self.ledit_sm_email_password.show()
            self.chkbox_sm_email_password_show.show()
            self.label_sm_email_tls.show()
            self.chkbox_sm_email_tls.show()
        else:
            for r in range(self.model_rules.rowCount()):
                item = self.model_rules.item(r, 5)
                index = self.model_rules.indexFromItem(item)
                widget = self.tview_sm_rules.indexWidget(index)
                widget.setEnabled(False)

            self.label_sm_email_from.hide()
            self.ledit_sm_email_from.hide()
            self.label_sm_email_to.hide()
            self.ledit_sm_email_to.hide()
            self.label_sm_email_server.hide()
            self.ledit_sm_email_server.hide()
            self.label_sm_email_port.hide()
            self.sbox_sm_email_port.hide()
            self.label_sm_email_username.hide()
            self.ledit_sm_email_username.hide()
            self.label_sm_email_password.hide()
            self.ledit_sm_email_password.hide()
            self.chkbox_sm_email_password_show.hide()
            self.label_sm_email_tls.hide()
            self.chkbox_sm_email_tls.hide()
            
    def slot_chkbox_sm_email_password_show_state_changed(self, state):
        if state == QtCore.Qt.Checked:
            self.ledit_sm_email_password.setEchoMode(QtGui.QLineEdit.Normal)
        else:
            self.ledit_sm_email_password.setEchoMode(QtGui.QLineEdit.Password)
