# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014 Ishraq Ibne Ashraf <ishraq@tinkerforge.com>

red_tab_settings_ap_dhcp_leases_dialog.py: RED settings access point DHCP leases dialog implementation

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

from PyQt4 import QtCore, QtGui
from brickv.plugin_system.plugins.red.ui_red_tab_settings_ap_dhcp_leases_dialog import Ui_REDTabSettingsAPDhcpLeasesDialog
from brickv.plugin_system.plugins.red.api import *
from brickv.async_call import async_call
from brickv.utils import get_main_window

DNSMASQ_LEASES_FILE = '/var/lib/misc/dnsmasq.leases'

DEFAULT_TVIEW_HOST_NAME_HEADER_WIDTH  = 300 # in pixels
DEFAULT_TVIEW_MAC_HEADER_WIDTH        = 130 # in pixels
DEFAULT_TVIEW_IP_HEADER_WIDTH         = 130 # in pixels
DEFAULT_TVIEW_EXPIRATION_HEADER_WIDTH = 150 # in pixels

class REDTabSettingsAPDhcpLeasesDialog(QtGui.QDialog, Ui_REDTabSettingsAPDhcpLeasesDialog):
    def __init__(self, parent, session):
        QtGui.QDialog.__init__(self, parent)

        self.setupUi(self)

        self.session = session

        self.slot_pbutton_ap_leases_refresh_clicked()

        self.pbutton_ap_leases_refresh.clicked.connect(self.slot_pbutton_ap_leases_refresh_clicked)
        self.pbutton_ap_leases_close.clicked.connect(self.slot_pbutton_ap_leases_close_clicked)

    def slot_pbutton_ap_leases_refresh_clicked(self):
        def cb_open_dnsmasq_leases(red_file):
            def cb_read(red_file, result):
                self.pbutton_ap_leases_refresh.setText('Refresh')
                self.pbutton_ap_leases_refresh.setEnabled(True)

                red_file.release()

                if result and result.data and not result.error:
                    self.tview_ap_leases.setEnabled(True)

                    leases_content = unicode(result.data)
                    leases_lines = leases_content.splitlines()

                    leases_model = QtGui.QStandardItemModel(0, 3, self)
                    leases_model.setHorizontalHeaderItem(0, QtGui.QStandardItem("Hostname"))
                    leases_model.setHorizontalHeaderItem(1, QtGui.QStandardItem("MAC"))
                    leases_model.setHorizontalHeaderItem(2, QtGui.QStandardItem("IP"))
                    leases_model.setHorizontalHeaderItem(3, QtGui.QStandardItem("Expiration"))

                    for i, l in enumerate(leases_lines):
                        l_split = l.strip().split(' ')
                        if len(l_split) != 5:
                            continue
                
                        for j in range(0, len(l_split)):
                            if j == 4:
                                continue
                
                            if j == 0:
                                leases_model.setItem(i, 3, QtGui.QStandardItem(QtCore.QDateTime.fromTime_t(int(l_split[j])).toString('yyyy-MM-dd HH:mm:ss')))
                            elif j == 3:
                                leases_model.setItem(i, 0, QtGui.QStandardItem(l_split[j]))
                            else:
                                leases_model.setItem(i, j, QtGui.QStandardItem(l_split[j]))

                    self.tview_ap_leases.setModel(leases_model)

                    self.tview_ap_leases.setColumnWidth(0, DEFAULT_TVIEW_HOST_NAME_HEADER_WIDTH)
                    self.tview_ap_leases.setColumnWidth(1, DEFAULT_TVIEW_MAC_HEADER_WIDTH)
                    self.tview_ap_leases.setColumnWidth(2, DEFAULT_TVIEW_IP_HEADER_WIDTH)
                    self.tview_ap_leases.setColumnWidth(3, DEFAULT_TVIEW_EXPIRATION_HEADER_WIDTH)
                else:
                    self.pbutton_ap_leases_refresh.setText('Refresh')
                    self.pbutton_ap_leases_refresh.setEnabled(True)
                    err_msg = 'Error reading dnsmasq leases file\n\n'+result.error
                    QtGui.QMessageBox.critical(get_main_window(),
                                               'Settings | Access Point',
                                               err_msg,
                                               QtGui.QMessageBox.Ok)

            red_file.read_async(4096, lambda x: cb_read(red_file, x))

        def cb_open_error_dnsmasq_leases():
            self.pbutton_ap_leases_refresh.setText('Refresh')
            self.pbutton_ap_leases_refresh.setEnabled(True)
            err_msg = 'Error opening dnsmasq leases file'
            QtGui.QMessageBox.critical(get_main_window(),
                                       'Settings | Access Point',
                                       err_msg,
                                       QtGui.QMessageBox.Ok)

        self.pbutton_ap_leases_refresh.setText('Refreshing...')
        self.pbutton_ap_leases_refresh.setEnabled(False)

        dnsmasq_leases_rfile = REDFile(self.session)
        async_call(dnsmasq_leases_rfile.open,
                   (DNSMASQ_LEASES_FILE, REDFile.FLAG_READ_ONLY | REDFile.FLAG_NON_BLOCKING, 0, 0, 0),
                   cb_open_dnsmasq_leases,
                   cb_open_error_dnsmasq_leases)

    def slot_pbutton_ap_leases_close_clicked(self):
        self.done(0)
