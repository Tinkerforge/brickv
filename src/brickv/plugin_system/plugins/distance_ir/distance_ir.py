# -*- coding: utf-8 -*-
"""
Distance IR Plugin
Copyright (C) 2011-2012 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2014-2016 Matthias Bolte <matthias@tinkerforge.com>

distance_ir.py: Distance IR Plugin Implementation

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

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QVBoxLayout, QHBoxLayout, QLabel, QPushButton, \
                        QLineEdit, QApplication, QMessageBox, QFrame

from brickv.plugin_system.plugin_base import PluginBase
from brickv.bindings import ip_connection
from brickv.bindings.bricklet_distance_ir import BrickletDistanceIR
from brickv.plot_widget import PlotWidget, FixedSizeLabel
from brickv.async_call import async_call
from brickv.callback_emulator import CallbackEmulator
from brickv.utils import get_main_window, get_home_path, get_open_file_name

# this class is directly based on the QwtSpline class from the Qwt library
class NaturalSpline(object):
    def __init__(self):
        self.points = []
        self.a = []
        self.b = []
        self.c = []

    def set_points(self, points):
        length = len(points)

        if length < 3:
            return False

        a = [0.0] * (length - 1)
        b = [0.0] * (length - 1)
        c = [0.0] * (length - 1)
        h = [0.0] * (length - 1)

        for i in range(length - 1):
            h[i] = points[i + 1][0] - points[i][0]

            if h[i] <= 0:
                return False

        d = [0.0] * (length - 1)
        dy1 = (points[1][1] - points[0][1]) / h[0]

        for i in range(1, length - 1):
            c[i] = h[i]
            b[i] = h[i]
            a[i] = 2.0 * (h[i - 1] + h[i])
            dy2 = (points[i + 1][1] - points[i][1]) / h[i]
            d[i] = 6.0 * (dy1 - dy2)
            dy1 = dy2

        for i in range(1, length - 2):
            c[i] /= a[i]
            a[i + 1] -= b[i] * c[i]

        s = [0.0] * length
        s[1] = d[1]

        for i in range(2, length - 1):
            s[i] = d[i] - c[i - 1] * s[i - 1]

        s[length - 2] = -s[length - 2] / a[length - 2]

        for i in reversed(range(1, length - 2)):
            s[i] = - ( s[i] + b[i] * s[i+1] ) / a[i]

        s[length - 1] = s[0] = 0.0

        for i in range(length - 1):
            a[i] = (s[i+1] - s[i]) / (6.0 * h[i])
            b[i] = 0.5 * s[i]
            c[i] = (points[i+1][1] - points[i][1]) / h[i] - (s[i + 1] + 2.0 * s[i]) * h[i] / 6.0

        self.points = points
        self.a = a
        self.b = b
        self.c = c

        return True

    def get_index(self, x):
        points = self.points
        length = len(points)

        if x <= points[0][0]:
            i1 = 0
        elif x >= points[length - 2][0]:
            i1 = length - 2
        else:
            i1 = 0
            i2 = length - 2
            i3 = 0

            while i2 - i1 > 1:
                i3 = i1 + ((i2 - i1) >> 1)

                if points[i3][0] > x:
                    i2 = i3
                else:
                    i1 = i3

        return i1

    def get_value(self, x):
        if len(self.a) == 0:
            return 0.0

        i = self.get_index(x)
        delta = x - self.points[i][0]

        return (((self.a[i] * delta) + self.b[i]) * delta + self.c[i]) * delta + self.points[i][1]

class AnalogLabel(FixedSizeLabel):
    def setText(self, text):
        text = "Analog Value: " + str(text)
        super(AnalogLabel, self).setText(text)

class DistanceIR(PluginBase):
    NUM_VALUES = 128
    DIVIDER = 2**12/NUM_VALUES

    def __init__(self, *args):
        PluginBase.__init__(self, BrickletDistanceIR, *args)

        self.dist = self.device

        self.cbe_distance = CallbackEmulator(self.dist.get_distance,
                                             self.cb_distance,
                                             self.increase_error_count)
        self.cbe_analog_value = CallbackEmulator(self.dist.get_analog_value,
                                                 self.cb_analog_value,
                                                 self.increase_error_count)

        self.analog_label = AnalogLabel('Analog Value: ')
        hlayout = QHBoxLayout()
        self.sample_label = QLabel('Sample Points:')
        self.sample_edit = QLineEdit()
        self.sample_file = QPushButton("Browse")
        self.sample_save = QPushButton("Save")

        self.sample_file.clicked.connect(self.sample_file_clicked)
        self.sample_save.clicked.connect(self.sample_save_clicked)

        hlayout.addWidget(self.sample_label)
        hlayout.addWidget(self.sample_edit)
        hlayout.addWidget(self.sample_file)
        hlayout.addWidget(self.sample_save)

        self.current_distance = None # float, cm

        plots = [('Distance', Qt.red, lambda: self.current_distance, '{} cm'.format)]
        self.plot_widget = PlotWidget('Distance [cm]', plots, extra_key_widgets=[self.analog_label])

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)

        layout = QVBoxLayout(self)
        layout.addWidget(self.plot_widget)
        layout.addWidget(line)
        layout.addLayout(hlayout)

    def start(self):
        async_call(self.dist.get_distance, None, self.cb_distance, self.increase_error_count)
        self.cbe_distance.set_period(100)
        self.cbe_analog_value.set_period(100)

        self.plot_widget.stop = False

    def stop(self):
        self.cbe_distance.set_period(0)
        self.cbe_analog_value.set_period(0)

        self.plot_widget.stop = True

    def destroy(self):
        pass

    def get_url_part(self):
        return 'distance_ir'

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletDistanceIR.DEVICE_IDENTIFIER

    def sample_file_clicked(self):
        if len(self.sample_edit.text()) > 0:
            last_dir = os.path.dirname(os.path.realpath(self.sample_edit.text()))
        else:
            last_dir = get_home_path()

        filename = get_open_file_name(get_main_window(), "Open Sample Points", last_dir)

        if len(filename) > 0:
            self.sample_edit.setText(filename)

    def sample_interpolate(self, x, y):
        spline = NaturalSpline()
        points = []

        for point in zip(x, y):
            points.append((float(point[0]), float(point[1])))

        spline.set_points(points)

        px = range(0, 2**12, DistanceIR.DIVIDER)
        py = []

        for X in px:
            py.append(spline.get_value(X))

        for i in range(x[0]/DistanceIR.DIVIDER):
            py[i] = y[0]

        for i in range(x[-1]/DistanceIR.DIVIDER, 2**12/DistanceIR.DIVIDER):
            py[i] = y[-1]

        for i in range(len(py)):
            if py[i] > y[0]:
                py[i] = y[0]
            if py[i] < y[-1]:
                py[i] = y[-1]

        try:
            old_text = self.sample_edit.text()
            for i in range(DistanceIR.NUM_VALUES):
                value = int(round(py[i]*100))
                self.dist.set_sampling_point(i, value)
                self.sample_edit.setText("Writing sample point, value: " +  str((i, value)))

                QApplication.processEvents()
            self.sample_edit.setText(old_text)
        except ip_connection.Error:
            return

    def sample_save_clicked(self):
        x = []
        y = []
        filename = self.sample_edit.text()

        with open(filename, 'rb') as f:
            for line in f:
                c = line.find('#')
                if c != -1:
                    line = line[:c]

                line = line.strip()

                if line.startswith('\xEF\xBB\xBF'): # strip UTF-8 BOM, Internet Explorer adds it to text files
                    line = line[3:]

                if len(line) == 0:
                    continue

                if ':' not in line:
                    QMessageBox.critical(get_main_window(), "Sample points",
                                         "Sample points file is malformed (error code 1)",
                                         QMessageBox.Ok)
                    return

                s = line.split(':')

                if len(s) != 2:
                    QMessageBox.critical(get_main_window(), "Sample points",
                                         "Sample points file is malformed (error code 2)",
                                         QMessageBox.Ok)
                    return

                try:
                    x.append(int(s[1]))
                    y.append(int(s[0]))
                except:
                    QMessageBox.critical(get_main_window(), "Sample points",
                                         "Sample points file is malformed (error code 3)",
                                         QMessageBox.Ok)
                    return

        self.sample_interpolate(x, y)

    def cb_distance(self, distance):
        self.current_distance = distance / 10.0

    def cb_analog_value(self, analog_value):
        self.analog_label.setText(analog_value)
