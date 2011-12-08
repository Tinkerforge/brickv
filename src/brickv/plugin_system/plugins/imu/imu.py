# -*- coding: utf-8 -*-  
"""
Master Plugin
Copyright (C) 2010-2011 Olaf Lüke <olaf@tinkerforge.com>

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
import ip_connection

from PyQt4.QtCore import Qt, QTimer
from PyQt4.QtGui import QVBoxLayout, QLabel, QColor
import PyQt4.Qwt5 as Qwt

from ui_imu import Ui_IMU

import brick_imu

class Plot(Qwt.QwtPlot):
    def __init__(self, y_axis, plot_list, *args):
        Qwt.QwtPlot.__init__(self, *args)
        
        self.setAxisTitle(Qwt.QwtPlot.xBottom, "Time [s]")
        self.setAxisTitle(Qwt.QwtPlot.yLeft, y_axis)
        
        #self.setTitle("Test")
        
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
        
        
        #self.setAxisAutoScale(Qwt.QwtPlot.xBottom, True)
        #self.curve.setData([0,1,2,3,4,5,6,7], [1,2,3,4,4,4,3,2])
        
    def show_curve(self, item, on):
        item.setVisible(on)
        widget = self.legend().find(item)
        if isinstance(widget, Qwt.QwtLegendItem):
            widget.setChecked(on)
        self.replot()
           

    def add_data(self, i, data_x, data_y):
        #print index, data
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
        
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_data)
        
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
        
        self.grid_layout.addWidget(self.gyr_plot, 0, 0)
        self.grid_layout.addWidget(self.acc_plot, 0, 2)
        self.grid_layout.addWidget(self.mag_plot, 0, 4)
        self.grid_layout.addWidget(self.imu_gl, 2, 2)
        self.grid_layout.addWidget(self.tem_plot, 2, 4)
        
        self.save_orientation.clicked.connect(self.imu_gl.save_orientation)
        self.clear_graphs.clicked.connect(self.clear_graphs_clicked)
        
        #max: (189, 769, 467)
        #min: (-872, -252, -392)

    def start(self):
        self.update_timer.start(50)

    def stop(self):
        self.update_timer.stop()
        
    @staticmethod
    def has_name(name):
        return 'IMU Brick' in name 
        
    def clear_graphs_clicked(self):
        self.counter = 0
        self.mag_plot.clear_graph()
        self.acc_plot.clear_graph()
        self.gyr_plot.clear_graph()
        self.tem_plot.clear_graph()
        
    def update_data(self):
        try:
            acc_x, acc_y, acc_z, \
            mag_x, mag_y, mag_z, \
            gyr_x, gyr_y, gyr_z, tem = self.imu.get_all_data()
            qua_x, qua_y, qua_z, qua_w = self.imu.get_quaternion()
            roll, pitch, yaw = self.imu.get_orientation()
        except ip_connection.Error:
            return
        
        gyr_x = gyr_x/14.375
        gyr_y = gyr_y/14.375
        gyr_z = gyr_z/14.375
        tem = 35.0 + (tem + 13200)/280.0
        
        self.acceleration_update(acc_x, acc_y, acc_z)
        self.magnetometer_update(mag_x, mag_y, mag_z)
        self.gyroscope_update(gyr_x, gyr_y, gyr_z)
        self.orientation_update(roll, pitch, yaw)
        self.temperature_update(tem)
        
        #print qua_x, qua_y, qua_z, qua_w
        
#        import math
#        print math.atan2((float((mag_x-self.min_x))/(self.max_x-self.min_x))*2 - 1.0, 
#                         (float((mag_y-self.min_y))/(self.max_y-self.min_y))*2 - 1.0)*360.0/math.pi

        # MAGNETORMETER
        #print mag_x, mag_y, mag_z
        
        #if mag_x > self.max_x:
        #    self.max_x = int(mag_x)
        #if mag_x < self.min_x:
        #    self.min_x = int(mag_x)
            
        #if mag_y > self.max_y:
        #    self.max_y = int(mag_y)
        #if mag_y < self.min_y:
        #    self.min_y = int(mag_y)
            
        #if mag_z > self.max_z:
        #    self.max_z = int(mag_z)
        #if mag_z < self.min_z:
        #    self.min_z = int(mag_z)
            
        # ACCELEROMETER
        #print acc_x, acc_y, acc_z
        
        #if acc_x > self.max_x:
        #    self.max_x = int(acc_x)
        #if acc_x < self.min_x:
        #    self.min_x = int(acc_x)
           
        #if acc_y > self.max_y:
        #    self.max_y = int(acc_y)
        #if acc_y < self.min_y:
        #    self.min_y = int(acc_y)
            
        #if acc_z > self.max_z:
        #    self.max_z = int(acc_z)
        #if acc_z < self.min_z:
        #    self.min_z = int(acc_z)
        
        # GYROSCOPE
        #print self.counter, gyr_x, gyr_y, gyr_z

        #if self.counter % 1000 == 0:
        #    print "avg: " + str((self.max_x/1000.0, self.max_y/1000.0, self.max_z/1000.0))
        #    self.max_x = 0
        #    self.max_y = 0
        #    self.max_z = 0
        #    if self.counter != 0:
        #        exit()
        
        #self.max_x += gyr_x
        #self.max_y += gyr_y
        #self.max_z += gyr_z
        
        #self.counter += 1
            
        #print "max: " + str((self.max_x, self.max_y, self.max_z))
        #print "min: " + str((self.min_x, self.min_y, self.min_z))
        
        
        self.imu_gl.update(qua_x, qua_y, qua_z, qua_w, roll, pitch, yaw)
        #self.imu_gl.update(1.0, 0.0, 0.0, 0.0)
        
        
        self.gyr_plot.add_data(0, self.counter, gyr_x)
        self.gyr_plot.add_data(1, self.counter, gyr_y)
        self.gyr_plot.add_data(2, self.counter, gyr_z)
        
        self.acc_plot.add_data(0, self.counter, acc_x)
        self.acc_plot.add_data(1, self.counter, acc_y)
        self.acc_plot.add_data(2, self.counter, acc_z)
        
        self.mag_plot.add_data(0, self.counter, mag_x)
        self.mag_plot.add_data(1, self.counter, mag_y)
        self.mag_plot.add_data(2, self.counter, mag_z)
        
        self.tem_plot.add_data(0, self.counter, tem)
        
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
        r_str = "%g" % r
        p_str = "%g" % p
        y_str = "%g" % y
        self.roll_label.setText(r_str)
        self.pitch_label.setText(p_str)
        self.yaw_label.setText(y_str)
        
    def temperature_update(self, t):
        t_str = "%.2f" % t
        self.tem_label.setText(t_str)
        
        
