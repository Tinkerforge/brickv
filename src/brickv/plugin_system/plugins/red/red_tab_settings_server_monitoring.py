# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2015 Ishraq Ibne Ashraf <ishraq@tinkerforge.com>

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

import re
from PyQt4 import QtCore, QtGui
from brickv.plugin_system.plugins.red.ui_red_tab_settings_server_monitoring import\
     Ui_REDTabSettingsServerMonitoring
from brickv.plugin_system.plugins.red.red_tab_settings_server_monitoring_add_host_dialog import\
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
from brickv.plugin_system.plugins.red.widget_spinbox_span_slider import\
     widgetSpinBoxSpanSlider
import json

# Constants
DEFAULT_COL_WIDTH_RULES_NAME                = 160
DEFAULT_COL_WIDTH_RULES_HOST                = 140
DEFAULT_COL_WIDTH_RULES_BRICKLET            = 140
DEFAULT_COL_WIDTH_RULES_UID                 = 130
DEFAULT_COL_WIDTH_RULES_WARNING             = 360
DEFAULT_COL_WIDTH_RULES_CRITICAL            = 360
DEFAULT_COL_WIDTH_RULES_UNIT                = 40
DEFAULT_COL_WIDTH_RULES_EMAIL_NOTIFICATIONS = 140
DEFAULT_COL_WIDTH_RULES_REMOVE              = 100
DEFAULT_COL_WIDTH_HOSTS_USED                = 40
DEFAULT_COL_WIDTH_HOSTS_HOST                = 200
DEFAULT_COL_WIDTH_HOSTS_PORT                = 250
DEFAULT_COL_WIDTH_HOSTS_AUTHENTICATION      = 200
DEFAULT_COL_WIDTH_HOSTS_SECRET              = 250
DEFAULT_COL_WIDTH_HOSTS_REFRESH_UIDS        = 200
DEFAULT_COL_WIDTH_HOSTS_REMOVE              = 200

HEADERS_TVIEW_RULES = ['Name',
                       'Host',
                       'Bricklet',
                       'UID',
                       'Warning',
                       'Critical',
                       'Unit',
                       'Email Notifications',
                       'Remove']

HEADERS_TVIEW_HOSTS = ['Used',
                       'Host',
                       'Port',
                       'Authentication',
                       'Secret',
                       'Refresh UIDs',
                       'Remove']

COLUMN_EMAIL_NOTIFICATIONS_ITEMS = ['No Notifications',
                                    'Critical',
                                    'Critical/Warning']

SUPPORTED_BRICKLETS = {'PTC (2-/4-wire)' :{'id':'ptc24', 'unit':'°C'.decode('utf-8')},
                       'PTC (3-wire)'    :{'id':'ptc3', 'unit':'°C'.decode('utf-8')},
                       'Temperature'     :{'id':'temperature', 'unit':'°C'.decode('utf-8')},
                       'Humidity'        :{'id':'humidity', 'unit':'%RH'},
                       'Ambient Light'   :{'id':'ambient_light', 'unit':'Lux'}}

ITEMS_AUTHENTICATION = ['On', 'Off']

RANGE_MIN_PTC           = 0
RANGE_MAX_PTC           = 100
RANGE_MIN_TEMPERATURE   = 0
RANGE_MAX_TEMPERATURE   = 100
RANGE_MIN_HUMIDITY      = 0
RANGE_MAX_HUMIDITY      = 100
RANGE_MIN_AMBIENT_LIGHT = 0
RANGE_MAX_AMBIENT_LIGHT = 1300 # Ambient Light = fixed 900, Ambient Light 2.0 = configured to 1300

INDEX_EMAIL_NO_NOTIFICATIONS        = 0
INDEX_EMAIL_CRITICAL                = 1
INDEX_EMAIL_WARNING_CRITICAL        = 2
INDEX_COL_RULES_NAME                = 0
INDEX_COL_RULES_HOST                = 1
INDEX_COL_RULES_BRICKLET            = 2
INDEX_COL_RULES_UID                 = 3
INDEX_COL_RULES_WARNING             = 4
INDEX_COL_RULES_CRITICAL            = 5
INDEX_COL_RULES_UNIT                = 6
INDEX_COL_RULES_EMAIL_NOTIFICATIONS = 7
INDEX_COL_RULES_REMOVE              = 8
INDEX_COL_HOSTS_USED                = 0
INDEX_COL_HOSTS_HOST                = 1
INDEX_COL_HOSTS_PORT                = 2
INDEX_COL_HOSTS_AUTHENTICATION      = 3
INDEX_COL_HOSTS_SECRET              = 4
INDEX_COL_HOSTS_REFRESH_UIDS        = 5
INDEX_COL_HOSTS_REMOVE              = 6
INDEX_COL_HOSTS_HIDDEN_HOST         = 7

COUNT_COLUMNS_RULES_MODEL = 9
COUNT_COLUMNS_HOSTS_MODEL = 8

EVENT_CLICKED_REFRESH                = 1
EVENT_CLICKED_SAVE                   = 2
EVENT_CLICKED_REFRESH_GENERIC        = 3
EVENT_INPUT_CHANGED                  = 4
EVENT_RETURNED_REFRESH_TRUE          = 5
EVENT_RETURNED_REFRESH_FALSE         = 6
EVENT_RETURNED_SAVE_TRUE             = 7
EVENT_RETURNED_SAVE_FALSE            = 8
EVENT_RETURNED_REFRESH_GENERIC       = 9
EVENT_UPDATE_UIDS_IN_RULES           = 10

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
CHECK_FAILED_EMAIL_FROM_MALFORMED      = 9
CHECK_FAILED_EMAIL_TO_EMPTY            = 10
CHECK_FAILED_EMAIL_TO_NON_ASCII        = 11
CHECK_FAILED_EMAIL_TO_WHITESPACE       = 12
CHECK_FAILED_EMAIL_TO_MALFORMED        = 13
CHECK_FAILED_EMAIL_SERVER_EMPTY        = 14
CHECK_FAILED_EMAIL_SERVER_NON_ASCII    = 15
CHECK_FAILED_EMAIL_SERVER_WHITESPACE   = 16
CHECK_FAILED_EMAIL_USERNAME_EMPTY      = 17
CHECK_FAILED_EMAIL_USERNAME_NON_ASCII  = 18
CHECK_FAILED_EMAIL_USERNAME_WHITESPACE = 19
CHECK_FAILED_EMAIL_PASSWORD_EMPTY      = 20
CHECK_FAILED_EMAIL_PASSWORD_NON_ASCII  = 21
CHECK_FAILED_NON_ASCII                 = 22

MESSAGEBOX_TITLE                              = 'Settings | Server Monitoring'
MESSAGE_INFO_SAVE_OK                          = 'Rules saved and applied successfully'
MESSAGE_INFO_NO_RULES_TO_SAVE                 = 'No rules to save'
MESSAGE_INFO_TEST_EMAIL_SENT                  = 'Test email sent successfully'
MESSAGE_ERROR_SAVE_NOT_OK                     = 'Error occured while saving and applying rules'
MESSAGE_ERROR_GET_FAILED                      = 'Error occured while trying to get existing rules'
MESSAGE_ERROR_ENUMERATION_FAILED              = 'Error occured while enumerating host'
MESSAGE_ERROR_CHECK_SERVICE_NAME_EMPTY        = 'Service name empty'
MESSAGE_ERROR_CHECK_SERVICE_NAME_DUPLICATE    = 'Duplicated service name'
MESSAGE_ERROR_CHECK_UID_EMPTY                 = 'UID empty'
MESSAGE_ERROR_CHECK_UID_INVALID               = 'Invalid UID'
MESSAGE_ERROR_CHECK_EMAIL_FROM_EMPTY          = 'Email from address empty'
MESSAGE_ERROR_CHECK_EMAIL_FROM_NON_ASCII      = 'Email from address contains non ASCII character'
MESSAGE_ERROR_CHECK_EMAIL_FROM_WHITESPACE     = 'Email from address contains whitespace'
MESSAGE_ERROR_CHECK_EMAIL_FROM_MALFORMED      = 'Email from address is malformed'
MESSAGE_ERROR_CHECK_EMAIL_TO_EMPTY            = 'Email to address empty'
MESSAGE_ERROR_CHECK_EMAIL_TO_NON_ASCII        = 'Email to address contains non ASCII character'
MESSAGE_ERROR_CHECK_EMAIL_TO_WHITESPACE       = 'Email to address contains whitespace'
MESSAGE_ERROR_CHECK_EMAIL_TO_MALFORMED        = 'Email to address is malformed'
MESSAGE_ERROR_CHECK_EMAIL_SERVER_EMPTY        = 'SMTP server empty'
MESSAGE_ERROR_CHECK_EMAIL_SERVER_NON_ASCII    = 'SMTP server contains non ASCII character'
MESSAGE_ERROR_CHECK_EMAIL_SERVER_WHITESPACE   = 'SMTP server contains whitespace'
MESSAGE_ERROR_CHECK_EMAIL_USERNAME_EMPTY      = 'SMTP username empty'
MESSAGE_ERROR_CHECK_EMAIL_USERNAME_NON_ASCII  = 'SMTP username contains non ASCII character'
MESSAGE_ERROR_CHECK_EMAIL_USERNAME_WHITESPACE = 'SMTP username contains whitespace'
MESSAGE_ERROR_CHECK_EMAIL_PASSWORD_EMPTY      = 'SMTP password empty'
MESSAGE_ERROR_CHECK_EMAIL_PASSWORD_NON_ASCII  = 'SMTP password contains non ASCII character'
MESSAGE_ERROR_TEST_EMAIL_FAILED               = 'Sending test email failed'
MESSAGE_ERROR_CHECK_NON_ASCII                 = 'Non ASCII character'
MESSAGE_ERROR_GET_LOCALHOST                   = 'Error occured while getting hostname'
MESSAGE_ERROR_NO_LOCALHOST                    = 'No localhost found'
MESSAGE_ERROR_HOST_ALREADY_EXISTS             = 'The host already exists'
MESSAGE_ERROR_ENUMERATION_ERROR               = 'Enumeration failed'
MESSAGE_ERROR_SCRIPT_RETURN_DATA              = 'Error occured while processing data returned from script'
MESSAGE_ERROR_HOSTNAME_EMPTY                  = 'Hostname empty'
MESSAGE_WARNING_CHECK_UNUSED_HOST             = 'There are unused hosts which will be lost after a save. Continue?'
MESSAGE_WARNING_REMOVE_ALL_RULES              = 'This will remove all the rules those do not depend on the default host. Continue?'
MESSAGE_WARNING_REMOVE_ALL_HOSTS              = 'This will remove all the hosts except the default host and the rules those depend on these hosts. Continue?'
MESSAGE_WARNING_REMOVE_DEPENDENT_RULES        = 'There are rules which depend on this host. Deleting this host will also delete all the dependant rules. Continue?'
MESSAGE_WARNING_REMOVE_CORRESPONDING_HOST     = 'If this is the only rule that depends on the host then the corresponding host will be also removed. Continue?'

NEW_RULE                 = True
NOT_NEW_RULE             = False

_find_unsafe = re.compile(r'[^\w@%+=:,./-]').search

def quote(s):
    """Return a shell-escaped version of the string *s*."""
    if not s:
        return "''"
    if _find_unsafe(s) is None:
        return s

    # use single quotes, and put single quotes into double quotes
    # the string $'b is then quoted as '$'"'"'b'
    return "'" + s.replace("'", "'\"'\"'") + "'"

class REDTabSettingsServerMonitoring(QtGui.QWidget, Ui_REDTabSettingsServerMonitoring):
    def __init__(self):
        QtGui.QWidget.__init__(self)

        self.setupUi(self)

        self.session        = None # Set from REDTabSettings
        self.script_manager = None # Set from REDTabSettings
        self.image_version  = None # Set from REDTabSettings
        self.service_state  = None # Set from REDTabSettings

        self.is_tab_on_focus = False

        self.working = False
        self.remaining_enumerations = 0

        self.label_sm_unsupported.hide()
        self.label_sm_disabled.hide()
        self.show_working_wait(False)
        self.sarea_sm.hide()

        # This dictionary is needed to be kept in sync with all the GUI changes
        # on the hosts as some of the rule fields depend on available host information
        self.dict_hosts = {}
        self.model_hosts = QtGui.QStandardItemModel()
        self.model_hosts.setHorizontalHeaderLabels(HEADERS_TVIEW_HOSTS)
        self.tview_sm_hosts.setModel(self.model_hosts)
        self.set_default_col_width_hosts()
        self.defaulthost = None

        # This list is used as a temporary storage for the saved rules
        # until the enumeration calls for all the saved hosts return.
        # No need to keep this data structure in sync with the changes made on the GUI model
        self.list_rules = []
        self.dict_email = {}
        self.model_rules = QtGui.QStandardItemModel()
        self.model_rules.setHorizontalHeaderLabels(HEADERS_TVIEW_RULES)
        self.tview_sm_rules.setModel(self.model_rules)
        self.set_default_col_width_rules()

        self.label_sm_unsaved_changes.setStyleSheet('QLabel { color : red }')
        self.label_sm_unsaved_changes.hide()

        # Connecting signals to slots
        self.pbutton_sm_add_rule.clicked.connect(self.slot_pbutton_sm_add_rule_clicked)
        self.pbutton_sm_remove_all_rules.clicked.connect(self.slot_pbutton_sm_remove_all_rules_clicked)
        self.pbutton_sm_remove_all_hosts.clicked.connect(self.slot_pbutton_sm_remove_all_hosts_clicked)
        self.pbutton_sm_add_host.clicked.connect(self.slot_pbutton_sm_add_host_clicked)
        self.pbutton_sm_refresh.clicked.connect(self.slot_pbutton_sm_refresh_clicked)
        self.pbutton_sm_save.clicked.connect(self.slot_pbutton_sm_save_clicked)
        self.chkbox_sm_email_enable.stateChanged.connect(self.slot_chkbox_sm_email_enable_state_changed)
        self.chkbox_sm_email_tls.stateChanged.connect(self.slot_input_changed)
        self.ledit_sm_email_from.textEdited.connect(self.slot_input_changed)
        self.ledit_sm_email_to.textEdited.connect(self.slot_input_changed)
        self.ledit_sm_email_server.textEdited.connect(self.slot_input_changed)
        self.sbox_sm_email_port.valueChanged.connect(self.slot_input_changed)
        self.ledit_sm_email_username.textEdited.connect(self.slot_input_changed)
        self.ledit_sm_email_password.textEdited.connect(self.slot_input_changed)
        self.chkbox_sm_email_password_show.stateChanged.connect(self.slot_chkbox_sm_email_password_show_state_changed)
        self.pbutton_sm_email_test.clicked.connect(self.slot_pbutton_sm_email_test_clicked)

        self.from_constructor = True
        self.slot_chkbox_sm_email_enable_state_changed(self.chkbox_sm_email_enable.isChecked())

    def tab_on_focus(self):
        self.is_tab_on_focus = True

        if self.image_version.number < (1, 6):
            self.label_sm_unsupported.show()
            return

        if not self.service_state.servermonitoring:
            self.label_sm_disabled.show()
            return

        self.sarea_sm.show()
        self.slot_pbutton_sm_refresh_clicked()

    def tab_off_focus(self):
        self.is_tab_on_focus = False

    def tab_destroy(self):
        pass

    def cb_settings_server_monitoring_test_email(self, result):
        self.working = False

        if not report_script_result(result,
                                    MESSAGEBOX_TITLE,
                                    MESSAGE_ERROR_TEST_EMAIL_FAILED):
            self.update_gui(EVENT_RETURNED_REFRESH_GENERIC)
            return

        QtGui.QMessageBox.information(get_main_window(),
                                      MESSAGEBOX_TITLE,
                                      MESSAGE_INFO_TEST_EMAIL_SENT)

        self.update_gui(EVENT_RETURNED_REFRESH_GENERIC)

    def get_host_parameters(self, host_name):
        port           = ''
        authentication = ''
        secret         = ''

        for r in range(self.model_hosts.rowCount()):
            for c in range(COUNT_COLUMNS_HOSTS_MODEL):
                if c == INDEX_COL_HOSTS_HOST:
                    item_host = self.model_hosts.item(r, c)
                    index_host = self.model_hosts.indexFromItem(item_host)
                    widget_host = self.tview_sm_hosts.indexWidget(index_host)

                    if widget_host.text() == host_name:
                        item_port = self.model_hosts.item(r, INDEX_COL_HOSTS_PORT)
                        index_port = self.model_hosts.indexFromItem(item_port)
                        item_authentication = self.model_hosts.item(r, INDEX_COL_HOSTS_AUTHENTICATION)
                        index_authentication = self.model_hosts.indexFromItem(item_authentication)
                        item_secret = self.model_hosts.item(r, INDEX_COL_HOSTS_SECRET)
                        index_secret = self.model_hosts.indexFromItem(item_secret)

                        widget_port = self.tview_sm_hosts.indexWidget(index_port)
                        widget_authentication = self.tview_sm_hosts.indexWidget(index_authentication)
                        widget_secret = self.tview_sm_hosts.indexWidget(index_secret)

                        port = unicode(widget_port.value())
                        authentication = widget_authentication.currentText()
                        secret = widget_secret.text()

        return port, authentication, secret

    def add_new_host(self, dict_enumerate):
        host          = dict_enumerate['host']
        port          = dict_enumerate['port']
        secret        = dict_enumerate['secret']
        ptc           = dict_enumerate['ptc']
        temperature   = dict_enumerate['temperature']
        humidity      = dict_enumerate['humidity']
        ambient_light = dict_enumerate['ambient_light']

        if not host or not port:
            return

        self.dict_hosts[host]                  = {}
        self.dict_hosts[host]['port']          = port
        self.dict_hosts[host]['secret']        = secret
        self.dict_hosts[host]['ptc']           = ptc
        self.dict_hosts[host]['temperature']   = temperature
        self.dict_hosts[host]['humidity']      = humidity
        self.dict_hosts[host]['ambient_light'] = ambient_light

        row_host = []

        for i in range(COUNT_COLUMNS_HOSTS_MODEL):
            row_host.append(QtGui.QStandardItem(''))

        self.model_hosts.appendRow(row_host)

        r = self.model_hosts.rowCount() - 1

        for c in range(COUNT_COLUMNS_HOSTS_MODEL):
            # Add Used field widget
            if c == INDEX_COL_HOSTS_USED:
                item = self.model_hosts.item(r, c)
                index = self.model_hosts.indexFromItem(item)
                chkbox = QtGui.QCheckBox()
                chkbox.setChecked(False)
                chkbox.setEnabled(False)
                self.tview_sm_hosts.setIndexWidget(index, chkbox)

            # Add Host field widget
            elif c == INDEX_COL_HOSTS_HOST:
                item = self.model_hosts.item(r, c)
                index = self.model_hosts.indexFromItem(item)
                ledit = QtGui.QLineEdit()
                ledit.setText(host)

                if host == self.defaulthost:
                    ledit.setEnabled(False)
                else:
                    ledit.textEdited.connect(self.slot_host_edited)

                self.tview_sm_hosts.setIndexWidget(index, ledit)

            # Add Port field widget
            elif c == INDEX_COL_HOSTS_PORT:
                item = self.model_hosts.item(r, c)
                index = self.model_hosts.indexFromItem(item)
                sbox = QtGui.QSpinBox()
                sbox.setRange(1, 65535)
                sbox.valueChanged.connect(self.slot_input_changed)
                sbox.setValue(int(port))
                self.tview_sm_hosts.setIndexWidget(index, sbox)

            # Add Authentication field widget
            elif c == INDEX_COL_HOSTS_AUTHENTICATION:
                item = self.model_hosts.item(r, c)
                index = self.model_hosts.indexFromItem(item)
                cbox = QtGui.QComboBox()
                cbox.addItems(ITEMS_AUTHENTICATION)

                if not secret:
                    cbox.setCurrentIndex(1)
                else:
                    cbox.setCurrentIndex(0)

                cbox.activated.connect(self.slot_cbox_authentication_activated)
                self.tview_sm_hosts.setIndexWidget(index, cbox)

            # Add Secret field widget
            elif c == INDEX_COL_HOSTS_SECRET:
                item = self.model_hosts.item(r, c)
                index = self.model_hosts.indexFromItem(item)
                ledit = QtGui.QLineEdit()

                if not secret:
                    ledit.setText('')
                    ledit.setEnabled(False)
                else:
                    ledit.setText(secret)
                    ledit.setEnabled(True)

                ledit.textChanged.connect(self.slot_input_changed)
                self.tview_sm_hosts.setIndexWidget(index, ledit)

            # Add Refresh UIDs field widget
            elif c == INDEX_COL_HOSTS_REFRESH_UIDS:
                item = self.model_hosts.item(r, c)
                index = self.model_hosts.indexFromItem(item)
                btn = QtGui.QPushButton()
                btn.setText('Refresh UIDs')
                btn.clicked.connect(self.slot_refresh_uids_clicked)
                self.tview_sm_hosts.setIndexWidget(index, btn)

            # Add Remove field widget
            elif c == INDEX_COL_HOSTS_REMOVE:
                item = self.model_hosts.item(r, c)
                index = self.model_hosts.indexFromItem(item)
                btn = QtGui.QPushButton()

                btn.setText('Remove')

                if host == self.defaulthost:
                    btn.setEnabled(False)

                btn.clicked.connect(self.slot_remove_host_clicked)
                self.tview_sm_hosts.setIndexWidget(index, btn)

            # Add Hidden Host column
            elif c == INDEX_COL_HOSTS_HIDDEN_HOST:
                item = self.model_hosts.item(r, c)
                item.setText(host)

        self.tview_sm_hosts.setColumnHidden(INDEX_COL_HOSTS_HIDDEN_HOST, True)

    def add_widget_spin_span(self, r, c, color, low, high):
        item = self.model_rules.item(r, c)
        index = self.model_rules.indexFromItem(item)
        item_bricklet = self.model_rules.item(r, INDEX_COL_RULES_BRICKLET)
        index_bricklet = self.model_rules.indexFromItem(item_bricklet)

        cbox_bricklet = self.tview_sm_rules.indexWidget(index_bricklet)
        widget_spin_span = widgetSpinBoxSpanSlider()

        self.set_range_widgetSpinBoxSpanSlider(SUPPORTED_BRICKLETS[cbox_bricklet.currentText()]['id'],
                                               widget_spin_span)

        widget_spin_span.sbox_upper.setValue(high)
        widget_spin_span.sbox_lower.setValue(low)

        widget_spin_span.span_slider.setColorOutsideRange(color)
        widget_spin_span.sbox_upper.valueChanged.connect(self.slot_input_changed)
        widget_spin_span.sbox_lower.valueChanged.connect(self.slot_input_changed)
        self.tview_sm_rules.setIndexWidget(index, widget_spin_span)

    def set_range_widgetSpinBoxSpanSlider(self, bricklet, widget_spin_span):
        if bricklet == 'ptc24' or bricklet == 'ptc3':
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

    def set_initial_value_widgetSpinBoxSpanSlider(self, widget_spin_span):
        span_minimum = widget_spin_span.span_slider.minimum()
        span_maximum = widget_spin_span.span_slider.maximum()
        span = abs(span_minimum - span_maximum)
        span_mid = span/2
        widget_spin_span.sbox_upper.setValue(0)
        widget_spin_span.sbox_lower.setValue(0)
        widget_spin_span.sbox_upper.setValue(span_mid + abs(span_mid - span_maximum)/2)
        widget_spin_span.sbox_lower.setValue(span_minimum + abs(span_mid - span_minimum)/2)

    def set_default_col_width_hosts(self):
        self.tview_sm_hosts.setColumnWidth(INDEX_COL_HOSTS_USED, DEFAULT_COL_WIDTH_HOSTS_USED)
        self.tview_sm_hosts.setColumnWidth(INDEX_COL_HOSTS_HOST, DEFAULT_COL_WIDTH_HOSTS_HOST)
        self.tview_sm_hosts.setColumnWidth(INDEX_COL_HOSTS_PORT, DEFAULT_COL_WIDTH_HOSTS_PORT)
        self.tview_sm_hosts.setColumnWidth(INDEX_COL_HOSTS_AUTHENTICATION, DEFAULT_COL_WIDTH_HOSTS_AUTHENTICATION)
        self.tview_sm_hosts.setColumnWidth(INDEX_COL_HOSTS_SECRET, DEFAULT_COL_WIDTH_HOSTS_SECRET)
        self.tview_sm_hosts.setColumnWidth(INDEX_COL_HOSTS_REFRESH_UIDS, DEFAULT_COL_WIDTH_HOSTS_REFRESH_UIDS)
        self.tview_sm_hosts.setColumnWidth(INDEX_COL_HOSTS_REMOVE, DEFAULT_COL_WIDTH_HOSTS_REMOVE)

    def set_default_col_width_rules(self):
        self.tview_sm_rules.setColumnWidth(INDEX_COL_RULES_NAME, DEFAULT_COL_WIDTH_RULES_NAME)
        self.tview_sm_rules.setColumnWidth(INDEX_COL_RULES_HOST, DEFAULT_COL_WIDTH_RULES_HOST)
        self.tview_sm_rules.setColumnWidth(INDEX_COL_RULES_BRICKLET, DEFAULT_COL_WIDTH_RULES_BRICKLET)
        self.tview_sm_rules.setColumnWidth(INDEX_COL_RULES_UID, DEFAULT_COL_WIDTH_RULES_UID)
        self.tview_sm_rules.setColumnWidth(INDEX_COL_RULES_WARNING, DEFAULT_COL_WIDTH_RULES_WARNING)
        self.tview_sm_rules.setColumnWidth(INDEX_COL_RULES_CRITICAL, DEFAULT_COL_WIDTH_RULES_CRITICAL)
        self.tview_sm_rules.setColumnWidth(INDEX_COL_RULES_UNIT, DEFAULT_COL_WIDTH_RULES_UNIT)
        self.tview_sm_rules.setColumnWidth(INDEX_COL_RULES_EMAIL_NOTIFICATIONS, DEFAULT_COL_WIDTH_RULES_EMAIL_NOTIFICATIONS)
        self.tview_sm_rules.setColumnWidth(INDEX_COL_RULES_REMOVE, DEFAULT_COL_WIDTH_RULES_REMOVE)

    def cb_settings_server_monitoring_enumerate(self, add_rule, result, refresh_uids = False):
        def restore_gui_on_exception():
            if refresh_uids or not add_rule and self.remaining_enumerations < 1:
                self.update_gui(EVENT_RETURNED_REFRESH_GENERIC)
            else:
                self.update_gui(EVENT_RETURNED_REFRESH_FALSE)

        self.remaining_enumerations = self.remaining_enumerations - 1

        if self.remaining_enumerations < 1:
            self.working = False

        # Not using report_script_result() because this is a special case
        # in which we usually ignore errors occured while enumeration
        # and only consider an error if the script was called with wrong
        # arguments. Therefore we only need to check the exit code.
        if result and result.exit_code != 0:
            QtGui.QMessageBox.critical(get_main_window(),
                                       MESSAGEBOX_TITLE,
                                       MESSAGE_ERROR_ENUMERATION_ERROR)
            restore_gui_on_exception()
            return

        try:
            dict_enumerate = json.loads(result.stdout)
        except:
            QtGui.QMessageBox.critical(get_main_window(),
                                       MESSAGEBOX_TITLE,
                                       MESSAGE_ERROR_SCRIPT_RETURN_DATA)
            restore_gui_on_exception()
            return

        # Updating host data structure of the corresponding host
        dict_enumerate['ptc'].append(EMPTY_UID)
        dict_enumerate['temperature'].append(EMPTY_UID)
        dict_enumerate['humidity'].append(EMPTY_UID)
        dict_enumerate['ambient_light'].append(EMPTY_UID)

        self.dict_hosts[dict_enumerate['host']] = {}
        self.dict_hosts[dict_enumerate['host']]['port']          = dict_enumerate['port']
        self.dict_hosts[dict_enumerate['host']]['secret']        = dict_enumerate['secret']
        self.dict_hosts[dict_enumerate['host']]['ptc']           = dict_enumerate['ptc']
        self.dict_hosts[dict_enumerate['host']]['temperature']   = dict_enumerate['temperature']
        self.dict_hosts[dict_enumerate['host']]['humidity']      = dict_enumerate['humidity']
        self.dict_hosts[dict_enumerate['host']]['ambient_light'] = dict_enumerate['ambient_light']

        # Enumeration was for refresh uids
        if refresh_uids and self.remaining_enumerations < 1:
            self.update_gui(EVENT_UPDATE_UIDS_IN_RULES)
            self.update_gui(EVENT_RETURNED_REFRESH_GENERIC)
            return

        self.add_new_host(dict_enumerate)

        # Enumeration after adding new host
        if not add_rule and self.remaining_enumerations < 1:
            self.update_gui(EVENT_RETURNED_REFRESH_GENERIC)
            self.update_gui(EVENT_INPUT_CHANGED)
            return

        # Enumeration calls of refresh event
        if self.remaining_enumerations < 1:
            # Populating rules list after all host information is available
            # This is why we are using self.list_rules as a temporary storage
            # of the rules until all the enumeration calls are returned. This is
            # applicable only for a refresh
            self.populate_rules()
            self.update_gui(EVENT_RETURNED_REFRESH_TRUE)

    def populate_rules(self):
        for dict_rule in self.list_rules:
            if dict_rule['host'] not in self.dict_hosts:
                continue

            if dict_rule['bricklet'] == 'ptc24' or\
               dict_rule['bricklet'] == 'ptc3' and\
               dict_rule['uid'] not in self.dict_hosts[dict_rule['host']]['ptc']:
                    self.dict_hosts[dict_rule['host']]['ptc'].insert(0, dict_rule['uid'])

            elif dict_rule['bricklet'] == 'temperature' and\
                 dict_rule['uid'] not in self.dict_hosts[dict_rule['host']]['temperature']:
                    self.dict_hosts[dict_rule['host']]['temperature'].insert(0, dict_rule['uid'])

            elif dict_rule['bricklet'] == 'humidity' and\
                 dict_rule['uid'] not in self.dict_hosts[dict_rule['host']]['humidity']:
                    self.dict_hosts[dict_rule['host']]['humidity'].insert(0, dict_rule['uid'])

            elif dict_rule['bricklet'] == 'ambient_light' and\
                 dict_rule['uid'] not in self.dict_hosts[dict_rule['host']]['ambient_light']:
                    self.dict_hosts[dict_rule['host']]['ambient_light'].insert(0, dict_rule['uid'])

            self.add_new_rule(dict_rule['name'],
                              dict_rule['host'],
                              dict_rule['bricklet'],
                              dict_rule['uid'],
                              dict_rule['warning_low'],
                              dict_rule['warning_high'],
                              dict_rule['critical_low'],
                              dict_rule['critical_high'],
                              dict_rule['email_notification_enabled'],
                              dict_rule['email_notifications'])

            if dict_rule['email_notification_enabled'] == '1':
                self.ledit_sm_email_from.setText(self.dict_email['from'])
                self.ledit_sm_email_to.setText(self.dict_email['to'])
                self.ledit_sm_email_server.setText(self.dict_email['server'])
                self.sbox_sm_email_port.setValue(int(self.dict_email['port']))
                self.ledit_sm_email_username.setText(self.dict_email['username'])
                self.ledit_sm_email_password.setText(self.dict_email['password'])

                if self.dict_email['tls'] == 'yes':
                    self.chkbox_sm_email_tls.setChecked(True)
                else:
                    self.chkbox_sm_email_tls.setChecked(False)

                self.chkbox_sm_email_enable.setChecked(True)

            # Updating the used field of the hosts list
            self.update_hosts_used()
        
        # Clearing temporary rules list
        self.list_rules = []

    def cb_settings_server_monitoring_get(self, result):
        if not report_script_result(result, MESSAGEBOX_TITLE, MESSAGE_ERROR_GET_FAILED):
            self.update_gui(EVENT_RETURNED_REFRESH_FALSE)
            return

        try:
            dict_return = json.loads(result.stdout)
        except:
            QtGui.QMessageBox.critical(get_main_window(),
                                       MESSAGEBOX_TITLE,
                                       MESSAGE_ERROR_SCRIPT_RETURN_DATA)
            return

        # Reset data structures
        self.list_rules = []
        self.dict_hosts.clear()
        self.model_rules.clear()
        self.model_hosts.clear()
        self.model_rules.setHorizontalHeaderLabels(HEADERS_TVIEW_RULES)
        self.model_hosts.setHorizontalHeaderLabels(HEADERS_TVIEW_HOSTS)
        self.set_default_col_width_rules()
        self.set_default_col_width_hosts()

        # Populate rules data structure
        if dict_return['rules']:
            for dict_rule in dict_return['rules']:
                rule = {}
                rule['name']                       = dict_rule['name']
                rule['host']                       = dict_rule['host']
                rule['bricklet']                   = dict_rule['bricklet']
                rule['uid']                        = dict_rule['uid']
                rule['warning_low']                = dict_rule['warning_low']
                rule['warning_high']               = dict_rule['warning_high']
                rule['critical_low']               = dict_rule['critical_low']
                rule['critical_high']              = dict_rule['critical_high']
                rule['email_notification_enabled'] = dict_rule['email_notification_enabled']
                rule['email_notifications']        = dict_rule['email_notifications']

                self.dict_email['from']     = None
                self.dict_email['to']       = None
                self.dict_email['server']   = None
                self.dict_email['port']     = None
                self.dict_email['username'] = None
                self.dict_email['password'] = None
                self.dict_email['tls']      = None

                if rule['email_notification_enabled'] == '1' and dict_return['email']:
                    self.dict_email['from']     = dict_return['email']['from']
                    self.dict_email['to']       = dict_return['email']['to']
                    self.dict_email['server']   = dict_return['email']['server']
                    self.dict_email['port']     = dict_return['email']['port']
                    self.dict_email['username'] = dict_return['email']['username']
                    self.dict_email['password'] = dict_return['email']['password']
                    self.dict_email['tls']      = dict_return['email']['tls']

                self.list_rules.append(rule)

        # Host data structure is populated on enumerate script callback
        if dict_return['hosts'] and len(dict_return['hosts']) > 0:
            if self.defaulthost not in dict_return['hosts']:
                self.remaining_enumerations = len(dict_return['hosts']) + 1
                self.script_manager.execute_script('settings_server_monitoring',
                                                   lambda result: self.cb_settings_server_monitoring_enumerate(True, result),
                                                   ['ENUMERATE',
                                                    self.defaulthost,
                                                    '4223',
                                                    ''])
            else:
                self.remaining_enumerations = len(dict_return['hosts'])

            for host in dict_return['hosts']:
                # Call enumerate for each host
                self.script_manager.execute_script('settings_server_monitoring',
                                                   lambda result: self.cb_settings_server_monitoring_enumerate(True, result),
                                                   ['ENUMERATE',
                                                    host,
                                                    dict_return['hosts'][host]['port'],
                                                    dict_return['hosts'][host]['secret']])

        else:
            self.remaining_enumerations = 1
            self.script_manager.execute_script('settings_server_monitoring',
                                               lambda result: self.cb_settings_server_monitoring_enumerate(True, result),
                                               ['ENUMERATE',
                                                self.defaulthost,
                                                '4223',
                                                ''])

    def cb_settings_server_monitoring_get_localhost(self, result):
        if not report_script_result(result, MESSAGEBOX_TITLE, MESSAGE_ERROR_GET_LOCALHOST):
            self.update_gui(EVENT_RETURNED_REFRESH_FALSE)
            self.defaulthost = None
            return

        self.defaulthost = result.stdout

        if not self.defaulthost:
            QtGui.QMessageBox.information(get_main_window(),
                                          MESSAGEBOX_TITLE,
                                          MESSAGE_ERROR_HOSTNAME_EMPTY)
            self.update_gui(EVENT_RETURNED_REFRESH_FALSE)
            return

        self.script_manager.execute_script('settings_server_monitoring',
                                           self.cb_settings_server_monitoring_get,
                                           ['GET'])

    def cb_settings_server_monitoring_apply(self, result):
        self.working = False

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

    def populate_cbox_uids(self, cbox_host, cbox_bricklet, cbox_uid):
        def populate_and_select(bricklet):
            cbox_uid.clear()
            cbox_uid.addItems(self.dict_hosts[cbox_host.currentText()][bricklet])
            uid_from_rule = cbox_bricklet.itemData(cbox_bricklet.currentIndex(), QtCore.Qt.UserRole)

            if uid_from_rule:
                if uid_from_rule not in self.dict_hosts[cbox_host.currentText()][bricklet]:
                    self.dict_hosts[cbox_host.currentText()][bricklet].insert(0, uid_from_rule)
                    cbox_uid.clear()
                    cbox_uid.addItems(self.dict_hosts[cbox_host.currentText()][bricklet])

                for i in range(cbox_uid.count()):
                    if cbox_uid.itemText(i) == uid_from_rule:
                        cbox_uid.setCurrentIndex(i)
                        break

            if cbox_uid.count() == 1:
                cbox_uid.setEditable(True)
                cbox_uid.setInsertPolicy(QtGui.QComboBox.InsertBeforeCurrent)
                cbox_uid.lineEdit().selectAll()
            else:
                cbox_uid.setEditable(False)

        if cbox_host.currentText() not in self.dict_hosts:
            cbox_uid.clear()
            cbox_uid.addItem(EMPTY_UID)
            cbox_uid.setEditable(True)
            cbox_uid.setInsertPolicy(QtGui.QComboBox.InsertBeforeCurrent)
            cbox_uid.lineEdit().selectAll()
            return

        if SUPPORTED_BRICKLETS[cbox_bricklet.currentText()]['id'] == 'ptc24' or\
           SUPPORTED_BRICKLETS[cbox_bricklet.currentText()]['id'] == 'ptc3':
                populate_and_select('ptc')

        elif SUPPORTED_BRICKLETS[cbox_bricklet.currentText()]['id'] == 'temperature':
            populate_and_select('temperature')

        elif SUPPORTED_BRICKLETS[cbox_bricklet.currentText()]['id'] == 'humidity':
            populate_and_select('humidity')

        elif SUPPORTED_BRICKLETS[cbox_bricklet.currentText()]['id'] == 'ambient_light':
            populate_and_select('ambient_light')

    def update_hosts_used(self):
        for r_hosts in range(self.model_hosts.rowCount()):
            for c_hosts in range(COUNT_COLUMNS_HOSTS_MODEL):
                if c_hosts == INDEX_COL_HOSTS_HOST:
                    item_hosts_host   = self.model_hosts.item(r_hosts, c_hosts)
                    index_hosts_host  = self.model_hosts.indexFromItem(item_hosts_host)
                    ledit_hosts_host  = self.tview_sm_hosts.indexWidget(index_hosts_host)

                    match_found = False

                    for r_rules in range(self.model_rules.rowCount()):
                        for c_rules in range(COUNT_COLUMNS_RULES_MODEL):
                            if c_rules == INDEX_COL_RULES_HOST:
                                item_rules_host  = self.model_rules.item(r_rules, c_rules)
                                index_rules_host = self.model_rules.indexFromItem(item_rules_host)
                                cbox_rules_host  = self.tview_sm_rules.indexWidget(index_rules_host)

                                if ledit_hosts_host.text() == cbox_rules_host.currentText():
                                    match_found = True
                                    break

                    item_hosts_used   = self.model_hosts.item(r_hosts, INDEX_COL_HOSTS_USED)
                    index_hosts_used  = self.model_hosts.indexFromItem(item_hosts_used)
                    chkbox_hosts_used = self.tview_sm_hosts.indexWidget(index_hosts_used)

                    if match_found:
                        chkbox_hosts_used.setChecked(True)
                    else:
                        chkbox_hosts_used.setChecked(False)

    def check_unused_host(self):
        if self.model_hosts.rowCount() == 1:
            return True

        for r in range(self.model_hosts.rowCount()):
            for c in range(COUNT_COLUMNS_HOSTS_MODEL):
                if c == INDEX_COL_HOSTS_USED:
                    item_used   = self.model_hosts.item(r, c)
                    index_used  = self.model_hosts.indexFromItem(item_used)
                    chkbox_used = self.tview_sm_hosts.indexWidget(index_used)

                    item_host   = self.model_hosts.item(r, INDEX_COL_HOSTS_HOST)
                    index_host  = self.model_hosts.indexFromItem(item_host)
                    ledit_host = self.tview_sm_hosts.indexWidget(index_host)

                    host = ledit_host.text()

                    if not chkbox_used.isChecked() and host != self.defaulthost:
                        return False

        return True

    def check_rules(self, check_only_email_fields = False):
        def check_email_fields():
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
                return None, None, CHECK_FAILED_EMAIL_FROM_WHITESPACE

            elif not re.match('^.+@.+$', email_from):
                return None, None, CHECK_FAILED_EMAIL_FROM_MALFORMED

            elif not email_to:
                return None, None, CHECK_FAILED_EMAIL_TO_EMPTY

            elif not self.is_ascii(email_to):
                return None, None, CHECK_FAILED_EMAIL_TO_NON_ASCII

            elif ' ' in email_to:
                return None, None, CHECK_FAILED_EMAIL_TO_WHITESPACE

            elif not re.match('^.+@.+$', email_to):
                return None, None, CHECK_FAILED_EMAIL_TO_MALFORMED

            elif not email_server:
                return None, None, CHECK_FAILED_EMAIL_SERVER_EMPTY

            elif not self.is_ascii(email_server):
                return None, None, CHECK_FAILED_EMAIL_SERVER_NON_ASCII

            elif ' ' in email_server:
                return None, None, CHECK_FAILED_EMAIL_SERVER_WHITESPACE

            elif not email_username:
                return None, None, CHECK_FAILED_EMAIL_USERNAME_EMPTY

            elif not self.is_ascii(email_username):
                return None, None, CHECK_FAILED_EMAIL_USERNAME_NON_ASCII

            elif ' ' in email_username:
                return None, None, CHECK_FAILED_EMAIL_USERNAME_WHITESPACE

            elif not email_password:
                return None, None, CHECK_FAILED_EMAIL_PASSWORD_EMPTY

            elif not self.is_ascii(email_password):
                return None, None, CHECK_FAILED_EMAIL_PASSWORD_NON_ASCII

            return None, None, CHECK_OK

        list_service_names = []

        if check_only_email_fields:
            rule_number, field_number, check_result = check_email_fields()

            if check_result == CHECK_OK:
                return rule_number, field_number, CHECK_OK
            else:
                return rule_number, field_number, check_result

        for r in range(self.model_rules.rowCount()):
            for c in range(COUNT_COLUMNS_RULES_MODEL):
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

                # Check email fields
                elif self.chkbox_sm_email_enable.isChecked():
                    rule_number, field_number, check_result = check_email_fields()

                    if check_result != CHECK_OK:
                        return rule_number, field_number, check_result

        return None, None, CHECK_OK

    def show_working_wait(self, show):
        if show:
            self.label_sm_working_wait.show()
            self.pbar_sm_working_wait.show()
        else:
            self.label_sm_working_wait.hide()
            self.pbar_sm_working_wait.hide()

    def add_new_rule(self,
                     name,
                     host,
                     bricklet,
                     uid,
                     warning_low,
                     warning_high,
                     critical_low,
                     critical_high,
                     email_notification_enabled,
                     email_notifications):
        rule = []

        for i in range(COUNT_COLUMNS_RULES_MODEL):
            rule.append(QtGui.QStandardItem(''))

        self.model_rules.appendRow(rule)

        r = self.model_rules.rowCount() - 1

        for c in range(COUNT_COLUMNS_RULES_MODEL):
            # Add Name field widget
            if c == INDEX_COL_RULES_NAME:
                item = self.model_rules.item(r, c)
                index = self.model_rules.indexFromItem(item)
                ledit_name = QtGui.QLineEdit()
                ledit_name.textEdited.connect(self.slot_input_changed)
                ledit_name.setText(name)
                self.tview_sm_rules.setIndexWidget(index, ledit_name)

            # Add Host field widget
            elif c == INDEX_COL_RULES_HOST:
                item = self.model_rules.item(r, c)
                index = self.model_rules.indexFromItem(item)
                cbox = QtGui.QComboBox()

                cbox.setModel(self.model_hosts)
                cbox.setModelColumn(INDEX_COL_HOSTS_HIDDEN_HOST)

                for i in range(cbox.count()):
                    if cbox.itemText(i) == host:
                        cbox.setCurrentIndex(i)
                        break

                cbox.activated.connect(self.slot_cbox_host_activated)
                self.tview_sm_rules.setIndexWidget(index, cbox)

            # Add Bricklet field widget
            elif c == INDEX_COL_RULES_BRICKLET:
                item = self.model_rules.item(r, c)
                index = self.model_rules.indexFromItem(item)
                cbox = QtGui.QComboBox()
                cbox.addItems(sorted(SUPPORTED_BRICKLETS.keys()))

                for i in range(cbox.count()):
                    if bricklet == SUPPORTED_BRICKLETS[cbox.itemText(i)]['id']:
                        cbox.setItemData(i, uid, QtCore.Qt.UserRole)
                        cbox.setCurrentIndex(i)
                        break

                cbox.activated.connect(self.slot_cbox_bricklet_activated)
                self.tview_sm_rules.setIndexWidget(index, cbox)

            # Add UID field widget
            elif c == INDEX_COL_RULES_UID:
                item_host = self.model_rules.item(r, INDEX_COL_RULES_HOST)
                index_host = self.model_rules.indexFromItem(item_host)
                cbox_host = self.tview_sm_rules.indexWidget(index_host)

                item_bricklet = self.model_rules.item(r, INDEX_COL_RULES_BRICKLET)
                index_bricklet = self.model_rules.indexFromItem(item_bricklet)
                cbox_bricklet = self.tview_sm_rules.indexWidget(index_bricklet)

                item_uid = self.model_rules.item(r, c)
                index_uid = self.model_rules.indexFromItem(item_uid)
                cbox_uid = QtGui.QComboBox()

                self.populate_cbox_uids(cbox_host, cbox_bricklet, cbox_uid)

                cbox_uid.activated.connect(self.slot_cbox_uid_activated)
                self.tview_sm_rules.setIndexWidget(index_uid, cbox_uid)

            # Add Warning field widget
            elif c == INDEX_COL_RULES_WARNING:
                self.add_widget_spin_span(r,
                                          c,
                                          COLOR_WARNING,
                                          int(warning_low),
                                          int(warning_high))

            # Add Critical field widget
            elif c == INDEX_COL_RULES_CRITICAL:
                self.add_widget_spin_span(r,
                                          c,
                                          COLOR_CRITICAL,
                                          int(critical_low),
                                          int(critical_high))

            # Add Unit field widget
            elif c == INDEX_COL_RULES_UNIT:
                item_unit = self.model_rules.item(r, c)
                index_unit = self.model_rules.indexFromItem(item_unit)
                label_unit = QtGui.QLabel()
                item_bricklet = self.model_rules.item(r, INDEX_COL_RULES_BRICKLET)
                index_bricklet = self.model_rules.indexFromItem(item_bricklet)
                cbox_bricklet = self.tview_sm_rules.indexWidget(index_bricklet)
                label_unit.setText(SUPPORTED_BRICKLETS[cbox_bricklet.currentText()]['unit'])
                self.tview_sm_rules.setIndexWidget(index_unit, label_unit)

            # Add email field widget
            elif c == INDEX_COL_RULES_EMAIL_NOTIFICATIONS:
                item = self.model_rules.item(r, c)
                index = self.model_rules.indexFromItem(item)
                cbox = QtGui.QComboBox()
                cbox.addItems(COLUMN_EMAIL_NOTIFICATIONS_ITEMS)

                if email_notification_enabled == '1':
                    if email_notifications == 'c,r':
                        cbox.setCurrentIndex(INDEX_EMAIL_CRITICAL)
                    elif email_notifications == 'w,c,r':
                        cbox.setCurrentIndex(INDEX_EMAIL_WARNING_CRITICAL)
                else:
                    cbox.setCurrentIndex(INDEX_EMAIL_NO_NOTIFICATIONS)

                if self.chkbox_sm_email_enable.isChecked():
                    cbox.setEnabled(True)
                else:
                    cbox.setEnabled(False)

                cbox.activated.connect(self.slot_input_changed)
                self.tview_sm_rules.setIndexWidget(index, cbox)

            # Add Remove field widget
            elif c == INDEX_COL_RULES_REMOVE:
                item = self.model_rules.item(r, c)
                index = self.model_rules.indexFromItem(item)
                btn = QtGui.QPushButton('Remove')
                btn.clicked.connect(self.slot_remove_rule_clicked)
                self.tview_sm_rules.setIndexWidget(index, btn)

    def update_gui(self, event):
        if event == EVENT_CLICKED_REFRESH:
            self.show_working_wait(True)
            self.pbutton_sm_refresh.setText('Refreshing...')
            self.sarea_sm.setEnabled(False)

        elif event == EVENT_CLICKED_SAVE:
            self.show_working_wait(True)
            self.pbutton_sm_save.setText('Saving...')
            self.sarea_sm.setEnabled(False)

        elif event == EVENT_CLICKED_REFRESH_GENERIC:
            self.show_working_wait(True)
            self.sarea_sm.setEnabled(False)

        elif event == EVENT_INPUT_CHANGED:
            if self.remaining_enumerations > 0:
                return

            self.pbutton_sm_save.setEnabled(True)
            self.label_sm_unsaved_changes.show()

            if self.model_rules.rowCount() > 0:
                self.pbutton_sm_remove_all_rules.setEnabled(True)
                self.gbox_sm_email.setEnabled(True)
            else:
                self.pbutton_sm_remove_all_rules.setEnabled(False)
                self.gbox_sm_email.setEnabled(False)
                self.chkbox_sm_email_enable.setChecked(False)

            if self.model_hosts.rowCount() > 1:
                self.pbutton_sm_remove_all_hosts.setEnabled(True)
            else:
                self.pbutton_sm_remove_all_hosts.setEnabled(False)

        elif event == EVENT_RETURNED_REFRESH_TRUE:
            self.show_working_wait(False)
            self.sarea_sm.setEnabled(True)
            self.pbutton_sm_refresh.setText('Refresh')
            self.pbutton_sm_save.setText('Save')

            if self.model_rules.rowCount() > 0:
                self.pbutton_sm_remove_all_rules.setEnabled(True)
                self.gbox_sm_email.setEnabled(True)

            self.pbutton_sm_save.setEnabled(False)
            self.label_sm_unsaved_changes.hide()

        elif event == EVENT_RETURNED_REFRESH_FALSE:
            self.show_working_wait(False)
            self.sarea_sm.setEnabled(True)
            self.pbutton_sm_refresh.setText('Refresh')
            self.pbutton_sm_save.setText('Save')

            if self.model_rules.rowCount() > 0:
                self.pbutton_sm_remove_all_rules.setEnabled(True)
                self.gbox_sm_email.setEnabled(True)

        elif event == EVENT_RETURNED_SAVE_TRUE:
            self.show_working_wait(False)
            self.sarea_sm.setEnabled(True)
            self.label_sm_unsaved_changes.hide()
            self.pbutton_sm_save.setText('Save')
            self.pbutton_sm_save.setEnabled(False)

        elif event == EVENT_RETURNED_SAVE_FALSE:
            self.show_working_wait(False)
            self.sarea_sm.setEnabled(True)
            self.pbutton_sm_save.setText('Save')
            self.pbutton_sm_save.setEnabled(True)

        elif event == EVENT_RETURNED_REFRESH_GENERIC:
            self.show_working_wait(False)
            self.sarea_sm.setEnabled(True)
            self.pbutton_sm_refresh.setText('Refresh')
            self.pbutton_sm_save.setText('Save')

            if self.model_rules.rowCount() > 0:
                self.pbutton_sm_remove_all_rules.setEnabled(True)
                self.gbox_sm_email.setEnabled(True)

        elif event == EVENT_UPDATE_UIDS_IN_RULES:
            if self.model_rules.rowCount() < 1:
                return

            for r in range(self.model_rules.rowCount()):
                host = None
                bricklet = None
                previously_selected_uid = None

                item_host = self.model_rules.item(r, INDEX_COL_HOSTS_HOST)
                index_host = self.model_rules.indexFromItem(item_host)
                cbox_host = self.tview_sm_rules.indexWidget(index_host)

                item_bricklet = self.model_rules.item(r, INDEX_COL_RULES_BRICKLET)
                index_bricklet = self.model_rules.indexFromItem(item_bricklet)
                cbox_bricklet = self.tview_sm_rules.indexWidget(index_bricklet)

                item_uid = self.model_rules.item(r, INDEX_COL_RULES_UID)
                index_uid = self.model_rules.indexFromItem(item_uid)
                cbox_uid = self.tview_sm_rules.indexWidget(index_uid)

                host = cbox_host.currentText()
                bricklet = cbox_bricklet.currentText()
                previously_selected_uid = cbox_uid.currentText()

                if not host or not bricklet or not previously_selected_uid:
                    continue

                self.populate_cbox_uids(cbox_host, cbox_bricklet, cbox_uid)

    def slot_pbutton_sm_email_test_clicked(self):
        if self.working:
            return

        rule_number, field_number, check_result = self.check_rules(check_only_email_fields = True)

        if check_result == CHECK_FAILED_EMAIL_FROM_EMPTY:
            QtGui.QMessageBox.critical(get_main_window(),
                                       MESSAGEBOX_TITLE,
                                       MESSAGE_ERROR_CHECK_EMAIL_FROM_EMPTY)
            return

        elif check_result == CHECK_FAILED_EMAIL_FROM_NON_ASCII:
            QtGui.QMessageBox.critical(get_main_window(),
                                       MESSAGEBOX_TITLE,
                                       MESSAGE_ERROR_CHECK_EMAIL_FROM_NON_ASCII)
            return

        elif check_result == CHECK_FAILED_EMAIL_FROM_WHITESPACE:
            QtGui.QMessageBox.critical(get_main_window(),
                                       MESSAGEBOX_TITLE,
                                       MESSAGE_ERROR_CHECK_EMAIL_FROM_WHITESPACE)
            return

        elif check_result == CHECK_FAILED_EMAIL_FROM_MALFORMED:
            QtGui.QMessageBox.critical(get_main_window(),
                                       MESSAGEBOX_TITLE,
                                       MESSAGE_ERROR_CHECK_EMAIL_FROM_MALFORMED)
            return

        elif check_result == CHECK_FAILED_EMAIL_TO_EMPTY:
            QtGui.QMessageBox.critical(get_main_window(),
                                       MESSAGEBOX_TITLE,
                                       MESSAGE_ERROR_CHECK_EMAIL_TO_EMPTY)
            return

        elif check_result == CHECK_FAILED_EMAIL_TO_NON_ASCII:
            QtGui.QMessageBox.critical(get_main_window(),
                                       MESSAGEBOX_TITLE,
                                       MESSAGE_ERROR_CHECK_EMAIL_TO_NON_ASCII)
            return

        elif check_result == CHECK_FAILED_EMAIL_TO_WHITESPACE:
            QtGui.QMessageBox.critical(get_main_window(),
                                       MESSAGEBOX_TITLE,
                                       MESSAGE_ERROR_CHECK_EMAIL_TO_WHITESPACE)
            return

        elif check_result == CHECK_FAILED_EMAIL_TO_MALFORMED:
            QtGui.QMessageBox.critical(get_main_window(),
                                       MESSAGEBOX_TITLE,
                                       MESSAGE_ERROR_CHECK_EMAIL_TO_MALFORMED)
            return

        elif check_result == CHECK_FAILED_EMAIL_SERVER_EMPTY:
            QtGui.QMessageBox.critical(get_main_window(),
                                       MESSAGEBOX_TITLE,
                                       MESSAGE_ERROR_CHECK_EMAIL_SERVER_EMPTY)
            return

        elif check_result == CHECK_FAILED_EMAIL_SERVER_NON_ASCII:
            QtGui.QMessageBox.critical(get_main_window(),
                                       MESSAGEBOX_TITLE,
                                       MESSAGE_ERROR_CHECK_EMAIL_SERVER_NON_ASCII)
            return

        elif check_result == CHECK_FAILED_EMAIL_SERVER_WHITESPACE:
            QtGui.QMessageBox.critical(get_main_window(),
                                       MESSAGEBOX_TITLE,
                                       MESSAGE_ERROR_CHECK_EMAIL_SERVER_WHITESPACE)
            return

        elif check_result == CHECK_FAILED_EMAIL_USERNAME_EMPTY:
            QtGui.QMessageBox.critical(get_main_window(),
                                       MESSAGEBOX_TITLE,
                                       MESSAGE_ERROR_CHECK_EMAIL_USERNAME_EMPTY)
            return

        elif check_result == CHECK_FAILED_EMAIL_USERNAME_NON_ASCII:
            QtGui.QMessageBox.critical(get_main_window(),
                                       MESSAGEBOX_TITLE,
                                       MESSAGE_ERROR_CHECK_EMAIL_USERNAME_NON_ASCII)
            return

        elif check_result == CHECK_FAILED_EMAIL_USERNAME_WHITESPACE:
            QtGui.QMessageBox.critical(get_main_window(),
                                       MESSAGEBOX_TITLE,
                                       MESSAGE_ERROR_CHECK_EMAIL_USERNAME_WHITESPACE)
            return

        elif check_result == CHECK_FAILED_EMAIL_PASSWORD_EMPTY:
            QtGui.QMessageBox.critical(get_main_window(),
                                       MESSAGEBOX_TITLE,
                                       MESSAGE_ERROR_CHECK_EMAIL_PASSWORD_EMPTY)
            return

        elif check_result == CHECK_FAILED_EMAIL_PASSWORD_NON_ASCII:
            QtGui.QMessageBox.critical(get_main_window(),
                                       MESSAGEBOX_TITLE,
                                       MESSAGE_ERROR_CHECK_EMAIL_PASSWORD_NON_ASCII)
            return

        test_email_dict = {'test_email_from'    : self.ledit_sm_email_from.text(),
                           'test_email_to'      : self.ledit_sm_email_to.text(),
                           'test_email_server'  : self.ledit_sm_email_server.text(),
                           'test_email_port'    : str(self.sbox_sm_email_port.value()),
                           'test_email_username': self.ledit_sm_email_username.text(),
                           'test_email_password': self.ledit_sm_email_password.text(),
                           'test_email_tls'     : 'no'}

        if self.chkbox_sm_email_tls.isChecked():
            test_email_dict['test_email_tls'] = 'yes'

        self.working = True
        self.update_gui(EVENT_CLICKED_REFRESH_GENERIC)
        self.script_manager.execute_script('settings_server_monitoring',
                                           self.cb_settings_server_monitoring_test_email,
                                           ['TEST_EMAIL', json.dumps(test_email_dict)])

    def slot_cbox_authentication_activated(self, index):
        sender = self.sender()

        for r in range(self.model_hosts.rowCount()):
            for c in range(COUNT_COLUMNS_HOSTS_MODEL):
                item = self.model_hosts.item(r, c)
                index = self.model_hosts.indexFromItem(item)

                if sender == self.tview_sm_hosts.indexWidget(index):
                    item_secret = self.model_hosts.item(r, INDEX_COL_HOSTS_SECRET)
                    index_secret = self.model_hosts.indexFromItem(item_secret)
                    ledit_secret = self.tview_sm_hosts.indexWidget(index_secret)

                    if sender.currentText() == 'On':
                        ledit_secret.setEnabled(True)
                    elif sender.currentText() == 'Off':
                        ledit_secret.setEnabled(False)

        self.update_gui(EVENT_INPUT_CHANGED)

    def slot_refresh_uids_clicked(self):
        if self.working:
            return

        sender = self.sender()
        host   = None
        port   = None
        secret = None

        for r in range(self.model_hosts.rowCount()):
            for c in range(COUNT_COLUMNS_HOSTS_MODEL):
                item = self.model_hosts.item(r, c)
                index = self.model_hosts.indexFromItem(item)

                if sender == self.tview_sm_hosts.indexWidget(index):
                    item_host = self.model_hosts.item(r, INDEX_COL_HOSTS_HOST)
                    index_host = self.model_hosts.indexFromItem(item_host)
                    ledit_host = self.tview_sm_hosts.indexWidget(index_host)

                    item_port = self.model_hosts.item(r, INDEX_COL_HOSTS_PORT)
                    index_port = self.model_hosts.indexFromItem(item_port)
                    sbox_port = self.tview_sm_hosts.indexWidget(index_port)

                    item_secret = self.model_hosts.item(r, INDEX_COL_HOSTS_SECRET)
                    index_secret = self.model_hosts.indexFromItem(item_secret)
                    ledit_secret = self.tview_sm_hosts.indexWidget(index_secret)

                    host = ledit_host.text()
                    port = unicode(sbox_port.value())

                    if not ledit_secret.isEnabled():
                        secret = ''
                    else:
                        secret = ledit_secret.text()

        if host and port:
            self.working = True
            self.update_gui(EVENT_CLICKED_REFRESH_GENERIC)
            self.remaining_enumerations = 1
            self.script_manager.execute_script('settings_server_monitoring',
                                               lambda result: self.cb_settings_server_monitoring_enumerate(False, result, True),
                                               ['ENUMERATE',
                                                host,
                                                port,
                                                secret])

    def slot_remove_host_clicked(self):
        sender = self.sender()
        host = None

        for r in range(self.model_hosts.rowCount()):
            for c in range(COUNT_COLUMNS_HOSTS_MODEL):
                item = self.model_hosts.item(r, c)
                index = self.model_hosts.indexFromItem(item)

                if sender == self.tview_sm_hosts.indexWidget(index):
                    item_host  = self.model_hosts.item(r, INDEX_COL_HOSTS_HOST)
                    index_host = self.model_hosts.indexFromItem(item_host)
                    ledit_host = self.tview_sm_hosts.indexWidget(index_host)

                    item_used   = self.model_hosts.item(r, INDEX_COL_HOSTS_USED)
                    index_used  = self.model_hosts.indexFromItem(item_used)
                    chkbox_used = self.tview_sm_hosts.indexWidget(index_used)

                    host = ledit_host.text()

                    if chkbox_used.isChecked():
                        reply = QtGui.QMessageBox.question(get_main_window(),
                                                           MESSAGEBOX_TITLE,
                                                           MESSAGE_WARNING_REMOVE_DEPENDENT_RULES,
                                                           QtGui.QMessageBox.Yes,
                                                           QtGui.QMessageBox.No)

                        if reply != QtGui.QMessageBox.Yes:
                            return

                        # Remove rules those depend on the host that is being removed
                        for r_rules in reversed(range(self.model_rules.rowCount())):
                            item_rules_host   = self.model_rules.item(r_rules, INDEX_COL_RULES_HOST)
                            index_rules_host  = self.model_rules.indexFromItem(item_rules_host)
                            cbox_rules_host   = self.tview_sm_rules.indexWidget(index_rules_host)

                            if host == cbox_rules_host.currentText():
                                self.model_rules.removeRows(r_rules, 1)

                    self.model_hosts.removeRows(r, 1)

        if host:
            del self.dict_hosts[host]

        self.update_gui(EVENT_INPUT_CHANGED)

    def slot_host_edited(self, text):
        self.update_gui(EVENT_INPUT_CHANGED)
        sender = self.sender()

        for r in range(self.model_hosts.rowCount()):
            for c in range(COUNT_COLUMNS_HOSTS_MODEL):
                item = self.model_hosts.item(r, c)
                index = self.model_hosts.indexFromItem(item)

                if sender == self.tview_sm_hosts.indexWidget(index):
                    item_hidden_host = self.model_hosts.item(r, INDEX_COL_HOSTS_HIDDEN_HOST)
                    item_hidden_host.setText(text)

                    break

        self.slot_cbox_host_activated(-1)

    def slot_remove_rule_clicked(self):
        sender = self.sender()

        for r in range(self.model_rules.rowCount()):
            for c in range(COUNT_COLUMNS_RULES_MODEL):
                item = self.model_rules.item(r, c)
                index = self.model_rules.indexFromItem(item)
                if sender == self.tview_sm_rules.indexWidget(index):
                    self.model_rules.removeRows(r, 1)
                    break

        self.update_hosts_used()
        self.update_gui(EVENT_INPUT_CHANGED)

    def slot_pbutton_sm_add_rule_clicked(self):
        if not self.defaulthost:
            QtGui.QMessageBox.critical(get_main_window(),
                                       MESSAGEBOX_TITLE,
                                       MESSAGE_ERROR_NO_LOCALHOST)
            return

        bricklet = 'ambient_light'
        uid = ''
        warning_low = '225'
        warning_high = '1075'
        critical_low = '225'
        critical_high = '1075'
        email_notification_enabled = '0'
        email_notifications = 'c,r'

        self.add_new_rule(EMPTY_SERVICE_NAME,
                          self.defaulthost,
                          bricklet,
                          uid,
                          warning_low,
                          warning_high,
                          critical_low,
                          critical_high,
                          email_notification_enabled,
                          email_notifications)

        self.update_hosts_used()
        self.update_gui(EVENT_INPUT_CHANGED)

    def slot_pbutton_sm_remove_all_rules_clicked(self):
        reply = QtGui.QMessageBox.question(get_main_window(),
                                           MESSAGEBOX_TITLE,
                                           MESSAGE_WARNING_REMOVE_ALL_RULES,
                                           QtGui.QMessageBox.Yes,
                                           QtGui.QMessageBox.No)

        if reply != QtGui.QMessageBox.Yes:
            return

        # Remove all rules from GUI model
        for r in reversed(range(self.model_rules.rowCount())):
            self.model_rules.removeRows(r, 1)

        self.update_hosts_used()
        self.update_gui(EVENT_INPUT_CHANGED)

    def slot_pbutton_sm_remove_all_hosts_clicked(self):
        reply = QtGui.QMessageBox.question(get_main_window(),
                                           MESSAGEBOX_TITLE,
                                           MESSAGE_WARNING_REMOVE_ALL_HOSTS,
                                           QtGui.QMessageBox.Yes,
                                           QtGui.QMessageBox.No)

        if reply != QtGui.QMessageBox.Yes:
            return

        # Delete all hosts except the default one.
        # Also remove all dependent rules from rules GUI model

        # From data structure
        for host in self.dict_hosts.keys():
            if host == self.defaulthost:
                continue

            for r in reversed(range(self.model_rules.rowCount())):
                item_host = self.model_rules.item(r, INDEX_COL_RULES_HOST)
                index_host = self.model_rules.indexFromItem(item_host)

                if host != self.tview_sm_rules.indexWidget(index_host).currentText():
                    continue

                self.model_rules.removeRows(r, 1)

            del self.dict_hosts[host]

        # From the GUI model
        for r in reversed(range(self.model_hosts.rowCount())):
            item_host = self.model_hosts.item(r, INDEX_COL_HOSTS_HOST)
            index_host = self.model_hosts.indexFromItem(item_host)
            
            if self.defaulthost == self.tview_sm_hosts.indexWidget(index_host).text():
                continue

            self.model_hosts.removeRows(r, 1)

        self.update_gui(EVENT_INPUT_CHANGED)

    def slot_pbutton_sm_add_host_clicked(self):
        if self.working:
            return

        add_host_dialog = REDTabSettingsServerMonitoringAddHostDialog(self)
        return_code_dialog = add_host_dialog.exec_()

        if return_code_dialog == QtGui.QDialog.Accepted:
            # Check if host is already there
            for r in range(self.model_hosts.rowCount()):
                for c in range(COUNT_COLUMNS_HOSTS_MODEL):
                    if c == INDEX_COL_HOSTS_HOST:
                        item_host = self.model_hosts.item(r, c)
                        index_host = self.model_hosts.indexFromItem(item_host)
                        ledit_host = self.tview_sm_hosts.indexWidget(index_host)

                        if ledit_host.text() == add_host_dialog.host:
                            QtGui.QMessageBox.critical(get_main_window(),
                                                       MESSAGEBOX_TITLE,
                                                       MESSAGE_ERROR_HOST_ALREADY_EXISTS)
                            return

            self.working = True
            self.update_gui(EVENT_CLICKED_REFRESH_GENERIC)
            self.remaining_enumerations = 1
            self.script_manager.execute_script('settings_server_monitoring',
                                               lambda result: self.cb_settings_server_monitoring_enumerate(False, result),
                                               ['ENUMERATE',
                                                add_host_dialog.host,
                                                add_host_dialog.port,
                                                add_host_dialog.secret])
            add_host_dialog.done(0)
        else:
            add_host_dialog.done(0)

    def slot_pbutton_sm_refresh_clicked(self):
        if self.working:
            return

        self.update_gui(EVENT_CLICKED_REFRESH)

        result = self.check_unused_host()

        self.working = True

        self.script_manager.execute_script('settings_server_monitoring',
                                           self.cb_settings_server_monitoring_get_localhost,
                                           ['GET_LOCALHOST'])

    def slot_pbutton_sm_save_clicked(self):
        if self.working:
            return

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

            elif check_result == CHECK_FAILED_EMAIL_FROM_MALFORMED:
                QtGui.QMessageBox.critical(get_main_window(),
                                           MESSAGEBOX_TITLE,
                                           MESSAGE_ERROR_CHECK_EMAIL_FROM_MALFORMED)
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

            elif check_result == CHECK_FAILED_EMAIL_TO_MALFORMED:
                QtGui.QMessageBox.critical(get_main_window(),
                                           MESSAGEBOX_TITLE,
                                           MESSAGE_ERROR_CHECK_EMAIL_TO_MALFORMED)
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

        result = self.check_unused_host()

        if not result:
            reply = QtGui.QMessageBox.question(get_main_window(),
                                               MESSAGEBOX_TITLE,
                                               MESSAGE_WARNING_CHECK_UNUSED_HOST,
                                               QtGui.QMessageBox.Yes,
                                               QtGui.QMessageBox.No)
            if reply != QtGui.QMessageBox.Yes:
                self.update_gui(EVENT_RETURNED_SAVE_FALSE)
                return

            for r in reversed(range(self.model_hosts.rowCount())):
                for c in range(COUNT_COLUMNS_HOSTS_MODEL):
                    if c == INDEX_COL_HOSTS_USED:
                        item_used   = self.model_hosts.item(r, c)
                        index_used  = self.model_hosts.indexFromItem(item_used)
                        chkbox_used = self.tview_sm_hosts.indexWidget(index_used)
    
                        if not chkbox_used.isChecked():
                            self.model_hosts.removeRows(r, 1)

        if self.model_rules.rowCount() > 0:
            # Generating data structure
            apply_dict = {}

            apply_dict['rules'] = []

            for r in range(self.model_rules.rowCount()):
                widget_name                = None
                widget_bricklet            = None
                widget_uid                 = None
                widget_warning             = None
                widget_critical            = None
                widget_email_notifications = None

                for c in range(COUNT_COLUMNS_RULES_MODEL):
                    item = self.model_rules.item(r, c)
                    index = self.model_rules.indexFromItem(item)

                    if c == INDEX_COL_RULES_NAME:
                        widget_name = self.tview_sm_rules.indexWidget(index)

                    elif c == INDEX_COL_RULES_HOST:
                        widget_host = self.tview_sm_rules.indexWidget(index)

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

                host_name = widget_host.currentText()
                host_port, host_authentication, host_secret = self.get_host_parameters(host_name)

                if host_authentication == 'Off':
                    command_line = '''/usr/local/bin/check_tinkerforge.py \
-H {0} \
-P {1} \
-b {2} \
-u {3} \
-w {4} \
-c {5} \
-w2 {6} \
-c2 {7}'''.format(quote(host_name),
                  host_port,
                  SUPPORTED_BRICKLETS[widget_bricklet.currentText()]['id'],
                  widget_uid.currentText(),
                  str(widget_warning.sbox_upper.value()),
                  str(widget_critical.sbox_upper.value()),
                  str(widget_warning.sbox_lower.value()),
                  str(widget_critical.sbox_lower.value()))
                else:
                    command_line = '''/usr/local/bin/check_tinkerforge.py \
-H {0} \
-P {1} \
-S {2} \
-b {3} \
-u {4} \
-w {5} \
-c {6} \
-w2 {7} \
-c2 {8}'''.format(quote(host_name),
                  host_port,
                  host_secret,
                  SUPPORTED_BRICKLETS[widget_bricklet.currentText()]['id'],
                  widget_uid.currentText(),
                  str(widget_warning.sbox_upper.value()),
                  str(widget_critical.sbox_upper.value()),
                  str(widget_warning.sbox_lower.value()),
                  str(widget_critical.sbox_lower.value()))

                if widget_email_notifications.currentIndex() == INDEX_EMAIL_NO_NOTIFICATIONS or\
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

            self.working = True
            self.script_manager.execute_script('settings_server_monitoring',
                                               self.cb_settings_server_monitoring_apply,
                                               ['APPLY', json.dumps(apply_dict)])

        else:
            self.working = True
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
            self.pbutton_sm_email_test.show()
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
            self.pbutton_sm_email_test.hide()

        if self.from_constructor:
            self.from_constructor = False
            return

        self.update_gui(EVENT_INPUT_CHANGED)

    def slot_chkbox_sm_email_password_show_state_changed(self, state):
        if state == QtCore.Qt.Checked:
            self.ledit_sm_email_password.setEchoMode(QtGui.QLineEdit.Normal)
        else:
            self.ledit_sm_email_password.setEchoMode(QtGui.QLineEdit.Password)

    def slot_cbox_host_activated(self, index):
        sender = self.sender()

        if index == -1:
            for r in range(self.model_rules.rowCount()):
                item_host      = self.model_rules.item(r, INDEX_COL_RULES_HOST)
                index_host     = self.model_rules.indexFromItem(item_host)
                cbox_host      = self.tview_sm_rules.indexWidget(index_host)

                item_bricklet  = self.model_rules.item(r, INDEX_COL_RULES_BRICKLET)
                index_bricklet = self.model_rules.indexFromItem(item_bricklet)
                cbox_bricklet  = self.tview_sm_rules.indexWidget(index_bricklet)

                item_uid       = self.model_rules.item(r, INDEX_COL_RULES_UID)
                index_uid      = self.model_rules.indexFromItem(item_uid)
                cbox_uid       = self.tview_sm_rules.indexWidget(index_uid)

                self.populate_cbox_uids(cbox_host, cbox_bricklet, cbox_uid)

            self.update_hosts_used()
            self.update_gui(EVENT_INPUT_CHANGED)

            return

        for r in range(self.model_rules.rowCount()):
            for c in range(COUNT_COLUMNS_RULES_MODEL):
                item = self.model_rules.item(r, c)
                index = self.model_rules.indexFromItem(item)

                if sender == self.tview_sm_rules.indexWidget(index):
                    cbox_host = self.tview_sm_rules.indexWidget(index)

                    item_bricklet  = self.model_rules.item(r, INDEX_COL_RULES_BRICKLET)
                    index_bricklet = self.model_rules.indexFromItem(item_bricklet)
                    cbox_bricklet  = self.tview_sm_rules.indexWidget(index_bricklet)

                    item_uid       = self.model_rules.item(r, INDEX_COL_RULES_UID)
                    index_uid      = self.model_rules.indexFromItem(item_uid)
                    cbox_uid       = self.tview_sm_rules.indexWidget(index_uid)

                    self.populate_cbox_uids(cbox_host, cbox_bricklet, cbox_uid)

                    break

        self.update_hosts_used()
        self.update_gui(EVENT_INPUT_CHANGED)

    def slot_cbox_bricklet_activated(self, index):
        sender = self.sender()

        for r in range(self.model_rules.rowCount()):
            for c in range(COUNT_COLUMNS_RULES_MODEL):
                item = self.model_rules.item(r, c)
                index = self.model_rules.indexFromItem(item)

                if sender == self.tview_sm_rules.indexWidget(index):
                    cbox_bricklet = self.tview_sm_rules.indexWidget(index)

                    item_host      = self.model_rules.item(r, INDEX_COL_RULES_HOST)
                    index_host     = self.model_rules.indexFromItem(item_host)
                    cbox_host      = self.tview_sm_rules.indexWidget(index_host)

                    item_uid       = self.model_rules.item(r, INDEX_COL_RULES_UID)
                    index_uid      = self.model_rules.indexFromItem(item_uid)
                    cbox_uid       = self.tview_sm_rules.indexWidget(index_uid)

                    item_warning_widget_spin_span = self.model_rules.item(r, INDEX_COL_RULES_WARNING)
                    index_warning_widget_spin_span = self.model_rules.indexFromItem(item_warning_widget_spin_span)
                    warning_widget_spin_span = self.tview_sm_rules.indexWidget(index_warning_widget_spin_span)

                    item_critical_widget_spin_span = self.model_rules.item(r, INDEX_COL_RULES_CRITICAL)
                    index_critical_widget_spin_span = self.model_rules.indexFromItem(item_critical_widget_spin_span)
                    critical_widget_spin_span = self.tview_sm_rules.indexWidget(index_critical_widget_spin_span)

                    item_unit = self.model_rules.item(r, INDEX_COL_RULES_UNIT)
                    index_unit = self.model_rules.indexFromItem(item_unit)
                    label_unit = self.tview_sm_rules.indexWidget(index_unit)

                    self.populate_cbox_uids(cbox_host, cbox_bricklet, cbox_uid)

                    self.set_range_widgetSpinBoxSpanSlider(SUPPORTED_BRICKLETS[sender.currentText()]['id'],
                                                           warning_widget_spin_span)
                    self.set_initial_value_widgetSpinBoxSpanSlider(warning_widget_spin_span)
                    self.set_range_widgetSpinBoxSpanSlider(SUPPORTED_BRICKLETS[sender.currentText()]['id'],
                                                           critical_widget_spin_span)
                    self.set_initial_value_widgetSpinBoxSpanSlider(critical_widget_spin_span)

                    label_unit.setText(SUPPORTED_BRICKLETS[sender.currentText()]['unit'])

                    break

        self.update_gui(EVENT_INPUT_CHANGED)

    def slot_cbox_uid_activated(self, index):
        sender = self.sender()

        for r in range(self.model_rules.rowCount()):
            for c in range(COUNT_COLUMNS_RULES_MODEL):
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

    def slot_input_changed(self, value):
        self.update_gui(EVENT_INPUT_CHANGED)
