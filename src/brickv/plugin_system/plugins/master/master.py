# -*- coding: utf-8 -*-
"""
Master Plugin
Copyright (C) 2010-2012 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2014-2016 Matthias Bolte <matthias@tinkerforge.com>

master.py: Master Plugin implementation

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

import functools

from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import QAction, QTabBar, QLabel, QWidget, QVBoxLayout
from PyQt5.QtGui import QIcon

from brickv.plugin_system.plugin_base import PluginBase
from brickv.plugin_system.plugins.master.ui_master import Ui_Master
from brickv.plugin_system.plugins.master.extension_type import ExtensionType
from brickv.plugin_system.plugins.master.chibi import Chibi
from brickv.plugin_system.plugins.master.rs485 import RS485
from brickv.plugin_system.plugins.master.wifi import Wifi
from brickv.plugin_system.plugins.master.ethernet import Ethernet
from brickv.plugin_system.plugins.master.wifi2 import Wifi2
from brickv.bindings.brick_master import BrickMaster
from brickv.async_call import async_call
from brickv.infos import ExtensionInfo, inventory
from brickv.utils import get_main_window, format_current
from brickv.tab_window import IconButton
from brickv.load_pixmap import load_pixmap

class Master(PluginBase, Ui_Master):
    def __init__(self, *args):
        PluginBase.__init__(self, BrickMaster, *args)

        self.setupUi(self)

        self.master = self.device

        # the firmware version of a Brick can (under common circumstances) not
        # change during the lifetime of a Brick plugin. therefore, it's okay to
        # make final decisions based on it here
        self.has_status_led = self.firmware_version >= (2, 3, 2)

        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_data)

        self.extension_type = None

        self.extension_tabs = []

        self.wifi2_firmware_version = None

        self.update_tab_button = IconButton(QIcon(load_pixmap('update-icon-normal.png')), QIcon(load_pixmap('update-icon-hover.png')), parent=get_main_window().tab_widget)
        self.update_tab_button.setToolTip('Update available')
        self.update_tab_button.clicked.connect(lambda: get_main_window().show_brick_update(self.device_info.url_part))
        self.update_tab_button.hide()

        self.wifi2_update_button = IconButton(QIcon(load_pixmap('update-icon-normal.png')),
                                              QIcon(load_pixmap('update-icon-hover.png')),
                                              self.tab_widget)
        self.wifi2_update_button.setToolTip('Update available')
        self.wifi2_update_button.clicked.connect(lambda: get_main_window().show_extension_update(self.device_info.uid))
        self.wifi2_update_button.hide()

        self.wifi2_tab_idx = None
        self.wifi2_start_done = False

        self.extension_label.setText("None Present")
        self.tab_widget.removeTab(0)
        self.tab_widget.hide()

        self.start_extensions = True
        self.extension_type_button.clicked.connect(self.extension_clicked)

        if self.has_status_led:
            self.status_led_action = QAction('Status LED', self)
            self.status_led_action.setCheckable(True)
            self.status_led_action.toggled.connect(lambda checked: self.master.enable_status_led() if checked else self.master.disable_status_led())
            self.set_configs([(0, None, [self.status_led_action])])
        else:
            self.status_led_action = None

        reset = QAction('Reset', self)
        reset.triggered.connect(self.master.reset)
        self.set_actions([(0, None, [reset])])

        self.extension_type_present = [None,  # None
                                       False, # Chibi
                                       False, # RS485
                                       False, # WIFI
                                       False, # Ethernet
                                       False] # WIFI 2.0

        self.query_extensions()

    def show_wifi_update(self):
        tab_idx = get_main_window().tab_widget.indexOf(self.device_info.tab_window)
        self.update_tab_button.setToolTip('WIFI Extension 2.0 Update available')
        self.update_tab_button.clicked.connect(lambda: get_main_window().show_extension_update(self.device_info.uid))
        self.update_tab_button.show()

        # The tab bar sometimes does not show the tab button if it is set without first removing the old button
        get_main_window().tab_widget.tabBar().setTabButton(tab_idx, QTabBar.RightSide, None)
        get_main_window().tab_widget.tabBar().setTabButton(tab_idx, QTabBar.RightSide, self.update_tab_button)

        if self.wifi2_tab_idx is not None:
            self.tab_widget.tabBar().setTabButton(self.wifi2_tab_idx, QTabBar.LeftSide, self.wifi2_update_button)
            self.wifi2_update_button.show()

            for ext in self.extension_tabs:
                if isinstance(ext, Wifi2):
                    ext.wifi_update_firmware_button.show()

    def hide_wifi_update(self):
        tab_idx = get_main_window().tab_widget.indexOf(self.device_info.tab_window)
        get_main_window().tab_widget.tabBar().setTabButton(tab_idx, QTabBar.RightSide, None)
        self.update_tab_button.hide()

        if self.wifi2_tab_idx is not None:
            self.tab_widget.tabBar().setTabButton(self.wifi2_tab_idx, QTabBar.LeftSide, None)

        if self.wifi2_update_button is not None:
            self.wifi2_update_button.hide()

            for ext in self.extension_tabs:
                if isinstance(ext, Wifi2):
                    ext.wifi_update_firmware_button.hide()

    def hide_master_update(self):
        tab_idx = get_main_window().tab_widget.indexOf(self.device_info.tab_window)
        get_main_window().tab_widget.tabBar().setTabButton(tab_idx, QTabBar.RightSide, None)
        self.update_tab_button.hide()

        if self.device_info.tab_window is not None:
            self.device_info.tab_window.button_update.hide()

    def show_master_update(self):
        tab_idx = get_main_window().tab_widget.indexOf(self.device_info.tab_window)
        self.update_tab_button.setToolTip('Update available')
        self.update_tab_button.clicked.connect(lambda: get_main_window().show_brick_update(self.device_info.url_part))
        self.update_tab_button.show()

         # The tab bar sometimes does not show the tab button if it is set without first removing the old button
        get_main_window().tab_widget.tabBar().setTabButton(tab_idx, QTabBar.RightSide, None)
        get_main_window().tab_widget.tabBar().setTabButton(tab_idx, QTabBar.RightSide, self.update_tab_button)

        if self.device_info.tab_window is not None:
            self.device_info.tab_window.button_update.show()

    # overrides PluginBase.device_info_changed
    def device_info_changed(self, uid):
        if uid != self.device_info.uid:
            return

        if self.extension_type_present[self.master.EXTENSION_TYPE_WIFI2]:
            wifi_info = self.device_info.get_extension_info(self.master.EXTENSION_TYPE_WIFI2)

            if wifi_info is None:
                wifi_update_avail = False
            else:
                wifi_update_avail = wifi_info.firmware_version_installed != (0, 0, 0) and wifi_info.firmware_version_installed < wifi_info.firmware_version_latest
        else:
            wifi_update_avail = False

        brick_update_avail = self.device_info.firmware_version_installed < self.device_info.firmware_version_latest

        # As the master and wifi update share buttons, first hide all updates,
        # then show all updates. Control flow such as
        #   if master_update: show else: hide
        #   if wifi_update: show else: hide
        # would hide some of the controls for the master update if there is no wifi update.
        if not brick_update_avail:
            self.hide_master_update()

        if not wifi_update_avail:
            self.hide_wifi_update()

        if brick_update_avail:
            self.show_master_update()

        # Intentionally override possible Master Brick update notification: The Extension update is easier for users
        # so they are more likely to update at least the Extension. Also when the Extension is updated, device_info_changed
        # will be called again, then notifying the user of the Master Brick update.
        if wifi_update_avail:
            self.show_wifi_update()

    def query_extensions(self):
        def is_present_async(extension_type, name, present):
            self.extension_type_present[extension_type] = present

            if not present:
                return

            if self.device_info.extensions['ext0'] == None:
                ext = 'ext0'
            elif self.device_info.extensions['ext1'] == None:
                ext = 'ext1'
            else:
                return # This should never be the case

            self.device_info.extensions[ext] = ExtensionInfo()
            self.device_info.extensions[ext].name = name
            self.device_info.extensions[ext].extension_type = extension_type
            self.device_info.extensions[ext].position = ext
            self.device_info.extensions[ext].master_info = self.device_info

            if extension_type == self.master.EXTENSION_TYPE_WIFI2:
                self.device_info.extensions[ext].url_part = 'wifi_v2'

                self.device_info.extensions[ext].update_firmware_version_latest()

                label = QLabel('Waiting for WIFI Extension 2.0 firmware version...')
                label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

                wrapper = QWidget()

                layout = QVBoxLayout(wrapper)
                layout.addWidget(label)
                layout.setContentsMargins(0, 0, 0, 0)

                self.wifi2_tab_idx = self.tab_widget.addTab(wrapper, 'WIFI 2.0')

                # When WIFI2 extension firmware version is being requested the
                # extension might still not be done with booting and thus the
                # message won't be received by the extension. So we delay sending
                # the request which gives enough time to the extension to finish
                # booting. Note that this delay is only induced when there is a
                # WIFI2 extension present.
                async_call(self.master.get_wifi2_firmware_version, None, functools.partial(self.get_wifi2_firmware_version_async, ext), self.increase_error_count, delay=2.0)

            inventory.sync()

        def get_connection_type_async(connection_type):
            self.device_info.connection_type = connection_type
            inventory.sync()

        async_call(self.master.is_chibi_present, None, functools.partial(is_present_async, self.master.EXTENSION_TYPE_CHIBI, 'Chibi Extension'), self.increase_error_count)
        async_call(self.master.is_rs485_present, None, functools.partial(is_present_async, self.master.EXTENSION_TYPE_RS485, 'RS485 Extension'), self.increase_error_count)
        async_call(self.master.is_wifi_present, None, functools.partial(is_present_async, self.master.EXTENSION_TYPE_WIFI, 'WIFI Extension'), self.increase_error_count)

        if self.firmware_version >= (2, 1, 0):
            async_call(self.master.is_ethernet_present, None, functools.partial(is_present_async, self.master.EXTENSION_TYPE_ETHERNET, 'Ethernet Extension'), self.increase_error_count)

        if self.firmware_version >= (2, 4, 0):
            async_call(self.master.is_wifi2_present, None, functools.partial(is_present_async, self.master.EXTENSION_TYPE_WIFI2, 'WIFI Extension 2.0'), self.increase_error_count)
            async_call(self.master.get_connection_type, None, get_connection_type_async, self.increase_error_count)

        async_call(lambda: None, None, get_main_window().update_tree_view, None)

    def get_wifi2_firmware_version_async(self, ext, version):
        self.wifi2_firmware_version = version

        self.device_info.extensions[ext].firmware_version_installed = version

        # Start the plugin before sending the device_info_changed signal, so that
        # the slot registered to the signal will already see the plugin in self.extension_tabs.
        self.wifi2_start()

        inventory.sync()

    def wifi2_start(self):
        if self.wifi2_start_done or self.wifi2_firmware_version == None:
            return

        self.wifi2_start_done = True

        wifi2 = Wifi2(self.wifi2_firmware_version, self)
        wifi2.start()

        self.extension_tabs.append(wifi2)

        wrapper = self.tab_widget.widget(self.wifi2_tab_idx)
        wrapper.layout().replaceWidget(wrapper.layout().itemAt(0).widget(), wifi2)

    def add_non_wifi2_tab(self, widget, title):
        if self.wifi2_tab_idx != None:
            self.tab_widget.insertTab(self.wifi2_tab_idx, widget, title)
            self.wifi2_tab_idx += 1
        else:
            self.tab_widget.addTab(widget, title)

        self.tab_widget.setCurrentIndex(0)

    def ethernet_start(self):
        ethernet = Ethernet(self)
        ethernet.start()

        self.extension_tabs.append(ethernet)
        self.add_non_wifi2_tab(ethernet, 'Ethernet')

    def wifi_start(self):
        wifi = Wifi(self)
        wifi.start()

        self.extension_tabs.append(wifi)
        self.add_non_wifi2_tab(wifi, 'WIFI')

    def rs485_start(self):
        rs485 = RS485(self)
        rs485.start()

        self.extension_tabs.append(rs485)
        self.add_non_wifi2_tab(rs485, 'RS485')

    def chibi_start(self):
        chibi = Chibi(self)
        chibi.start()

        self.extension_tabs.append(chibi)
        self.add_non_wifi2_tab(chibi, 'Chibi')

    def start(self):
        if self.has_status_led:
            async_call(self.master.is_status_led_enabled, None, self.status_led_action.setChecked, self.increase_error_count)

        if self.start_extensions:
            self.start_extensions = False

            if self.extension_type_present[self.master.EXTENSION_TYPE_CHIBI]:
                self.chibi_start()

            if self.extension_type_present[self.master.EXTENSION_TYPE_RS485]:
                self.rs485_start()

            if self.extension_type_present[self.master.EXTENSION_TYPE_WIFI]:
                self.wifi_start()

            if self.extension_type_present[self.master.EXTENSION_TYPE_ETHERNET]:
                self.ethernet_start()

            if self.extension_type_present[self.master.EXTENSION_TYPE_WIFI2]:
                self.wifi2_start()

            if self.tab_widget.count() > 0:
                self.tab_widget.show()
                self.extension_label.setText(str(self.tab_widget.count()) + " Present")
                self.label_no_extension.hide()

        self.update_timer.start(1000)

    def show_extension(self, ext_idx):
        self.tab_widget.setCurrentIndex(ext_idx)

    def stop(self):
        self.update_timer.stop()

    def destroy(self):
        for ext in self.extension_tabs:
            ext.destroy()
            ext.hide()
            ext.setParent(None)

        self.extension_tabs = []

        if self.extension_type:
            self.extension_type.close()

    def is_hardware_version_relevant(self):
        return True

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickMaster.DEVICE_IDENTIFIER

    def update_data(self):
        async_call(self.master.get_stack_voltage, None, self.get_stack_voltage_async, self.increase_error_count)
        async_call(self.master.get_stack_current, None, self.get_stack_current_async, self.increase_error_count)

        for ext in self.extension_tabs:
            ext.update_data()

    def get_stack_voltage_async(self, voltage):
        self.stack_voltage_label.setText('{:g} V'.format(round(voltage / 1000.0, 1)))

    def get_stack_current_async(self, current):
        self.stack_current_label.setText(format_current(current / 1000.0))

    def extension_clicked(self):
        if self.extension_type is None:
            self.extension_type = ExtensionType(self)

        self.extension_type.show()
