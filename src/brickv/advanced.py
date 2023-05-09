# -*- coding: utf-8 -*-
"""
brickv (Brick Viewer)
Copyright (C) 2011-2012, 2018 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2012 Bastian Nordmeyer <bastian@tinkerforge.com>
Copyright (C) 2012, 2014-2015, 2017 Matthias Bolte <matthias@tinkerforge.com>

advanced.py: GUI for advanced features

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

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog

from brickv.ui_advanced import Ui_Advanced
from brickv.utils import get_modeless_dialog_flags
from brickv.infos import inventory
from brickv.async_call import async_call

NO_BRICK = 'No Brick found'

class AdvancedWindow(QDialog, Ui_Advanced):
    def __init__(self, parent):
        QDialog.__init__(self, parent, get_modeless_dialog_flags())

        self.setupUi(self)

        self.ipcon_available = False
        self.calibration_allowed = False

        self.button_calibrate.setEnabled(False)

        self.label_msg_a.setVisible(False)
        self.label_msg_b.setVisible(False)
        self.label_msg_c.setVisible(True)

        self.brick_infos = []

        self.parent = parent
        self.button_calibrate.clicked.connect(self.calibrate_clicked)
        self.combo_brick.currentIndexChanged.connect(self.brick_changed)
        self.check_enable_calibration.stateChanged.connect(self.enable_calibration_changed)

        inventory.info_changed.connect(self.update_bricks)

        self.button_close.clicked.connect(self.hide)

        self.update_bricks()
        self.update_ui_state()

    def reject(self):
        pass # avoid closing using ESC key

    def closeEvent(self, event):
        pass # dont touch event to avoid closing using ESC key

    def update_bricks(self):
        self.brick_infos = []
        self.combo_brick.clear()

        for info in inventory.get_brick_infos():
            self.brick_infos.append(info)
            self.combo_brick.addItem(info.get_combo_item())

        if self.combo_brick.count() == 0:
            self.combo_brick.addItem(NO_BRICK)

        self.update_calibration()
        self.update_ui_state()

    def calibrate_clicked(self):
        port_names = ['a', 'b', 'c', 'd']

        self.parent.ipcon.adc_calibrate(self.current_device(),
                                        port_names[self.combo_port.currentIndex()])

        self.update_calibration()

    def current_device(self):
        try:
            return self.brick_infos[self.combo_brick.currentIndex()].plugin.device
        except IndexError:
            return None

    def allow_calibration(self, allow, offset='-', gain='-'):
        self.calibration_allowed = allow

        self.label_msg_a.setVisible(allow and self.combo_port.count() > 0)
        self.label_msg_b.setVisible(not allow and self.combo_port.count() > 0)
        self.label_msg_c.setVisible(False)

        if not allow:
            self.check_enable_calibration.setChecked(False)

        self.label_offset.setText(offset)
        self.label_gain.setText(gain)

        self.update_ui_state()

    def get_adc_calibration_async(self, device, offset, gain):
        if device != self.current_device():
            return

        self.allow_calibration(True, offset=str(offset), gain=str(gain))

    def update_calibration(self):
        self.label_msg_a.setVisible(False)
        self.label_msg_b.setVisible(False)
        self.label_msg_c.setVisible(True)

        device = self.current_device()

        if device is None or self.combo_port.count() == 0:
            self.allow_calibration(False)
        else:
            async_call(self.parent.ipcon.get_adc_calibration, device, self.get_adc_calibration_async, lambda: self.allow_calibration(False),
                       pass_arguments_to_result_callback=True, expand_result_tuple_for_callback=True)

    def brick_changed(self, index):
        self.combo_port.clear()

        if index < 0 or index >= len(self.brick_infos):
            return

        info = self.brick_infos[index]

        for key in info.bricklet_ports:
            if not key in info.connections_keys() or info.connections_get(key)[0].kind != 'bricklet':
                self.combo_port.addItem(key.upper())
            else:
                self.combo_port.addItem('{0}: {1}'.format(key.upper(), info.connections_get(key)[0].get_combo_item()))

        self.update_ui_state()
        self.update_calibration()

        if self.combo_port.count() == 0:
            self.check_enable_calibration.setChecked(False)

    def enable_calibration_changed(self, state):
        self.button_calibrate.setEnabled(state == Qt.Checked)

    def update_ui_state(self):
        enabled = len(self.brick_infos) > 0

        self.combo_brick.setEnabled(enabled and self.ipcon_available)
        self.combo_port.setEnabled(enabled and self.ipcon_available)
        self.check_enable_calibration.setEnabled(enabled and self.ipcon_available and self.combo_port.count() > 0 and self.calibration_allowed)
        self.button_calibrate.setEnabled(enabled and self.ipcon_available and self.combo_port.count() > 0 and self.check_enable_calibration.isChecked())

    def set_ipcon_available(self, ipcon_available):
        self.ipcon_available = ipcon_available

        self.update_ui_state()
