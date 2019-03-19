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

import os
import time
import functools
import logging
from datetime import datetime

from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QRegExp
from PyQt5.QtWidgets import QDialog, QMessageBox, QLineEdit, QSpinBox, QCheckBox, QComboBox, \
                        QHBoxLayout, QWidget
from PyQt5.QtGui import QPalette, QStandardItemModel, QStandardItem, QRegExpValidator, QIcon, QColor, QTextCursor

from brickv.bindings.ip_connection import BASE58
from brickv.load_pixmap import load_pixmap
from brickv.utils import get_save_file_name, get_open_file_name, \
                         get_home_path, get_resources_path, get_modeless_dialog_flags
from brickv.data_logger.event_logger import EventLogger, GUILogger
from brickv.data_logger.gui_config_handler import GuiConfigHandler
from brickv.data_logger.job import GuiDataJob
from brickv.data_logger.loggable_devices import device_specs
from brickv.data_logger import utils
from brickv.data_logger.device_dialog import DeviceDialog
from brickv.data_logger.configuration import load_and_validate_config, save_config
from brickv.data_logger.ui_setup_dialog import Ui_SetupDialog

class IntervalWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.spinbox = QSpinBox(self)
        self.combo = QComboBox(self)

        sp = self.spinbox.sizePolicy()
        sp.setHorizontalStretch(1)
        self.spinbox.setSizePolicy(sp)

        self.spinbox.setRange(0, (1 << 31) - 1)
        self.spinbox.setSingleStep(1)

        self.combo.addItem('Seconds')
        self.combo.addItem('Milliseconds')

        layout.addWidget(self.spinbox)
        layout.addWidget(self.combo)

    def set_interval(self, interval):
        if ('%.03f' % interval).endswith('.000'):
            self.spinbox.setValue(int(interval))
            self.combo.setCurrentIndex(0)
        else:
            self.spinbox.setValue(round(interval * 1000.0))
            self.combo.setCurrentIndex(1)

    def get_interval(self):
        if self.combo.currentIndex() == 0:
            return self.spinbox.value()
        else:
            return self.spinbox.value() / 1000.0

# noinspection PyProtectedMember,PyCallByClass
class SetupDialog(QDialog, Ui_SetupDialog):
    """
        Function and Event handling class for the Ui_SetupDialog.
    """

    def __init__(self, parent, host_infos):
        QDialog.__init__(self, parent, get_modeless_dialog_flags())

        self._gui_logger = GUILogger("GUILogger", logging.INFO)
        self._gui_job = None
        EventLogger.add_logger(self._gui_logger)

        self.data_logger_thread = None
        self.tab_debug_warning = False
        self.device_dialog = None
        self.last_host_index = -1

        self.setupUi(self)

        self.model_data = QStandardItemModel(self)
        self.model_data.setHorizontalHeaderLabels(['Time', 'Name', 'UID', 'Var', 'Raw', 'Unit'])
        self.table_data.setModel(self.model_data)
        self.table_data.setColumnWidth(0, 160)
        self.table_data.setColumnWidth(1, 170)
        self.table_data.setColumnWidth(2, 50)
        self.table_data.setColumnWidth(3, 110)
        self.table_data.setColumnWidth(4, 70)
        self.table_data.setColumnWidth(5, 100)

        self.model_devices = QStandardItemModel(self)
        self.model_devices.setHorizontalHeaderLabels(['Device', 'Value'])
        self.tree_devices.setModel(self.model_devices)
        self.tree_devices.setColumnWidth(0, 300)

        self.signal_initialization()

        self.check_authentication.stateChanged.connect(self.authentication_state_changed)
        self.label_secret.hide()
        self.edit_secret.hide()
        self.edit_secret.setEchoMode(QLineEdit.Password)
        self.check_secret_show.hide()
        self.check_secret_show.stateChanged.connect(self.secret_show_state_changed)

        self.btn_start_logging.setIcon(QIcon(load_pixmap('data_logger/start-icon.png')))

        self.example_timestamp = time.time()

        self.edit_csv_file_name.setText(os.path.join(get_home_path(), 'logger_data_{0}.csv'.format(int(self.example_timestamp))))
        self.edit_log_file_name.setText(os.path.join(get_home_path(), 'logger_debug_{0}.log'.format(int(self.example_timestamp))))

        self.combo_data_time_format.addItem(utils.timestamp_to_de(self.example_timestamp) + ' (DD.MM.YYYY HH:MM:SS)', 'de')
        self.combo_data_time_format.addItem(utils.timestamp_to_de_msec(self.example_timestamp) + ' (DD.MM.YYYY HH:MM:SS,000)', 'de-msec')
        self.combo_data_time_format.insertSeparator(self.combo_data_time_format.count())
        self.combo_data_time_format.addItem(utils.timestamp_to_us(self.example_timestamp) + ' (MM/DD/YYYY HH:MM:SS)', 'us')
        self.combo_data_time_format.addItem(utils.timestamp_to_us_msec(self.example_timestamp) + ' (MM/DD/YYYY HH:MM:SS.000)', 'us-msec')
        self.combo_data_time_format.insertSeparator(self.combo_data_time_format.count())
        self.combo_data_time_format.addItem(utils.timestamp_to_iso(self.example_timestamp) + ' (ISO 8601)', 'iso')
        self.combo_data_time_format.addItem(utils.timestamp_to_iso_msec(self.example_timestamp) + ' (ISO 8601 + Milliseconds)', 'iso-msec')
        self.combo_data_time_format.insertSeparator(self.combo_data_time_format.count())
        self.combo_data_time_format.addItem(utils.timestamp_to_unix(self.example_timestamp) + ' (Unix)', 'unix')
        self.combo_data_time_format.addItem(utils.timestamp_to_unix_msec(self.example_timestamp) + ' (Unix + Milliseconds)', 'unix-msec')
        self.combo_data_time_format.insertSeparator(self.combo_data_time_format.count())

        t = utils.timestamp_to_strftime(self.example_timestamp, self.edit_data_time_format_strftime.text())
        if len(t) == 0:
            t = '<empty>'

        self.combo_data_time_format.addItem((t + ' (strftime)'), 'strftime')

        self.combo_debug_time_format.addItem(utils.timestamp_to_de(self.example_timestamp) + ' (DD.MM.YYYY HH:MM:SS)', 'de')
        self.combo_debug_time_format.addItem(utils.timestamp_to_us(self.example_timestamp) + ' (MM/DD/YYYY HH:MM:SS)', 'us')
        self.combo_debug_time_format.addItem(utils.timestamp_to_iso(self.example_timestamp) + ' (ISO 8601)', 'iso')
        self.combo_debug_time_format.addItem(utils.timestamp_to_unix(self.example_timestamp) + ' (Unix)', 'unix')

        self.combo_log_level.addItem('Debug', 'debug')
        self.combo_log_level.addItem('Info', 'info')
        self.combo_log_level.addItem('Warning', 'warning')
        self.combo_log_level.addItem('Error', 'error')
        self.combo_log_level.addItem('Critical', 'critical')
        self.combo_log_level.setCurrentIndex(0) # debug

        self.combo_debug_level.addItem('Debug', logging.DEBUG)
        self.combo_debug_level.addItem('Info', logging.INFO)
        self.combo_debug_level.addItem('Warning', logging.WARNING)
        self.combo_debug_level.addItem('Error', logging.ERROR)
        self.combo_debug_level.addItem('Critical', logging.CRITICAL)
        self.combo_debug_level.setCurrentIndex(1) # info

        for host_info in host_infos:
            self.combo_host.addItem(host_info.host, (host_info.port, host_info.use_authentication, host_info.secret))

        self._host_index_changed(0)

        self.update_ui_state()

    def update_ui_state(self):
        index = self.combo_data_time_format.currentIndex()

        if index > 0:
            time_format = self.combo_data_time_format.itemData(index)
        else:
            time_format = 'unknown'

        data_to_csv_file = self.check_data_to_csv_file.isChecked()
        debug_to_log_file = self.check_debug_to_log_file.isChecked()

        self.edit_data_time_format_strftime.setVisible(time_format == 'strftime')
        self.label_data_time_format_strftime_help.setVisible(time_format == 'strftime')

        self.label_csv_file_name.setVisible(data_to_csv_file)
        self.edit_csv_file_name.setVisible(data_to_csv_file)
        self.btn_browse_csv_file_name.setVisible(data_to_csv_file)

        self.label_log_file_name.setVisible(debug_to_log_file)
        self.edit_log_file_name.setVisible(debug_to_log_file)
        self.btn_browse_log_file_name.setVisible(debug_to_log_file)
        self.label_log_level.setVisible(debug_to_log_file)
        self.combo_log_level.setVisible(debug_to_log_file)

    def signal_initialization(self):
        """
            Init of all important Signals and connections.
        """
        # Buttons
        self.btn_start_logging.clicked.connect(self.btn_start_logging_clicked)
        self.btn_save_config.clicked.connect(self.btn_save_config_clicked)
        self.btn_load_config.clicked.connect(self.btn_load_config_clicked)
        self.combo_data_time_format.currentIndexChanged.connect(self.update_ui_state)
        self.edit_data_time_format_strftime.textChanged.connect(self.edit_data_time_format_strftime_changed)
        self.check_data_to_csv_file.stateChanged.connect(self.update_ui_state)
        self.check_debug_to_log_file.stateChanged.connect(self.update_ui_state)
        self.btn_browse_csv_file_name.clicked.connect(self.btn_browse_csv_file_name_clicked)
        self.btn_browse_log_file_name.clicked.connect(self.btn_browse_log_file_name_clicked)
        self.btn_clear_debug.clicked.connect(self.btn_clear_debug_clicked)
        self.combo_debug_level.currentIndexChanged.connect(self.combo_debug_level_changed)
        self.btn_add_device.clicked.connect(self.btn_add_device_clicked)
        self.btn_remove_device.clicked.connect(self.btn_remove_device_clicked)
        self.btn_remove_all_devices.clicked.connect(self.btn_remove_all_devices_clicked)

        self.tab_widget.currentChanged.connect(self.tab_reset_warning)
        self.btn_clear_data.clicked.connect(self.btn_clear_data_clicked)

        self._gui_logger.newEventMessage.connect(self.add_debug_message)
        self._gui_logger.newEventTabHighlight.connect(self.highlight_debug_tab)

        self.combo_host.currentIndexChanged.connect(self._host_index_changed)

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

            self._gui_job = GuiDataJob(name="GuiData-Writer")

            self._gui_job.signalNewData.connect(self.table_add_row)

            self.data_logger_thread = main.main(None, GuiConfigHandler.create_config(self), self._gui_job, None, None, None)

            if self.data_logger_thread is not None:
                self.btn_start_logging.setText("Stop Logging")
                self.btn_start_logging.setIcon(QIcon(load_pixmap('data_logger/stop-icon.png')))
                self.tab_devices.setEnabled(False)
                self.tab_setup.setEnabled(False)
                self.tab_widget.setCurrentIndex(self.tab_widget.indexOf(self.tab_data))
                self.tab_reset_warning()

    def _reset_stop(self):
        self.tab_devices.setEnabled(True)
        self.tab_setup.setEnabled(True)
        self.btn_start_logging.setText("Start Logging")
        self.btn_start_logging.setIcon(QIcon(load_pixmap('data_logger/start-icon.png')))


        self._gui_job.signalNewData.disconnect(self.table_add_row)
        self.data_logger_thread = None
        self._gui_job = None

        self.btn_start_logging.clicked.connect(self.btn_start_logging_clicked)

    def authentication_state_changed(self, state):
        visible = state == Qt.Checked

        self.label_secret.setVisible(visible)
        self.edit_secret.setVisible(visible)
        self.check_secret_show.setVisible(visible)

    def secret_show_state_changed(self, state):
        if state == Qt.Checked:
            self.edit_secret.setEchoMode(QLineEdit.Normal)
        else:
            self.edit_secret.setEchoMode(QLineEdit.Password)

    def edit_data_time_format_strftime_changed(self):
        index = self.combo_data_time_format.findData('strftime')

        if index < 0:
            return

        t = utils.timestamp_to_strftime(self.example_timestamp, self.edit_data_time_format_strftime.text())
        if len(t) == 0:
            t = '<empty>'

        self.combo_data_time_format.setItemText(index, (t + ' (strftime)'))

        if self.edit_data_time_format_strftime.isVisible():
            self.edit_data_time_format_strftime.setFocus()

    def btn_save_config_clicked(self):
        filename = get_save_file_name(self, 'Save Config',
                                      get_home_path(), 'JSON Files (*.json)')

        if len(filename) == 0:
            return

        if not filename.lower().endswith('.json'):
            filename += '.json'

        config = GuiConfigHandler.create_config(self)

        if not save_config(config, filename):
            QMessageBox.warning(self, 'Save Config',
                                'Could not save config to file! See Debug tab for details.',
                                QMessageBox.Ok)

    def btn_load_config_clicked(self):
        filename = get_open_file_name(self, 'Load Config',
                                      get_home_path(), 'JSON Files (*.json)')

        if len(filename) == 0:
            return

        config = load_and_validate_config(filename)

        if config == None:
            QMessageBox.warning(self, 'Load Config',
                                'Could not load config from file! See Debug tab for details.',
                                QMessageBox.Ok)
            return

        self.update_setup_tab(config)
        self.update_devices_tab(config)

    def btn_browse_csv_file_name_clicked(self):
        if len(self.edit_csv_file_name.text()) > 0:
            last_dir = os.path.dirname(os.path.realpath(self.edit_csv_file_name.text()))
        else:
            last_dir = get_home_path()

        filename = get_save_file_name(self, 'Choose CSV File',
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

        filename = get_save_file_name(self, 'Choose Log File',
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

        self.device_dialog.btn_refresh_clicked()
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
            Resets the Warning @ the debug tab.
        """
        if not self.tab_debug_warning or self.tab_widget.currentIndex() != self.tab_widget.indexOf(self.tab_debug):
            return

        self.tab_debug_warning = False

        self.tab_set(self.tab_widget.indexOf(self.tab_debug), self.palette().color(QPalette.WindowText), None)

    def combo_debug_level_changed(self):
        """
            Changes the log level dynamically.
        """
        self._gui_logger.level = self.combo_debug_level.itemData(self.combo_debug_level.currentIndex())

    def tab_set(self, tab_index, color, icon=None):
        """
            Sets the font Color and an icon, if given, at a specific tab.
        """
        self.tab_widget.tabBar().setTabTextColor(tab_index, color)
        if icon is not None:
            self.tab_widget.setTabIcon(tab_index, QIcon(icon))
        else:
            self.tab_widget.setTabIcon(tab_index, QIcon())

    def _host_index_changed(self, i):
        if self.last_host_index >= 0:
            self.combo_host.setItemData(self.last_host_index,
                                        (self.spin_port.value(),
                                         self.check_authentication.isChecked(),
                                         self.edit_secret.text()))

        self.last_host_index = i

        if i < 0:
            return

        host_info = self.combo_host.itemData(i)

        self.spin_port.setValue(host_info[0])
        self.check_authentication.setChecked(host_info[1])
        self.edit_secret.setText(host_info[2])

    def update_setup_tab(self, config):
        EventLogger.debug('Updating setup tab from config')

        name = config['hosts']['default']['name']
        port = config['hosts']['default']['port']
        secret = config['hosts']['default']['secret']

        i = self.combo_host.findText(name)
        if i >= 0:
            self.combo_host.setCurrentIndex(i)
        else:
            self.combo_host.insertItem(0, name, (port, secret != None, secret))
            self.combo_host.setCurrentIndex(0)

        self.spin_port.setValue(port)

        self.check_authentication.setChecked(secret != None)
        self.edit_secret.setText(secret if secret != None else '')

        self.combo_data_time_format.setCurrentIndex(max(self.combo_data_time_format.findData(config['data']['time_format']), 0))
        self.edit_data_time_format_strftime.setText(config['data']['time_format_strftime'])
        self.check_data_to_csv_file.setChecked(config['data']['csv']['enabled'])
        self.edit_csv_file_name.setText(config['data']['csv']['file_name'])

        self.combo_debug_time_format.setCurrentIndex(max(self.combo_debug_time_format.findData(config['debug']['time_format']), 0))
        self.check_debug_to_log_file.setChecked(config['debug']['log']['enabled'])
        self.edit_log_file_name.setText(config['debug']['log']['file_name'])
        self.combo_log_level.setCurrentIndex(max(self.combo_debug_time_format.findData(config['debug']['log']['level']), 0))

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

        value_specs = device_specs[device['name']]['values']
        parent_item = QStandardItem('Values')

        name_item.appendRow([parent_item, QStandardItem('')])
        self.tree_devices.expand(parent_item.index())

        # add values
        for value_spec in value_specs:
            value_name_item = QStandardItem(value_spec['name'])
            value_interval_item = QStandardItem('')

            parent_item.appendRow([value_name_item, value_interval_item])

            spinbox_interval = IntervalWidget()
            spinbox_interval.set_interval(device['values'][value_spec['name']]['interval'])

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
        option_specs = device_specs[device['name']]['options']

        if option_specs != None:
            parent_item = QStandardItem('Options')

            name_item.appendRow([parent_item, QStandardItem('')])

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
                elif option_spec['type'] == 'bool':
                    widget_option_value = QCheckBox()
                    widget_option_value.setChecked(device['options'][option_spec['name']]['value'])

                self.tree_devices.setIndexWidget(option_widget_item.index(), widget_option_value)

    def add_debug_message(self, message):
        self.text_debug.append(message)

        while self.text_debug.document().blockCount() > 1000:
            cursor = QTextCursor(self.text_debug.document().begin())
            cursor.select(QTextCursor.BlockUnderCursor)
            cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor)
            cursor.removeSelectedText()

        if self.checkbox_debug_auto_scroll.isChecked():
            self.text_debug.verticalScrollBar().setValue(self.text_debug.verticalScrollBar().maximum())

    def btn_clear_debug_clicked(self):
        self.text_debug.clear()

    def highlight_debug_tab(self):
        """
            SIGNAL function:
            Highlight the debug tab when an error occurs.
        """
        if not self.tab_debug_warning and self.tab_widget.currentIndex() != self.tab_widget.indexOf(self.tab_debug):
            self.tab_debug_warning = True
            self.tab_set(self.tab_widget.indexOf(self.tab_debug), QColor(255, 0, 0),
                         get_resources_path("warning-icon-16.png"))

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

        self.model_data.appendRow([QStandardItem(csv_data.timestamp),
                                   QStandardItem(csv_data.name),
                                   QStandardItem(csv_data.uid),
                                   QStandardItem(csv_data.var_name),
                                   QStandardItem(str(csv_data.raw_data)),
                                   QStandardItem(csv_data.var_unit)])

        if row_number != None:
            self.model_data.setHeaderData(rows, Qt.Vertical, str(row_number + 1))

        if self.checkbox_data_auto_scroll.isChecked():
            self.table_data.scrollToBottom()
