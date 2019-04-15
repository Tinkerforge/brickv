# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2015 Ishraq Ibne Ashraf <ishraq@tinkerforge.com>
Copyright (C) 2015 Matthias Bolte <matthias@tinkerforge.com>

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

from PyQt5.QtCore import QDateTime
from PyQt5.QtWidgets import QMessageBox, QDialog
from PyQt5.QtGui import QStandardItemModel, QStandardItem

from brickv.plugin_system.plugins.red.ui_red_tab_settings_ap_dhcp_leases_dialog import Ui_REDTabSettingsAPDhcpLeasesDialog
from brickv.plugin_system.plugins.red.api import *
from brickv.plugin_system.plugins.red.program_utils import TextFile
from brickv.async_call import async_call
from brickv.utils import get_main_window

DNSMASQ_LEASES_FILE = '/var/lib/misc/dnsmasq.leases'

DEFAULT_TVIEW_HOST_NAME_HEADER_WIDTH  = 300 # in pixels
DEFAULT_TVIEW_MAC_HEADER_WIDTH        = 130 # in pixels
DEFAULT_TVIEW_IP_HEADER_WIDTH         = 130 # in pixels
DEFAULT_TVIEW_EXPIRATION_HEADER_WIDTH = 150 # in pixels

class REDTabSettingsAPDhcpLeasesDialog(QDialog, Ui_REDTabSettingsAPDhcpLeasesDialog):
    def __init__(self, parent, session):
        QDialog.__init__(self, parent)

        self.setupUi(self)

        self.session = session

        self.slot_pbutton_ap_leases_refresh_clicked()

        self.pbutton_ap_leases_refresh.clicked.connect(self.slot_pbutton_ap_leases_refresh_clicked)
        self.pbutton_ap_leases_close.clicked.connect(self.slot_pbutton_ap_leases_close_clicked)

    def slot_pbutton_ap_leases_refresh_clicked(self):
        def cb_dnsmasq_leases_content(content):
            self.pbutton_ap_leases_refresh.setText('Refresh')
            self.pbutton_ap_leases_refresh.setEnabled(True)

            self.tview_ap_leases.setEnabled(True)

            leases_lines = content.splitlines()

            leases_model = QStandardItemModel(0, 3, self)
            leases_model.setHorizontalHeaderItem(0, QStandardItem("Hostname"))
            leases_model.setHorizontalHeaderItem(1, QStandardItem("MAC"))
            leases_model.setHorizontalHeaderItem(2, QStandardItem("IP"))
            leases_model.setHorizontalHeaderItem(3, QStandardItem("Expiration"))

            for i, l in enumerate(leases_lines):
                l_split = l.strip().split(' ')
                if len(l_split) != 5:
                    continue

                for j in range(0, len(l_split)):
                    if j == 4:
                        continue

                    if j == 0:
                        #FIXME: fromTime_t is obsolete: https://doc.qt.io/qt-5/qdatetime-obsolete.html#toTime_t
                        leases_model.setItem(i, 3, QStandardItem(QDateTime.fromTime_t(int(l_split[j])).toString('yyyy-MM-dd HH:mm:ss')))
                    elif j == 3:
                        leases_model.setItem(i, 0, QStandardItem(l_split[j]))
                    else:
                        leases_model.setItem(i, j, QStandardItem(l_split[j]))

            self.tview_ap_leases.setModel(leases_model)

            self.tview_ap_leases.setColumnWidth(0, DEFAULT_TVIEW_HOST_NAME_HEADER_WIDTH)
            self.tview_ap_leases.setColumnWidth(1, DEFAULT_TVIEW_MAC_HEADER_WIDTH)
            self.tview_ap_leases.setColumnWidth(2, DEFAULT_TVIEW_IP_HEADER_WIDTH)
            self.tview_ap_leases.setColumnWidth(3, DEFAULT_TVIEW_EXPIRATION_HEADER_WIDTH)

        def cb_dnsmasq_leases_error(kind, error):
            self.pbutton_ap_leases_refresh.setText('Refresh')
            self.pbutton_ap_leases_refresh.setEnabled(True)

            kind_text = {
                TextFile.ERROR_KIND_OPEN: 'opening',
                TextFile.ERROR_KIND_READ: 'reading',
                TextFile.ERROR_KIND_UTF8: 'decoding'
            }

            QMessageBox.critical(get_main_window(),
                                 'Settings | Access Point',
                                 'Error {0} dnsmasq leases file:\n\n{1}'.format(kind_text[kind], error))

        self.pbutton_ap_leases_refresh.setText('Refreshing...')
        self.pbutton_ap_leases_refresh.setEnabled(False)

        TextFile.read_async(self.session, DNSMASQ_LEASES_FILE,
                            cb_dnsmasq_leases_content, cb_dnsmasq_leases_error)

    def slot_pbutton_ap_leases_close_clicked(self):
        self.done(0)
