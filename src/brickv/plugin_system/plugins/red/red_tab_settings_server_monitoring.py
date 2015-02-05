# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014 Ishraq Ibne Ashraf <ishraq@tinkerforge.com>

red_tab_settings_server_monitoring.py: RED settings server monitoring tab implementation

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

import json
from PyQt4 import QtCore, QtGui
from brickv.plugin_system.plugins.red.ui_red_tab_settings_server_monitoring import Ui_REDTabSettingsServerMonitoring
from brickv.plugin_system.plugins.red.api import *
from brickv.plugin_system.plugins.red.program_utils import TextFile
from brickv.async_call import async_call
from brickv.utils import get_main_window
from brickv.plugin_system.plugins.red.widget_spinbox_span_slider import widgetSpinBoxSpanSlider

class REDTabSettingsServerMonitoring(QtGui.QWidget, Ui_REDTabSettingsServerMonitoring):
    def __init__(self):
        QtGui.QWidget.__init__(self)

        self.setupUi(self)

        self.session        = None # Set from REDTabSettings
        self.script_manager = None # Set from REDTabSettings
        self.image_version  = None # Set from REDTabSettings
        self.service_state  = None # Set from REDTabSettings

        self.is_tab_on_focus = False
        
        self.label_unsupported.hide()
        self.label_disabled.hide()
        self.label_working_wait.hide()
        self.pbar_working_wait.hide()
        self.sarea_sm.hide()

        self.model = QtGui.QStandardItemModel()
        headerRow = []
        headerRow.append('Bricklet')
        headerRow.append('UID')
        headerRow.append('Mode')
        headerRow.append('Warning')
        headerRow.append('Critical')
        headerRow.append('Email')
        headerRow.append('Remove')
        self.model.setHorizontalHeaderLabels(headerRow)

        row = []
        row.append(QtGui.QStandardItem(''))
        row.append(QtGui.QStandardItem(''))
        row.append(QtGui.QStandardItem(''))
        row.append(QtGui.QStandardItem(''))
        row.append(QtGui.QStandardItem(''))
        row.append(QtGui.QStandardItem(''))
        row.append(QtGui.QStandardItem(''))
        self.model.appendRow(row)
        self.treeView.setModel(self.model)

        for i in range(self.model.rowCount()):
            for j in range(0, 7):
                if j == 0 or j == 1 or j == 2 or j == 5:
                    item = self.model.item(i, j)
                    index = self.model.indexFromItem(item)
                    self.treeView.setIndexWidget(index, QtGui.QComboBox())
                elif j == 3 or j == 4:
                    item = self.model.item(i, j)
                    index = self.model.indexFromItem(item)
                    sss = widgetSpinBoxSpanSlider(self.treeView)
                    sss.span_slider.setLowerValue(10)
                    sss.sbox_lower.setValue(10)
                    sss.span_slider.setUpperValue(30)
                    sss.sbox_upper.setValue(30)
                    self.treeView.setIndexWidget(index, sss)
                elif j == 6:
                    item = self.model.item(i, j)
                    index = self.model.indexFromItem(item)
                    self.treeView.setIndexWidget(index, QtGui.QPushButton('X'))

    def tab_on_focus(self):
        self.is_tab_on_focus = True

        if self.image_version.number < (1, 6):
            self.label_unsupported.show()
        elif not self.service_state.servermonitoring:
            self.label_disabled.show()
        else:
            self.sarea_sm.show()

    def tab_off_focus(self):
        self.is_tab_on_focus = False

    def tab_destroy(self):
        pass
