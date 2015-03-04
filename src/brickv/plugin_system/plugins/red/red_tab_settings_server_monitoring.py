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
from brickv.plugin_system.plugins.red.red_tab_settings_server_monitoring_add_host_dialog import \
     REDTabSettingsServerMonitoringAddHostDialog
from brickv.plugin_system.plugins.red.api import *
from brickv.async_call import async_call
from brickv.utils import get_main_window
from brickv.bindings.ip_connection import BASE58
from brickv.bindings.bricklet_ptc import BrickletPTC
from brickv.bindings.bricklet_temperature import BrickletTemperature
from brickv.bindings.bricklet_humidity import BrickletHumidity
from brickv.bindings.bricklet_ambient_light import BrickletAmbientLight
from brickv.plugin_system.plugins.red.script_manager import report_script_result
from brickv.plugin_system.plugins.red.widget_spinbox_span_slider import \
     widgetSpinBoxSpanSlider
import json

# Constants
DEFAULT_COL_WIDTH_RULES_NAME                = 140
DEFAULT_COL_WIDTH_RULES_HOST                = 140
DEFAULT_COL_WIDTH_RULES_BRICKLET            = 140
DEFAULT_COL_WIDTH_RULES_UID                 = 100
DEFAULT_COL_WIDTH_RULES_WARNING             = 380
DEFAULT_COL_WIDTH_RULES_CRITICAL            = 380
DEFAULT_COL_WIDTH_RULES_EMAIL_NOTIFICATIONS = 140
DEFAULT_COL_WIDTH_RULES_REMOVE              = 80
DEFAULT_COL_WIDTH_HOSTS_HOST                = 300
DEFAULT_COL_WIDTH_HOSTS_PORT                = 300
DEFAULT_COL_WIDTH_HOSTS_AUTHENTICATION      = 200
DEFAULT_COL_WIDTH_HOSTS_SECRET              = 450
DEFAULT_COL_WIDTH_HOSTS_REMOVE              = 80

'''
HEADERS_TVIEW_RULES = ['Name',
                       'Host',
                       'Bricklet',
                       'UID',
                       'Warning',
                       'Critical',
                       'Email Notifications',
                       'Remove']
'''

HEADERS_TVIEW_RULES = ['Name',
                       'Bricklet',
                       'UID',
                       'Warning',
                       'Critical',
                       'Email Notifications',
                       'Remove']

HEADERS_TVIEW_HOSTS = ['Host',
                       'Port',
                       'Authentication',
                       'Secret',
                       'Remove']

COLUMN_EMAIL_NOTIFICATIONS_ITEMS    = ['No Notifications',
                                       'Critical',
                                       'Critical/Warning']

SUPPORTED_BRICKLETS = {'PTC'          :'ptc',
                       'Temperature'  :'temperature',
                       'Humidity'     :'humidity',
                       'Ambient Light':'ambient_light'}

RANGE_MIN_PTC           = 0
RANGE_MAX_PTC           = 100
RANGE_MIN_TEMPERATURE   = 0
RANGE_MAX_TEMPERATURE   = 100
RANGE_MIN_HUMIDITY      = 0
RANGE_MAX_HUMIDITY      = 100
RANGE_MIN_AMBIENT_LIGHT = 0
RANGE_MAX_AMBIENT_LIGHT = 900

INDEX_EMAIL_NO_NOTIFICATIONS        = 0
INDEX_EMAIL_CRITICAL                = 1
INDEX_EMAIL_WARNING_CRITICAL        = 2
INDEX_COL_RULES_NAME                = 0
#INDEX_COL_RULES_HOST                = *
INDEX_COL_RULES_BRICKLET            = 1
INDEX_COL_RULES_UID                 = 2
INDEX_COL_RULES_WARNING             = 3
INDEX_COL_RULES_CRITICAL            = 4
INDEX_COL_RULES_EMAIL_NOTIFICATIONS = 5
INDEX_COL_RULES_REMOVE              = 6
INDEX_COL_HOSTS_HOST                = 0
INDEX_COL_HOSTS_PORT                = 1
INDEX_COL_HOSTS_AUTHENTICATION      = 2
INDEX_COL_HOSTS_SECRET              = 3
INDEX_COL_HOSTS_REMOVE              = 4

#COUNT_COLUMNS_RULES_MODEL = 8
COUNT_COLUMNS_RULES_MODEL = 7
COUNT_COLUMNS_HOSTS_MODEL = 5

EVENT_CLICKED_REMOVE_ALL     = 1
EVENT_CLICKED_REFRESH        = 2
EVENT_CLICKED_SAVE           = 3
EVENT_INPUT_CHANGED          = 4
EVENT_RETURNED_REFRESH_TRUE  = 5
EVENT_RETURNED_REFRESH_FALSE = 6
EVENT_RETURNED_SAVE_TRUE     = 7
EVENT_RETURNED_SAVE_FALSE    = 8

COLOR_WARNING  = QtGui.QColor(255, 255, 0)
COLOR_CRITICAL = QtGui.QColor(255, 0, 0)

EMPTY_SERVICE_NAME = '<Enter Service Name>'
EMPTY_UID          = '<Enter UID>'

CHECK_OK                               = 1
CHECK_FAILED_SERVICE_NAME_EMPTY        = 2
CHECK_FAILED_SERVICE_NAME_DUPLICATE    = 3
CHECK_FAILED_UID_EMPTY                 = 4
CHECK_FAILED_UID_INVALID               = 5
CHECK_FAILED_EMAIL_FROM_EMPTY          = 6
CHECK_FAILED_EMAIL_FROM_NON_ASCII      = 7
CHECK_FAILED_EMAIL_FROM_WHITESPACE     = 8
CHECK_FAILED_EMAIL_TO_EMPTY            = 9
CHECK_FAILED_EMAIL_TO_NON_ASCII        = 10
CHECK_FAILED_EMAIL_TO_WHITESPACE       = 11
CHECK_FAILED_EMAIL_SERVER_EMPTY        = 12
CHECK_FAILED_EMAIL_SERVER_NON_ASCII    = 13
CHECK_FAILED_EMAIL_SERVER_WHITESPACE   = 14
CHECK_FAILED_EMAIL_USERNAME_EMPTY      = 15
CHECK_FAILED_EMAIL_USERNAME_NON_ASCII  = 16
CHECK_FAILED_EMAIL_USERNAME_WHITESPACE = 17
CHECK_FAILED_EMAIL_PASSWORD_EMPTY      = 18
CHECK_FAILED_EMAIL_PASSWORD_NON_ASCII  = 19
CHECK_FAILED_NON_ASCII                 = 20

MESSAGEBOX_TITLE                              = 'Settings | Server Monitoring'
MESSAGE_INFO_SAVE_OK                          = 'Rules saved and applied successfully'
MESSAGE_INFO_NO_RULES_TO_SAVE                 = 'No rules to save'
MESSAGE_ERROR_SAVE_NOT_OK                     = 'Error occured while saving and applying rules'
MESSAGE_ERROR_GET_FAILED                      = 'Error occured while trying to get existing rules'
MESSAGE_ERROR_CHECK_SERVICE_NAME_EMPTY        = 'Service name empty'
MESSAGE_ERROR_CHECK_SERVICE_NAME_DUPLICATE    = 'Duplicated service name'
MESSAGE_ERROR_CHECK_UID_EMPTY                 = 'UID empty'
MESSAGE_ERROR_CHECK_UID_INVALID               = 'Invalid UID'
MESSAGE_ERROR_CHECK_EMAIL_FROM_EMPTY          = 'Email from address empty'
MESSAGE_ERROR_CHECK_EMAIL_FROM_NON_ASCII      = 'Email from address contains non ASCII character'
MESSAGE_ERROR_CHECK_EMAIL_FROM_WHITESPACE     = 'Email from address contains whitespace'
MESSAGE_ERROR_CHECK_EMAIL_TO_EMPTY            = 'Email to address empty'
MESSAGE_ERROR_CHECK_EMAIL_TO_NON_ASCII        = 'Email to address contains non ASCII character'
MESSAGE_ERROR_CHECK_EMAIL_TO_WHITESPACE       = 'Email to address contains whitespace'
MESSAGE_ERROR_CHECK_EMAIL_SERVER_EMPTY        = 'SMTP server empty'
MESSAGE_ERROR_CHECK_EMAIL_SERVER_NON_ASCII    = 'SMTP server contains non ASCII character'
MESSAGE_ERROR_CHECK_EMAIL_SERVER_WHITESPACE   = 'SMTP server contains whitespace'
MESSAGE_ERROR_CHECK_EMAIL_USERNAME_EMPTY      = 'SMTP username empty'
MESSAGE_ERROR_CHECK_EMAIL_USERNAME_NON_ASCII  = 'SMTP username contains non ASCII character'
MESSAGE_ERROR_CHECK_EMAIL_USERNAME_WHITESPACE = 'SMTP username contains whitespace'
MESSAGE_ERROR_CHECK_EMAIL_PASSWORD_EMPTY      = 'SMTP password empty'
MESSAGE_ERROR_CHECK_EMAIL_PASSWORD_NON_ASCII  = 'SMTP password contains non ASCII character'
MESSAGE_ERROR_CHECK_NON_ASCII                 = 'Non ASCII character'

NEW     = True
NOT_NEW = False

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
        self.gbox_sm_hosts.hide()

        self.uids_ptc = []
        self.uids_temperature = []
        self.uids_humidity = []
        self.uids_ambient_light = []

        self.model_hosts = QtGui.QStandardItemModel()
        self.model_hosts.setHorizontalHeaderLabels(HEADERS_TVIEW_HOSTS)
        self.tview_sm_hosts.setModel(self.model_hosts)
        self.tview_sm_hosts.setColumnHidden(INDEX_COL_HOSTS_HOST, True)
        self.set_default_col_width_hosts()

        self.model_rules = QtGui.QStandardItemModel()
        self.model_rules.setHorizontalHeaderLabels(HEADERS_TVIEW_RULES)
        self.tview_sm_rules.setModel(self.model_rules)
        self.set_default_col_width_rules()

        # Connecting signals to slots
        self.pbutton_sm_add_rule.clicked.connect(self.slot_pbutton_sm_add_rule_clicked)
        self.pbutton_sm_remove_all_rules.clicked.connect(self.slot_pbutton_sm_remove_all_rules_clicked)
        self.pbutton_sm_add_host.clicked.connect(self.slot_pbutton_sm_add_host_clicked)
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
        self.chkbox_sm_email_password_show.stateChanged.connect(self.slot_chkbox_sm_email_password_show_state_changed)

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

    def add_widget_spin_span(self, r, c, new, color, low = None, high = None):
        item = self.model_rules.item(r, c)
        index = self.model_rules.indexFromItem(item)
        item_bricklet = self.model_rules.item(r, INDEX_COL_RULES_BRICKLET)
        index_bricklet = self.model_rules.indexFromItem(item_bricklet)

        cbox_bricklet = self.tview_sm_rules.indexWidget(index_bricklet)
        widget_spin_span = widgetSpinBoxSpanSlider()

        self.setRangeWidgetSpinBoxSpanSlider(SUPPORTED_BRICKLETS[cbox_bricklet.currentText()],
                                             widget_spin_span)

        if new:
            self.set_initial_value_widget_spinBoxSpanSlider(widget_spin_span)
        else:
            widget_spin_span.sbox_upper.setValue(high)
            widget_spin_span.sbox_lower.setValue(low)

        widget_spin_span.span_slider.setColorOutsideRange(color)
        widget_spin_span.sbox_upper.valueChanged.connect(self.slot_sbox_value_changed)
        widget_spin_span.sbox_lower.valueChanged.connect(self.slot_sbox_value_changed)
        self.tview_sm_rules.setIndexWidget(index, widget_spin_span)

    def setRangeWidgetSpinBoxSpanSlider(self, bricklet, widget_spin_span):
        if bricklet == 'ptc':
            widget_spin_span.span_slider.setRange(RANGE_MIN_PTC, RANGE_MAX_PTC)
            widget_spin_span.sbox_lower.setRange(RANGE_MIN_PTC, RANGE_MAX_PTC)
            widget_spin_span.sbox_upper.setRange(RANGE_MIN_PTC, RANGE_MAX_PTC)
    
        elif bricklet == 'temperature':
            widget_spin_span.span_slider.setRange(RANGE_MIN_TEMPERATURE, RANGE_MAX_TEMPERATURE)
            widget_spin_span.sbox_lower.setRange(RANGE_MIN_TEMPERATURE, RANGE_MAX_TEMPERATURE)
            widget_spin_span.sbox_upper.setRange(RANGE_MIN_TEMPERATURE, RANGE_MAX_TEMPERATURE)
    
        elif bricklet == 'humidity':
            widget_spin_span.span_slider.setRange(RANGE_MIN_HUMIDITY, RANGE_MAX_HUMIDITY)
            widget_spin_span.sbox_lower.setRange(RANGE_MIN_HUMIDITY, RANGE_MAX_HUMIDITY)
            widget_spin_span.sbox_upper.setRange(RANGE_MIN_HUMIDITY, RANGE_MAX_HUMIDITY)
    
        elif bricklet == 'ambient_light':
            widget_spin_span.span_slider.setRange(RANGE_MIN_AMBIENT_LIGHT, RANGE_MAX_AMBIENT_LIGHT)
            widget_spin_span.sbox_lower.setRange(RANGE_MIN_AMBIENT_LIGHT, RANGE_MAX_AMBIENT_LIGHT)
            widget_spin_span.sbox_upper.setRange(RANGE_MIN_AMBIENT_LIGHT, RANGE_MAX_AMBIENT_LIGHT)

    def set_initial_value_widget_spinBoxSpanSlider(self, widget_spin_span):
        span_minimum = widget_spin_span.span_slider.minimum()
        span_maximum = widget_spin_span.span_slider.maximum()
        span = abs(span_minimum - span_maximum)
        span_mid = span/2
        widget_spin_span.sbox_upper.setValue(0)
        widget_spin_span.sbox_lower.setValue(0)
        widget_spin_span.sbox_upper.setValue(span_mid + abs(span_mid - span_maximum)/2)
        widget_spin_span.sbox_lower.setValue(span_minimum + abs(span_mid - span_minimum)/2)

    def set_default_col_width_hosts(self):
        self.tview_sm_hosts.setColumnWidth(INDEX_COL_HOSTS_HOST, DEFAULT_COL_WIDTH_HOSTS_HOST)
        self.tview_sm_hosts.setColumnWidth(INDEX_COL_HOSTS_PORT, DEFAULT_COL_WIDTH_HOSTS_PORT)
        self.tview_sm_hosts.setColumnWidth(INDEX_COL_HOSTS_AUTHENTICATION, DEFAULT_COL_WIDTH_HOSTS_AUTHENTICATION)
        self.tview_sm_hosts.setColumnWidth(INDEX_COL_HOSTS_SECRET, DEFAULT_COL_WIDTH_HOSTS_SECRET)
        self.tview_sm_hosts.setColumnWidth(INDEX_COL_HOSTS_REMOVE, DEFAULT_COL_WIDTH_HOSTS_REMOVE)

    def set_default_col_width_rules(self):
        self.tview_sm_rules.setColumnWidth(INDEX_COL_RULES_NAME, DEFAULT_COL_WIDTH_RULES_NAME)
        #self.tview_sm_rules.setColumnWidth(INDEX_COL_RULES_HOST, DEFAULT_COL_WIDTH_RULES_HOST)
        self.tview_sm_rules.setColumnWidth(INDEX_COL_RULES_BRICKLET, DEFAULT_COL_WIDTH_RULES_BRICKLET)
        self.tview_sm_rules.setColumnWidth(INDEX_COL_RULES_UID, DEFAULT_COL_WIDTH_RULES_UID)
        self.tview_sm_rules.setColumnWidth(INDEX_COL_RULES_WARNING, DEFAULT_COL_WIDTH_RULES_WARNING)
        self.tview_sm_rules.setColumnWidth(INDEX_COL_RULES_CRITICAL, DEFAULT_COL_WIDTH_RULES_CRITICAL)
        self.tview_sm_rules.setColumnWidth(INDEX_COL_RULES_EMAIL_NOTIFICATIONS, DEFAULT_COL_WIDTH_RULES_EMAIL_NOTIFICATIONS)
        self.tview_sm_rules.setColumnWidth(INDEX_COL_RULES_REMOVE, DEFAULT_COL_WIDTH_RULES_REMOVE)

    def cb_settings_server_monitoring_get(self, result):
        if not report_script_result(result, MESSAGEBOX_TITLE, MESSAGE_ERROR_GET_FAILED):
            self.update_gui(EVENT_RETURNED_REFRESH_FALSE)
            self.update_gui(EVENT_RETURNED_REFRESH_FALSE)
            return

        dict_return = json.loads(result.stdout)

        if dict_return['rules']:
            self.model_rules.clear()
            self.model_rules.setHorizontalHeaderLabels(HEADERS_TVIEW_RULES)
            self.tview_sm_rules.setModel(self.model_rules)
            self.set_default_col_width_rules()

            for dict_rule in dict_return['rules']:
                self.add_new_rule(NOT_NEW,
                                  dict_rule['name'],
                                  'Host',
                                  dict_rule['bricklet'],
                                  dict_rule['uid'],
                                  dict_rule['warning_low'],
                                  dict_rule['warning_high'],
                                  dict_rule['critical_low'],
                                  dict_rule['critical_high'],
                                  dict_rule['email_notification_enabled'],
                                  dict_rule['email_notifications'])

        if dict_return['email']:
            self.chkbox_sm_email_enable.setCheckState(QtCore.Qt.Checked)
            self.ledit_sm_email_from.setText(dict_return['email']['from'])
            self.ledit_sm_email_to.setText(dict_return['email']['to'])
            self.ledit_sm_email_server.setText(dict_return['email']['server'])
            self.sbox_sm_email_port.setValue(int(dict_return['email']['port']))
            self.ledit_sm_email_username.setText(dict_return['email']['username'])
            self.ledit_sm_email_password.setText(dict_return['email']['password'])
            if dict_return['email']['tls'] == 'yes':
                self.chkbox_sm_email_tls.setCheckState(QtCore.Qt.Checked)
            else:
                self.chkbox_sm_email_tls.setCheckState(QtCore.Qt.Unchecked)
        else:
            self.chkbox_sm_email_enable.setCheckState(QtCore.Qt.Unchecked)

        self.update_gui(EVENT_RETURNED_REFRESH_TRUE)
        self.update_gui(EVENT_RETURNED_REFRESH_TRUE)

    def cb_settings_server_monitoring_apply(self, result):
        if not report_script_result(result, MESSAGEBOX_TITLE, MESSAGE_ERROR_SAVE_NOT_OK):
            self.update_gui(EVENT_RETURNED_SAVE_FALSE)
            return

        QtGui.QMessageBox.information(get_main_window(),
                                      MESSAGEBOX_TITLE,
                                      MESSAGE_INFO_SAVE_OK)

        self.update_gui(EVENT_RETURNED_SAVE_TRUE)
        self.slot_pbutton_sm_refresh_clicked()

    def is_ascii(self, text):
        try:
            text.encode('ascii')
            return True
        except:
            return False

    def populate_cbox_uids(self, cbox_bricklet, cbox_uids):
        def find_matched_index(search_for, search_in):
            if search_for not in search_in:
                return -1
            else:
                for index, element in enumerate(search_in):
                    if element == search_for:
                        return index

        if SUPPORTED_BRICKLETS[cbox_bricklet.currentText()] == 'ptc':
            cbox_uids.clear()
            cbox_uids.addItems(self.uids_ptc)

            uid_from_rule = cbox_bricklet.itemData(cbox_bricklet.currentIndex(), QtCore.Qt.UserRole)

            if uid_from_rule:
                index_found = find_matched_index(uid_from_rule, self.uids_ptc)

                if index_found > -1:
                    cbox_uids.setCurrentIndex(index_found)
                else:
                    cbox_uids.insertItem(0, uid_from_rule)
                    cbox_uids.setCurrentIndex(0)

            if cbox_uids.count() == 1:
                cbox_uids.setEditable(True)
                cbox_uids.setInsertPolicy(QtGui.QComboBox.InsertBeforeCurrent)
                cbox_uids.lineEdit().selectAll()
            else:
                cbox_uids.setEditable(False)

        elif SUPPORTED_BRICKLETS[cbox_bricklet.currentText()] == 'temperature':
            cbox_uids.clear()
            cbox_uids.addItems(self.uids_temperature)

            uid_from_rule = cbox_bricklet.itemData(cbox_bricklet.currentIndex(), QtCore.Qt.UserRole)

            if uid_from_rule:
                index_found = find_matched_index(uid_from_rule, self.uids_temperature)

                if index_found > -1:
                    cbox_uids.setCurrentIndex(index_found)
                else:
                    cbox_uids.insertItem(0, uid_from_rule)
                    cbox_uids.setCurrentIndex(0)

            if cbox_uids.count() == 1:
                cbox_uids.setEditable(True)
                cbox_uids.setInsertPolicy(QtGui.QComboBox.InsertBeforeCurrent)
                cbox_uids.lineEdit().selectAll()
            else:
                cbox_uids.setEditable(False)

        elif SUPPORTED_BRICKLETS[cbox_bricklet.currentText()] == 'humidity':
            cbox_uids.clear()
            cbox_uids.addItems(self.uids_humidity)

            uid_from_rule = cbox_bricklet.itemData(cbox_bricklet.currentIndex(), QtCore.Qt.UserRole)

            if uid_from_rule:
                index_found = find_matched_index(uid_from_rule, self.uids_humidity)

                if index_found > -1:
                    cbox_uids.setCurrentIndex(index_found)
                else:
                    cbox_uids.insertItem(0, uid_from_rule)
                    cbox_uids.setCurrentIndex(0)

            if cbox_uids.count() == 1:
                cbox_uids.setEditable(True)
                cbox_uids.setInsertPolicy(QtGui.QComboBox.InsertBeforeCurrent)
                cbox_uids.lineEdit().selectAll()
            else:
                cbox_uids.setEditable(False)

        elif SUPPORTED_BRICKLETS[cbox_bricklet.currentText()] == 'ambient_light':
            cbox_uids.clear()
            cbox_uids.addItems(self.uids_ambient_light)

            uid_from_rule = cbox_bricklet.itemData(cbox_bricklet.currentIndex(), QtCore.Qt.UserRole)

            if uid_from_rule:
                index_found = find_matched_index(uid_from_rule, self.uids_ambient_light)

                if index_found > -1:
                    cbox_uids.setCurrentIndex(index_found)
                else:
                    cbox_uids.insertItem(0, uid_from_rule)
                    cbox_uids.setCurrentIndex(0)

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
                if c == INDEX_COL_RULES_NAME:
                    item = self.model_rules.item(r, c)
                    index = self.model_rules.indexFromItem(item)
                    ledit_name_text = self.tview_sm_rules.indexWidget(index).text()

                    if EMPTY_SERVICE_NAME in ledit_name_text or not ledit_name_text:
                        return r, c, CHECK_FAILED_SERVICE_NAME_EMPTY
                    elif ledit_name_text in list_service_names:
                        return r, c,  CHECK_FAILED_SERVICE_NAME_DUPLICATE
                    elif not self.is_ascii(ledit_name_text):
                        return r, c,  CHECK_FAILED_NON_ASCII
                    else:
                        list_service_names.append(ledit_name_text)

                # Check UID field
                elif c == INDEX_COL_RULES_UID:
                    item = self.model_rules.item(r, c)
                    index = self.model_rules.indexFromItem(item)
                    uid = self.tview_sm_rules.indexWidget(index).currentText()

                    if EMPTY_UID in uid or not uid:
                        return r, c, CHECK_FAILED_UID_EMPTY
                    elif not self.is_ascii(uid):
                        return r, c, CHECK_FAILED_NON_ASCII
                    else:
                        for c in list(uid):
                            if c not in BASE58:
                                return r, c, CHECK_FAILED_UID_INVALID

                # Check Email fields
                elif self.chkbox_sm_email_enable.isChecked():
                    email_from     = self.ledit_sm_email_from.text()
                    email_to       = self.ledit_sm_email_to.text()
                    email_server   = self.ledit_sm_email_server.text()
                    email_username = self.ledit_sm_email_username.text()
                    email_password = self.ledit_sm_email_password.text()

                    if not email_from:
                        return None, None, CHECK_FAILED_EMAIL_FROM_EMPTY

                    elif not self.is_ascii(email_from):
                        return None, None,  CHECK_FAILED_EMAIL_FROM_NON_ASCII

                    elif ' ' in email_from:
                        return None, None,  CHECK_FAILED_EMAIL_FROM_WHITESPACE

                    elif not email_to:
                        return None, None, CHECK_FAILED_EMAIL_TO_EMPTY

                    elif not self.is_ascii(email_to):
                        return None, None,  CHECK_FAILED_EMAIL_TO_NON_ASCII

                    elif ' ' in email_to:
                        return None, None,  CHECK_FAILED_EMAIL_TO_WHITESPACE

                    elif not email_server:
                        return None, None, CHECK_FAILED_EMAIL_SERVER_EMPTY

                    elif not self.is_ascii(email_server):
                        return None, None,  CHECK_FAILED_EMAIL_SERVER_NON_ASCII

                    elif ' ' in email_server:
                        return None, None,  CHECK_FAILED_EMAIL_SERVER_WHITESPACE

                    elif not email_username:
                        return None, None, CHECK_FAILED_EMAIL_USERNAME_EMPTY

                    elif not self.is_ascii(email_username):
                        return None, None,  CHECK_FAILED_EMAIL_USERNAME_NON_ASCII

                    elif ' ' in email_username:
                        return None, None,  CHECK_FAILED_EMAIL_USERNAME_WHITESPACE

                    elif not email_password:
                        return None, None, CHECK_FAILED_EMAIL_PASSWORD_EMPTY

                    elif not self.is_ascii(email_password):
                        return None, None,  CHECK_FAILED_EMAIL_PASSWORD_NON_ASCII

        return None, None, CHECK_OK

    def show_working_wait(self, show):
        if show:
            self.label_sm_working_wait.show()
            self.pbar_sm_working_wait.show()
        else:
            self.label_sm_working_wait.hide()
            self.pbar_sm_working_wait.hide()

    def add_new_rule(self,
                     new,
                     name                       = None,
                     host                       = None,
                     bricklet                   = None,
                     uid                        = None,
                     warning_low                = None,
                     warning_high               = None,
                     critical_low               = None,
                     critical_high              = None,
                     email_notification_enabled = None,
                     email_notifications        = None):
        rule = []

        for i in range(0, COUNT_COLUMNS_RULES_MODEL):
            rule.append(QtGui.QStandardItem(''))

        self.model_rules.appendRow(rule)

        r = self.model_rules.rowCount() - 1

        for c in range(0, COUNT_COLUMNS_RULES_MODEL):
            # Add Name field widget
            if c == INDEX_COL_RULES_NAME:
                item = self.model_rules.item(r, c)
                index = self.model_rules.indexFromItem(item)
                ledit_name = QtGui.QLineEdit()
                ledit_name.textEdited.connect(self.slot_ledit_edited)

                if new:
                    ledit_name.setText(EMPTY_SERVICE_NAME)
                    ledit_name.selectAll()
                else:
                    ledit_name.setText(name)

                self.tview_sm_rules.setIndexWidget(index, ledit_name)

            # Add Host field widget
            #elif c == INDEX_COL_RULES_HOST:
            #    item = self.model_rules.item(r, c)
            #    index = self.model_rules.indexFromItem(item)
            #    cbox = QtGui.QComboBox()

            #    self.tview_sm_rules.setIndexWidget(index, cbox)

            # Add Bricklet field widget
            elif c == INDEX_COL_RULES_BRICKLET:
                item = self.model_rules.item(r, c)
                index = self.model_rules.indexFromItem(item)
                cbox = QtGui.QComboBox()
                cbox.addItems(SUPPORTED_BRICKLETS.keys())

                if not new:
                    for i in range(0, cbox.count()):
                        if bricklet == SUPPORTED_BRICKLETS[cbox.itemText(i)]:
                            cbox.setCurrentIndex(i)
                            cbox.setItemData(i, uid, QtCore.Qt.UserRole)
                            break

                cbox.activated.connect(self.slot_cbox_bricklet_activated)
                self.tview_sm_rules.setIndexWidget(index, cbox)

            # Add UID field widget
            elif c == INDEX_COL_RULES_UID:
                item_uid = self.model_rules.item(r, c)
                index_uid = self.model_rules.indexFromItem(item_uid)
                cbox_uid = QtGui.QComboBox()
                item_bricklet = self.model_rules.item(r, c - 1)
                index_bricklet = self.model_rules.indexFromItem(item_bricklet)
                cbox_bricklet = self.tview_sm_rules.indexWidget(index_bricklet)

                self.populate_cbox_uids(cbox_bricklet, cbox_uid)

                cbox_uid.activated.connect(self.slot_cbox_uid_activated)
                self.tview_sm_rules.setIndexWidget(index_uid, cbox_uid)

            # Add Warning field widget
            elif c == INDEX_COL_RULES_WARNING:
                if new:
                    self.add_widget_spin_span(r, c, new, COLOR_WARNING)
                else:
                    self.add_widget_spin_span(r, c, new, COLOR_WARNING,
                                              int(warning_low), int(warning_high))

            # Add Critical field widget
            elif c == INDEX_COL_RULES_CRITICAL:
                if new:
                    self.add_widget_spin_span(r, c, new, COLOR_CRITICAL)
                else:
                    self.add_widget_spin_span(r, c, new, COLOR_CRITICAL,
                                              int(critical_low), int(critical_high))

            # Add Email field widget
            elif c == INDEX_COL_RULES_EMAIL_NOTIFICATIONS:
                item = self.model_rules.item(r, c)
                index = self.model_rules.indexFromItem(item)
                cbox = QtGui.QComboBox()
                cbox.addItems(COLUMN_EMAIL_NOTIFICATIONS_ITEMS)

                if not new and email_notification_enabled == '1':
                    if email_notifications == 'c,r':
                        cbox.setCurrentIndex(INDEX_EMAIL_CRITICAL)
                    elif email_notifications == 'w,c,r':
                        cbox.setCurrentIndex(INDEX_EMAIL_WARNING_CRITICAL)

                if self.chkbox_sm_email_enable.isChecked():
                    cbox.setEnabled(True)
                else:
                    cbox.setEnabled(False)

                cbox.activated.connect(self.slot_cbox_email_activated)
                self.tview_sm_rules.setIndexWidget(index, cbox)

            # Add Remove field widget
            elif c == INDEX_COL_RULES_REMOVE:
                item = self.model_rules.item(r, c)
                index = self.model_rules.indexFromItem(item)
                btn = QtGui.QPushButton('X')
                btn.clicked.connect(self.slot_remove_rule_clicked)
                self.tview_sm_rules.setIndexWidget(index, btn)

    def update_gui(self, event):
        if event == EVENT_CLICKED_REMOVE_ALL:
            self.chkbox_sm_email_enable.setCheckState(QtCore.Qt.Unchecked)

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

        elif event == EVENT_RETURNED_REFRESH_TRUE:
            self.show_working_wait(False)
            self.sarea_sm.setEnabled(True)
            self.pbutton_sm_refresh.setText('Refresh')
            self.pbutton_sm_save.setText('Save')
    
            if self.model_rules.rowCount() > 0:
                self.pbutton_sm_remove_all_rules.setEnabled(True)

            self.pbutton_sm_save.setEnabled(False)

        elif event == EVENT_RETURNED_REFRESH_FALSE:
            self.show_working_wait(False)
            self.sarea_sm.setEnabled(True)
            self.pbutton_sm_refresh.setText('Refresh')
            self.pbutton_sm_save.setText('Save')

            if self.model_rules.rowCount() > 0:
                self.pbutton_sm_remove_all_rules.setEnabled(True)

        elif event == EVENT_RETURNED_SAVE_TRUE:
            self.show_working_wait(False)
            self.sarea_sm.setEnabled(True)
            self.pbutton_sm_save.setText('Save')
            self.pbutton_sm_save.setEnabled(False)

        elif event == EVENT_RETURNED_SAVE_FALSE:
            self.show_working_wait(False)
            self.sarea_sm.setEnabled(True)
            self.pbutton_sm_save.setText('Save')
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
        self.add_new_rule(NEW)
        self.update_gui(EVENT_INPUT_CHANGED)

    def slot_pbutton_sm_remove_all_rules_clicked(self):
        reply = QtGui.QMessageBox.question(get_main_window(),
                                           'Settings | Server Monitoring',
                                           'Are you sure you want to remove all rules?',
                                           QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)

        if (reply == QtGui.QMessageBox.Yes):
            self.model_rules.removeRows(0, self.model_rules.rowCount())
            self.pbutton_sm_remove_all_rules.setEnabled(False)
            self.update_gui(EVENT_CLICKED_REMOVE_ALL)
            self.update_gui(EVENT_INPUT_CHANGED)

    def slot_pbutton_sm_add_host_clicked(self):
        add_host_dialog = REDTabSettingsServerMonitoringAddHostDialog(self)
        return_code_dialog = add_host_dialog.exec_()

        if return_code_dialog == QtGui.QDialog.Accepted:
            print 'ACCEPTED'
            #read the data and save
            #destroy the dialog
            add_host_dialog.done(0)
        else:
            print 'REJECTED'
            add_host_dialog.done(0)
            #destroy the dialog

    def slot_pbutton_sm_refresh_clicked(self):
        self.update_gui(EVENT_CLICKED_REFRESH)

        # Populating bricklet UID lists
        self.uids_ptc = []
        self.uids_temperature = []
        self.uids_humidity = []
        self.uids_ambient_light = []

        for bricklet in infos.get_bricklet_infos():
            if bricklet.device_identifier == BrickletPTC.DEVICE_IDENTIFIER:
                self.uids_ptc.append(bricklet.uid)
            elif bricklet.device_identifier == BrickletTemperature.DEVICE_IDENTIFIER:
                self.uids_temperature.append(bricklet.uid)
            elif bricklet.device_identifier == BrickletHumidity.DEVICE_IDENTIFIER:
                self.uids_humidity.append(bricklet.uid)
            elif bricklet.device_identifier == BrickletAmbientLight.DEVICE_IDENTIFIER:
                self.uids_ambient_light.append(bricklet.uid)

        self.uids_ptc.append(EMPTY_UID)
        self.uids_temperature.append(EMPTY_UID)
        self.uids_humidity.append(EMPTY_UID)
        self.uids_ambient_light.append(EMPTY_UID)

        self.script_manager.execute_script('settings_server_monitoring',
                                           self.cb_settings_server_monitoring_get,
                                           ['GET'])

    def slot_pbutton_sm_save_clicked(self):
        self.update_gui(EVENT_CLICKED_SAVE)

        if self.model_rules.rowCount() > 0:
            rule_number, field_number, check_result = self.check_rules()
            rule = 'Rule-' + str(rule_number) + ', Field-' + str(field_number) + ': '

            if check_result == CHECK_FAILED_SERVICE_NAME_EMPTY:
                QtGui.QMessageBox.critical(get_main_window(),
                                           MESSAGEBOX_TITLE,
                                           rule + MESSAGE_ERROR_CHECK_SERVICE_NAME_EMPTY)
                self.update_gui(EVENT_RETURNED_SAVE_FALSE)
                return

            elif check_result == CHECK_FAILED_SERVICE_NAME_DUPLICATE:
                QtGui.QMessageBox.critical(get_main_window(),
                                           MESSAGEBOX_TITLE,
                                           rule + MESSAGE_ERROR_CHECK_SERVICE_NAME_DUPLICATE)
                self.update_gui(EVENT_RETURNED_SAVE_FALSE)
                return

            elif check_result == CHECK_FAILED_UID_EMPTY:
                QtGui.QMessageBox.critical(get_main_window(),
                                           MESSAGEBOX_TITLE,
                                           rule + MESSAGE_ERROR_CHECK_UID_EMPTY)
                self.update_gui(EVENT_RETURNED_SAVE_FALSE)
                return

            elif check_result == CHECK_FAILED_UID_INVALID:
                QtGui.QMessageBox.critical(get_main_window(),
                                           MESSAGEBOX_TITLE,
                                           rule + MESSAGE_ERROR_CHECK_UID_INVALID)
                self.update_gui(EVENT_RETURNED_SAVE_FALSE)
                return

            elif check_result == CHECK_FAILED_NON_ASCII:
                QtGui.QMessageBox.critical(get_main_window(),
                                           MESSAGEBOX_TITLE,
                                           rule + MESSAGE_ERROR_CHECK_NON_ASCII)
                self.update_gui(EVENT_RETURNED_SAVE_FALSE)
                return

            elif check_result == CHECK_FAILED_EMAIL_FROM_EMPTY:
                QtGui.QMessageBox.critical(get_main_window(),
                                           MESSAGEBOX_TITLE,
                                           MESSAGE_ERROR_CHECK_EMAIL_FROM_EMPTY)
                self.update_gui(EVENT_RETURNED_SAVE_FALSE)
                return

            elif check_result == CHECK_FAILED_EMAIL_FROM_NON_ASCII:
                QtGui.QMessageBox.critical(get_main_window(),
                                           MESSAGEBOX_TITLE,
                                           MESSAGE_ERROR_CHECK_EMAIL_FROM_NON_ASCII)
                self.update_gui(EVENT_RETURNED_SAVE_FALSE)
                return

            elif check_result == CHECK_FAILED_EMAIL_FROM_WHITESPACE:
                QtGui.QMessageBox.critical(get_main_window(),
                                           MESSAGEBOX_TITLE,
                                           MESSAGE_ERROR_CHECK_EMAIL_FROM_WHITESPACE)
                self.update_gui(EVENT_RETURNED_SAVE_FALSE)
                return

            elif check_result == CHECK_FAILED_EMAIL_TO_EMPTY:
                QtGui.QMessageBox.critical(get_main_window(),
                                           MESSAGEBOX_TITLE,
                                           MESSAGE_ERROR_CHECK_EMAIL_TO_EMPTY)
                self.update_gui(EVENT_RETURNED_SAVE_FALSE)
                return

            elif check_result == CHECK_FAILED_EMAIL_TO_NON_ASCII:
                QtGui.QMessageBox.critical(get_main_window(),
                                           MESSAGEBOX_TITLE,
                                           MESSAGE_ERROR_CHECK_EMAIL_TO_NON_ASCII)
                self.update_gui(EVENT_RETURNED_SAVE_FALSE)
                return

            elif check_result == CHECK_FAILED_EMAIL_TO_WHITESPACE:
                QtGui.QMessageBox.critical(get_main_window(),
                                           MESSAGEBOX_TITLE,
                                           MESSAGE_ERROR_CHECK_EMAIL_TO_WHITESPACE)
                self.update_gui(EVENT_RETURNED_SAVE_FALSE)
                return

            elif check_result == CHECK_FAILED_EMAIL_SERVER_EMPTY:
                QtGui.QMessageBox.critical(get_main_window(),
                                           MESSAGEBOX_TITLE,
                                           MESSAGE_ERROR_CHECK_EMAIL_SERVER_EMPTY)
                self.update_gui(EVENT_RETURNED_SAVE_FALSE)
                return

            elif check_result == CHECK_FAILED_EMAIL_SERVER_NON_ASCII:
                QtGui.QMessageBox.critical(get_main_window(),
                                           MESSAGEBOX_TITLE,
                                           MESSAGE_ERROR_CHECK_EMAIL_SERVER_NON_ASCII)
                self.update_gui(EVENT_RETURNED_SAVE_FALSE)
                return

            elif check_result == CHECK_FAILED_EMAIL_SERVER_WHITESPACE:
                QtGui.QMessageBox.critical(get_main_window(),
                                           MESSAGEBOX_TITLE,
                                           MESSAGE_ERROR_CHECK_EMAIL_SERVER_WHITESPACE)
                self.update_gui(EVENT_RETURNED_SAVE_FALSE)
                return

            elif check_result == CHECK_FAILED_EMAIL_USERNAME_EMPTY:
                QtGui.QMessageBox.critical(get_main_window(),
                                           MESSAGEBOX_TITLE,
                                           MESSAGE_ERROR_CHECK_EMAIL_USERNAME_EMPTY)
                self.update_gui(EVENT_RETURNED_SAVE_FALSE)
                return

            elif check_result == CHECK_FAILED_EMAIL_USERNAME_NON_ASCII:
                QtGui.QMessageBox.critical(get_main_window(),
                                           MESSAGEBOX_TITLE,
                                           MESSAGE_ERROR_CHECK_EMAIL_USERNAME_NON_ASCII)
                self.update_gui(EVENT_RETURNED_SAVE_FALSE)
                return

            elif check_result == CHECK_FAILED_EMAIL_USERNAME_WHITESPACE:
                QtGui.QMessageBox.critical(get_main_window(),
                                           MESSAGEBOX_TITLE,
                                           MESSAGE_ERROR_CHECK_EMAIL_USERNAME_WHITESPACE)
                self.update_gui(EVENT_RETURNED_SAVE_FALSE)
                return

            elif check_result == CHECK_FAILED_EMAIL_PASSWORD_EMPTY:
                QtGui.QMessageBox.critical(get_main_window(),
                                           MESSAGEBOX_TITLE,
                                           MESSAGE_ERROR_CHECK_EMAIL_PASSWORD_EMPTY)
                self.update_gui(EVENT_RETURNED_SAVE_FALSE)
                return

            elif check_result == CHECK_FAILED_EMAIL_PASSWORD_NON_ASCII:
                QtGui.QMessageBox.critical(get_main_window(),
                                           MESSAGEBOX_TITLE,
                                           MESSAGE_ERROR_CHECK_EMAIL_PASSWORD_NON_ASCII)
                self.update_gui(EVENT_RETURNED_SAVE_FALSE)
                return

            # Generate data structure here
            apply_dict = {}

            apply_dict['rules'] = []

            for r in range(self.model_rules.rowCount()):
                widget_name                = None
                widget_bricklet            = None
                widget_uid                 = None
                widget_warning             = None
                widget_critical            = None
                widget_email_notifications = None

                for c in range(0, COUNT_COLUMNS_RULES_MODEL):
                    item = self.model_rules.item(r, c)
                    index = self.model_rules.indexFromItem(item)

                    if c == INDEX_COL_RULES_NAME:
                        widget_name = self.tview_sm_rules.indexWidget(index)

                    elif c == INDEX_COL_RULES_BRICKLET:
                        widget_bricklet = self.tview_sm_rules.indexWidget(index)

                    elif c == INDEX_COL_RULES_UID:
                        widget_uid = self.tview_sm_rules.indexWidget(index)

                    elif c == INDEX_COL_RULES_WARNING:
                        widget_warning = self.tview_sm_rules.indexWidget(index)

                    elif c == INDEX_COL_RULES_CRITICAL:
                        widget_critical = self.tview_sm_rules.indexWidget(index)

                    elif c == INDEX_COL_RULES_EMAIL_NOTIFICATIONS:
                        widget_email_notifications = self.tview_sm_rules.indexWidget(index)

                command_line = '''/usr/local/bin/check_tinkerforge.py \
-b {0} \
-u {1} \
-m range \
-w {2} \
-c {3} \
-w2 {4} \
-c2 {5}'''.format(SUPPORTED_BRICKLETS[widget_bricklet.currentText()],
                  widget_uid.currentText(),
                  str(widget_warning.sbox_upper.value()),
                  str(widget_critical.sbox_upper.value()),
                  str(widget_warning.sbox_lower.value()),
                  str(widget_critical.sbox_lower.value()))

                if widget_email_notifications.currentIndex() == INDEX_EMAIL_NO_NOTIFICATIONS or \
                   not self.chkbox_sm_email_enable.isChecked():
                        notification_options  = 'c,r'
                        notifications_enabled = '0'
                        contact_groups        = 'admins'

                elif widget_email_notifications.currentIndex() == INDEX_EMAIL_CRITICAL:
                        notification_options  = 'c,r'
                        notifications_enabled = '1'
                        contact_groups        = 'tinkerforge-contact-group'

                elif widget_email_notifications.currentIndex() == INDEX_EMAIL_WARNING_CRITICAL:
                        notification_options  = 'w,c,r'
                        notifications_enabled = '1'
                        contact_groups        = 'tinkerforge-contact-group'

                service_description   = widget_name.text()
                command_line          = command_line
                check_command         = 'tinkerforge-command-' + str(r)
                notification_options  = notification_options
                notifications_enabled = notifications_enabled

                a_rule = {'service_description'  : service_description,
                          'command_line'         : command_line,
                          'check_command'        : check_command,
                          'notification_options' : notification_options,
                          'notifications_enabled': notifications_enabled,
                          'contact_groups'       : contact_groups}

                apply_dict['rules'].append(a_rule)

            if self.chkbox_sm_email_enable.isChecked():
                email_from     = self.ledit_sm_email_from.text()
                email_to       = self.ledit_sm_email_to.text()
                email_server   = self.ledit_sm_email_server.text()
                email_port     = str(self.sbox_sm_email_port.value())
                email_username = self.ledit_sm_email_username.text()
                email_password = self.ledit_sm_email_password.text()

                if self.chkbox_sm_email_tls.isChecked():
                    email_tls = 'yes'
                else:
                    email_tls = 'no'

                apply_dict['email'] = {'from'    :email_from,
                                       'to'      :email_to,
                                       'server'  :email_server,
                                       'port'    :email_port,
                                       'username':email_username,
                                       'password':email_password,
                                       'tls'     :email_tls}
            else:
                apply_dict['email'] = None

            self.script_manager.execute_script('settings_server_monitoring',
                                               self.cb_settings_server_monitoring_apply,
                                               ['APPLY', json.dumps(apply_dict)])

        else:
            self.script_manager.execute_script('settings_server_monitoring',
                                               self.cb_settings_server_monitoring_apply,
                                               ['APPLY_EMPTY'])

    def slot_chkbox_sm_email_enable_state_changed(self, state):
        if state == QtCore.Qt.Checked:
            for r in range(self.model_rules.rowCount()):
                item = self.model_rules.item(r, INDEX_COL_RULES_EMAIL_NOTIFICATIONS)
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
                item = self.model_rules.item(r, INDEX_COL_RULES_EMAIL_NOTIFICATIONS)
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

    def slot_chkbox_sm_email_tls_state_changed(self, state):
        self.update_gui(EVENT_INPUT_CHANGED)

    def slot_cbox_bricklet_activated(self, index):
        sender = self.sender()

        for r in range(self.model_rules.rowCount()):
            for c in range(0, COUNT_COLUMNS_RULES_MODEL):
                item = self.model_rules.item(r, c)
                index = self.model_rules.indexFromItem(item)

                if sender == self.tview_sm_rules.indexWidget(index):
                    item_cbox_uids = self.model_rules.item(r, INDEX_COL_RULES_UID)
                    index_cbox_uids = self.model_rules.indexFromItem(item_cbox_uids)
                    item_warning_widget_spin_span = self.model_rules.item(r, INDEX_COL_RULES_WARNING)
                    index_warning_widget_spin_span = self.model_rules.indexFromItem(item_warning_widget_spin_span)
                    item_critical_widget_spin_span = self.model_rules.item(r, INDEX_COL_RULES_CRITICAL)
                    index_critical_widget_spin_span = self.model_rules.indexFromItem(item_critical_widget_spin_span)

                    cbox_uids = self.tview_sm_rules.indexWidget(index_cbox_uids)
                    warning_widget_spin_span = self.tview_sm_rules.indexWidget(index_warning_widget_spin_span)
                    critical_widget_spin_span = self.tview_sm_rules.indexWidget(index_critical_widget_spin_span)

                    self.populate_cbox_uids(sender, cbox_uids)
                    self.setRangeWidgetSpinBoxSpanSlider(SUPPORTED_BRICKLETS[sender.currentText()],
                                                         warning_widget_spin_span)
                    self.set_initial_value_widget_spinBoxSpanSlider(warning_widget_spin_span)
                    self.setRangeWidgetSpinBoxSpanSlider(SUPPORTED_BRICKLETS[sender.currentText()],
                                                         critical_widget_spin_span)
                    self.set_initial_value_widget_spinBoxSpanSlider(critical_widget_spin_span)

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
