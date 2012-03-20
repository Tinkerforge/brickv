# -*- coding: utf-8 -*-  
"""
IMU Plugin
Copyright (C) 2010-2012 Olaf Lüke <olaf@tinkerforge.com>

imu.py: IMU Plugin implementation

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

#import logging

from plugin_system.plugin_base import PluginBase
from calibrate_window import CalibrateWindow
import ip_connection

from PyQt4.QtGui import QLabel, QVBoxLayout
from PyQt4.QtCore import Qt, QTimer
import PyQt4.Qwt5 as Qwt

from ui_imu import Ui_IMU

import brick_imu

class Plot(Qwt.QwtPlot):
    def __init__(self, y_axis, plot_list, *args):
        Qwt.QwtPlot.__init__(self, *args)
        
        self.setAxisTitle(Qwt.QwtPlot.xBottom, "Time [s]")
        self.setAxisTitle(Qwt.QwtPlot.yLeft, y_axis)
        
        legend = Qwt.QwtLegend()
        legend.setItemMode(Qwt.QwtLegend.CheckableItem)
        self.insertLegend(legend, Qwt.QwtPlot.RightLegend)
        
        self.setAutoReplot(True)
        
        self.curve = []
        
        self.data_x = []
        self.data_y = []
        
        for x in plot_list:
            c = Qwt.QwtPlotCurve(x[0])
            self.curve.append(c)
            self.data_x.append([])
            self.data_y.append([])
        
            c.attach(self)
            c.setPen(x[1])
            self.show_curve(c, True)
        
        self.legendChecked.connect(self.show_curve)
        
        
    def show_curve(self, item, on):
        item.setVisible(on)
        widget = self.legend().find(item)
        if isinstance(widget, Qwt.QwtLegendItem):
            widget.setChecked(on)
        self.replot()
           

    def add_data(self, i, data_x, data_y):
        self.data_x[i].append(data_x)
        self.data_y[i].append(data_y)
        if len(self.data_x[i]) == 600: # 300 = 5 minutes
            self.data_x[i] = self.data_x[i][10:]
            self.data_y[i] = self.data_y[i][10:]
        
        self.curve[i].setData(self.data_x[i], self.data_y[i])
        
    def clear_graph(self):
        for i in range(len(self.data_x)):
            self.data_x[i] = []
            self.data_y[i] = []

class IMU(PluginBase, Ui_IMU):
    def __init__ (self, ipcon, uid):
        PluginBase.__init__(self, ipcon, uid)
        self.setupUi(self)
        
        self.imu = brick_imu.IMU(self.uid)
        self.device = self.imu
        self.ipcon.add_device(self.imu)
        self.version = '.'.join(map(str, self.imu.get_version()[1]))
        
        self.acc_x = 0
        self.acc_y = 0
        self.acc_z = 0
        self.mag_x = 0
        self.mag_y = 0
        self.mag_z = 0
        self.gyr_x = 0
        self.gyr_y = 0
        self.gyr_z = 0
        self.tem   = 0
        self.roll  = 0
        self.pitch = 0
        self.yaw   = 0
        self.qua_x = 0
        self.qua_y = 0
        self.qua_z = 0
        self.qua_w = 0
        
        self.old_time = 0
        
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_data)
        
        self.imu.register_callback(self.imu.CALLBACK_ALL_DATA, 
                                   self.all_data_callback)
        self.imu.register_callback(self.imu.CALLBACK_ORIENTATION,
                                   self.orientation_callback)
        self.imu.register_callback(self.imu.CALLBACK_QUATERNION,
                                   self.quaternion_callback)
        
        # Import IMUGLWidget here, not global. If globally included we get
        # 'No OpenGL_accelerate module loaded: No module named OpenGL_accelerate'
        # as soon as IMU is set as device_class in __init__. 
        # No idea why this happens, doesn't make sense.
        from imu_gl_widget import IMUGLWidget
        
        self.imu_gl = IMUGLWidget(self)
        self.imu_gl.setMinimumSize(200, 200)
        self.min_x = 0
        self.min_y = 0
        self.min_z = 0
        self.max_x = 0 
        self.max_y = 0
        self.max_z = 0
        
        self.counter = 0
        
        self.mag_plot = Plot("Magnetic Field [mG]",
                             [["X", Qt.red],
                              ["Y", Qt.green],
                              ["Z", Qt.blue]])
        self.acc_plot = Plot("Acceleration [mG]",
                             [["X", Qt.red],
                              ["Y", Qt.green],
                              ["Z", Qt.blue]])
        self.gyr_plot = Plot("Angular Velocity [%c/s]" % 0xB0,
                             [["X", Qt.red],
                              ["Y", Qt.green],
                              ["Z", Qt.blue]])
        
        self.tem_plot = Plot("Temperature [%cC]" % 0xB0,
                             [["t", Qt.red]])
        
        
        self.orientation_label = QLabel("""Position your IMU Brick as shown \
in the image above, then press "Save Orientation".""")
        self.orientation_label.setWordWrap(True)
        self.orientation_label.setAlignment(Qt.AlignHCenter)
        self.gl_layout = QVBoxLayout()
        self.gl_layout.addWidget(self.imu_gl)
        self.gl_layout.addWidget(self.orientation_label)
        
        self.grid_layout.addWidget(self.gyr_plot, 0, 0)
        self.grid_layout.addWidget(self.acc_plot, 0, 2)
        self.grid_layout.addWidget(self.mag_plot, 0, 4)
        self.grid_layout.addLayout(self.gl_layout, 2, 2)
        self.grid_layout.addWidget(self.tem_plot, 2, 4)
        
        self.save_orientation.clicked.connect(self.imu_gl.save_orientation)
        self.clear_graphs.clicked.connect(self.clear_graphs_clicked)
        self.calibrate.clicked.connect(self.calibrate_pressed)
        self.led_button.clicked.connect(self.led_clicked)
        self.speed_spinbox.editingFinished.connect(self.speed_finished)
        
    def start(self):
        self.gl_layout.activate()
        self.imu.set_all_data_period(100)
        self.imu.set_orientation_period(100)
        self.imu.set_quaternion_period(50)
        self.update_timer.start(50)
        
        speed = self.imu.get_convergence_speed()
        self.speed_spinbox.setValue(speed)
        # self.orientation_label.setText("")
        #self.gl_layout.removeWidget(self..orientation_label)
        #self.orientation_label.destroy()

        #self.orientation_label.setFixedHeight()
    def stop(self):
        self.update_timer.stop()
        self.imu.set_all_data_period(0)
        self.imu.set_orientation_period(0)
        self.imu.set_quaternion_period(0)
        
    @staticmethod
    def has_name(name):
        return 'IMU Brick' in name 
        
    def all_data_callback(self, acc_x, acc_y, acc_z, mag_x, mag_y, mag_z, gyr_x, gyr_y, gyr_z, tem):
        self.acc_x = acc_x
        self.acc_y = acc_y
        self.acc_z = acc_z
        self.mag_x = mag_x
        self.mag_y = mag_y
        self.mag_z = mag_z
        self.gyr_x = gyr_x
        self.gyr_y = gyr_y
        self.gyr_z = gyr_z
        self.tem = tem
        
    def quaternion_callback(self, qua_x, qua_y, qua_z, qua_w):
        self.qua_x = qua_x
        self.qua_y = qua_y
        self.qua_z = qua_z
        self.qua_w = qua_w
        
    def orientation_callback(self, roll, pitch, yaw):
        self.roll = roll
        self.pitch = pitch
        self.yaw = yaw
        
    def clear_graphs_clicked(self):
        self.counter = 0
        self.mag_plot.clear_graph()
        self.acc_plot.clear_graph()
        self.gyr_plot.clear_graph()
        self.tem_plot.clear_graph()
        
    def led_clicked(self):
        if 'On' in self.led_button.text():
            self.led_button.setText('Turn LEDs Off')
            self.imu.leds_on()
        elif 'Off' in self.led_button.text():
            self.led_button.setText('Turn LEDs On')
            self.imu.leds_off()
        
    def update_data(self):
        gyr_x = self.gyr_x/14.375
        gyr_y = self.gyr_y/14.375
        gyr_z = self.gyr_z/14.375
        
        self.acceleration_update(self.acc_x, self.acc_y, self.acc_z)
        self.magnetometer_update(self.mag_x, self.mag_y, self.mag_z)
        self.gyroscope_update(gyr_x, gyr_y, gyr_z)
        self.orientation_update(self.roll, self.pitch, self.yaw)
        self.temperature_update(self.tem)
        
        self.imu_gl.update(self.qua_x, self.qua_y, self.qua_z, self.qua_w)
        
        
        self.gyr_plot.add_data(0, self.counter, gyr_x)
        self.gyr_plot.add_data(1, self.counter, gyr_y)
        self.gyr_plot.add_data(2, self.counter, gyr_z)
        
        self.acc_plot.add_data(0, self.counter, self.acc_x)
        self.acc_plot.add_data(1, self.counter, self.acc_y)
        self.acc_plot.add_data(2, self.counter, self.acc_z)
        
        self.mag_plot.add_data(0, self.counter, self.mag_x)
        self.mag_plot.add_data(1, self.counter, self.mag_y)
        self.mag_plot.add_data(2, self.counter, self.mag_z)
        
        self.tem_plot.add_data(0, self.counter, self.tem/100.0)
        
        self.counter += 0.1
        
    def acceleration_update(self, x, y, z):
        x_str = "%g" % x
        y_str = "%g" % y
        z_str = "%g" % z
        self.acc_y_label.setText(y_str)
        self.acc_x_label.setText(x_str)
        self.acc_z_label.setText(z_str)
        
    def magnetometer_update(self, x, y, z):
        # Earth magnetic field. 0.5 Gauss
        x_str = "%g" % x
        y_str = "%g" % y
        z_str = "%g" % z
        self.mag_x_label.setText(x_str)
        self.mag_y_label.setText(y_str)
        self.mag_z_label.setText(z_str)
        
    def gyroscope_update(self, x, y, z):
        x_str = "%g" % int(x)
        y_str = "%g" % int(y)
        z_str = "%g" % int(z)
        self.gyr_x_label.setText(x_str)
        self.gyr_y_label.setText(y_str)
        self.gyr_z_label.setText(z_str)
        
    def orientation_update(self, r, p, y):
        r_str = "%g" % (r/100)
        p_str = "%g" % (p/100)
        y_str = "%g" % (y/100)
        self.roll_label.setText(r_str)
        self.pitch_label.setText(p_str)
        self.yaw_label.setText(y_str)
        
    def temperature_update(self, t):
        t_str = "%.2f" % (t/100.0)
        self.tem_label.setText(t_str)
        
    def calibrate_pressed(self):
        self.stop()
        aw = CalibrateWindow(self)  
        aw.setAttribute(Qt.WA_QuitOnClose)
        aw.show()
        
    def speed_finished(self):
        speed = self.speed_spinbox.value()
        self.imu.set_convergence_speed(speed)