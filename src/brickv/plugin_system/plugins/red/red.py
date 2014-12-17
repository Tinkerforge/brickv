# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014 Matthias Bolte <matthias@tinkerforge.com>
Copyright (C) 2014 Ishraq Ibne Ashraf <ishraq@tinkerforge.com>

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

from PyQt4.QtGui import QLabel, QVBoxLayout
from PyQt4.QtCore import Qt

from brickv.plugin_system.plugin_base import PluginBase

from brickv.plugin_system.plugins.red.ui_red import Ui_RED
from brickv.plugin_system.plugins.red.api import *
from brickv.plugin_system.plugins.red.script_manager import ScriptManager

class RED(PluginBase, Ui_RED):
    def __init__(self, *args):
        PluginBase.__init__(self, 'RED Brick', REDBrick, *args)

        try:
            self.session = REDSession(self.device, self.increase_error_count).create()
        except Exception as e:
            self.session = None

            layout = QVBoxLayout(self)
            layout.addStretch()
            label = QLabel('Could not create session. There seems to be a problem with the RED Brick API Daemon:\n\n' + unicode(e))
            label.setAlignment(Qt.AlignHCenter)
            layout.addWidget(label)
            layout.addStretch()

            return

        self.script_manager = ScriptManager(self.session)

        self.setupUi(self)

        self.tabs_list = []
        for index in range(0, self.red_tab_widget.count()):
            self.tabs_list.append(self.red_tab_widget.widget(index))
            self.tabs_list[index].session = self.session
            self.tabs_list[index].script_manager = self.script_manager

        # signals and slots
        self.red_tab_widget.currentChanged.connect(self.cb_red_tab_widget_current_changed)

        # FIXME: RED Brick doesn't do enumerate-connected callback correctly yet
        #        for Brick(let)s connected to it. Trigger a enumerate to pick up
        #        all devices connected to a RED Brick properly
        self.ipcon.enumerate()

    def start(self):
        if self.session == None:
            return

        for index, tab in enumerate(self.tabs_list):
            if index == self.red_tab_widget.currentIndex():
                tab.tab_on_focus()
            else:
                tab.tab_off_focus()

        self.tabs_list[4].label_version = self.label_version
        self.tabs_list[4].update_main()

    def stop(self):
        if self.session == None:
            return

        for tab in self.tabs_list:
            tab.tab_off_focus()

    def destroy(self):
        if self.session == None:
            return

        for tab in self.tabs_list:
            tab.tab_destroy()

        self.script_manager.destroy()
        self.session.expire()

    def has_reset_device(self):
        return False # FIXME: will have reboot, instead of reset

    def reset_device(self):
        pass

    def has_drop_down(self):
        return ['System', 'Restart Brick Daemon', 'Reboot RED Brick', 'Shut down RED Brick']

    def drop_down_triggered(self, action):
        if self.session == None:
            return

        def cb(result):
            if result == None or result.stderr != '':
                pass # TODO: Error popup?

        t = action.text()
        param = -1

        if t == 'Restart Brick Daemon':
            param = 0
        elif t == 'Reboot RED Brick':
            param = 1
        elif t == 'Shut down RED Brick':
            param = 2

        if param != -1:
            self.script_manager.execute_script('restart_reboot_shutdown', cb, [str(param)])

    def has_custom_version(self, label_version_name, label_version):
        self.label_version_name = label_version_name
        self.label_version_name.setText('Image Version: ')
        self.label_version = label_version

        return True

    def is_brick(self):
        return True

    def get_url_part(self):
        return 'red'

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickRED.DEVICE_IDENTIFIER

    # the callbacks
    def cb_red_tab_widget_current_changed(self, tab_index):
        for index, tab in enumerate(self.tabs_list):
            if index == tab_index:
                tab.tab_on_focus()
            else:
                tab.tab_off_focus()
