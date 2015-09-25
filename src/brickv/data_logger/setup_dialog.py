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
import json
import os
import time
import functools
from datetime import datetime

from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import Qt  # , SIGNAL
from PyQt4.QtGui import QDialog, QMessageBox, QPalette

from brickv import config
from brickv.utils import get_save_file_name, get_open_file_name, get_main_window, get_home_path
from brickv.data_logger.event_logger import EventLogger, GUILogger
from brickv.data_logger.gui_config_handler import GuiConfigHandler
from brickv.data_logger.job import GuiDataJob
from brickv.data_logger.loggable_devices import Identifier
from brickv.data_logger import utils
from brickv.data_logger.device_dialog import DeviceDialog
from brickv.data_logger.configuration_validator import load_and_validate_config
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

        # Code Inspector
        self.host_infos = None
        self.last_host = None
        self.host_index_changing = None

        # if self._table_widget is not None:#FIXME rework this like the console_tab <-- what does that mean?!
        # self.jobs.append()

        self.setupUi(self)
        self.widget_initialization()

        timestamp = int(time.time())
        self.line_csv_data_file.setText(os.path.join(get_home_path(), 'logger_data_{0}.csv'.format(timestamp)))
        self.line_event_log_file.setText(os.path.join(get_home_path(), 'logger_events_{0}.log'.format(timestamp)))

        self.combo_time_format.addItem(utils.timestamp_to_de(timestamp) + ' (DD.MM.YYYY HH:MM:SS)', 'de')
        self.combo_time_format.addItem(utils.timestamp_to_us(timestamp) + ' (MM/DD/YYYY HH:MM:SS)', 'us')
        self.combo_time_format.addItem(utils.timestamp_to_iso(timestamp) + ' (ISO 8601)', 'iso')
        self.combo_time_format.addItem(utils.timestamp_to_unix(timestamp) + ' (Unix)', 'unix')

    def widget_initialization(self):
        """
            Sets default values for some widgets
        """
        # Login data
        self.host_info_initialization()
        # GUI LOG LEVEL
        self.combo_log_level_init(self.combo_console_level)
        self.combo_console_level.setCurrentIndex(1)  # INFO LEVEL
        # set loglevel
        self.combo_console_level_changed()

        # LOGLEVEL FROM CONFIG
        self.combo_log_level_init(self.combo_loglevel)
        self.combo_loglevel.setCurrentIndex(0)  # DEBUG LEVEL

        self.signal_initialization()

    def signal_initialization(self):
        """
            Init of all important Signals and connections.
        """
        # Buttons
        self.btn_start_logging.clicked.connect(self.btn_start_logging_clicked)
        self.btn_save_config.clicked.connect(self.btn_save_config_clicked)
        self.btn_load_config.clicked.connect(self.btn_load_config_clicked)
        self.btn_csv_data_file.clicked.connect(self.btn_csv_data_file_clicked)
        self.btn_event_log_file.clicked.connect(self.btn_event_log_file_clicked)
        self.btn_clear_events.clicked.connect(self.btn_clear_events_clicked)
        self.combo_console_level.currentIndexChanged.connect(self.combo_console_level_changed)
        self.btn_add_device.clicked.connect(self.btn_add_device_clicked)
        self.btn_remove_device.clicked.connect(self.btn_remove_device_clicked)
        self.btn_remove_all_devices.clicked.connect(self.btn_remove_all_devices_clicked)

        self.tab_widget.currentChanged.connect(self.tab_reset_warning)
        self.btn_clear_tabel.clicked.connect(self.btn_clear_table_clicked)

        self.connect(self._gui_logger, QtCore.SIGNAL(GUILogger.SIGNAL_NEW_MESSAGE), self.txt_console_output)
        self.connect(self._gui_logger, QtCore.SIGNAL(GUILogger.SIGNAL_NEW_MESSAGE_TAB_HIGHLIGHT),
                     self.txt_console_highlight_tab)

        # login information
        self.combo_host.currentIndexChanged.connect(self._host_index_changed)
        self.spinbox_port.valueChanged.connect(self._port_changed)

        self.tree_devices.itemDoubleClicked.connect(self.tree_on_double_click)
        self.tree_devices.itemChanged.connect(self.tree_on_change)
        self.tree_devices.itemChanged.connect(self.cb_device_interval_changed)

    def combo_log_level_init(self, combo_widget):
        combo_widget.clear()
        od = collections.OrderedDict(sorted(GUILogger._convert_level.items()))
        for k in od.keys():
            combo_widget.addItem(od[k])

            # TODO dynamic way to set GUI LogLevel - not used at the moment!
            # set index
            # ll = GUILogger._convert_level[EventLogger.EVENT_LOG_LEVEL]
            # combo_widget_count = combo_widget.count()
            # for i in range(0, combo_widget_count):
            # if ll == combo_widget.itemText(i):
            # combo_widget.setCurrentIndex(i)
            # break

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
        self.spinbox_port.setValue(self.host_infos[0].port)
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
            arguments_map[main.GUI_CONFIG] = GuiConfigHandler.create_config_file(self)
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
        """
            Opens a FileSelectionDialog and saves the current config.
        """
        filename = get_save_file_name(get_main_window(), 'Save Config File',
                                      get_home_path(), 'JSON Files (*.json)')

        if len(filename) == 0:
            return

        if not filename.lower().endswith('.json'):
            filename += '.json'

        config = GuiConfigHandler.create_config_file(self)

        try:
            with open(filename, 'w') as outfile:
                json.dump(config, outfile, sort_keys=True, indent=2)
        except Exception as e1:
            EventLogger.warning("Load Config - Exception: " + str(e1))
            QMessageBox.warning(self, 'Error',
                                'Could not save the Config-File! Look at the Log-File for further information.',
                                QMessageBox.Ok)
            return

        QMessageBox.information(self, 'Success', 'Config file saved!', QMessageBox.Ok)
        EventLogger.info("Config file saved to: " + str(filename))

    def btn_load_config_clicked(self):
        """
            Opens a FileSelectionDialog and loads the selected config.
        """
        filename = get_open_file_name(get_main_window(), 'Load Config File', get_home_path(), 'JSON Files (*.json)')

        if len(filename) == 0:
            return

        config = load_and_validate_config(filename)

        if config == None:
            return

        # devices
        config_blueprint = GuiConfigHandler.load_devices(config)

        if config_blueprint == None:
            return

        self.create_tree_items(config_blueprint)
        self.update_setup_tab(config)

    def btn_csv_data_file_clicked(self):
        """
            Opens a FileSelectionDialog and sets the selected path for the CSV data output file.
        """
        if len(self.line_csv_data_file.text()) > 0:
            last_dir = os.path.dirname(os.path.realpath(self.line_csv_data_file.text()))
        else:
            last_dir = get_home_path()

        filename = get_save_file_name(get_main_window(), 'Choose CSV File',
                                      last_dir, "CSV Files (*.csv)")

        if len(filename) > 0:
            if filename.lower().endswith('.csv'):
                filename += '.csv'

            self.line_csv_data_file.setText(filename)

    def btn_event_log_file_clicked(self):
        """
            Opens a FileSelectionDialog and sets the selected path for the event log output file.
        """
        if len(self.line_event_log_file.text()) > 0:
            last_dir = os.path.dirname(os.path.realpath(self.line_event_log_file.text()))
        else:
            last_dir = get_home_path()

        filename = get_save_file_name(get_main_window(), 'Choose Log File',
                                      last_dir, "Log Files (*.log)")

        if len(filename) > 0:
            if not filename.lower().endswith('.log'):
                filename += '.log'

            self.line_event_log_file.setText(filename)

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
        """
            Removes selected Device
        """
        selected_item = self.tree_devices.selectedItems()
        for index in range(0, len(selected_item)):
            try:
                if selected_item[index] is None:
                    continue

                device_name = selected_item[index].text(0)
                device_id = selected_item[index].text(1)

                if selected_item[index].text(0) not in Identifier.DEVICE_DEFINITIONS:
                    # have to find the parent
                    current_item = selected_item[0]

                    while True:
                        if current_item.parent() is None:
                            if current_item.text(0) not in Identifier.DEVICE_DEFINITIONS:
                                EventLogger.error("Cant remove device: " + selected_item[index].text(0))
                                device_name = ""
                                device_id = ""
                                break
                            else:
                                device_name = current_item.text(0)
                                device_id = current_item.text(1)
                                break
                        else:
                            current_item = current_item.parent()

                self.remove_item_from_tree(device_name, device_id)
            except Exception as e:
                if not str(e).startswith("wrapped C/C++ object"):
                    EventLogger.error("Cant remove device: " + str(e))  # was already removed


    def btn_remove_all_devices_clicked(self):
        self.tree_devices.clear()

    def btn_clear_table_clicked(self):
        """
            Clears the Data table.
        """
        self.table_widget.setRowCount(0)

    def tab_reset_warning(self):
        """
            Resets the Warning @ the console tab.
        """
        if not self.tab_console_warning or self.tab_widget.currentWidget().objectName() != self.tab_console.objectName():
            return

        self.tab_console_warning = False
        from PyQt4.QtGui import QColor

        self.tab_set(self.tab_widget.indexOf(self.tab_console), self.palette().color(QPalette.WindowText), None)

    def combo_console_level_changed(self):
        """
            Changes the log level dynamically.
        """
        ll = self.combo_console_level.currentText()

        od = collections.OrderedDict(sorted(self._gui_logger._convert_level.items()))
        for k in od.keys():
            if ll == od[k]:
                self._gui_logger.level = k
                break

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
        self.spinbox_port.setValue(self.host_infos[i].port)
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

        self.host_infos[i].port = self.spinbox_port.value()

    def update_setup_tab(self, config):
        """
            Update the information of the setup tab with the given general_section.
        """
        from brickv.data_logger.configuration_validator import ConfigurationReader

        try:
            i = self.combo_time_format.findData(config['general']['time_format'])

            if i >= 0:
                self.combo_time_format.setCurrentIndex(i)

            # host            combo_host              setEditText(str)
            self.combo_host.setEditText(config['hosts']['default']['name'])
            # port            spinbox_port            setValue(int)
            self.spinbox_port.setValue(config['hosts']['default']['port'])
            # file_count      spin_file_count         setValue(int)
            self.spin_file_count.setValue(config['general'][ConfigurationReader.GENERAL_LOG_COUNT])
            # file_size       spin_file_size          setValue(int/1024/1024)  (Byte -> MB)
            self.spin_file_size.setValue((config['general'][ConfigurationReader.GENERAL_LOG_FILE_SIZE] / 1024.0 / 1024.0))
            # path_to_file    line_csv_data_file      setText(str)
            self.line_csv_data_file.setText(config['general'][ConfigurationReader.GENERAL_PATH_TO_FILE])
            # eventlog_path   line_event_log_file      setText(str)
            self.line_event_log_file.setText(config['general'][ConfigurationReader.GENERAL_EVENTLOG_PATH])
            # loglevel
            ll = config['general'][ConfigurationReader.GENERAL_EVENTLOG_LEVEL]
            od = collections.OrderedDict(sorted(GUILogger._convert_level.items()))

            counter = 0  # TODO better way to set the combo box index?
            for k in od.keys():
                if ll == k:
                    break
                counter += 1
            self.combo_loglevel.setCurrentIndex(counter)

            # log_to_console
            def __checkbox_bool_setter(bool_value):
                if bool_value:
                    return 2
                else:
                    return 0

            self.checkbox_to_file.setChecked(
                __checkbox_bool_setter(config['general'][ConfigurationReader.GENERAL_EVENTLOG_TO_FILE]))
            # log_to_file
            self.checkbox_to_console.setCheckState(
                __checkbox_bool_setter(config['general'][ConfigurationReader.GENERAL_EVENTLOG_TO_CONSOLE]))

        except Exception as e:
            EventLogger.critical("Could not read the General Section of the Config-File! -> " + str(e))
            return

    def create_tree_items(self, blueprint):
        """
            Create the device tree with the given blueprint.
            Shows all possible devices, if the view_all Flag is True.
        """
        self.tree_devices.clear()
        self.tree_devices.setSortingEnabled(False)

        try:
            for dev in blueprint:
                self.__add_item_to_tree(dev)
            EventLogger.debug("Device Tree created.")

        except Exception as e:
            EventLogger.warning("DeviceTree - Exception while creating the Tree: " + str(e))

        self.tree_devices.sortItems(0, QtCore.Qt.AscendingOrder)
        self.tree_devices.setSortingEnabled(True)

    def add_item_to_tree(self, item_blueprint):
        self.tree_devices.setSortingEnabled(False)

        self.__add_item_to_tree(item_blueprint)

        self.tree_devices.sortItems(0, QtCore.Qt.AscendingOrder)
        self.tree_devices.setSortingEnabled(True)

    def cb_device_interval_changed(self, item, column):
        widget = self.tree_devices.itemWidget(item, 1)

        if widget != None:
            try:
                widget.setValue(int(item.text(1)))
            except:
                print "foobar"

    def __add_item_to_tree(self, item_blueprint):
        """
        Private function with NO sort = false
        :param item_blueprint:
        :return:
        """
        # counts topLevelItems
        lv0_counter = self.tree_devices.topLevelItemCount()

        # counts values in devices
        value_counter = 0

        # lvl0: new entry(name|UID)
        item_0 = QtGui.QTreeWidgetItem(self.tree_devices)
        item_0.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
        # set name|UID
        self.tree_devices.topLevelItem(lv0_counter).setText(0, str(item_blueprint[Identifier.DD_NAME]))
        self.tree_devices.topLevelItem(lv0_counter).setText(1, str(item_blueprint[Identifier.DD_UID]))
        self.tree_devices.topLevelItem(lv0_counter).setToolTip(1, self.__tree_uid_tooltip)

        def value_changed(item, value):
            item.setText(1, str(value))

        for item_value in item_blueprint[Identifier.DD_VALUES]:
            # lvl1: new entry(value_name|interval)
            item_1 = QtGui.QTreeWidgetItem(item_0)
            item_1.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            interval = item_blueprint[Identifier.DD_VALUES][item_value][Identifier.DD_VALUES_INTERVAL]
            child = self.tree_devices.topLevelItem(lv0_counter).child(value_counter)
            child.setText(0, str(item_value))
            child.setText(1, str(interval))
            child.setToolTip(1, self.__tree_interval_tooltip)

            spinbox_interval = QtGui.QSpinBox()
            spinbox_interval.setRange(0, (1 << 31) - 1)
            spinbox_interval.setSingleStep(1)
            spinbox_interval.setValue(interval)
            spinbox_interval.setSuffix(" seconds")
            spinbox_interval.valueChanged.connect(functools.partial(value_changed, child))

            self.tree_devices.setItemWidget(child, 1, spinbox_interval)

            # check sub_values
            sub_values = item_blueprint[Identifier.DD_VALUES][item_value][Identifier.DD_SUBVALUES]
            if sub_values is not None:
                # counts sub values in devices
                sub_value_counter = 0
                for item_sub_value in sub_values:
                    # lvl2: new entry (sub_value_name|True/False)
                    item_2 = QtGui.QTreeWidgetItem(item_1)
                    item_2.setFlags(
                        QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
                    lvl2_item = self.tree_devices.topLevelItem(lv0_counter).child(value_counter).child(sub_value_counter)
                    item_sub_value_value = \
                        item_blueprint[Identifier.DD_VALUES][item_value][Identifier.DD_SUBVALUES][item_sub_value]
                    lvl2_item.setText(0, str(item_sub_value))
                    if item_sub_value_value:
                        lvl2_item.setCheckState(1, QtCore.Qt.Checked)
                    else:
                        lvl2_item.setCheckState(1, QtCore.Qt.Unchecked)
                    lvl2_item.setText(1, "")

                    sub_value_counter += 1
            value_counter += 1

    def remove_item_from_tree(self, item_name, item_uid):
        """
            Removes an item from the device tree. The first match is removed!
        """
        # remove first found match!
        # removed_item = False
        t0_max = self.tree_devices.topLevelItemCount()

        for t0 in range(0, t0_max):

            dev_name = self.tree_devices.topLevelItem(t0).text(0)
            dev_uid = self.tree_devices.topLevelItem(t0).text(1)

            if dev_name == item_name and dev_uid == item_uid:
                # removed_item = True
                self.tree_devices.takeTopLevelItem(t0)
                break

                # can't use this approach because of multiple selection in tree_devices
                # if not removed_item:
                # QMessageBox.information(self, 'No Device found?', 'No Device was not found and could not be deleted!', QMessageBox.Ok)

    def tree_on_change(self, item, column):
        # check for wrong input number in interval or uid
        if column == 1:
            # check if tooltip is set
            tt = item.toolTip(1)
            if tt != "":
                # check if tooltip is interval
                if tt == self.__tree_interval_tooltip:
                    item.setText(1, str(utils.Utilities.parse_to_int(item.text(1))))
                # check if tooltip is uid
                elif tt == self.__tree_uid_tooltip:
                    text = item.text(1)
                    if not utils.Utilities.is_valid_string(text, 1):
                        text = Identifier.DD_UID_DEFAULT
                    item.setText(1, text)

    def tree_on_double_click(self, item, column):
        """
            Is called, when a cell in the tree was doubleclicked.
            Is used to allow the changing of the interval
            numbers and UID's but not empty cells.
        """
        edit_flag = (
            QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
        non_edit_flag = (QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)

        if column == 0:
            item.setFlags(non_edit_flag)

        elif item.text(column) != "" or item.text(column) is None:
            item.setFlags(edit_flag)

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
        # disable sort
        self.table_widget.setSortingEnabled(False)

        row = self.table_widget.rowCount()
        self.table_widget.insertRow(row)
        self.table_widget.setItem(row, 0, QtGui.QTableWidgetItem(str(csv_data.uid)))
        self.table_widget.setItem(row, 1, QtGui.QTableWidgetItem(str(csv_data.name)))
        self.table_widget.setItem(row, 2, QtGui.QTableWidgetItem(str(csv_data.var_name)))
        self.table_widget.setItem(row, 3, QtGui.QTableWidgetItem(str(csv_data.raw_data)))
        self.table_widget.setItem(row, 4, QtGui.QTableWidgetItem(str(csv_data.var_unit)))
        self.table_widget.setItem(row, 5, QtGui.QTableWidgetItem(str(csv_data.timestamp)))

        if self.checkbox_data_auto_scroll.isChecked():
            self.table_widget.scrollToBottom()

        # enable sort
        self.table_widget.setSortingEnabled(True)
