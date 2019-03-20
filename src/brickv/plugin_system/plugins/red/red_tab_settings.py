# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014 Ishraq Ibne Ashraf <ishraq@tinkerforge.com>
Copyright (C) 2014 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2014-2015 Matthias Bolte <matthias@tinkerforge.com>

red_tab_settings.py: RED settings tab implementation

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

from brickv.plugin_system.plugins.red.red_tab import REDTab
from brickv.plugin_system.plugins.red.ui_red_tab_settings import Ui_REDTabSettings
import json

class ServiceState:
    fetched          = False
    gpu              = None
    desktopenv       = None
    webserver        = None
    splashscreen     = None
    ap               = None
    servermonitoring = None
    openhab          = None
    mobileinternet   = None

class REDTabSettings(REDTab, Ui_REDTabSettings):
    def __init__(self):
        REDTab.__init__(self)

        self.tabs          = []
        self.service_state = ServiceState()

        self.setupUi(self)

        self.tab_widget.hide()

        for i in range(self.tab_widget.count()):
            self.tabs.append(self.tab_widget.widget(i))

        self.tab_widget.currentChanged.connect(self.tab_widget_current_changed)

    def tab_on_focus(self):
        for tab in self.tabs:
            tab.session        = self.session
            tab.script_manager = self.script_manager
            tab.image_version  = self.image_version
            tab.service_state  = self.service_state

        if not self.service_state.fetched:
            def cb_settings_services_check(result):
                if result and result.stdout and not result.stderr and result.exit_code == 0:
                    services_check_result = json.loads(result.stdout)

                    if services_check_result:
                        if services_check_result['gpu'] is None or \
                           services_check_result['desktopenv'] is None or \
                           services_check_result['webserver'] is None or \
                           services_check_result['splashscreen'] is None or \
                           services_check_result['ap'] is None or \
                           services_check_result['servermonitoring'] is None or \
                           services_check_result['openhab'] is None or \
                           services_check_result['mobileinternet'] is None:
                            self.label_discovering.setText('Received incomplete current services status.')
                        else:
                            self.service_state.fetched          = True
                            self.service_state.gpu              = services_check_result['gpu']
                            self.service_state.desktopenv       = services_check_result['desktopenv']
                            self.service_state.webserver        = services_check_result['webserver']
                            self.service_state.splashscreen     = services_check_result['splashscreen']
                            self.service_state.ap               = services_check_result['ap']
                            self.service_state.servermonitoring = services_check_result['servermonitoring']
                            self.service_state.openhab          = services_check_result['openhab']
                            self.service_state.mobileinternet   = services_check_result['mobileinternet']

                            if self.image_version.number < (1, 4):
                                self.service_state.desktopenv = self.image_version.flavor == 'full'

                            self.label_discovering.hide()
                            self.tab_widget.show()
                            self.tab_widget.currentWidget().tab_on_focus()
                elif result and result.stderr:
                    self.label_discovering.setText('Error getting current services status:\n\n' + result.stderr)
                else:
                    self.label_discovering.setText('Error getting current services status.')

            self.script_manager.execute_script('settings_services',
                                               cb_settings_services_check,
                                               ['CHECK'])
        else:
            self.tab_widget.currentWidget().tab_on_focus()

    def tab_off_focus(self):
        for tab in self.tabs:
            tab.tab_off_focus()

    def tab_destroy(self):
        pass

    def tab_widget_current_changed(self, index):
        for i, tab in enumerate(self.tabs):
            if i == index:
                tab.tab_on_focus()
            else:
                tab.tab_off_focus()
