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

from brickv.data_logger.event_logger import EventLogger, GUILogger
from brickv.data_logger.loggable_devices import Identifier as Idf

'''
/*---------------------------------------------------------------------------
                                GuiConfigHandler
 ---------------------------------------------------------------------------*/
 '''


class GuiConfigHandler(object):
    """
        This static class is used to convert a config into a blueprint for the gui and vice versa.
        It also holds a blueprint with all supported devices. If a new device should be supported,
        this string should be updatetd, too.
    """

    device_blueprint = []

    def load_devices(device_json):
        """
        Loads the config as json and converts all devices into the blueprint part.
        Returns the blueprint of the devices.
        """
        try:
            GuiConfigHandler.clear_blueprint()
            GuiConfigHandler.create_device_blueprint(device_json[Idf.DEVICES])

        except Exception as e:
            EventLogger.warning("Devices could not be fully loaded! -> " + str(e))

        return GuiConfigHandler.device_blueprint

    @staticmethod
    def clear_blueprint():
        """
        Resets the current blueprints save in device_blueprint.
        """
        GuiConfigHandler.device_blueprint = None
        GuiConfigHandler.device_blueprint = []

    def create_device_blueprint(devices):
        import copy

        for dev in devices:
            bp_dev = None  # Blueprint Device

            # check for blueprint KEY(DEVICE_DEFINITIONS)
            if dev[Idf.DD_NAME] in Idf.DEVICE_DEFINITIONS:
                bp_dev = copy.deepcopy(Idf.DEVICE_DEFINITIONS[dev[Idf.DD_NAME]])
                # remove unused entries(class)
                del bp_dev[Idf.DD_CLASS]

                # add new entries(name, uid)
                bp_dev[Idf.DD_NAME] = dev[Idf.DD_NAME]
                bp_dev[Idf.DD_UID] = dev[Idf.DD_UID]

                # add/remove entries for values
                for val in bp_dev[Idf.DD_VALUES]:

                    # remove getter
                    del bp_dev[Idf.DD_VALUES][val][Idf.DD_GETTER]

                    # add interval, check if exists
                    if val in bp_dev[Idf.DD_VALUES]:
                        # check for NO device values
                        if not val in dev[Idf.DD_VALUES]:
                            # create necessary structures for the checks
                            dev[Idf.DD_VALUES][val] = {}
                            dev[Idf.DD_VALUES][val][Idf.DD_SUBVALUES] = {}

                        if Idf.DD_VALUES_INTERVAL in dev[Idf.DD_VALUES][val]:
                            bp_dev[Idf.DD_VALUES][val][Idf.DD_VALUES_INTERVAL] = dev[Idf.DD_VALUES][val][Idf.DD_VALUES_INTERVAL]
                        else:
                            bp_dev[Idf.DD_VALUES][val][Idf.DD_VALUES_INTERVAL] = 0

                        # subvalues

                        if bp_dev[Idf.DD_VALUES][val][Idf.DD_SUBVALUES] is not None:
                            bp_sub_values = bp_dev[Idf.DD_VALUES][val][Idf.DD_SUBVALUES]

                            # delete subvalues old entries
                            bp_dev[Idf.DD_VALUES][val][Idf.DD_SUBVALUES] = {}

                            for i in range(0, len(bp_sub_values)):
                                # check sub_val for bool
                                sub_val = bp_sub_values[i]

                                # check if list in list #FIXME multi layer? sub_sub_sub_....
                                if type(sub_val) == list:
                                    for j in range(0, len(sub_val)):
                                        sub_sub_val = sub_val[j]

                                        if sub_sub_val in dev[Idf.DD_VALUES][val][Idf.DD_SUBVALUES]:
                                            bp_dev[Idf.DD_VALUES][val][Idf.DD_SUBVALUES][sub_sub_val] = dev[Idf.DD_VALUES][val][Idf.DD_SUBVALUES][sub_sub_val]
                                        else:
                                            bp_dev[Idf.DD_VALUES][val][Idf.DD_SUBVALUES][sub_sub_val] = False
                                    continue

                                if sub_val in dev[Idf.DD_VALUES][val][Idf.DD_SUBVALUES]:
                                    bp_dev[Idf.DD_VALUES][val][Idf.DD_SUBVALUES][sub_val] = dev[Idf.DD_VALUES][val][Idf.DD_SUBVALUES][sub_val]
                                else:
                                    bp_dev[Idf.DD_VALUES][val][Idf.DD_SUBVALUES][sub_val] = False

                    else:
                        bp_dev[Idf.DD_VALUES][val][Idf.DD_VALUES_INTERVAL] = 0  # Default Value for Interval

            else:
                EventLogger.warning("No Device Definition found in Config for Device Name: " + str(dev[Idf.DD_NAME]) + "! Device will be ignored!")

            GuiConfigHandler.device_blueprint.append(bp_dev)

    def create_config_file(setup_dialog):
        """
        Creates a config file. Converst all devices from the tree_widget and
        fetches the GENERAL_SECTION information.
        Returns the config as dictonary.
        """
        config_root = {}
        # add general section
        general_section = GuiConfigHandler.create_general_section(setup_dialog)

        # add device section
        device_section = GuiConfigHandler.create_device_section(setup_dialog)

        from brickv.data_logger.configuration_validator import ConfigurationReader

        config_root[ConfigurationReader.GENERAL_SECTION] = general_section
        config_root[Idf.DEVICES] = device_section

        return config_root

    def create_general_section(setup_dialog):
        """
        Creates the GENERAL_SECTION part of the config file 
        and returns it as a dictonary.
        """
        from brickv.data_logger.configuration_validator import ConfigurationReader

        general_section = {}

        # host            combo_host              currentText()   : str
        general_section[ConfigurationReader.GENERAL_HOST] = setup_dialog.combo_host.currentText()
        # port            spinbox_port            value()         : int
        general_section[ConfigurationReader.GENERAL_PORT] = setup_dialog.spinbox_port.value()
        # file_count      spin_file_count         value()         : int
        general_section[ConfigurationReader.GENERAL_LOG_COUNT] = setup_dialog.spin_file_count.value()
        # file_size       spin_file_size          value()         : int * 1024 * 1024! (MB -> Byte)
        general_section[ConfigurationReader.GENERAL_LOG_FILE_SIZE] = (setup_dialog.spin_file_size.value() * 1024 * 1024)
        # path_to_file    line_csv_data_file      text()          : str
        path_to_file = setup_dialog.line_csv_data_file.text()

        log_to_file = True
        if path_to_file is None or path_to_file == "":
            log_to_file = False
        # log_to_file     (if path_to_file != None || "")
        general_section[ConfigurationReader.GENERAL_PATH_TO_FILE] = path_to_file
        general_section[ConfigurationReader.GENERAL_LOG_TO_FILE] = log_to_file

        # logfile path
        general_section[ConfigurationReader.GENERAL_EVENTLOG_PATH] = setup_dialog.line_event_log_file.text()
        # loglevel
        ll = setup_dialog.combo_loglevel.currentText()
        log_level_num = 0
        od = collections.OrderedDict(sorted(GUILogger._convert_level.items()))
        for k in od.keys():
            if ll == od[k]:
                log_level_num = k
                break
        general_section[ConfigurationReader.GENERAL_EVENTLOG_LEVEL] = log_level_num
        # log_to_console
        general_section[ConfigurationReader.GENERAL_EVENTLOG_TO_FILE] = setup_dialog.checkbox_to_file.isChecked()
        # log_to_file
        general_section[ConfigurationReader.GENERAL_EVENTLOG_TO_CONSOLE] = setup_dialog.checkbox_to_console.isChecked()

        return general_section

    def create_device_section(setup_dialog):
        tree_widget = setup_dialog.tree_devices
        devices = []

        # start lvl0 - basics(name|uid)
        lvl0_max = tree_widget.topLevelItemCount()
        for lvl0 in range(0, lvl0_max):
            lvl0_item = tree_widget.topLevelItem(lvl0)
            # create device item
            dev = {}
            dev_name = lvl0_item.text(0)
            dev[Idf.DD_NAME] = dev_name
            dev[Idf.DD_UID] = lvl0_item.text(1)
            dev[Idf.DD_VALUES] = {}

            # start lvl1 - values(name|interval)
            lvl1_max = lvl0_item.childCount()
            for lvl1 in range(0, lvl1_max):
                lvl1_item = lvl0_item.child(lvl1)
                # add device information
                value_name = lvl1_item.text(0)
                dev[Idf.DD_VALUES][value_name] = {}
                dev[Idf.DD_VALUES][value_name][Idf.DD_VALUES_INTERVAL] = int(lvl1_item.text(1))

                # check in blueprint for subvalues
                if Idf.DEVICE_DEFINITIONS[dev_name][Idf.DD_VALUES][value_name][
                    Idf.DD_SUBVALUES] is not None:
                    dev[Idf.DD_VALUES][value_name][Idf.DD_SUBVALUES] = {}
                    # start lvl2
                    lvl2_max = lvl1_item.childCount()
                    for lvl2 in range(0, lvl2_max):
                        lvl2_item = lvl1_item.child(lvl2)
                        lvl2_item_value = False
                        """
                        http://pyqt.sourceforge.net/Docs/PyQt4/qt.html#CheckState-enum
                        Qt.Unchecked	    0	The item is unchecked.
                        Qt.PartiallyChecked	1	The item is partially checked. Items in hierarchical models may be partially checked if some, but not all, of their children are checked.
                        Qt.Checked	        2	The item is checked.
                        """
                        if lvl2_item.checkState(1) >= 1:
                            lvl2_item_value = True
                        dev[Idf.DD_VALUES][value_name][Idf.DD_SUBVALUES][
                            lvl2_item.text(0)] = lvl2_item_value

            devices.append(dev)
        return devices

    def get_simple_blueprint(setup_dialog):
        """
        Returns a very simple bluepirnt version of the current 
        devices in the tree_widget. Is used for the DeviceDialog.
        This blueprint only contains the name and uid of a device.
        """
        simple_blueprint = []

        tree_widget = setup_dialog.tree_devices

        r0_max = tree_widget.topLevelItemCount()

        for r0 in range(0, r0_max):
            item = {}

            tw_root = tree_widget.topLevelItem(r0)
            item[tw_root.text(0)] = tw_root.text(1)

            simple_blueprint.append(item)

        return simple_blueprint

    def get_device_blueprint(device_name):
        """
        Returns a single blueprint for a given device_name.
        Used to add a device from the DeviceDialog.
        """
        dev = None
        try:
            import copy

            dev = copy.deepcopy(Idf.DEVICE_DEFINITIONS[device_name])
            # delet class & getter
            del dev[Idf.DD_CLASS]
            for val in dev[Idf.DD_VALUES]:
                del dev[Idf.DD_VALUES][val][Idf.DD_GETTER]
                # add interval
                dev[Idf.DD_VALUES][val][Idf.DD_VALUES_INTERVAL] = 0

                # set default values
                if dev[Idf.DD_VALUES][val][Idf.DD_SUBVALUES] is not None:

                    sub_values = dev[Idf.DD_VALUES][val][Idf.DD_SUBVALUES]
                    dev[Idf.DD_VALUES][val][Idf.DD_SUBVALUES] = {}
                    for i in range(0, len(sub_values)):
                        sub_val = sub_values[i]
                        # check for multi lists
                        if type(sub_val) == list:
                            for j in range(0, len(sub_val)):
                                sub_sub_val = sub_val[j]
                                dev[Idf.DD_VALUES][val][Idf.DD_SUBVALUES][
                                    sub_sub_val] = True
                        else:
                            dev[Idf.DD_VALUES][val][Idf.DD_SUBVALUES][sub_val] = True

            # add name & uid
            dev[Idf.DD_NAME] = device_name
            dev[Idf.DD_UID] = "Enter UID"

        except Exception:
            pass
            # its expected to fail some times
            # EventLogger.debug("Error in get_device_blueprint("+str(device_name)+"): " + str(e))

        return dev

    load_devices = staticmethod(load_devices)
    # clear_blueprint = staticmethod(clear_blueprint)
    create_device_blueprint = staticmethod(create_device_blueprint)
    create_config_file = staticmethod(create_config_file)
    create_general_section = staticmethod(create_general_section)
    get_simple_blueprint = staticmethod(get_simple_blueprint)
    get_device_blueprint = staticmethod(get_device_blueprint)
    create_device_section = staticmethod(create_device_section)

    
