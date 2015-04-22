# -*- coding: utf-8 -*-
"""
IMU 2.0 Plugin
Copyright (C) 2015 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2015 Matthias Bolte <matthias@tinkerforge.com>

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

from PyQt4.QtCore import Qt, QTimer
from PyQt4.QtGui import QLabel, QVBoxLayout, QColor, QPalette, \
                        QFrame, QPainter, QBrush, QDialog

from brickv.plugin_system.plugin_base import PluginBase
from brickv.plugin_system.plugins.imu_v2.ui_imu_v2 import Ui_IMUV2
from brickv.plugin_system.plugins.imu_v2.ui_calibration import Ui_Calibration
from brickv.bindings.brick_imu_v2 import BrickIMUV2
from brickv.async_call import async_call
from brickv.plot_widget import PlotWidget
from brickv.callback_emulator import CallbackEmulator

class Calibration(QDialog, Ui_Calibration):
    def __init__(self, parent):
        QDialog.__init__(self, parent)

        self.setupUi(self)

        self.text_browser.setHtml("""
<p><b>General:</b> The IMU does continous calibration during usage.
It is not necessary to start a specific calibration process.</p>
<p>Accelerometer and gyroscope are factory calibrated and are less susceptible
to external disturbances. As a result the offsets can be seen as negligble and
calibration is not important. For the magnetometer on the other hand calibration
is mandatory after each &quot;power on reset&quot;.</p>
<p>To make this easier we allow to save the calibration to the flash of the
IMU Brick and load the calibration on each startup. This way there is no
&quot;startup phase&quot; that is necessary until the IMU Brick has calibrated
itself.</p>
<p><b>Calibration values:</b> Saving a calibration is only possible if all
sensors are fully calibrated.</p>
<ul>
<li>green = fully calibrated,</li>
<li>yellow = calibration OK,</li>
<li>orange = calibration recommended and</li>
<li>red = not calibrated.</li>
</ul>
<p><b>Accelerometer:</b> Place the IMU Brick in 6 different stable position for
a period of a few seconds. Use slow movement between stable positions. Use at
least one position that is perpendicular to the x, y and z axis.</p>
<p><b>Magnetometer:</b> Make random movements (e.g. write a figure 8 in air).</p>
<p><b>Gyroscope:</b> Place the IMU Brick in a single stable position for a
period of several seconds.</p>
<p><b>System:</b> Wait for the system to stabilize. Use only small movements
during stabilization.</p>""")

        self.parent = parent
        self.ipcon = parent.ipcon
        self.imu = parent.imu
        
        self.acc_color = ColorFrame()
        self.mag_color = ColorFrame()
        self.gyr_color = ColorFrame()
        self.sys_color = ColorFrame()
        
        self.grid.addWidget(self.acc_color, 2, 2)
        self.grid.addWidget(self.mag_color, 3, 2)
        self.grid.addWidget(self.gyr_color, 4, 2)
        self.grid.addWidget(self.sys_color, 5, 2)
        
        self.save_calibration.clicked.connect(self.save_calibration_clicked)
        
    def save_calibration_clicked(self):
        async_call(self.imu.save_calibration, None, self.async_save_calibration, self.parent.increase_error_count)
        
    def async_save_calibration(self, calibration_done):
        # TODO: Show user that calibration was is done/not done?
        pass
        
    def closeEvent(self, event):
        self.parent.button_calibration.setEnabled(True)
        
class ColorFrame(QFrame):
    def __init__(self, parent = None):
        QFrame.__init__(self, parent)
        self.color = Qt.red
        self.setMinimumSize(15, 15)
        self.setMaximumSize(15, 15)

    def set_color(self, color):
        self.color = color
        self.repaint()

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        qp.setBrush(QBrush(self.color))
        qp.setPen(self.color)
        qp.drawRect(0, 0, 15, 15)
        qp.setBrush(Qt.NoBrush)
        qp.setPen(Qt.black)
        qp.drawRect(1, 1, 14, 14)
        qp.end()

class IMUV2(PluginBase, Ui_IMUV2):
    def __init__(self, *args):
        PluginBase.__init__(self, BrickIMUV2, *args)

        self.setupUi(self)

        self.imu = self.device

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
        self.imu_gl.setFixedSize(200, 200)
        self.min_x = 0
        self.min_y = 0
        self.min_z = 0
        self.max_x = 0
        self.max_y = 0
        self.max_z = 0

        self.data_plot_widget = []
        self.sensor_data = [0]*23

        self.data_labels = [self.label_acceleration_x, self.label_acceleration_y, self.label_acceleration_z, 
                            self.label_magnetic_field_x, self.label_magnetic_field_y, self.label_magnetic_field_z, 
                            self.label_angular_velocity_x, self.label_angular_velocity_y, self.label_angular_velocity_z, 
                            self.label_euler_angle_heading, self.label_euler_angle_roll, self.label_euler_angle_pitch, 
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

        self.plot_timer = QTimer(self)
        self.plot_timer.start(100)

        for i in range(23):
            self.data_plot_widget.append(PlotWidget("",
                                                    [["", self.data_color[i][0], get_lambda_data_getter(i)]],
                                                    self.clear_graphs, 
                                                    scales_visible=False, 
                                                    curve_outer_border_visible=False,
                                                    curve_motion_granularity=1,
                                                    canvas_color=self.data_color[i][1],
                                                    external_timer=self.plot_timer))

        for w in self.data_plot_widget:
            w.setMinimumHeight(15)
            w.setMaximumHeight(25)
                    
        for i in range(23):
            self.data_grid.addWidget(self.data_plot_widget[i], i, 4)
            
        self.data_grid.setColumnMinimumWidth(2, 75)

        self.gl_layout = QVBoxLayout()
        self.gl_layout.addWidget(self.imu_gl)
        
        self.v_layout = QVBoxLayout()
        self.layout_bottom.addLayout(self.gl_layout)

        self.save_orientation.clicked.connect(self.imu_gl.save_orientation)
        self.checkbox_leds.stateChanged.connect(self.led_clicked)
        self.button_calibration.clicked.connect(self.calibration_clicked)
        self.calibration_color = [Qt.red, QColor(0xFF, 0xA0, 0x00), Qt.yellow, Qt.darkGreen]

        self.calibration = None
        self.alive = True
        self.callback_counter = 0

    def start(self):
        if not self.alive:
            return

        self.gl_layout.activate()
        self.cbe_all_data.set_period(50)

        for w in self.data_plot_widget:
            w.stop = False

    def stop(self):
        for w in self.data_plot_widget:
            w.stop = True

        self.cbe_all_data.set_period(0)

    def destroy(self):
        self.alive = False
        if self.calibration:
            self.calibration.close()

    def has_reset_device(self):
        return True

    def reset_device(self):
        self.imu.reset()

    def is_brick(self):
        return True

    def get_url_part(self):
        return 'imu_v2'

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickIMUV2.DEVICE_IDENTIFIER
    
    def calibration_clicked(self):
        if self.calibration is None:
            self.calibration = Calibration(self)

        self.button_calibration.setEnabled(False)
        self.calibration.show()

    def all_data_callback(self, data):
        self.callback_counter += 1

        if self.callback_counter % 2 == 0:
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

            self.imu_gl.update(self.sensor_data[12],
                               self.sensor_data[13],
                               self.sensor_data[14],
                               self.sensor_data[15])
            
            cal_mag = data.calibration_status & 3;
            cal_acc = (data.calibration_status & (3 << 2)) >> 2
            cal_gyr = (data.calibration_status & (3 << 4)) >> 4
            cal_sys = (data.calibration_status & (3 << 6)) >> 6

            if self.calibration != None:
                self.calibration.save_calibration.setEnabled(data.calibration_status == 0xFF)
                    
                self.calibration.mag_color.set_color(self.calibration_color[cal_mag])
                self.calibration.acc_color.set_color(self.calibration_color[cal_acc])
                self.calibration.gyr_color.set_color(self.calibration_color[cal_gyr])
                self.calibration.sys_color.set_color(self.calibration_color[cal_sys])
        else:
            self.imu_gl.update(data.quaternion[0]/(float(2**14-1)),
                               data.quaternion[1]/(float(2**14-1)),
                               data.quaternion[2]/(float(2**14-1)),
                               data.quaternion[3]/(float(2**14-1)))

    def led_clicked(self, state):
        if state == Qt.Checked:
            self.imu.leds_on()
        else:
            self.imu.leds_off()
    
    def get_data(self, i):
        return self.sensor_data[i]
