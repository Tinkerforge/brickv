# -*- coding: utf-8 -*-
"""
brickv (Brick Viewer)
Copyright (C) 2012, 2014 Roland Dudko <roland.dudko@gmail.com>
Copyright (C) 2012, 2014 Marvin Lutz <marvin.lutz.mail@gmail.com>

logger_setup.py: Data logger setup dialog

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

import codecs
import collections
import os
import time
import functools
import logging
from datetime import datetime

from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import Qt, QRegExp
from PyQt4.QtGui import QDialog, QMessageBox, QPalette, QStandardItemModel, \
                        QStandardItem, QLineEdit, QSpinBox, QCheckBox, QComboBox, \
                        QSpinBox, QDoubleSpinBox, QRegExpValidator

from brickv import config
from brickv.bindings.ip_connection import BASE58
from brickv.utils import get_save_file_name, get_open_file_name, get_main_window, get_home_path
from brickv.data_logger.event_logger import EventLogger, GUILogger
from brickv.data_logger.gui_config_handler import GuiConfigHandler
from brickv.data_logger.job import GuiDataJob
from brickv.data_logger.loggable_devices import Identifier
from brickv.data_logger import utils
from brickv.data_logger.device_dialog import DeviceDialog
from brickv.data_logger.configuration import load_and_validate_config, save_config
from brickv.data_logger.ui_setup_dialog import Ui_SetupDialog

# noinspection PyProtectedMember,PyCallByClass
class SetupDialog(QDialog, Ui_SetupDialog):
    """
        Function and Event handling class for the Ui_SetupDialog.
    """

    def __init__(self, parent):
        QDialog.__init__(self, parent)

        self._gui_logger = GUILogger("GUILogger", EventLogger.EVENT_LOG_LEVEL)
        self._gui_job = None
        EventLogger.add_logger(self._gui_logger)

        # FIXME better way to find interval and uids in tree_widget?!
        self.__tree_interval_tooltip = "Update interval in seconds"
        self.__tree_uid_tooltip = "UID cannot be empty"
        self.data_logger_thread = None
        self.tab_console_warning = False

        self.device_dialog = None

        self.host_infos = None
        self.last_host = None
        self.host_index_changing = None

        self.setupUi(self)

        self.model_data = QStandardItemModel()
        self.model_data.setHorizontalHeaderLabels(['UID', 'Name', 'Var', 'Raw', 'Unit', 'Time'])
        self.table_data.setModel(self.model_data)

        self.model_devices = QStandardItemModel()
        self.model_devices.setHorizontalHeaderLabels(['Device', 'Value'])
        self.tree_devices.setModel(self.model_devices)
        self.tree_devices.setColumnWidth(0, 300)

        self.widget_initialization()

        timestamp = int(time.time())
        self.edit_csv_file_name.setText(os.path.join(get_home_path(), 'logger_data_{0}.csv'.format(timestamp)))
        self.edit_log_file_name.setText(os.path.join(get_home_path(), 'logger_events_{0}.log'.format(timestamp)))

        self.combo_data_time_format.addItem(utils.timestamp_to_de(timestamp) + ' (DD.MM.YYYY HH:MM:SS)', 'de')
        self.combo_data_time_format.addItem(utils.timestamp_to_us(timestamp) + ' (MM/DD/YYYY HH:MM:SS)', 'us')
        self.combo_data_time_format.addItem(utils.timestamp_to_iso(timestamp) + ' (ISO 8601)', 'iso')
        self.combo_data_time_format.addItem(utils.timestamp_to_unix(timestamp) + ' (Unix)', 'unix')

        self.combo_events_time_format.addItem(utils.timestamp_to_de(timestamp) + ' (DD.MM.YYYY HH:MM:SS)', 'de')
        self.combo_events_time_format.addItem(utils.timestamp_to_us(timestamp) + ' (MM/DD/YYYY HH:MM:SS)', 'us')
        self.combo_events_time_format.addItem(utils.timestamp_to_iso(timestamp) + ' (ISO 8601)', 'iso')
        self.combo_events_time_format.addItem(utils.timestamp_to_unix(timestamp) + ' (Unix)', 'unix')

        self.combo_log_level.addItem('Debug', 'debug')
        self.combo_log_level.addItem('Info', 'info')
        self.combo_log_level.addItem('Warning', 'warning')
        self.combo_log_level.addItem('Error', 'error')
        self.combo_log_level.addItem('Critical', 'critical')
        self.combo_log_level.setCurrentIndex(0) # debug

        self.combo_events_level.addItem('Debug', logging.DEBUG)
        self.combo_events_level.addItem('Info', logging.INFO)
        self.combo_events_level.addItem('Warning', logging.WARNING)
        self.combo_events_level.addItem('Error', logging.ERROR)
        self.combo_events_level.addItem('Critical', logging.CRITICAL)
        self.combo_events_level.setCurrentIndex(1) # info

        self.update_ui_state()

    def update_ui_state(self):
        data_to_csv_file = self.check_data_to_csv_file.isChecked()
        events_to_log_file = self.check_events_to_log_file.isChecked()

        self.label_csv_file_name.setVisible(data_to_csv_file)
        self.edit_csv_file_name.setVisible(data_to_csv_file)
        self.btn_browse_csv_file_name.setVisible(data_to_csv_file)
        self.label_csv_file_count.setVisible(data_to_csv_file)
        self.spin_csv_file_count.setVisible(data_to_csv_file)
        self.label_csv_file_size.setVisible(data_to_csv_file)
        self.spin_csv_file_size.setVisible(data_to_csv_file)

        self.label_log_file_name.setVisible(events_to_log_file)
        self.edit_log_file_name.setVisible(events_to_log_file)
        self.btn_browse_log_file_name.setVisible(events_to_log_file)
        self.label_log_level.setVisible(events_to_log_file)
        self.combo_log_level.setVisible(events_to_log_file)

    def widget_initialization(self):
        """
            Sets default values for some widgets
        """
        # Login data
        self.host_info_initialization()

        self.signal_initialization()

    def signal_initialization(self):
        """
            Init of all important Signals and connections.
        """
        # Buttons
        self.btn_start_logging.clicked.connect(self.btn_start_logging_clicked)
        self.btn_save_config.clicked.connect(self.btn_save_config_clicked)
        self.btn_load_config.clicked.connect(self.btn_load_config_clicked)
        self.check_data_to_csv_file.stateChanged.connect(self.update_ui_state)
        self.check_events_to_log_file.stateChanged.connect(self.update_ui_state)
        self.btn_browse_csv_file_name.clicked.connect(self.btn_browse_csv_file_name_clicked)
        self.btn_browse_log_file_name.clicked.connect(self.btn_browse_log_file_name_clicked)
        self.btn_clear_events.clicked.connect(self.btn_clear_events_clicked)
        self.combo_events_level.currentIndexChanged.connect(self.combo_events_level_changed)
        self.btn_add_device.clicked.connect(self.btn_add_device_clicked)
        self.btn_remove_device.clicked.connect(self.btn_remove_device_clicked)
        self.btn_remove_all_devices.clicked.connect(self.btn_remove_all_devices_clicked)

        self.tab_widget.currentChanged.connect(self.tab_reset_warning)
        self.btn_clear_data.clicked.connect(self.btn_clear_data_clicked)

        self.connect(self._gui_logger, QtCore.SIGNAL(GUILogger.SIGNAL_NEW_MESSAGE), self.txt_console_output)
        self.connect(self._gui_logger, QtCore.SIGNAL(GUILogger.SIGNAL_NEW_MESSAGE_TAB_HIGHLIGHT),
                     self.txt_console_highlight_tab)

        # login information
        self.combo_host.currentIndexChanged.connect(self._host_index_changed)
        self.spin_port.valueChanged.connect(self._port_changed)

        #self.tree_devices.itemDoubleClicked.connect(self.tree_on_double_click)
        #self.tree_devices.itemChanged.connect(self.tree_on_change)
        #self.tree_devices.itemChanged.connect(self.cb_device_interval_changed)

    def host_info_initialization(self):
        """
            initialize host by getting information out of brickv.config
        """
        self.host_infos = config.get_host_infos(config.HOST_INFO_COUNT)
        self.host_index_changing = True

        for host_info in self.host_infos:
            self.combo_host.addItem(host_info.host)

        self.last_host = None
        self.combo_host.setCurrentIndex(0)
        self.spin_port.setValue(self.host_infos[0].port)
        self.host_index_changing = False

    def btn_start_logging_clicked(self):
        """
            Start/Stop of the logging process
        """
        if (self.data_logger_thread is not None) and (not self.data_logger_thread.stopped):
            self.btn_start_logging.clicked.disconnect()

            self.data_logger_thread.stop()
            self._reset_stop()

        elif self.data_logger_thread is None:
            from brickv.data_logger import main

            arguments_map = {}
            arguments_map[main.GUI_CONFIG] = GuiConfigHandler.create_config(self)
            self._gui_job = GuiDataJob(name="GuiData-Writer")
            self.connect(self._gui_job, QtCore.SIGNAL(GuiDataJob.SIGNAL_NEW_DATA), self.table_add_row)
            arguments_map[main.GUI_ELEMENT] = self._gui_job

            self.data_logger_thread = main.main(arguments_map)

            if self.data_logger_thread is not None:
                self.btn_start_logging.setText("Stop Logging")
                self.tab_devices.setEnabled(False)
                self.tab_setup.setEnabled(False)
                self.tab_widget.setCurrentIndex(self.tab_widget.indexOf(self.tab_csv_data))
                self.tab_reset_warning()

    def _reset_stop(self):
        self.tab_devices.setEnabled(True)
        self.tab_setup.setEnabled(True)
        self.btn_start_logging.setText("Start Logging")

        self.disconnect(self._gui_job, QtCore.SIGNAL(GuiDataJob.SIGNAL_NEW_DATA), self.table_add_row)
        self.data_logger_thread = None
        self._gui_job = None

        self.btn_start_logging.clicked.connect(self.btn_start_logging_clicked)

    def btn_save_config_clicked(self):
        filename = get_save_file_name(get_main_window(), 'Save Config',
                                      get_home_path(), 'JSON Files (*.json)')

        if len(filename) == 0:
            return

        if not filename.lower().endswith('.json'):
            filename += '.json'

        config = GuiConfigHandler.create_config(self)

        if not save_config(config, filename):
            QMessageBox.warning(get_main_window(), 'Save Config',
                                'Could not save config to file! See Events tab for details.',
                                QMessageBox.Ok)

    def btn_load_config_clicked(self):
        filename = get_open_file_name(get_main_window(), 'Load Config',
                                      get_home_path(), 'JSON Files (*.json)')

        if len(filename) == 0:
            return

        config = load_and_validate_config(filename)

        if config == None:
            QMessageBox.warning(get_main_window(), 'Load Config',
                                'Could not load config from file! See Events tab for details.',
                                QMessageBox.Ok)
            return

        self.update_setup_tab(config)
        self.update_devices_tab(config)

    def btn_browse_csv_file_name_clicked(self):
        if len(self.edit_csv_file_name.text()) > 0:
            last_dir = os.path.dirname(os.path.realpath(self.edit_csv_file_name.text()))
        else:
            last_dir = get_home_path()

        filename = get_save_file_name(get_main_window(), 'Choose CSV File',
                                      last_dir, "CSV Files (*.csv)")

        if len(filename) > 0:
            if not filename.lower().endswith('.csv'):
                filename += '.csv'

            self.edit_csv_file_name.setText(filename)

    def btn_browse_log_file_name_clicked(self):
        if len(self.edit_log_file_name.text()) > 0:
            last_dir = os.path.dirname(os.path.realpath(self.edit_log_file_name.text()))
        else:
            last_dir = get_home_path()

        filename = get_save_file_name(get_main_window(), 'Choose Log File',
                                      last_dir, "Log Files (*.log)")

        if len(filename) > 0:
            if not filename.lower().endswith('.log'):
                filename += '.log'

            self.edit_log_file_name.setText(filename)

    def btn_add_device_clicked(self):
        """
            Opens the DeviceDialog in Add-Mode.
        """
        if self.device_dialog is None:
            self.device_dialog = DeviceDialog(self)

        # blueprint = Identifier.DEVICE_DEFINITIONS
        self.device_dialog.init_dialog(self)
        self.device_dialog.show()

    def btn_remove_device_clicked(self):
        selection = self.tree_devices.selectionModel().selectedIndexes()

        while len(selection) > 0:
            index = selection[0]

            while index.parent() != self.model_devices.invisibleRootItem().index():
                index = index.parent()

            self.model_devices.removeRows(index.row(), 1)

            # get new selection, because row removal might invalid indices
            selection = self.tree_devices.selectionModel().selectedIndexes()

    def btn_remove_all_devices_clicked(self):
        self.model_devices.removeRows(0, self.model_devices.rowCount())

    def btn_clear_data_clicked(self):
        self.model_data.removeRows(0, self.model_data.rowCount())

    def tab_reset_warning(self):
        """
            Resets the Warning @ the console tab.
        """
        if not self.tab_console_warning or self.tab_widget.currentWidget().objectName() != self.tab_console.objectName():
            return

        self.tab_console_warning = False
        from PyQt4.QtGui import QColor

        self.tab_set(self.tab_widget.indexOf(self.tab_console), self.palette().color(QPalette.WindowText), None)

    def combo_events_level_changed(self):
        """
            Changes the log level dynamically.
        """
        self._gui_logger.level = self.combo_events_level.itemData(self.combo_events_level.currentIndex())

    def tab_set(self, tab_index, color, icon=None):
        """
            Sets the font Color and an icon, if given, at a specific tab.
        """
        from PyQt4.QtGui import QIcon

        self.tab_widget.tabBar().setTabTextColor(tab_index, color)
        if icon is not None:
            self.tab_widget.setTabIcon(tab_index, QIcon(icon))
        else:
            self.tab_widget.setTabIcon(tab_index, QIcon())

    def btn_clear_events_clicked(self):
        """
            Clears the gui events tab.
        """
        self.txt_console.clear()

    def _host_index_changed(self, i):
        """
            Persists host information changes like in brickv.mainwindow
            Changes port if the host was changed
        """
        if i < 0:
            return

        self.host_index_changing = True
        self.spin_port.setValue(self.host_infos[i].port)
        self.host_index_changing = False

    def _port_changed(self, value):
        """
            Persists host information changes like in brickv.mainwindow
        """
        if self.host_index_changing:
            return

        i = self.combo_host.currentIndex()
        if i < 0:
            return

        self.host_infos[i].port = self.spin_port.value()

    def update_setup_tab(self, config):
        EventLogger.debug('Updating setup tab from config')

        self.combo_host.setEditText(config['hosts']['default']['name'])
        self.spin_port.setValue(config['hosts']['default']['port'])

        self.combo_data_time_format.setCurrentIndex(max(self.combo_data_time_format.findData(config['data']['time_format']), 0))
        self.check_data_to_csv_file.setChecked(config['data']['csv']['enabled'])
        self.edit_csv_file_name.setText(config['data']['csv']['file_name'])
        self.spin_csv_file_count.setValue(config['data']['csv']['file_count'])
        self.spin_csv_file_size.setValue(config['data']['csv']['file_size'])

        self.combo_events_time_format.setCurrentIndex(max(self.combo_events_time_format.findData(config['events']['time_format']), 0))
        self.check_events_to_log_file.setChecked(config['events']['log']['enabled'])
        self.edit_log_file_name.setText(config['events']['log']['file_name'])
        self.combo_log_level.setCurrentIndex(max(self.combo_events_time_format.findData(config['events']['log']['level']), 0))

    def update_devices_tab(self, config):
        EventLogger.debug('Updating devices tab from config')

        self.model_devices.removeRows(0, self.model_data.rowCount())

        for device in config['devices']:
            self.add_device_to_tree(device)

    def add_device_to_tree(self, device):
        # check if device is already added
        if len(device['uid']) > 0:
            for row in range(self.model_devices.rowCount()):
                existing_name = self.model_devices.item(row, 0).text()
                exisitng_uid = self.tree_devices.indexWidget(self.model_devices.item(row, 1).index()).text()

                if device['name'] == existing_name and device['uid'] == exisitng_uid:
                    EventLogger.info('Ignoring duplicate device "{0}" with UID "{1}"'
                                     .format(device['name'], device['uid']))
                    return

        # add device
        name_item = QStandardItem(device['name'])
        uid_item = QStandardItem('')

        self.model_devices.appendRow([name_item, uid_item])

        edit_uid = QLineEdit()
        edit_uid.setPlaceholderText('Enter UID')
        edit_uid.setValidator(QRegExpValidator(QRegExp('^[{0}]{{1,6}}$'.format(BASE58)))) # FIXME: use stricter logic
        edit_uid.setText(device['uid'])

        self.tree_devices.setIndexWidget(uid_item.index(), edit_uid)

        value_specs = Identifier.DEVICE_DEFINITIONS[device['name']]['values']
        parent_item = QStandardItem('Values')

        name_item.appendRow(parent_item)
        self.tree_devices.expand(parent_item.index())

        # add values
        for value_spec in value_specs:
            value_name_item = QStandardItem(value_spec['name'])
            value_interval_item = QStandardItem('')

            parent_item.appendRow([value_name_item, value_interval_item])

            spinbox_interval = QSpinBox()
            spinbox_interval.setRange(0, (1 << 31) - 1)
            spinbox_interval.setSingleStep(1)
            spinbox_interval.setValue(device['values'][value_spec['name']]['interval'])
            spinbox_interval.setSuffix(' seconds')

            self.tree_devices.setIndexWidget(value_interval_item.index(), spinbox_interval)

            if value_spec['subvalues'] != None:
                for subvalue_name in value_spec['subvalues']:
                    subvalue_name_item = QStandardItem(subvalue_name)
                    subvalue_check_item = QStandardItem('')

                    value_name_item.appendRow([subvalue_name_item, subvalue_check_item])

                    check_subvalue = QCheckBox()
                    check_subvalue.setChecked(device['values'][value_spec['name']]['subvalues'][subvalue_name])

                    self.tree_devices.setIndexWidget(subvalue_check_item.index(), check_subvalue)

        self.tree_devices.expand(name_item.index())

        # add options
        option_specs = Identifier.DEVICE_DEFINITIONS[device['name']]['options']

        if option_specs != None:
            parent_item = QStandardItem('Options')

            name_item.appendRow(parent_item)

            for option_spec in option_specs:
                option_name_item = QStandardItem(option_spec['name'])
                option_widget_item = QStandardItem('')

                parent_item.appendRow([option_name_item, option_widget_item])

                if option_spec['type'] == 'choice':
                    widget_option_value = QComboBox()

                    for option_value_spec in option_spec['values']:
                        widget_option_value.addItem(option_value_spec[0], option_value_spec[1])

                    widget_option_value.setCurrentIndex(widget_option_value.findText(device['options'][option_spec['name']]['value']))
                elif option_spec['type'] == 'int':
                    widget_option_value = QSpinBox()

                    widget_option_value.setRange(option_spec['minimum'], option_spec['maximum'])
                    widget_option_value.setSuffix(option_spec['suffix'])
                    widget_option_value.setValue(device['options'][option_spec['name']]['value'])
                elif option_spec['type'] == 'float':
                    widget_option_value = QDoubleSpinBox()

                    widget_option_value.setRange(option_spec['minimum'], option_spec['maximum'])
                    widget_option_value.setDecimals(option_spec['decimals'])
                    widget_option_value.setSuffix(option_spec['suffix'])
                    widget_option_value.setValue(device['options'][option_spec['name']]['value'])

                self.tree_devices.setIndexWidget(option_widget_item.index(), widget_option_value)

    def txt_console_output(self, msg):
        """
            SIGNAL function:
            Function to write text on the gui console tab.
        """
        self.txt_console.append(str(msg))
        if self.checkbox_console_auto_scroll.isChecked():
            self.txt_console.moveCursor(QtGui.QTextCursor.End)


    def txt_console_highlight_tab(self):
        """
            SIGNAL function:
            Highlight the events tab when an error occurs.
        """
        if not self.tab_console_warning and self.tab_widget.currentWidget().objectName() != self.tab_console.objectName():
            self.tab_console_warning = True
            from brickv.utils import get_resources_path
            from PyQt4.QtGui import QColor

            self.tab_set(self.tab_widget.indexOf(self.tab_console), QColor(255, 0, 0),
                         os.path.join(get_resources_path(), "warning-icon.png"))

    def table_add_row(self, csv_data):
        """
            SIGNAL function:
            Adds new CSV Data into the Table.
        """
        rows = self.model_data.rowCount()

        while rows >= 1000:
            self.model_data.removeRow(0)
            rows = self.model_data.rowCount()

        row_number = None

        if rows > 0:
            try:
                row_number = int(self.model_data.headerData(rows - 1, Qt.Vertical))
            except ValueError:
                pass

        self.model_data.appendRow([QStandardItem(csv_data.uid),
                                   QStandardItem(csv_data.name),
                                   QStandardItem(csv_data.var_name),
                                   QStandardItem(str(csv_data.raw_data)),
                                   QStandardItem(csv_data.var_unit),
                                   QStandardItem(csv_data.timestamp)])

        if row_number != None:
            self.model_data.setHeaderData(rows, Qt.Vertical, str(row_number + 1))

        if self.checkbox_data_auto_scroll.isChecked():
            self.table_data.scrollToBottom()
