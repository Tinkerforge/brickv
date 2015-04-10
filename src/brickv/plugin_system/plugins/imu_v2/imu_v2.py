# -*- coding: utf-8 -*-
"""
IMU 2.0 Plugin
Copyright (C) 2015 Olaf Lüke <olaf@tinkerforge.com>

imu_v2.py: IMU 2.0 Plugin implementation

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

from brickv.plugin_system.plugin_base import PluginBase
from brickv.bindings.brick_imu_v2 import BrickIMUV2
from brickv.async_call import async_call
from brickv.plot_widget import PlotWidget
from brickv.utils import CallbackEmulator

from PyQt4.QtGui import QLabel, QVBoxLayout, QSizePolicy, QColor, QPalette
from PyQt4.QtCore import Qt, QTimer

from brickv.plugin_system.plugins.imu_v2.ui_imu_v2 import Ui_IMUV2

class IMUV2(PluginBase, Ui_IMUV2):
    def __init__(self, *args):
        PluginBase.__init__(self, BrickIMUV2, *args)

        self.setupUi(self)

        self.imu = self.device

        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_data)

        self.cbe_all_data = CallbackEmulator(self.imu.get_all_data,
                                             self.all_data_callback,
                                             self.increase_error_count)

        # Import IMUGLWidget here, not global. If globally included we get
        # 'No OpenGL_accelerate module loaded: No module named OpenGL_accelerate'
        # as soon as IMU is set as device_class in __init__.
        # No idea why this happens, doesn't make sense.
        try:
            from .imu_v2_gl_widget import IMUV2GLWidget
        except:
            from imu_v2_gl_widget import IMUV2GLWidget

        self.imu_gl = IMUV2GLWidget(self)
        self.imu_gl.setMinimumSize(150, 150)
        self.imu_gl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.min_x = 0
        self.min_y = 0
        self.min_z = 0
        self.max_x = 0
        self.max_y = 0
        self.max_z = 0

        self.update_counter = 0

        self.data_plot_widget = []
        self.sensor_data = [0]*23

        self.data_labels = [self.label_acceleration_x, self.label_acceleration_y, self.label_acceleration_z, 
                            self.label_magnetic_field_x, self.label_magnetic_field_y, self.label_magnetic_field_z, 
                            self.label_angular_velocity_x, self.label_angular_velocity_y, self.label_angular_velocity_z, 
                            self.label_euler_angle_roll, self.label_euler_angle_pitch, self.label_euler_angle_heading, 
                            self.label_quaternion_w, self.label_quaternion_x, self.label_quaternion_y, self.label_quaternion_z, 
                            self.label_linear_acceleration_x, self.label_linear_acceleration_y, self.label_linear_acceleration_z, 
                            self.label_gravity_vector_x, self.label_gravity_vector_y, self.label_gravity_vector_z, 
                            self.label_temperature]
        
        self.data_rows = [[self.label_acceleration_11, self.label_acceleration_21, self.label_acceleration_22, self.label_acceleration_23, self.label_acceleration_41, self.label_acceleration_42, self.label_acceleration_43, self.label_acceleration_x, self.label_acceleration_y, self.label_acceleration_z],
                          [self.label_magnetic_field_11, self.label_magnetic_field_21, self.label_magnetic_field_22, self.label_magnetic_field_23, self.label_magnetic_field_41, self.label_magnetic_field_42, self.label_magnetic_field_43, self.label_magnetic_field_x, self.label_magnetic_field_y, self.label_magnetic_field_z],
                          [self.label_angular_velocity_11, self.label_angular_velocity_21, self.label_angular_velocity_22, self.label_angular_velocity_23, self.label_angular_velocity_41, self.label_angular_velocity_42, self.label_angular_velocity_43, self.label_angular_velocity_x, self.label_angular_velocity_y, self.label_angular_velocity_z],
                          [self.label_euler_angle_11, self.label_euler_angle_21, self.label_euler_angle_22, self.label_euler_angle_23, self.label_euler_angle_41, self.label_euler_angle_42, self.label_euler_angle_43, self.label_euler_angle_roll, self.label_euler_angle_pitch, self.label_euler_angle_heading],
                          [self.label_quaternion_11, self.label_quaternion_21, self.label_quaternion_22, self.label_quaternion_23, self.label_quaternion_24, self.label_quaternion_41, self.label_quaternion_42, self.label_quaternion_43, self.label_quaternion_44, self.label_quaternion_w, self.label_quaternion_x, self.label_quaternion_y, self.label_quaternion_z],
                          [self.label_linear_acceleration_11, self.label_linear_acceleration_21, self.label_linear_acceleration_22, self.label_linear_acceleration_23, self.label_linear_acceleration_41, self.label_linear_acceleration_42, self.label_linear_acceleration_43, self.label_linear_acceleration_x, self.label_linear_acceleration_y, self.label_linear_acceleration_z],
                          [self.label_gravity_vector_11, self.label_gravity_vector_21, self.label_gravity_vector_22, self.label_gravity_vector_23, self.label_gravity_vector_41, self.label_gravity_vector_42, self.label_gravity_vector_43, self.label_gravity_vector_x, self.label_gravity_vector_y, self.label_gravity_vector_z],
                          [self.label_temperature_11, self.label_temperature_21, self.label_temperature_41, self.label_temperature],
                         ]
        
        even_color = QColor(240, 240, 240)
        odd_color = QColor(255, 255, 255)
        
        self.data_color = [(Qt.red, even_color), (Qt.darkGreen, even_color), (Qt.blue, even_color),
                           (Qt.red, odd_color), (Qt.darkGreen, odd_color), (Qt.blue, odd_color),
                           (Qt.red, even_color), (Qt.darkGreen, even_color), (Qt.blue, even_color),
                           (Qt.red, odd_color), (Qt.darkGreen, odd_color), (Qt.blue, odd_color),
                           (Qt.magenta, even_color), (Qt.red, even_color), (Qt.darkGreen, even_color), (Qt.blue, even_color),
                           (Qt.red, odd_color), (Qt.darkGreen, odd_color), (Qt.blue, odd_color),
                           (Qt.red, even_color), (Qt.darkGreen, even_color), (Qt.blue, even_color),
                           (Qt.magenta, odd_color)]
        
        
        even_palette = QPalette()
        even_palette.setColor(QPalette.Window, even_color)
        odd_palette = QPalette()
        odd_palette.setColor(QPalette.Window, odd_color)
        
        for i, row in enumerate(self.data_rows):
            for label in row:
                if i % 2:
                    label.setPalette(odd_palette)
                else:
                    label.setPalette(even_palette)
                    
                label.setAutoFillBackground(True)

        def get_lambda_data_getter(i):
            return lambda: self.get_data(i)
        
        for i in range(23):
            self.data_plot_widget.append(PlotWidget("",
                                                    [["", self.data_color[i][0], get_lambda_data_getter(i)]],
                                                    self.clear_graphs, 
                                                    scales_visible=False, 
                                                    curve_outer_border_visible=False,
                                                    curve_motion_granularity=1,
                                                    canvas_color=self.data_color[i][1]))

        for w in self.data_plot_widget:
            w.setMinimumHeight(15)
            w.setMaximumHeight(25)
                    
        for i in range(23):
            self.data_grid.addWidget(self.data_plot_widget[i], i, 4)
            
        self.data_grid.setColumnMinimumWidth(2, 75)

        self.orientation_label = QLabel("""Position your IMU Brick 2.0 as shown \
in the image above, then press "Save Orientation".""")
        self.orientation_label.setWordWrap(True)
        self.orientation_label.setAlignment(Qt.AlignHCenter)
        self.gl_layout = QVBoxLayout()
        self.gl_layout.addWidget(self.imu_gl)
        self.gl_layout.addWidget(self.orientation_label)
        
        self.v_layout = QVBoxLayout()
        self.layout_bottom.addLayout(self.gl_layout)

        self.save_orientation.clicked.connect(self.imu_gl.save_orientation)
        self.led_button.clicked.connect(self.led_clicked)

        self.calibrate = None
        self.alive = True

    def start(self):
        if not self.alive:
            return

        self.gl_layout.activate()
        self.cbe_all_data.set_period(100)

        for w in self.data_plot_widget:
            w.stop = False

    def stop(self):
        for w in self.data_plot_widget:
            w.stop = True

        self.update_timer.stop()
        self.cbe_all_data.set_period(0)

    def destroy(self):
        self.alive = False
        if self.calibrate:
            self.calibrate.close()

    def has_reset_device(self):
        return self.firmware_version >= (1, 0, 7)

    def reset_device(self):
        if self.has_reset_device():
            self.imu.reset()

    def is_brick(self):
        return True

    def get_url_part(self):
        return 'imu_v2'

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickIMUV2.DEVICE_IDENTIFIER

    def all_data_callback(self, data):
        self.sensor_data[0]  = data.acceleration[0]/100.0
        self.sensor_data[1]  = data.acceleration[1]/100.0
        self.sensor_data[2]  = data.acceleration[2]/100.0
        self.sensor_data[3]  = data.magnetic_field[0]/16.0
        self.sensor_data[4]  = data.magnetic_field[1]/16.0
        self.sensor_data[5]  = data.magnetic_field[2]/16.0
        self.sensor_data[6]  = data.angular_velocity[0]/16.0
        self.sensor_data[7]  = data.angular_velocity[1]/16.0
        self.sensor_data[8]  = data.angular_velocity[2]/16.0
        self.sensor_data[9]  = data.euler_angle[0]/16.0
        self.sensor_data[10] = data.euler_angle[1]/16.0
        self.sensor_data[11] = data.euler_angle[2]/16.0
        self.sensor_data[12] = data.quaternion[0]/(float(2**14-1))
        self.sensor_data[13] = data.quaternion[1]/(float(2**14-1))
        self.sensor_data[14] = data.quaternion[2]/(float(2**14-1))
        self.sensor_data[15] = data.quaternion[3]/(float(2**14-1))
        self.sensor_data[16] = data.linear_acceleration[0]/100.0
        self.sensor_data[17] = data.linear_acceleration[1]/100.0
        self.sensor_data[18] = data.linear_acceleration[2]/100.0
        self.sensor_data[19] = data.gravity_vector[0]/100.0
        self.sensor_data[20] = data.gravity_vector[1]/100.0
        self.sensor_data[21] = data.gravity_vector[2]/100.0
        self.sensor_data[22] = data.temperature
        
        for i in range(23):
            self.data_labels[i].setText("{0:.2f}".format(self.sensor_data[i]))

    def led_clicked(self):
        if 'On' in self.led_button.text():
            self.led_button.setText('Turn LEDs Off')
            self.imu.leds_on()
        elif 'Off' in self.led_button.text():
            self.led_button.setText('Turn LEDs On')
            self.imu.leds_off()
    
    def get_data(self, i):
        return self.sensor_data[i]

    def update_data(self):
        print "update_data"
        self.update_counter += 1

        self.imu_gl.update(self.qua_x, self.qua_y, self.qua_z, self.qua_w)
