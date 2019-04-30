# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014-2015 Matthias Bolte <matthias@tinkerforge.com>
Copyright (C) 2014-2017 Ishraq Ibne Ashraf <ishraq@tinkerforge.com>

red.py: RED Plugin implementation

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
import json
import html
import functools
import traceback

from PyQt5.QtWidgets import QMessageBox, QLabel, QVBoxLayout, QAction, QTextBrowser

from brickv.plugin_system.plugin_base import PluginBase
from brickv.plugin_system.plugins.red.ui_red import Ui_RED
from brickv.plugin_system.plugins.red.api import *
from brickv.plugin_system.plugins.red.script_manager import ScriptManager, check_script_result
from brickv.async_call import async_call
from brickv.plugin_system.plugins.red.red_update_tinkerforge_software_dialog import REDUpdateTinkerforgeSoftwareDialog
import brickv.infos

class ImageVersion:
    string = None
    number = (0, 0)
    flavor = None

class RED(PluginBase, Ui_RED):
    def __init__(self, *args):
        PluginBase.__init__(self, REDBrick, *args)

        try:
            self.session = REDSession(self.device, self.increase_error_count).create()
        except Exception as e:
            self.session = None
            self.report_fatal_error('Could not create session', str(e), traceback.format_exc())
            return

        try:
            self.script_manager = ScriptManager(self.session)
        except Exception as e:
            self.session.expire()
            self.session = None
            self.report_fatal_error('Could not create script manager', str(e), traceback.format_exc())
            return

        self.image_version  = ImageVersion()
        self.label_version  = None
        self.tabs           = []

        self.setupUi(self)

        self.tab_widget.hide()

        for i in range(self.tab_widget.count()):
            tab = self.tab_widget.widget(i)

            tab.session        = self.session
            tab.script_manager = self.script_manager
            tab.image_version  = self.image_version

            self.tabs.append(tab)

        self.tab_widget.currentChanged.connect(self.tab_widget_current_changed)

        actions = []

        for param, name in enumerate(['Restart Brick Daemon', 'Reboot RED Brick', 'Shut down RED Brick', 'Update Tinkerforge Software']):
            action = QAction(name, self)
            action.triggered.connect(functools.partial(self.perform_action, param))
            actions.append(action)

        self.set_actions([(0, 'System', actions)])

        self.dialog_update_tinkerforge_software = None

        # FIXME: RED Brick doesn't do enumerate-connected callback correctly yet
        #        for Brick(let)s connected to it. Trigger a enumerate to pick up
        #        all devices connected to a RED Brick properly
        self.ipcon.enumerate()

    def report_fatal_error(self, title, message, trace):
        trace = '<pre>{}</pre>'.format(html.escape(trace).replace('\n', '<br>'))

        label_title = QLabel(title)

        font = label_title.font()
        font.setBold(True)
        label_title.setFont(font)

        label_message = QLabel('Error: ' + message)
        browser_trace = QTextBrowser()
        browser_trace.setHtml(trace)

        layout = QVBoxLayout(self)
        layout.addWidget(label_title)
        layout.addWidget(label_message)
        layout.addWidget(browser_trace)

    def get_image_version_async(self):
        if self.session == None:
            return

        def read_image_version_async(red_file):
            return red_file.open('/etc/tf_image_version',
                                 REDFile.FLAG_READ_ONLY | REDFile.FLAG_NON_BLOCKING,
                                 0, 0, 0).read(256).decode('utf-8').strip()

        def cb_success(image_version):
            if self.label_version != None:
                self.label_version.setText(image_version)

            m = re.match(r'(\d+)\.(\d+)\s+\((.+)\)', image_version)

            if m != None:
                try:
                    self.image_version.number = (int(m.group(1)), int(m.group(2)))
                    self.image_version.flavor = m.group(3)
                    self.image_version.string = image_version # set this last, because it is used as validity check
                except:
                    self.label_discovering.setText('Error: Could not parse Image Version: {0}'.format(image_version))
                else:
                    self.widget_discovering.hide()
                    self.tab_widget.show()
                    self.tab_widget_current_changed(self.tab_widget.currentIndex())
                    self.device_info.firmware_version_installed = self.image_version.number + (0, )
                    brickv.infos.update_info(self.device_info.uid)
            else:
                self.label_discovering.setText('Error: Could not parse Image Version: {0}'.format(image_version))

        self.label_discovering.setText('Discovering Image Version...')
        self.widget_discovering.show()
        async_call(read_image_version_async, REDFile(self.session), cb_success, None)

    def bindings_version_success(self, result):
        okay, message = check_script_result(result)
        if not okay:
            get_main_window().show_status('Failed to query RED Brick bindings versions: '+ message, message_id='red_bindings_version_success_error')
            return

        try:
            versions = json.loads(result.stdout)
        except Exception as e:
            get_main_window().show_status('Failed to parse RED Brick bindings versions as JSON: '+ str(e), message_id='red_bindings_version_success_error')
            return

        get_main_window().hide_status('red_bindings_version_success_error')

        self.device_info.bindings_infos = []
        for url_part, version in versions['bindings'].items():
            info = brickv.infos.BindingInfo()
            info.name = brickv.infos.get_bindings_name(url_part)
            info.url_part = url_part
            info.firmware_version_installed = tuple(int(i) for i in version.split('.'))

            brickv.infos.add_latest_fw(info)
            self.device_info.bindings_infos.append(info)

        red_brickv_info = brickv.infos.ToolInfo()
        red_brickv_info.name = 'Brick Viewer'
        red_brickv_info.url_part = 'brickv'
        red_brickv_info.firmware_version_installed = tuple(int(i) for i in versions['brickv'].split('.'))

        brickv.infos.add_latest_fw(red_brickv_info)
        self.device_info.brickv_info = red_brickv_info

        brickv.infos.get_infos_changed_signal().emit(self.device_info.uid)

    def get_bindings_versions_async(self):
        if self.session == None:
            return

        self.script_manager.execute_script('update_tf_software_get_installed_versions',
                                           self.bindings_version_success)

    def show_bindings_update(self, bindings=True, brickv=False):
        button_text = ""
        tool_tip_text = ""

        if bindings and brickv:
            button_text = "Update Bindings and Brick Viewer for RED Brick"
            tool_tip_text = "Binding and Brick Viewer Updates for RED Brick available"
        elif bindings:
            button_text = "Update Bindings for RED Brick"
            tool_tip_text = "Binding Updates for RED Brick available"
        elif brickv:
            button_text = "Update Brick Viewer for RED Brick"
            tool_tip_text = "Brick Viewer Update for RED Brick available"

        # Show "normal" update button and customize it
        self.show_update()

        self.device_info.tab_window.button_update.setText(button_text)
        self.device_info.tab_window.button_update.clicked.disconnect()
        self.device_info.tab_window.button_update.clicked.connect(lambda: self.perform_action(3))

        self.update_tab_button.setToolTip(tool_tip_text)
        self.update_tab_button.clicked.disconnect()
        self.update_tab_button.clicked.connect(lambda: self.perform_action(3))

    def show_image_update(self):
        self.show_update()

        # Maybe a bindings update was shown the last time,
        # revert changes to the update buttons.
        self.device_info.tab_window.button_update.setText("Update Image for RED Brick")
        self.device_info.tab_window.button_update.clicked.disconnect()
        self.device_info.tab_window.button_update.clicked.connect(get_main_window().show_red_brick_update)

        self.update_tab_button.setToolTip('Image Update for RED Brick available')
        self.update_tab_button.clicked.disconnect()
        self.update_tab_button.clicked.connect(lambda: get_main_window().show_red_brick_update())

    # Overrides PluginBase.device_infos_changed
    def device_infos_changed(self, uid):
        if uid != self.device_info.uid:
            return

        if self.device_info.tab_window is None:
            return

        # The rationale here is the same as with the Master Brick:
        # Prioritize bindings (and brickv) updates over image updates,
        # as they are easier to install. Also when they are updated,
        # device_infos_changed is triggered again, so the image update
        # will be shown afterwards.
        # A special case is the update to image 1.14: This adds
        # support for the Brick Viewer version 2.4.0 and should therefore
        # be prioritized.

        brickv_update = (self.device_info.brickv_info.firmware_version_installed != (0, 0, 0)) \
                        and (self.device_info.brickv_info.firmware_version_installed < self.device_info.brickv_info.firmware_version_latest) \
                        and self.device_info.firmware_version_installed >= (1, 14, 0) # Don't show brickv update if the image does not contain Qt5

        bindings_update = any(info.firmware_version_installed < info.firmware_version_latest for info in self.device_info.bindings_infos)

        image_update = self.device_info.firmware_version_installed != (0, 0, 0) \
                       and self.device_info.firmware_version_installed < self.device_info.firmware_version_latest

        if image_update and self.device_info.firmware_version_installed < (1, 14, 0):
            self.show_image_update()
        elif brickv_update or bindings_update:
            self.show_bindings_update(bindings=bindings_update, brickv=brickv_update)
        elif image_update:
            self.show_image_update()
        else:
            self.hide_update()

    def start(self):
        if self.session == None:
            return

        if self.image_version.string == None:
            # FIXME: this is should actually be sync to ensure that the image
            #        version is known before it'll be used
            self.get_image_version_async()
        else:
            self.tab_widget_current_changed(self.tab_widget.currentIndex())

    def stop(self):
        if self.session == None:
            return

        for tab in self.tabs:
            tab.tab_off_focus()

    def destroy(self):
        if self.session == None:
            return

        if self.dialog_update_tinkerforge_software is not None:
            self.dialog_update_tinkerforge_software.close()

        for tab in self.tabs:
            tab.tab_destroy()

        self.script_manager.destroy()
        self.session.expire()

    def has_custom_version(self, label_version_name, label_version):
        label_version_name.setText('Image Version:')

        self.label_version = label_version

        if hasattr(self, 'image_version') and self.image_version.string != None:
            self.label_version.setText(self.image_version.string)

        return True

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickRED.DEVICE_IDENTIFIER

    def tab_widget_current_changed(self, index):
        for i, tab in enumerate(self.tabs):
            if i == index:
                tab.tab_on_focus()
            else:
                tab.tab_off_focus()

    def perform_action(self, param):
        if self.session == None or self.image_version.string == None:
            return

        # Restart Brick Daemon
        if param == 0:
            self.script_manager.execute_script('restart_brickd', None)

        # Reboot or shutdown RED Brick
        elif param == 1 or param == 2:
            def cb(result):
                okay, message = check_script_result(result)
                if not okay:
                    op = 'reboot' if param == 1 else 'shutdown'
                    QMessageBox.critical(get_main_window(), 'Failed to {} RED Brick'.format(op), message)

            self.script_manager.execute_script('restart_reboot_shutdown_systemd', cb, [str(param)])

        # Update Tinkerforge software
        elif param == 3:
            self.dialog_update_tinkerforge_software = REDUpdateTinkerforgeSoftwareDialog(self, self.session, self.script_manager)
            self.dialog_update_tinkerforge_software.exec_()
            self.dialog_update_tinkerforge_software = None
