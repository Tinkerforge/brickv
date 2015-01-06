# -*- coding: utf-8 -*-
"""
Master Plugin
Copyright (C) 2010-2012 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2012-2014 Matthias Bolte <matthias@tinkerforge.com>

wifi_status.py: WifiStatus for Master Plugin implementation

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

from PyQt4.QtGui import QFrame
from PyQt4.QtCore import Qt

from brickv.plugin_system.plugins.master.ui_wifi_status import Ui_wifi_status
from brickv.async_call import async_call

class WifiStatus(QFrame, Ui_wifi_status):
    def __init__(self, parent):
        QFrame.__init__(self, parent, Qt.Popup | Qt.Window | Qt.Tool)

        self.setupUi(self)

        self.parent = parent
        self.master = self.parent.master

        self.button_close.clicked.connect(self.close)

        self.update_status()

    def update_status_async(self, status):
        mac, bssid, channel, rssi, ip, sub, gw, rx, tx, state = status

        self.wifi_status_mac.setText("%2.2x:%2.2x:%2.2x:%2.2x:%2.2x:%2.2x" % mac[::-1])
        self.wifi_status_bssid.setText("%2.2x:%2.2x:%2.2x:%2.2x:%2.2x:%2.2x" % bssid[::-1])
        self.wifi_status_channel.setText(str(channel))
        self.wifi_status_rssi.setText(str(rssi) + 'dB')
        self.wifi_status_ip.setText("%d.%d.%d.%d" % ip[::-1])
        self.wifi_status_sub.setText("%d.%d.%d.%d" % sub[::-1])
        self.wifi_status_gw.setText("%d.%d.%d.%d" % gw[::-1])
        self.wifi_status_rx.setText(str(rx))
        self.wifi_status_tx.setText(str(tx))

        state_str = "None"
        if state == 0:
            state_str = "Disassociated"
        elif state == 1:
            state_str = "Associated"
        elif state == 2:
            state_str = "Associating"
        elif state == 3:
            state_str = "Startup Error"
        elif state == 255:
            state_str = "No Startup"

        self.wifi_status_state.setText(state_str)

    def update_status(self):
        async_call(self.master.get_wifi_status, None, self.update_status_async, self.parent.parent.increase_error_count)
