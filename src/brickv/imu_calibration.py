# -*- coding: utf-8 -*-
"""
brickv (Brick Viewer)
Copyright (C) 2012 Olaf Lüke <olaf@tinkerforge.com>

imu_calibration.py: IMU Calibration parser

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

IMU_CALIBRATION_URL = 'http://download.tinkerforge.com/imu_calibration/'

def parse_imu_calibration(text):
    values = []
    for line in text.split('\n'):
        if not line.startswith('#'):
            x = line.split(':')
            if len(x) != 2:
                continue

            y = x[1].split(',')

            if x[0] in ('0', '2', '4'):
                a = y[0].split('/')
                b = y[1].split('/')
                c = y[2].split('/')
                values.append([int(x[0]), [int(a[0]), int(b[0]), int(c[0]), int(a[1]), int(b[1]), int(c[1]), 0, 0, 0, 0]])
            elif x[0] in ('1', '3'):
                values.append([int(x[0]), [int(y[0]), int(y[1]), int(y[2]), 0, 0, 0, 0, 0, 0, 0]])
            elif x[0] in ('5',):
                values.append([int(x[0]), [int(y[0]), int(y[1]), int(y[2]), int(y[3]), int(y[4]), int(y[5]), int(y[6]), int(y[7]), 0, 0]])

    return values
