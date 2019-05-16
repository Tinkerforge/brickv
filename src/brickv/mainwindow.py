# -*- coding: utf-8 -*-
"""
brickv (Brick Viewer)
Copyright (C) 2009-2012, 2018 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2012-2015 Matthias Bolte <matthias@tinkerforge.com>

mainwindow.py: New/Removed Bricks are handled here and plugins shown if clicked

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

import signal
import sys
import time
import gc
import functools

from PyQt5.QtCore import pyqtSignal, Qt, QTimer, QEvent, QThread
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QCursor, QIcon, QBrush, QColor
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, \
                            QPushButton, QHBoxLayout, QVBoxLayout, \
                            QLabel, QFrame, QSpacerItem, QSizePolicy, \
                            QToolButton, QLineEdit, QMenu, QTabBar, \
                            QCheckBox, QComboBox

from brickv.ui_mainwindow import Ui_MainWindow
from brickv.plugin_system.plugin_manager import PluginManager
from brickv.bindings.ip_connection import IPConnection
from brickv.flashing import FlashingWindow
from brickv.advanced import AdvancedWindow
from brickv.data_logger.setup_dialog import SetupDialog as DataLoggerWindow
from brickv.async_call import async_start_thread, async_next_session, async_call, async_stop_thread
from brickv.bindings.brick_master import BrickMaster
from brickv.bindings.brick_red import BrickRED
try:
    from brickv.bindings.brick_hat import BrickHAT
    hat_brick_supported = True
except ImportError:
    hat_brick_supported = False
try:
    from brickv.bindings.brick_hat_zero import BrickHATZero
    hat_zero_brick_supported = True
except ImportError:
    hat_zero_brick_supported = False
from brickv.bindings.bricklet_isolator import BrickletIsolator
from brickv.plugin_system.plugins.red import RED
from brickv import config
from brickv import infos
from brickv.tab_window import TabWindow, IconButton
from brickv.plugin_system.comcu_bootloader import COMCUBootloader
from brickv.load_pixmap import load_pixmap
from brickv.firmware_fetch import LatestFWVersionFetcher
from brickv.devicesproxymodel import DevicesProxyModel

class MainWindow(QMainWindow, Ui_MainWindow):
    qtcb_enumerate = pyqtSignal(str, str, str, type((0,)), type((0,)), int, int)
    qtcb_connected = pyqtSignal(int)
    qtcb_disconnected = pyqtSignal(int)

    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)

        self.setupUi(self)

        # Setting the minimum width of the setup tab ensures, that other tabs can grow
        # the window if more space is required, but we have a sane default for status
        # messages. Setting the minimum width of the main window itself would enfoce
        # it, even if children (i.e. tabs) need more space.
        self.tab_setup.setMinimumWidth(550)

        signal.signal(signal.SIGINT, self.exit_brickv)
        signal.signal(signal.SIGTERM, self.exit_brickv)

        self.async_thread = async_start_thread(self)

        title = 'Brick Viewer ' + config.BRICKV_VERSION

        if config.INTERNAL != None:
            title += '~{}'.format(config.INTERNAL)

        self.setWindowTitle(title)

        self.tree_view_model_labels = ['Name', 'UID', 'Position', 'FW Version']
        self.tree_view_model = QStandardItemModel(self)
        self.tree_view_proxy_model = DevicesProxyModel(self)
        self.tree_view_proxy_model.setSourceModel(self.tree_view_model)
        self.tree_view.setModel(self.tree_view_proxy_model)
        self.tree_view.activated.connect(self.item_activated)
        self.set_tree_view_defaults()

        self.tab_widget.removeTab(1) # remove dummy tab
        self.tab_widget.setUsesScrollButtons(True) # force scroll buttons

        self.update_tab_button = IconButton(QIcon(load_pixmap('update-icon-normal.png')),
                                            QIcon(load_pixmap('update-icon-hover.png')),
                                            parent=self.tab_setup)
        self.update_tab_button.setToolTip('Updates available')
        self.update_tab_button.clicked.connect(self.flashing_clicked)
        self.update_tab_button.hide()

        self.name = '<unknown>'
        self.uid = '<unknown>'
        self.version = (0, 0, 0)

        self.disconnect_times = []

        self.qtcb_enumerate.connect(self.cb_enumerate)
        self.qtcb_connected.connect(self.cb_connected)
        self.qtcb_disconnected.connect(self.cb_disconnected)

        self.ipcon = IPConnection()
        self.ipcon.register_callback(IPConnection.CALLBACK_ENUMERATE,
                                     self.qtcb_enumerate.emit)
        self.ipcon.register_callback(IPConnection.CALLBACK_CONNECTED,
                                     self.qtcb_connected.emit)
        self.ipcon.register_callback(IPConnection.CALLBACK_DISCONNECTED,
                                     self.qtcb_disconnected.emit)

        self.current_device_info = None
        self.flashing_window = None
        self.advanced_window = None
        self.data_logger_window = None
        self.delayed_refresh_updates_timer = QTimer(self)
        self.delayed_refresh_updates_timer.timeout.connect(self.delayed_refresh_updates)
        self.delayed_refresh_updates_timer.setInterval(100)
        self.reset_view()
        self.button_advanced.setDisabled(True)

        self.fw_version_fetcher = LatestFWVersionFetcher()
        self.fw_version_fetcher.fw_versions_avail.connect(self.fw_versions_fetched)
        self.fw_version_fetcher_thread = QThread()
        self.fw_version_fetcher_thread.setObjectName("fw_version_fetcher_thread")

        if config.get_auto_search_for_updates():
            self.enable_auto_search_for_updates()
        else:
            self.disable_auto_search_for_updates()

        self.tab_widget.currentChanged.connect(self.tab_changed)
        self.tab_widget.setMovable(True)
        self.tab_widget.tabBar().installEventFilter(self)

        self.button_connect.clicked.connect(self.connect_clicked)
        self.button_flashing.clicked.connect(self.flashing_clicked)
        self.button_advanced.clicked.connect(self.advanced_clicked)
        self.button_data_logger.clicked.connect(self.data_logger_clicked)
        self.plugin_manager = PluginManager()

        # host info
        self.host_infos = config.get_host_infos(config.HOST_INFO_COUNT)
        self.host_index_changing = True

        for host_info in self.host_infos:
            self.combo_host.addItem(host_info.host)

        self.last_host = None
        self.combo_host.installEventFilter(self)
        self.combo_host.currentIndexChanged.connect(self.host_index_changed)

        self.spinbox_port.setValue(self.host_infos[0].port)
        self.spinbox_port.valueChanged.connect(self.port_changed)
        self.spinbox_port.installEventFilter(self)

        self.checkbox_authentication.stateChanged.connect(self.authentication_state_changed)

        self.label_secret.hide()
        self.edit_secret.hide()
        self.edit_secret.setEchoMode(QLineEdit.Password)
        self.edit_secret.textEdited.connect(self.secret_changed)
        self.edit_secret.installEventFilter(self)

        self.checkbox_secret_show.hide()
        self.checkbox_secret_show.stateChanged.connect(self.secret_show_state_changed)

        self.checkbox_remember_secret.hide()
        self.checkbox_remember_secret.stateChanged.connect(self.remember_secret_state_changed)

        self.checkbox_authentication.setChecked(self.host_infos[0].use_authentication)
        self.edit_secret.setText(self.host_infos[0].secret)
        self.checkbox_remember_secret.setChecked(self.host_infos[0].remember_secret)

        self.host_index_changing = False

        # auto-reconnect
        self.label_auto_reconnects.hide()
        self.auto_reconnects = 0

        # RED Session losts
        self.label_red_session_losts.hide()
        self.red_session_losts = 0

        # fusion style
        self.check_fusion_gui_style.setChecked(config.get_use_fusion_gui_style())
        self.check_fusion_gui_style.stateChanged.connect(self.gui_style_changed)

        self.checkbox_auto_search_for_updates.setChecked(config.get_auto_search_for_updates())
        self.checkbox_auto_search_for_updates.stateChanged.connect(self.auto_search_for_updates_changed)

        self.button_update_pixmap_normal = load_pixmap('update-icon-normal.png')
        self.button_update_pixmap_hover = load_pixmap('update-icon-hover.png')

        self.last_status_message_id = ''

        infos.get_infos_changed_signal().connect(self.update_red_brick_version)

    def update_red_brick_version(self, uid):
        if not isinstance(infos.get_info(uid), infos.BrickREDInfo):
            return
        self.update_tree_view()

    def disable_auto_search_for_updates(self):
        self.fw_version_fetcher.abort()

    def enable_auto_search_for_updates(self):
        self.fw_version_fetcher.reset()
        self.fw_version_fetcher.moveToThread(self.fw_version_fetcher_thread)
        self.fw_version_fetcher_thread.started.connect(self.fw_version_fetcher.run)
        self.fw_version_fetcher.finished.connect(self.fw_version_fetcher_thread.quit)
        self.fw_version_fetcher_thread.start()

    # override QMainWindow.closeEvent
    def closeEvent(self, event):
        if not self.exit_logger():
            event.ignore()
            return

        self.exit_brickv()
        event.accept()
        async_stop_thread()

        # Without this, the quit event seems to not reach the main loop under OSX.
        QApplication.quit()

    def exit_brickv(self, signl=None, frme=None):
        self.update_current_host_info()
        config.set_host_infos(self.host_infos)

        self.do_disconnect()

        if signl != None and frme != None:
            print("Received SIGINT or SIGTERM, shutting down.")
            sys.exit()

    def exit_logger(self):
        exitBrickv = True
        if (self.data_logger_window is not None) and \
           (self.data_logger_window.data_logger_thread is not None) and \
           (not self.data_logger_window.data_logger_thread.stopped):
            quit_msg = "The Data Logger is running. Are you sure you want to exit the program?"
            reply = QMessageBox.question(self, 'Message', quit_msg, QMessageBox.Yes, QMessageBox.No)

            if reply == QMessageBox.Yes:
                self.data_logger_window.data_logger_thread.stop()
            else:
                exitBrickv = False

        return exitBrickv

    def host_index_changed(self, i):
        if i < 0:
            return

        self.host_index_changing = True

        self.spinbox_port.setValue(self.host_infos[i].port)
        self.checkbox_authentication.setChecked(self.host_infos[i].use_authentication)
        self.edit_secret.setText(self.host_infos[i].secret)
        self.checkbox_remember_secret.setChecked(self.host_infos[i].remember_secret)

        self.host_index_changing = False

    def port_changed(self, _value):
        self.update_current_host_info()

    def authentication_state_changed(self, state):
        visible = state == Qt.Checked

        self.label_secret.setVisible(visible)
        self.edit_secret.setVisible(visible)
        self.checkbox_secret_show.setVisible(visible)
        self.checkbox_remember_secret.setVisible(visible)

        self.update_current_host_info()

    def secret_changed(self):
        self.update_current_host_info()

    def secret_show_state_changed(self, state):
        if state == Qt.Checked:
            self.edit_secret.setEchoMode(QLineEdit.Normal)
        else:
            self.edit_secret.setEchoMode(QLineEdit.Password)

        self.update_current_host_info()

    def remember_secret_state_changed(self, _state):
        self.update_current_host_info()

    def tab_changed(self, i):
        if not hasattr(self.tab_widget.widget(i), '_info'):
            new_current_device_info = None
        else:
            new_current_device_info = self.tab_widget.widget(i)._info
            new_current_device_info.plugin.start_plugin()

        # stop the now deselected plugin, if there is one that's running
        if self.current_device_info is not None:
            self.current_device_info.plugin.stop_plugin()

        self.current_device_info = new_current_device_info

    def update_current_host_info(self):
        if self.host_index_changing:
            return

        i = self.combo_host.currentIndex()

        if i < 0:
            return

        self.host_infos[i].port = self.spinbox_port.value()
        self.host_infos[i].use_authentication = self.checkbox_authentication.isChecked()
        self.host_infos[i].secret = self.edit_secret.text()
        self.host_infos[i].remember_secret = self.checkbox_remember_secret.isChecked()

    def gui_style_changed(self):
        config.set_use_fusion_gui_style(self.check_fusion_gui_style.isChecked())

        QMessageBox.information(self, 'GUI Style', 'GUI style change will be applied on next Brick Viewer start.', QMessageBox.Ok)

    def auto_search_for_updates_changed(self):
        config.set_auto_search_for_updates(self.checkbox_auto_search_for_updates.isChecked())
        if self.checkbox_auto_search_for_updates.isChecked():
            self.enable_auto_search_for_updates()
        else:
            self.disable_auto_search_for_updates()

    def remove_all_device_infos(self):
        for device_info in infos.get_device_infos():
            self.remove_device_info(device_info.uid)

    def remove_device_info(self, uid):
        tab_id = self.tab_for_uid(uid)
        device_info = infos.get_info(uid)

        device_info.plugin.stop_plugin()
        device_info.plugin.destroy_plugin()

        if tab_id >= 0:
            self.tab_widget.removeTab(tab_id)

        # ensure that the widget gets correctly destroyed. otherwise QWidgets
        # tend to leak as Python is not able to collect their PyQt object
        tab_window = device_info.tab_window
        device_info.tab_window = None

        # If we reboot the RED Brick, the tab_window sometimes is
        # already None here
        if tab_window != None:
            tab_window.hide()
            tab_window.setParent(None)

        plugin = device_info.plugin
        device_info.plugin = None

        if plugin != None:
            plugin.hide()
            plugin.setParent(None)

        infos.remove_info(uid)

    def reset_view(self):
        self.tab_widget.setCurrentIndex(0)
        self.remove_all_device_infos()
        self.update_tree_view()

    def do_disconnect(self):
        self.auto_reconnects = 0
        self.label_auto_reconnects.hide()

        self.red_session_losts = 0
        self.label_red_session_losts.hide()

        self.reset_view()
        async_next_session()

        # force garbage collection, to ensure that all plugin related objects
        # got destroyed before disconnect is called. this is especially
        # important for the RED Brick plugin because its relies on releasing
        # the the RED Brick API objects in the __del__ method as a last resort
        # to avoid leaking object references. but this only works if garbage
        # collection is done before disconnect is called
        gc.collect()

        try:
            self.ipcon.disconnect()
        except:
            pass

    def do_authenticate(self, is_auto_reconnect):
        if not self.checkbox_authentication.isChecked():
            return True

        try:
            secret = self.edit_secret.text()
            # Try to encode the secret, as only ASCII chars are allowed. Don't save the result, as the IP Connection does the same.
            secret.encode('ascii')
        except:
            self.do_disconnect()

            QMessageBox.critical(self, 'Connection',
                                 'Authentication secret cannot contain non-ASCII characters.',
                                 QMessageBox.Ok)
            return False

        self.ipcon.set_auto_reconnect(False) # don't auto-reconnect on authentication error

        try:
            self.ipcon.authenticate(secret)
        except:
            self.do_disconnect()

            if is_auto_reconnect:
                extra = ' after auto-reconnect'
            else:
                extra = ''

            QMessageBox.critical(self, 'Connection',
                                 'Could not authenticate' + extra + '. Check secret and ensure ' +
                                 'authentication for Brick Daemon is enabled.',
                                 QMessageBox.Ok)
            return False

        self.ipcon.set_auto_reconnect(True)

        return True

    def flashing_clicked(self):
        if self.flashing_window is None:
            self.flashing_window = FlashingWindow(self)

        self.flashing_window.show()
        self.flashing_window.tab_widget.setCurrentWidget(self.flashing_window.tab_updates)
        self.flashing_window.update_version_info()

    def advanced_clicked(self):
        if self.advanced_window is None:
            self.advanced_window = AdvancedWindow(self)

        self.advanced_window.show()

    def data_logger_clicked(self):
        if self.data_logger_window is None:
            self.data_logger_window = DataLoggerWindow(self, self.host_infos)

        self.data_logger_window.show()

    def connect_error(self):
        self.setDisabled(False)
        self.button_connect.setText("Connect")
        QMessageBox.critical(self, 'Connection',
                             'Could not connect. Please check host, check ' +
                             'port and ensure that Brick Daemon is running.')

    def connect_clicked(self):
        if self.ipcon.get_connection_state() == IPConnection.CONNECTION_STATE_DISCONNECTED:
            self.last_host = self.combo_host.currentText()
            self.setDisabled(True)
            self.button_connect.setText("Connecting...")

            async_call(self.ipcon.connect, (self.last_host, self.spinbox_port.value()), None, self.connect_error)
        else:
            self.do_disconnect()

    def item_activated(self, index):
        index = self.tree_view_proxy_model.mapToSource(index)
        position_index = index.sibling(index.row(), 2)

        extension_clicked = position_index.isValid() and position_index.data().startswith('Ext')
        if extension_clicked:
            extension_index = int(position_index.data().replace('Ext', ''))
            index = index.parent()

        uid_index = index.sibling(index.row(), 1)

        if uid_index.isValid():
            plugin = self.show_plugin(uid_index.data())
            if extension_clicked:
                plugin.show_extension(extension_index)

    def show_brick_update(self, url_part):
        if self.flashing_window is None:
            self.flashing_window = FlashingWindow(self)

        self.flashing_window.show()
        self.flashing_window.update_version_info()
        self.flashing_window.show_brick_update(url_part)

    def show_bricklet_update(self, parent_uid, port):
        if self.flashing_window is None:
            self.flashing_window = FlashingWindow(self)

        self.flashing_window.show()
        self.flashing_window.update_version_info()
        self.flashing_window.show_bricklet_update(parent_uid, port)

    def show_extension_update(self, master_uid):
        if self.flashing_window is None:
            self.flashing_window = FlashingWindow(self)

        self.flashing_window.show()
        self.flashing_window.update_version_info()
        self.flashing_window.show_extension_update(master_uid)

    def show_red_brick_update(self):
        text = "To update the RED Brick Image, please follow the instructions " + \
               "<a href=https://www.tinkerforge.com/en/doc/Hardware/Bricks/RED_Brick.html#red-brick-copy-image>here</a>."
        QMessageBox.information(self, "RED Brick Update", text)

    def create_tab_window(self, device_info, ipcon):
        tab_window = TabWindow(self.tab_widget, device_info.name, self.untab)
        tab_window._info = device_info
        tab_window.add_callback_on_tab(lambda index:
                                       self.ipcon.get_connection_state() == IPConnection.CONNECTION_STATE_PENDING and \
                                       self.tab_widget.setTabEnabled(index, False),
                                       'main_window_disable_tab_if_connection_pending')

        layout = QVBoxLayout(tab_window)
        info_bars = [QHBoxLayout(), QHBoxLayout()]

        # uid
        info_bars[0].addWidget(QLabel('UID:'))

        label = QLabel('{0}'.format(device_info.uid))
        label.setTextInteractionFlags(Qt.TextSelectableByMouse |
                                      Qt.TextSelectableByKeyboard)

        info_bars[0].addWidget(label)
        info_bars[0].addSpacerItem(QSpacerItem(20, 1, QSizePolicy.Preferred))

        # firmware version
        label_version_name = QLabel('Version:')
        label_version = QLabel('Querying...')

        button_update = QPushButton(QIcon(self.button_update_pixmap_normal), 'Update')
        button_update.installEventFilter(self)

        if isinstance(device_info, infos.BrickREDInfo):
            button_update.clicked.connect(self.show_red_brick_update)
        elif device_info.type == 'brick':
            button_update.clicked.connect(lambda: self.show_brick_update(device_info.url_part))
        elif device_info.type == 'bricklet':
            button_update.clicked.connect(lambda: self.show_bricklet_update(device_info.connected_uid, device_info.position))

        if not device_info.plugin.has_custom_version(label_version_name, label_version):
            label_version_name.setText('FW Version:')
            label_version.setText(infos.get_version_string(device_info.plugin.firmware_version))

        info_bars[0].addWidget(label_version_name)
        info_bars[0].addWidget(label_version)
        info_bars[0].addWidget(button_update)
        button_update.hide()
        tab_window.button_update = button_update
        info_bars[0].addSpacerItem(QSpacerItem(20, 1, QSizePolicy.Preferred))

        # timeouts
        info_bars[0].addWidget(QLabel('Timeouts:'))

        label_timeouts = QLabel('0')

        info_bars[0].addWidget(label_timeouts)
        info_bars[0].addSpacerItem(QSpacerItem(1, 1, QSizePolicy.Expanding))

        # connected uid
        if device_info.connected_uid != '0':
            info_bars[1].addWidget(QLabel('Connected to:'))

            button = QToolButton()
            button.setText(device_info.connected_uid)
            button.clicked.connect(lambda: self.show_plugin(device_info.connected_uid))
            device_info.plugin.button_parent = button

            info_bars[1].addWidget(button)
            info_bars[1].addSpacerItem(QSpacerItem(20, 1, QSizePolicy.Preferred))

        # position
        info_bars[1].addWidget(QLabel('Position:'))
        label_position = QLabel('{0}'.format(device_info.position.title()))
        device_info.plugin.label_position = label_position
        info_bars[1].addWidget(label_position)
        info_bars[1].addSpacerItem(QSpacerItem(1, 1, QSizePolicy.Expanding))

        # configs
        configs = device_info.plugin.get_configs()

        def config_changed(combobox):
            i = combobox.currentIndex()

            if i < 0:
                return

            combobox.itemData(i).trigger()

        if len(configs) > 0:
            for cfg in configs:
                if cfg[1] != None:
                    combobox = QComboBox()

                    for i, item in enumerate(cfg[2]):
                        combobox.addItem(item.text(), item)
                        item.triggered.connect(functools.partial(combobox.setCurrentIndex, i))

                    combobox.currentIndexChanged.connect(functools.partial(config_changed, combobox))

                    info_bars[cfg[0]].addWidget(QLabel(cfg[1]))
                    info_bars[cfg[0]].addWidget(combobox)
                elif len(cfg[2]) > 0:
                    checkbox = QCheckBox(cfg[2][0].text())
                    cfg[2][0].toggled.connect(checkbox.setChecked)
                    checkbox.toggled.connect(cfg[2][0].setChecked)

                    info_bars[cfg[0]].addWidget(checkbox)

        # actions
        actions = device_info.plugin.get_actions()

        if len(actions) > 0:
            for action in actions:
                if action[1] != None:
                    button = QPushButton(action[1])
                    menu = QMenu()

                    for item in action[2]:
                        menu.addAction(item)

                    button.setMenu(menu)
                elif len(action[2]) > 0:
                    button = QPushButton(action[2][0].text())
                    button.clicked.connect(action[2][0].trigger)

                info_bars[action[0]].addWidget(button)

        def more_clicked(button, info_bar):
            visible = button.text().replace('&', '') == 'More' # remove &s, they mark the buttons hotkey

            if visible:
                button.setText('Less')
            else:
                button.setText('More')

            for i in range(info_bar.count()):
                widget = info_bar.itemAt(i).widget()

                if widget != None:
                    widget.setVisible(visible)

        more_button = QPushButton('More')
        more_button.clicked.connect(lambda: more_clicked(more_button, info_bars[1]))

        info_bars[0].addWidget(more_button)

        for i in range(info_bars[1].count()):
            widget = info_bars[1].itemAt(i).widget()

            if widget != None:
                widget.hide()

        layout.addLayout(info_bars[0])
        layout.addLayout(info_bars[1])

        line = QFrame()
        line.setObjectName("MainWindow_line")
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)

        device_info.plugin.label_timeouts = label_timeouts
        device_info.plugin.label_version = label_version
        device_info.plugin.layout().setContentsMargins(0, 0, 0, 0)

        layout.addWidget(line)
        if device_info.plugin.has_comcu:
            device_info.plugin.widget_bootloader = COMCUBootloader(ipcon, device_info)
            device_info.plugin.widget_bootloader.hide()
            layout.addWidget(device_info.plugin.widget_bootloader)
        layout.addWidget(device_info.plugin, 1)

        return tab_window

    def tab_move(self, event):
        # visualize rearranging of tabs (if allowed by tab_widget)
        if self.tab_widget.isMovable():
            if event.type() == QEvent.MouseButtonPress and event.button() & Qt.LeftButton:
                QApplication.setOverrideCursor(QCursor(Qt.SizeHorCursor))

            elif event.type() == QEvent.MouseButtonRelease and event.button() & Qt.LeftButton:
                QApplication.restoreOverrideCursor()

        return False

    def untab(self, tab_index):
        tab = self.tab_widget.widget(tab_index)
        tab.untab()
        tab._info.plugin.start_plugin()
        self.tab_widget.setCurrentIndex(0)

    def connect_on_return(self, event):
        if event.type() == QEvent.KeyPress and (event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter):
            self.connect_clicked()
            return True
        return False

    def eventFilter(self, source, event):
        if source is self.tab_widget.tabBar():
            return self.tab_move(event)

        if source is self.combo_host or source is self.spinbox_port or source is self.edit_secret:
            return self.connect_on_return(event)

        if isinstance(source, QPushButton) and event.type() == QEvent.Enter:
            source.setIcon(QIcon(self.button_update_pixmap_hover))
        elif isinstance(source, QPushButton) and  event.type() == QEvent.Leave:
            source.setIcon(QIcon(self.button_update_pixmap_normal))

        return False

    def tab_for_uid(self, uid):
        for index in range(1, self.tab_widget.count()):
            try:
                if self.tab_widget.widget(index)._info.uid == uid:
                    return index
            except:
                pass

        return -1

    def show_plugin(self, uid):
        device_info = infos.get_info(uid)

        if device_info == None:
            return

        index = self.tab_for_uid(uid)
        tab_window = device_info.tab_window

        if index > 0 and self.tab_widget.isTabEnabled(index):
            self.tab_widget.setCurrentIndex(index)

        QApplication.setActiveWindow(tab_window)

        tab_window.show()
        tab_window.activateWindow()
        tab_window.raise_()

        return device_info.plugin

    def cb_enumerate(self, uid, connected_uid, position,
                     hardware_version, firmware_version,
                     device_identifier, enumeration_type):
        if self.ipcon.get_connection_state() != IPConnection.CONNECTION_STATE_CONNECTED:
            # ignore enumerate callbacks that arrived after the connection got closed
            return

        if enumeration_type in [IPConnection.ENUMERATION_TYPE_AVAILABLE,
                                IPConnection.ENUMERATION_TYPE_CONNECTED]:
            device_info = infos.get_info(uid)
            something_changed_ref = [False]

            # If the enum_type is CONNECTED, the bricklet was restarted externally.
            # The plugin could now be in an inconsistent state.
            if enumeration_type == IPConnection.ENUMERATION_TYPE_CONNECTED and device_info is not None:
                if device_info.connected_uid != connected_uid:
                    # Fix connections if bricklet was connected to another brick.
                    parent_info = infos.get_info(device_info.connected_uid)
                    if parent_info is not None:
                        parent_info.connections.remove((device_info.position, device_info))
                        self.show_status("Hot plugging is not supported! Please reset the brick {} and restart brick viewer.".format(device_info.connected_uid))
                    device_info.reverse_connection = connected_uid
                elif device_info.position != position:
                    # Bricklet was connected to the same brick, but to another port
                    self.show_status("Hot plugging is not supported! Please reset the brick {} and restart brick viewer.".format(device_info.connected_uid))

                # If the plugin is not running, pause will do nothing, so it is always save to call it.
                # The plugin will be (unconditionally) resumed later, as resume also only does something
                # if it was paused before (e.g. here).
                if device_info.plugin is not None:
                    device_info.plugin.pause_plugin()

            if device_info == None:
                if device_identifier == BrickMaster.DEVICE_IDENTIFIER:
                    device_info = infos.BrickMasterInfo()
                elif device_identifier == BrickRED.DEVICE_IDENTIFIER:
                    device_info = infos.BrickREDInfo()
                elif hat_brick_supported and device_identifier == BrickHAT.DEVICE_IDENTIFIER:
                    device_info = infos.BrickHATInfo()
                elif hat_zero_brick_supported and device_identifier == BrickHATZero.DEVICE_IDENTIFIER:
                    device_info = infos.BrickHATZeroInfo()
                elif device_identifier == BrickletIsolator.DEVICE_IDENTIFIER:
                    device_info = infos.BrickletIsolatorInfo()
                elif '0' <= position <= '9':
                    device_info = infos.BrickInfo()
                    something_changed_ref[0] = True
                else:
                    device_info = infos.BrickletInfo()

            position = position.lower()

            def set_device_info_value(name, value):
                if getattr(device_info, name) != value:
                    setattr(device_info, name, value)
                    something_changed_ref[0] = True
                    infos.get_infos_changed_signal().emit(device_info.uid)

            set_device_info_value('uid', uid)
            set_device_info_value('connected_uid', connected_uid)
            set_device_info_value('position', position)
            set_device_info_value('hardware_version', hardware_version)
            if device_identifier != BrickRED.DEVICE_IDENTIFIER:
                set_device_info_value('firmware_version_installed', firmware_version)
            set_device_info_value('device_identifier', device_identifier)
            set_device_info_value('enumeration_type', enumeration_type)

            # Update connections and reverse_connection with new device
            for info in infos.get_device_infos():
                if info == device_info:
                    continue

                def add_to_connections(info_to_add, connected_info):
                    connected_info.connections.append((info_to_add.position, info_to_add))
                    info_to_add.reverse_connection = connected_info
                    something_changed_ref[0] = True
                    infos.get_infos_changed_signal().emit(connected_info.uid)

                if info.uid != '' and info.uid == device_info.connected_uid:
                    if device_info in info.connections_values(): #Device was already connected, but to another port
                        info.connections = [(pos, i) for pos, i in info.connections if i.uid != device_info.uid]
                    if device_info not in info.connections_get(device_info.position):
                        add_to_connections(device_info, info)


                if info.connected_uid != '' and info.connected_uid == device_info.uid:
                    if info in device_info.connections_values(): #Device was already connected, but to another port
                        device_info.connections = [(pos, i) for pos, i in device_info.connections if i.uid != info.uid]
                    if info not in device_info.connections_get(info.position):
                        add_to_connections(info, device_info)

            if device_info.plugin == None:
                plugin = self.plugin_manager.create_plugin_instance(device_identifier, self.ipcon, device_info)

                device_info.tab_window = self.create_tab_window(device_info, self.ipcon)
                device_info.tab_window.setWindowFlags(Qt.Widget)
                device_info.tab_window.tab()

                infos.add_info(device_info)

                something_changed_ref[0] = True

                if device_identifier == BrickRED.DEVICE_IDENTIFIER and isinstance(plugin, RED):
                    plugin.get_image_version_async()
                    plugin.get_bindings_versions_async()

            # The plugin was paused before if it was reconnected.
            device_info.plugin.resume_plugin()

            if something_changed_ref[0]:
                self.update_tree_view()
        elif enumeration_type == IPConnection.ENUMERATION_TYPE_DISCONNECTED:
            self.remove_device_tab(uid)

    def remove_device_tab(self, uid):
        for device_info in infos.get_device_infos():
            if device_info.uid == uid:
                self.tab_widget.setCurrentIndex(0)
                self.remove_device_info(device_info.uid)

            if isinstance(device_info, infos.DeviceInfo):
                to_delete = []
                for idx, tup in enumerate(device_info.connections):
                    port, info = tup
                    if info.uid == uid:
                        to_delete.append(idx)
                for idx in to_delete:
                    del device_info.connections[idx]

        self.update_tree_view()

    def hack_to_remove_red_brick_tab(self, red_brick_uid):
        for device_info in infos.get_device_infos():
            if device_info.uid == red_brick_uid:
                self.tab_widget.setCurrentIndex(0)
                self.remove_device_info(device_info.uid)

                self.red_session_losts += 1
                self.label_red_session_losts.setText('RED Brick Session Loss Count: {0}'.format(self.red_session_losts))
                self.label_red_session_losts.show()

                break

        self.update_tree_view()

    def cb_connected(self, connect_reason):
        self.disconnect_times = []

        self.update_ui_state()

        if connect_reason == IPConnection.CONNECT_REASON_REQUEST:
            self.setDisabled(False)

            self.auto_reconnects = 0
            self.label_auto_reconnects.hide()

            self.red_session_losts = 0
            self.label_red_session_losts.hide()

            self.ipcon.set_auto_reconnect(True)

            index = self.combo_host.findText(self.last_host)

            if index >= 0:
                self.combo_host.removeItem(index)

                host_info = self.host_infos[index]

                del self.host_infos[index]
                self.host_infos.insert(0, host_info)
            else:
                index = self.combo_host.currentIndex()

                host_info = self.host_infos[index].duplicate()
                host_info.host = self.last_host

                self.host_infos.insert(0, host_info)

            self.combo_host.insertItem(-1, self.last_host)
            self.combo_host.setCurrentIndex(0)

            while self.combo_host.count() > config.HOST_INFO_COUNT:
                self.combo_host.removeItem(self.combo_host.count() - 1)

            if not self.do_authenticate(False):
                return

            try:
                self.ipcon.enumerate()
            except:
                self.update_ui_state()
        elif connect_reason == IPConnection.CONNECT_REASON_AUTO_RECONNECT:
            self.auto_reconnects += 1
            self.label_auto_reconnects.setText('Auto-Reconnect Count: {0}'.format(self.auto_reconnects))
            self.label_auto_reconnects.show()

            if not self.do_authenticate(True):
                return

            try:
                self.ipcon.enumerate()
            except:
                self.update_ui_state()
        else:
            try:
                self.ipcon.enumerate()
            except:
                self.update_ui_state()

    def cb_disconnected(self, disconnect_reason):
        if disconnect_reason == IPConnection.DISCONNECT_REASON_REQUEST:
            self.auto_reconnects = 0
            self.label_auto_reconnects.hide()

            self.red_session_losts = 0
            self.label_red_session_losts.hide()

        if disconnect_reason == IPConnection.DISCONNECT_REASON_REQUEST or not self.ipcon.get_auto_reconnect():
            self.update_ui_state()
        elif len(self.disconnect_times) >= 3 and self.disconnect_times[-3] < time.time() + 1:
            self.disconnect_times = []
            self.ipcon.set_auto_reconnect(False)
            self.update_ui_state()
            self.reset_view()

            QMessageBox.critical(self, 'Connection',
                                 'Stopped automatic reconnecting due to multiple connection errors in a row.')
        else:
            self.disconnect_times.append(time.time())
            self.update_ui_state(IPConnection.CONNECTION_STATE_PENDING)

    def set_tree_view_defaults(self):
        self.tree_view_model.setHorizontalHeaderLabels(self.tree_view_model_labels)
        self.tree_view.expandAll()
        self.tree_view.setColumnWidth(0, 280)
        self.tree_view.setColumnWidth(1, 70)
        self.tree_view.setColumnWidth(2, 90)
        self.tree_view.setColumnWidth(3, 105)
        self.tree_view.setColumnWidth(4, 105)
        self.tree_view.setExpandsOnDoubleClick(False)
        self.tree_view.setSortingEnabled(True)
        self.tree_view.header().setSortIndicator(2, Qt.AscendingOrder)

    def update_ui_state(self, connection_state=None):
        # FIXME: need to call processEvents() otherwise get_connection_state()
        #        might return the wrong value
        QApplication.processEvents()

        if connection_state is None:
            connection_state = self.ipcon.get_connection_state()

        self.button_flashing.setDisabled(False)

        if connection_state == IPConnection.CONNECTION_STATE_DISCONNECTED:
            self.button_connect.setText('Connect')
            self.combo_host.setDisabled(False)
            self.spinbox_port.setDisabled(False)
            self.checkbox_authentication.setDisabled(False)
            self.edit_secret.setDisabled(False)
            self.button_advanced.setDisabled(True)
        elif connection_state == IPConnection.CONNECTION_STATE_CONNECTED:
            self.button_connect.setText("Disconnect")
            self.combo_host.setDisabled(True)
            self.spinbox_port.setDisabled(True)
            self.checkbox_authentication.setDisabled(True)
            self.edit_secret.setDisabled(True)
            self.update_advanced_window()

            # restart all pause plugins
            for info in infos.get_device_infos():
                info.plugin.resume_plugin()
        elif connection_state == IPConnection.CONNECTION_STATE_PENDING:
            self.button_connect.setText('Abort Pending Automatic Reconnect')
            self.combo_host.setDisabled(True)
            self.spinbox_port.setDisabled(True)
            self.checkbox_authentication.setDisabled(True)
            self.edit_secret.setDisabled(True)
            self.button_advanced.setDisabled(True)
            self.button_flashing.setDisabled(True)

            # pause all running plugins
            for info in infos.get_device_infos():
                info.plugin.pause_plugin()

        enable = connection_state == IPConnection.CONNECTION_STATE_CONNECTED

        for i in range(1, self.tab_widget.count()):
            self.tab_widget.setTabEnabled(i, enable)

        for device_info in infos.get_device_infos():
            device_info.tab_window.setEnabled(enable)

        QApplication.processEvents()


    def update_tree_view(self):
        self.tree_view_model.setHorizontalHeaderLabels(self.tree_view_model_labels)
        self.tab_widget.tabBar().setTabButton(0, QTabBar.RightSide, None)

        sis = self.tree_view.header().sortIndicatorSection()
        sio = self.tree_view.header().sortIndicatorOrder()

        self.tree_view_model.clear()

        def get_row(info):
            replacement = '0.0.0'
            is_red_brick = isinstance(info, infos.BrickREDInfo)

            if is_red_brick or info.url_part == 'wifi_v2':
                replacement = "Querying..."
            elif info.type == "extension":
                replacement = ""

            fw_version = infos.get_version_string(info.firmware_version_installed,
                                                  replace_unknown=replacement,
                                                  is_red_brick=is_red_brick)

            uid = info.uid if info.type != "extension" else ''

            row = [QStandardItem(info.name),
                   QStandardItem(uid),
                   QStandardItem(info.position.title()),
                   QStandardItem(fw_version)]

            updateable = info.firmware_version_installed != (0, 0, 0) and info.firmware_version_installed < info.firmware_version_latest

            if is_red_brick:
                old_updateable = updateable
                for binding in info.bindings_infos:
                    updateable |= binding.firmware_version_installed != (0, 0, 0) \
                                  and binding.firmware_version_installed < binding.firmware_version_latest
                updateable |= info.brickv_info.firmware_version_installed != (0, 0, 0) \
                              and info.brickv_info.firmware_version_installed < info.brickv_info.firmware_version_latest \
                              and not info.firmware_version_installed < (1, 14, 0) # Hide Brickv update if image is too old.
                # There are bindings/brickv updates but there is no image update
                red_brick_binding_update_only = not old_updateable and updateable
            else:
                red_brick_binding_update_only = False

            if updateable:
                self.tree_view_model.setHorizontalHeaderLabels(self.tree_view_model_labels + ['Update'])
                row.append(QStandardItem(
                    infos.get_version_string(info.firmware_version_latest, is_red_brick=is_red_brick) + ("+" if red_brick_binding_update_only else "")))

                self.tab_widget.tabBar().setTabButton(0, QTabBar.RightSide, self.update_tab_button)
                self.update_tab_button.show()

            for item in row:
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                if updateable:
                    item.setData(QBrush(QColor(255, 160, 55)), Qt.BackgroundRole)

            return row

        def recurse_on_device(info, insertion_point):
            row = get_row(info)
            insertion_point.appendRow(row)

            for child in info.connections_values():
                recurse_on_device(child, row[0])

            if info.can_have_extension:
                for extension in info.extensions.values():
                    if extension is None:
                        continue
                    ext_row = get_row(extension)
                    row[0].appendRow(ext_row)

        for info in infos.get_device_infos():
            # If a device has a reverse connection, it will be handled as a child of another top-level brick.
            if info.reverse_connection is not None:
                continue
            recurse_on_device(info, self.tree_view_model)

        self.set_tree_view_defaults()
        self.tree_view.header().setSortIndicator(sis, sio)
        self.update_advanced_window()
        self.delayed_refresh_updates_timer.start()

    def update_advanced_window(self):
        self.button_advanced.setEnabled(len(infos.get_brick_infos()) > 0)

    def delayed_refresh_updates(self):
        self.delayed_refresh_updates_timer.stop()

        if self.flashing_window is not None and self.flashing_window.isVisible():
            self.flashing_window.refresh_update_tree_view()

    def show_status(self, message, icon='warning', message_id=''):
        self.setStatusBar(None)

        if icon != 'none':
            icon_dict = {
                'warning': 'warning-icon-16.png',
            }

            icon_label = QLabel()
            icon_label.setPixmap(load_pixmap(icon_dict[icon]))

            self.statusBar().addWidget(icon_label)

        message_label = QLabel(message)
        message_label.setOpenExternalLinks(True)

        self.statusBar().addWidget(message_label, 1)

        self.last_status_message_id = message_id

    def hide_status(self, message_id):
        if self.last_status_message_id == message_id:
            self.setStatusBar(None)

    def fw_versions_fetched(self, firmware_info):
        if isinstance(firmware_info, int):
            if firmware_info > 0:
                if firmware_info == 1:
                    message = 'Update information could not be downloaded from tinkerforge.com.<br/>' + \
                              'Is your computer connected to the Internet?'
                else:
                    message = ("Update information on tinkerforge.com is malformed " +
                               "(error code {0}).<br/>Please report this error to " +
                               "<a href='mailto:info@tinkerforge.com'>info@tinkerforge.com</a>.").format(firmware_info)

                self.show_status(message, message_id='fw_versions_fetched_error')

            infos.reset_latest_fws()
        else:
            self.hide_status('fw_versions_fetched_error')
            infos.update_latest_fws(firmware_info)

        self.update_tree_view()
