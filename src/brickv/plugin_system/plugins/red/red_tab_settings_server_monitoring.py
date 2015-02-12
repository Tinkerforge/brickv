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

from PyQt4 import QtCore, QtGui
from brickv import infos
from brickv.plugin_system.plugins.red.ui_red_tab_settings_server_monitoring import \
     Ui_REDTabSettingsServerMonitoring
from brickv.plugin_system.plugins.red.api import *
from brickv.plugin_system.plugins.red.program_utils import TextFile
from brickv.async_call import async_call
from brickv.utils import get_main_window
from brickv.bindings.ip_connection import BASE58
from brickv.bindings.bricklet_ptc import BrickletPTC
from brickv.bindings.bricklet_temperature import BrickletTemperature
from brickv.bindings.bricklet_humidity import BrickletHumidity
from brickv.plugin_system.plugins.red.script_manager import report_script_result
from brickv.plugin_system.plugins.red.widget_spinbox_span_slider import \
     widgetSpinBoxSpanSlider

# Constants

DEFAULT_COL_WIDTH_NAME     = 160
DEFAULT_COL_WIDTH_BRICKLET = 160
DEFAULT_COL_WIDTH_UID      = 160
DEFAULT_COL_WIDTH_WARNING  = 350
DEFAULT_COL_WIDTH_CRITICAL = 350
DEFAULT_COL_WIDTH_EMAIL    = 160
DEFAULT_COL_WIDTH_REMOVE   = 100

COL_INDEX_NAME     = 0
COL_INDEX_BRICKLET = 1
COL_INDEX_UID      = 2
COL_INDEX_WARNING  = 3
COL_INDEX_CRITICAL = 4
COL_INDEX_EMAIL    = 5
COL_INDEX_REMOVE   = 6

COUNT_COLUMNS_RULES_MODEL = 7

COLUMN_EMAIL_ITEMS    = ['No Notifications',
                         'Critical',
                         'Critical/Warning']
COLUMN_BRICKLET_ITEMS = ['PTC',
                         'Temperature',
                         'Humidity']

INDEX_BRICKLET_PTC           = 0
INDEX_BRICKLET_TEMPERATURE   = 1
INDEX_BRICKLET_HUMIDITY      = 2
INDEX_EMAIL_NO_NOTIFICATIONS = 0
INDEX_EMAIL_CRITICAL         = 1
INDEX_EMAIL_CRITICAL_WARNING = 2

INITIAL_VALUE_LOWER = 30
INITIAL_VALUE_UPPER = 70

EVENT_CLICKED_ADD        = 1
EVENT_CLICKED_REMOVE_ALL = 2
EVENT_CLICKED_REFRESH    = 3
EVENT_CLICKED_SAVE       = 4
EVENT_INPUT_CHANGED      = 5

COLOR_WARNING  = QtGui.QColor(255, 255, 0)
COLOR_CRITICAL = QtGui.QColor(255, 0, 0)

EMPTY_SERVICE_NAME = '<Enter Service Name>'
EMPTY_UID          = '<Enter UID>'

CHECK_OK                            = 1
CHECK_FAILED_SERVICE_NAME_EMPTY     = 2
CHECK_FAILED_SERVICE_NAME_DUPLICATE = 3
CHECK_FAILED_UID_EMPTY              = 4
CHECK_FAILED_UID_INVALID            = 5
CHECK_FAILED_EMAIL_FROM_EMPTY       = 6
CHECK_FAILED_EMAIL_TO_EMPTY         = 7
CHECK_FAILED_EMAIL_SERVER_EMPTY     = 8
CHECK_FAILED_EMAIL_USERNAME_EMPTY   = 9
CHECK_FAILED_EMAIL_PASSWORD_EMPTY   = 10

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

        self.uids_ptc = []
        self.uids_temperature = []
        self.uids_humidity = []

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
        self.tview_sm_rules.setColumnWidth(6, DEFAULT_COL_WIDTH_REMOVE)

        # Connecting signals to slots
        self.pbutton_sm_add_rule.clicked.connect(self.slot_pbutton_sm_add_rule_clicked)
        self.pbutton_sm_remove_all_rules.clicked.connect(self.slot_pbutton_sm_remove_all_rules_clicked)
        self.pbutton_sm_refresh.clicked.connect(self.slot_pbutton_sm_refresh_clicked)
        self.pbutton_sm_save.clicked.connect(self.slot_pbutton_sm_save_clicked)
        self.chkbox_sm_email_enable.stateChanged.connect(self.slot_chkbox_sm_email_enable_state_changed)
        self.chkbox_sm_email_tls.stateChanged.connect(self.slot_chkbox_sm_email_tls_state_changed)
        self.ledit_sm_email_from.textEdited.connect(self.slot_ledit_edited)
        self.ledit_sm_email_to.textEdited.connect(self.slot_ledit_edited)
        self.ledit_sm_email_server.textEdited.connect(self.slot_ledit_edited)
        self.sbox_sm_email_port.valueChanged.connect(self.slot_sbox_value_changed)
        self.ledit_sm_email_username.textEdited.connect(self.slot_ledit_edited)
        self.ledit_sm_email_password.textEdited.connect(self.slot_ledit_edited)
        infos.get_infos_changed_signal().connect(self.slot_infos_changed)

        self.from_constructor = True
        self.slot_chkbox_sm_email_enable_state_changed(self.chkbox_sm_email_enable.checkState())

    def tab_on_focus(self):
        self.is_tab_on_focus = True

        if self.image_version.number < (1, 6):
            self.label_sm_unsupported.show()
        elif not self.service_state.servermonitoring:
            self.label_sm_disabled.show()
        else:
            self.sarea_sm.show()
            self.slot_pbutton_sm_refresh_clicked()

    def tab_off_focus(self):
        self.is_tab_on_focus = False

    def tab_destroy(self):
        pass

    def populate_cbox_uids(self, cbox_bricklet, cbox_uids):
        if cbox_bricklet.currentIndex() == INDEX_BRICKLET_PTC:
            cbox_uids.addItems(self.uids_ptc)
    
            if cbox_uids.count() == 1:
                cbox_uids.setEditable(True)
                cbox_uids.setInsertPolicy(QtGui.QComboBox.InsertBeforeCurrent)
                cbox_uids.lineEdit().selectAll()
            else:
                cbox_uids.setEditable(False)
    
        elif cbox_bricklet.currentIndex() == INDEX_BRICKLET_TEMPERATURE:
            cbox_uids.addItems(self.uids_temperature)
            
            if cbox_uids.count() == 1:
                cbox_uids.setEditable(True)
                cbox_uids.setInsertPolicy(QtGui.QComboBox.InsertBeforeCurrent)
                cbox_uids.lineEdit().selectAll()
            else:
                cbox_uids.setEditable(False)
    
        elif cbox_bricklet.currentIndex() == INDEX_BRICKLET_HUMIDITY:
            cbox_uids.addItems(self.uids_humidity)
            
            if cbox_uids.count() == 1:
                cbox_uids.setEditable(True)
                cbox_uids.setInsertPolicy(QtGui.QComboBox.InsertBeforeCurrent)
                cbox_uids.lineEdit().selectAll()
            else:
                cbox_uids.setEditable(False)

    def check_rules(self):
        list_service_names = []

        for r in range(self.model_rules.rowCount()):
            for c in range(0, COUNT_COLUMNS_RULES_MODEL):
                # Check Name field
                if c == COL_INDEX_NAME:
                    item = self.model_rules.item(r, c)
                    index = self.model_rules.indexFromItem(item)
                    ledit_name_text = self.tview_sm_rules.indexWidget(index).text()

                    if EMPTY_SERVICE_NAME in ledit_name_text or not ledit_name_text:
                        return CHECK_FAILED_SERVICE_NAME_EMPTY
                    elif ledit_name_text in list_service_names:
                        return CHECK_FAILED_SERVICE_NAME_DUPLICATE
                    else:
                        list_service_names.append(ledit_name_text)

                # Check UID field
                elif c == COL_INDEX_UID:
                    item = self.model_rules.item(r, c)
                    index = self.model_rules.indexFromItem(item)
                    uid = self.tview_sm_rules.indexWidget(index).currentText()
                    if EMPTY_UID in uid or not uid:
                        CHECK_FAILED_UID_EMPTY
                    else:
                        for c in list(uid):
                            if c not in BASE58:
                                return CHECK_FAILED_UID_INVALID
    
                # Check Email field
                elif self.chkbox_sm_email_enable.isChecked():
                    email_from     = self.ledit_sm_email_from.text()
                    email_to       = self.ledit_sm_email_to.text()
                    email_server   = self.ledit_sm_email_server.text()
                    email_username = self.ledit_sm_email_username.text()
                    email_password = self.ledit_sm_email_password.text()

                    if not email_from:
                         return CHECK_FAILED_EMAIL_FROM_EMPTY
                    if not email_to:
                        return CHECK_FAILED_EMAIL_TO_EMPTY
                    if not email_server:
                        return CHECK_FAILED_EMAIL_SERVER_EMPTY
                    if not email_username:
                        return CHECK_FAILED_EMAIL_USERNAME_EMPTY
                    if not email_password:
                        return CHECK_FAILED_EMAIL_PASSWORD_EMPTY

        return CHECK_OK

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
            # Add Name field widget
            if c == COL_INDEX_NAME:
                item = self.model_rules.item(r, c)
                index = self.model_rules.indexFromItem(item)
                ledit_name = QtGui.QLineEdit()
                ledit_name.textEdited.connect(self.slot_ledit_edited)
                ledit_name.setText(EMPTY_SERVICE_NAME)
                ledit_name.selectAll()
                self.tview_sm_rules.setIndexWidget(index, ledit_name)

            # Add Bricklet field widget
            elif c == COL_INDEX_BRICKLET:
                item = self.model_rules.item(r, c)
                index = self.model_rules.indexFromItem(item)
                cbox = QtGui.QComboBox(self.tview_sm_rules)
                cbox.addItems(COLUMN_BRICKLET_ITEMS)
                cbox.activated.connect(self.slot_cbox_bricklet_activated)
                self.tview_sm_rules.setIndexWidget(index, cbox)

            # Add UID field widget
            elif c == COL_INDEX_UID:
                item = self.model_rules.item(r, c)
                index = self.model_rules.indexFromItem(item)
                cbox = QtGui.QComboBox()
                item_bricklet = self.model_rules.item(r, 1)
                index_bricklet = self.model_rules.indexFromItem(item_bricklet)
                cbox_bricklet = self.tview_sm_rules.indexWidget(index_bricklet)
                self.populate_cbox_uids(cbox_bricklet, cbox)
                cbox.activated.connect(self.slot_cbox_uid_activated)
                self.tview_sm_rules.setIndexWidget(index, cbox)

            # Add Warning field widget
            elif c == COL_INDEX_WARNING:
                item = self.model_rules.item(r, c)
                index = self.model_rules.indexFromItem(item)
                widget_spin_span = widgetSpinBoxSpanSlider()
                widget_spin_span.sbox_upper.setValue(INITIAL_VALUE_UPPER)
                widget_spin_span.sbox_lower.setValue(INITIAL_VALUE_LOWER)
                widget_spin_span.span_slider.setColorOutsideRange(COLOR_WARNING)
                widget_spin_span.sbox_upper.valueChanged.connect(self.slot_sbox_value_changed)
                widget_spin_span.sbox_lower.valueChanged.connect(self.slot_sbox_value_changed)
                self.tview_sm_rules.setIndexWidget(index, widget_spin_span)

            # Add Critical field widget
            elif c == COL_INDEX_CRITICAL:
                item = self.model_rules.item(r, c)
                index = self.model_rules.indexFromItem(item)
                widget_spin_span = widgetSpinBoxSpanSlider()
                widget_spin_span.sbox_upper.setValue(INITIAL_VALUE_UPPER)
                widget_spin_span.sbox_lower.setValue(INITIAL_VALUE_LOWER)
                widget_spin_span.span_slider.setColorOutsideRange(COLOR_CRITICAL)
                widget_spin_span.sbox_upper.valueChanged.connect(self.slot_sbox_value_changed)
                widget_spin_span.sbox_lower.valueChanged.connect(self.slot_sbox_value_changed)
                self.tview_sm_rules.setIndexWidget(index, widget_spin_span)

            # Add Email field widget
            elif c == COL_INDEX_EMAIL:
                item = self.model_rules.item(r, c)
                index = self.model_rules.indexFromItem(item)
                cbox = QtGui.QComboBox()
                cbox.addItems(COLUMN_EMAIL_ITEMS)

                if self.chkbox_sm_email_enable.isChecked():
                    cbox.setEnabled(True)
                else:
                    cbox.setEnabled(False)

                cbox.activated.connect(self.slot_cbox_email_activated)
                self.tview_sm_rules.setIndexWidget(index, cbox)

            # Add Remove field widget
            elif c == COL_INDEX_REMOVE:
                item = self.model_rules.item(r, c)
                index = self.model_rules.indexFromItem(item)
                btn = QtGui.QPushButton('X')
                btn.clicked.connect(self.slot_remove_rule_clicked)
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

            if self.model_rules.rowCount() > 0:
                self.pbutton_sm_remove_all_rules.setEnabled(True)
            else:
                self.pbutton_sm_remove_all_rules.setEnabled(False)

    def update_gui_after_refresh(self, result):
        self.show_working_wait(False)
        self.sarea_sm.setEnabled(True)
        self.pbutton_sm_refresh.setText('Refresh')
        self.pbutton_sm_save.setText('Save')
        if result:
            self.pbutton_sm_save.setEnabled(False)

    def update_gui_after_save(self, result):
        self.show_working_wait(False)
        self.sarea_sm.setEnabled(True)
        self.pbutton_sm_save.setText('Save')

        if result:
            self.pbutton_sm_save.setEnabled(False)
        else:
            self.pbutton_sm_save.setEnabled(True)

    def slot_remove_rule_clicked(self):
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

        self.update_gui(EVENT_INPUT_CHANGED)

    def slot_pbutton_sm_add_rule_clicked(self):
        self.update_gui(EVENT_CLICKED_ADD)
        self.update_gui(EVENT_INPUT_CHANGED)

    def slot_pbutton_sm_remove_all_rules_clicked(self):
        self.update_gui(EVENT_CLICKED_REMOVE_ALL)
        self.update_gui(EVENT_INPUT_CHANGED)

    def slot_pbutton_sm_refresh_clicked(self):
        self.update_gui(EVENT_CLICKED_REFRESH)
        self.update_gui_after_refresh(True)

    def slot_pbutton_sm_save_clicked(self):
        check_result = self.check_rules()

        if self.model_rules.rowCount() > 0:
            if check_result == CHECK_FAILED_SERVICE_NAME_EMPTY:
                QtGui.QMessageBox.critical(get_main_window(), '', '')
                self.update_gui_after_save(False)
                return
            elif check_result == CHECK_FAILED_SERVICE_NAME_DUPLICATE:
                QtGui.QMessageBox.critical(get_main_window(), '', '')
                self.update_gui_after_save(False)
                return
            elif check_result == CHECK_FAILED_UID_EMPTY:
                QtGui.QMessageBox.critical(get_main_window(), '', '')
                self.update_gui_after_save(False)
                return
            elif check_result == CHECK_FAILED_UID_INVALID:
                QtGui.QMessageBox.critical(get_main_window(), '', '')
                self.update_gui_after_save(False)
                return
            elif check_result == CHECK_FAILED_EMAIL_FROM_EMPTY:
                QtGui.QMessageBox.critical(get_main_window(), '', '')
                self.update_gui_after_save(False)
                return
            elif check_result == CHECK_FAILED_EMAIL_TO_EMPTY:
                QtGui.QMessageBox.critical(get_main_window(), '', '')
                self.update_gui_after_save(False)
                return
            elif check_result == CHECK_FAILED_EMAIL_SERVER_EMPTY:
                QtGui.QMessageBox.critical(get_main_window(), '', '')
                self.update_gui_after_save(False)
                return
            elif check_result == CHECK_FAILED_EMAIL_USERNAME_EMPTY:
                QtGui.QMessageBox.critical(get_main_window(), '', '')
                self.update_gui_after_save(False)
                return
            elif check_result == CHECK_FAILED_EMAIL_PASSWORD_EMPTY:
                QtGui.QMessageBox.critical(get_main_window(), '', '')
                self.update_gui_after_save(False)
                return

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

        if self.from_constructor:
            self.from_constructor = False
            return

        self.update_gui(EVENT_INPUT_CHANGED)

    def slot_chkbox_sm_email_password_show_state_changed(self, state):
        if state == QtCore.Qt.Checked:
            self.ledit_sm_email_password.setEchoMode(QtGui.QLineEdit.Normal)
        else:
            self.ledit_sm_email_password.setEchoMode(QtGui.QLineEdit.Password)

        self.update_gui(EVENT_INPUT_CHANGED)

    def slot_chkbox_sm_email_tls_state_changed(self, state):
        self.update_gui(EVENT_INPUT_CHANGED)

    def slot_infos_changed(self, uid, action):
        self.uids_ptc = []
        self.uids_temperature = []
        self.uids_humidity = []

        # Populating bricklet UID lists
        for bricklet in infos.get_bricklet_infos():
            if bricklet.device_identifier == BrickletPTC.DEVICE_IDENTIFIER and \
               bricklet.uid not in self.uids_ptc:
                    self.uids_ptc.append(bricklet.uid)
            elif bricklet.device_identifier == BrickletTemperature.DEVICE_IDENTIFIER and \
                 bricklet.uid not in self.uids_temperature:
                    self.uids_temperature.append(bricklet.uid)
            elif bricklet.device_identifier == BrickletHumidity.DEVICE_IDENTIFIER and \
                 bricklet.uid not in self.uids_humidity:
                    self.uids_humidity.append(bricklet.uid)

        self.uids_ptc.append(EMPTY_UID)
        self.uids_temperature.append(EMPTY_UID)
        self.uids_humidity.append(EMPTY_UID)

    def slot_cbox_bricklet_activated(self, index):
        sender = self.sender()

        for r in range(self.model_rules.rowCount()):
            for c in range(0, COUNT_COLUMNS_RULES_MODEL):
                item = self.model_rules.item(r, c)
                index = self.model_rules.indexFromItem(item)
                if sender == self.tview_sm_rules.indexWidget(index):
                    item_cbox_uids = self.model_rules.item(r, COL_INDEX_UID)
                    index_cbox_uids = self.model_rules.indexFromItem(item_cbox_uids)
                    cbox_uids = self.tview_sm_rules.indexWidget(index_cbox_uids)

                    cbox_uids.clear()

                    self.populate_cbox_uids(sender, cbox_uids)

                    break

        self.update_gui(EVENT_INPUT_CHANGED)

    def slot_cbox_uid_activated(self, index):
        sender = self.sender()

        for r in range(self.model_rules.rowCount()):
            for c in range(0, COUNT_COLUMNS_RULES_MODEL):
                item_cbox_uid = self.model_rules.item(r, c)
                index_cbox_uid = self.model_rules.indexFromItem(item_cbox_uid)
                if sender == self.tview_sm_rules.indexWidget(index_cbox_uid):
                    if index == sender.count() - 1:
                        sender.setEditable(True)
                        sender.setInsertPolicy(QtGui.QComboBox.InsertBeforeCurrent)
                        sender.lineEdit().selectAll()
                    else:
                        sender.setEditable(False)
                    break

        self.update_gui(EVENT_INPUT_CHANGED)

    def slot_ledit_edited(self, text):
        self.update_gui(EVENT_INPUT_CHANGED)

    def slot_cbox_email_activated(self, index):
        self.update_gui(EVENT_INPUT_CHANGED)

    def slot_sbox_value_changed(self, value):
        self.update_gui(EVENT_INPUT_CHANGED)
