# -*- coding: utf-8 -*-
"""
brickv (Brick Viewer)
Copyright (C) 2012, 2014 Roland Dudko <roland.dudko@gmail.com>
Copyright (C) 2012, 2014 Marvin Lutz <marvin.lutz.mail@gmail.com>

gui_config_handler.py: Util classes for the data logger

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

import collections

from PyQt4.QtGui import QComboBox, QSpinBox, QDoubleSpinBox

from brickv.data_logger.event_logger import EventLogger, GUILogger

'''
/*---------------------------------------------------------------------------
                                GuiConfigHandler
 ---------------------------------------------------------------------------*/
 '''

class GuiConfigHandler(object):
    def create_config(setup_dialog):
        """
        Creates a config file. Converst all devices from the tree_widget and
        fetches the other information. Returns the config as dictonary.
        """
        config = {'hosts': GuiConfigHandler.create_hosts_section(setup_dialog),
                  'data': GuiConfigHandler.create_data_section(setup_dialog),
                  'events': GuiConfigHandler.create_events_section(setup_dialog),
                  'devices': GuiConfigHandler.create_devices_section(setup_dialog)}

        return config

    def create_hosts_section(setup_dialog):
        """
        Creates the hosts section part of the config file
        and returns it as a dictonary.
        """
        # store hosts as a dict as preparation for multi-host support. so the
        # config format doesn't have to be changed if multi-host support is added
        hosts = {'default': {'name': setup_dialog.combo_host.currentText(),
                             'port': setup_dialog.spin_port.value()}}

        return hosts

    def create_data_section(setup_dialog):
        """
        Creates the data section part of the config file
        and returns it as a dictonary.
        """
        data = {'time_format': setup_dialog.combo_data_time_format.itemData(setup_dialog.combo_data_time_format.currentIndex()),
                'csv': {'enabled': setup_dialog.check_data_to_csv_file.isChecked(),
                        'file_name': setup_dialog.edit_csv_file_name.text()}}

        return data

    def create_events_section(setup_dialog):
        """
        Creates the events section part of the config file
        and returns it as a dictonary.
        """
        events = {'time_format': setup_dialog.combo_events_time_format.itemData(setup_dialog.combo_events_time_format.currentIndex()),
                  'log': {'enabled': setup_dialog.check_events_to_log_file.isChecked(),
                          'file_name': setup_dialog.edit_log_file_name.text(),
                          'level': setup_dialog.combo_log_level.itemData(setup_dialog.combo_log_level.currentIndex())}}

        return events

    def create_devices_section(setup_dialog):
        devices = []

        for row in range(setup_dialog.model_devices.rowCount()):
            name_item = setup_dialog.model_devices.item(row, 0)
            uid_item = setup_dialog.model_devices.item(row, 1)
            device = {
                'host': 'default',
                'name': name_item.text(),
                'uid': setup_dialog.tree_devices.indexWidget(uid_item.index()).text(),
                'values': {}
            }

            for child_row in range(name_item.rowCount()):
                child_item = name_item.child(child_row, 0)

                if child_item.text() == 'Values':
                    for value_row in range(child_item.rowCount()):
                        value_name_item = child_item.child(value_row, 0)
                        value_interval_item = child_item.child(value_row, 1)

                        device['values'][value_name_item.text()] = {'interval': setup_dialog.tree_devices.indexWidget(value_interval_item.index()).value()}
                        subvalues = {}

                        for subvalue_row in range(value_name_item.rowCount()):
                            subvalue_name_item = value_name_item.child(subvalue_row, 0)
                            subvalue_check_item = value_name_item.child(subvalue_row, 1)
                            subvalues[subvalue_name_item.text()] = setup_dialog.tree_devices.indexWidget(subvalue_check_item.index()).isChecked()

                        if len(subvalues) > 0:
                            device['values'][value_name_item.text()]['subvalues'] = subvalues
                elif child_item.text() == 'Options':
                    options = {}

                    for option_row in range(child_item.rowCount()):
                        option_name_item = child_item.child(option_row, 0)
                        option_widget_item = child_item.child(option_row, 1)
                        widget_option_value = setup_dialog.tree_devices.indexWidget(option_widget_item.index())

                        if isinstance(widget_option_value, QComboBox):
                            options[option_name_item.text()] = {'value': widget_option_value.currentText()}
                        elif isinstance(widget_option_value, QSpinBox):
                            options[option_name_item.text()] = {'value': widget_option_value.value()}
                        elif isinstance(widget_option_value, QDoubleSpinBox):
                            options[option_name_item.text()] = {'value': widget_option_value.value()}

                    device['options'] = options

            devices.append(device)

        return devices

    create_config = staticmethod(create_config)
    create_hosts_section = staticmethod(create_hosts_section)
    create_data_section = staticmethod(create_data_section)
    create_events_section = staticmethod(create_events_section)
    create_devices_section = staticmethod(create_devices_section)
