# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014-2015 Matthias Bolte <matthias@tinkerforge.com>
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
from brickv.async_call import async_call
import re

class ImageVersion(object):
    string = None
    number = (0, 0)
    flavor = None

class RED(PluginBase, Ui_RED):
    def __init__(self, *args):
        PluginBase.__init__(self, 'RED Brick', REDBrick, *args)

        try:
            self.session = REDSession(self.device, self.increase_error_count).create()
        except Exception as e:
            self.session = None

            label = QLabel('Could not create session:\n\n{0}'.format(e))
            label.setAlignment(Qt.AlignHCenter)

            layout = QVBoxLayout(self)
            layout.addStretch()
            layout.addWidget(label)
            layout.addStretch()

            return

        self.image_version  = ImageVersion()
        self.label_version  = None
        self.script_manager = ScriptManager(self.session)
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

        # FIXME: RED Brick doesn't do enumerate-connected callback correctly yet
        #        for Brick(let)s connected to it. Trigger a enumerate to pick up
        #        all devices connected to a RED Brick properly
        self.ipcon.enumerate()

    def start(self):
        if self.session == None:
            return

        if self.image_version.string == None:
            # FIXME: this is should actually be sync to ensure that the image
            #        version is known before it'll be used
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
                        self.image_version.string = image_version
                        self.image_version.number = (int(m.group(1)), int(m.group(2)))
                        self.image_version.flavor = m.group(3)
                    except:
                        pass

                self.label_discovering.hide()
                self.tab_widget.show()
                self.tab_widget_current_changed(self.tab_widget.currentIndex())

            async_call(read_image_version_async, REDFile(self.session), cb_success, None)
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

        for tab in self.tabs:
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
        label_version_name.setText('Image Version: ')

        self.label_version = label_version

        if self.image_version.string != None:
            self.label_version.setText(self.image_version.string)

        return True

    def is_brick(self):
        return True

    def get_url_part(self):
        return 'red'

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickRED.DEVICE_IDENTIFIER

    def tab_widget_current_changed(self, index):
        for i, tab in enumerate(self.tabs):
            if i == index:
                tab.tab_on_focus()
            else:
                tab.tab_off_focus()
