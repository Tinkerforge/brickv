# -*- coding: utf-8 -*-
"""
IMU 2.0 Plugin
Copyright (C) 2020 Olaf Lüke <olaf@tinkerforge.com>

imu_v3_3d_widget.py: IMU 3.0 OpenGL representation

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

import os

from PyQt5.QtGui import QQuaternion

from brickv.utils import get_resources_path
from brickv.render_widget import RenderWidget

class IMUV33DWidget(RenderWidget):
    def __init__(self, parent=None):
        super().__init__(get_resources_path(os.path.join('plugin_system', 'plugins', 'imu_v3', 'imu_v3.obj')), parent)

        self.save_orientation_flag = False
        self.has_save_orientation = False

        self.reference_orientation = QQuaternion()
        self.rotation = QQuaternion()

    def save_orientation(self):
        self.save_orientation_flag = True

    def get_state(self):
        return self.save_orientation_flag, self.reference_orientation, self.has_save_orientation

    def set_state(self, tup):
        self.save_orientation_flag, self.reference_orientation, self.has_save_orientation = tup

    def get_model_matrix(self):
        result = super().get_model_matrix()
        result.rotate(self.rotation)
        return result

    def update_orientation(self, w, x, y, z):
        if self.save_orientation_flag:
            self.reference_orientation = QQuaternion(w, x, y, z)
            self.save_orientation_flag = False
            self.has_save_orientation = True

        if not self.has_save_orientation:
            return

        self.rotation = self.reference_orientation.conjugate() * QQuaternion(w, x, y, z)
        super().update()
