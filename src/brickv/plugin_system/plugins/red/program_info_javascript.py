# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014 Matthias Bolte <matthias@tinkerforge.com>

program_info_javascript.py: Program JavaScript Info Widget

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

from brickv.plugin_system.plugins.red.program_info import ProgramInfo
from brickv.plugin_system.plugins.red.program_utils import Constants
from brickv.plugin_system.plugins.red.ui_program_info_javascript import Ui_ProgramInfoJavaScript

class ProgramInfoJavaScript(ProgramInfo, Ui_ProgramInfoJavaScript):
    def __init__(self, context):
        ProgramInfo.__init__(self, context)

        self.setupUi(self)

        self.check_show_advanced_options.stateChanged.connect(self.update_ui_state)

    # overrides ProgramInfo.update_ui_state
    def update_ui_state(self):
        show_advanced_options = self.check_show_advanced_options.isChecked()

        # flavor
        flavor_api_name = self.program.cast_custom_option_value('javascript.flavor', unicode, '<unknown>')
        flavor          = Constants.get_javascript_flavor(flavor_api_name)
        flavor_browser  = flavor == Constants.JAVASCRIPT_FLAVOR_BROWSER
        flavor_nodejs   = flavor == Constants.JAVASCRIPT_FLAVOR_NODEJS

        if flavor_browser:
            self.label_flavor.setText('Client-Side')
        elif flavor_nodejs:
            def cb_nodejs_versions(versions):
                for version in versions:
                    if version.executable == self.program.executable:
                        self.label_flavor.setText('Server-Side (Node.js {0})'.format(version.version))
                        return

                self.label_flavor.setText('Server-Side (Node.js)')

            self.get_executable_versions('nodejs', cb_nodejs_versions)

        self.check_show_advanced_options.setVisible(flavor_nodejs)
        self.line.setVisible(flavor_nodejs)

        # start mode
        start_mode_api_name    = self.program.cast_custom_option_value('javascript.start_mode', unicode, '<unknown>')
        start_mode             = Constants.get_javascript_start_mode(start_mode_api_name)
        start_mode_script_file = start_mode == Constants.JAVASCRIPT_START_MODE_SCRIPT_FILE
        start_mode_command     = start_mode == Constants.JAVASCRIPT_START_MODE_COMMAND

        self.label_start_mode_title.setVisible(flavor_nodejs)
        self.label_start_mode.setVisible(flavor_nodejs)
        self.label_start_mode.setText(Constants.javascript_start_mode_display_names[start_mode])

        # script file
        self.label_script_file_title.setVisible(flavor_nodejs and start_mode_script_file)
        self.label_script_file.setVisible(flavor_nodejs and start_mode_script_file)
        self.label_script_file.setText(self.program.cast_custom_option_value('javascript.script_file', unicode, '<unknown>'))

        # command
        self.label_command_title.setVisible(flavor_nodejs and start_mode_command)
        self.label_command.setVisible(flavor_nodejs and start_mode_command)
        self.label_command.setText(self.program.cast_custom_option_value('javascript.command', unicode, '<unknown>'))

        # working directory
        self.label_working_directory_title.setVisible(flavor_nodejs and show_advanced_options)
        self.label_working_directory.setVisible(flavor_nodejs and show_advanced_options)
        self.label_working_directory.setText(self.program.working_directory)

        # options
        self.label_options_title.setVisible(flavor_nodejs and show_advanced_options)
        self.label_options.setVisible(flavor_nodejs and show_advanced_options)
        self.label_options.setText('\n'.join(self.program.cast_custom_option_value_list('javascript.options', unicode, [])))
