# -*- coding: utf-8 -*-
"""
IMU Plugin
Copyright (C) 2015 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2015 Matthias Bolte <matthias@tinkerforge.com>
Copyright (C) 2019 Erik Fleckstein <erik@tinkerforge.com>

imu_3d_widget.py: IMU OpenGL representation

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

import sys
import ctypes
import ctypes.util
import math
import array
import os

from PyQt5.QtGui import QMatrix4x4, QQuaternion

from brickv.utils import get_resources_path
from brickv.render_widget import RenderWidget

class IMU3DWidget(RenderWidget):
    def __init__(self, parent=None):
        super().__init__(get_resources_path(os.path.join('plugin_system', 'plugins', 'imu', 'imu.obj')), parent)

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
