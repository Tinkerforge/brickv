# -*- coding: utf-8 -*-
"""
IMU Plugin
Copyright (C) 2010-2012 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2014-2016 Matthias Bolte <matthias@tinkerforge.com>

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

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QSizePolicy, QAction

from brickv.plugin_system.plugin_base import PluginBase
from brickv.plugin_system.plugins.imu.imu_gl_widget import IMUGLWidget
from brickv.plugin_system.plugins.imu.ui_imu import Ui_IMU
from brickv.plugin_system.plugins.imu.calibrate_window import CalibrateWindow
from brickv.bindings.brick_imu import BrickIMU
from brickv.async_call import async_call
from brickv.plot_widget import PlotWidget
from brickv.callback_emulator import CallbackEmulator

class IMU(PluginBase, Ui_IMU):
    def __init__(self, *args):
        PluginBase.__init__(self, BrickIMU, *args)

        self.setupUi(self)

        self.imu = self.device

        self.acc_x = 0
        self.acc_y = 0
        self.acc_z = 0
        self.mag_x = 0
        self.mag_y = 0
        self.mag_z = 0
        self.gyr_x = 0
        self.gyr_y = 0
        self.gyr_z = 0
        self.temp  = 0
        self.roll  = 0
        self.pitch = 0
        self.yaw   = 0
        self.qua_x = 0
        self.qua_y = 0
        self.qua_z = 0
        self.qua_w = 0

        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_data)

        self.cbe_all_data = CallbackEmulator(self.imu.get_all_data,
                                             self.all_data_callback,
                                             self.increase_error_count,
                                             use_data_signal=False)
        self.cbe_orientation = CallbackEmulator(self.imu.get_orientation,
                                                self.orientation_callback,
                                                self.increase_error_count,
                                                use_data_signal=False)
        self.cbe_quaternion = CallbackEmulator(self.imu.get_quaternion,
                                               self.quaternion_callback,
                                               self.increase_error_count,
                                               use_data_signal=False)



        self.imu_gl = IMUGLWidget(self)
        self.imu_gl.setMinimumSize(150, 150)
        self.imu_gl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.update_counter = 0

        self.mag_plot_widget = PlotWidget("Magnetic Field [mG]",
                                          [("X", Qt.red, lambda: self.mag_x, str),
                                           ("Y", Qt.darkGreen, lambda: self.mag_y, str),
                                           ("Z", Qt.blue, lambda: self.mag_z, str)],
                                          clear_button=self.clear_graphs,
                                          key='right', y_resolution=0.001)
        self.acc_plot_widget = PlotWidget("Acceleration [mG]",
                                          [("X", Qt.red, lambda: self.acc_x, str),
                                           ("Y", Qt.darkGreen, lambda: self.acc_y, str),
                                           ("Z", Qt.blue, lambda: self.acc_z, str)],
                                          clear_button=self.clear_graphs,
                                          key='right', y_resolution=0.001)
        self.gyr_plot_widget = PlotWidget("Angular Velocity [°/s]",
                                          [("X", Qt.red, lambda: self.gyr_x / 14.375, str),
                                           ("Y", Qt.darkGreen, lambda: self.gyr_y / 14.375, str),
                                           ("Z", Qt.blue, lambda: self.gyr_z / 14.375, str)],
                                          clear_button=self.clear_graphs,
                                          key='right', y_resolution=0.05)
        self.temp_plot_widget = PlotWidget("Temperature [°C]",
                                           [("t", Qt.red, lambda: self.temp / 100.0, str)],
                                           clear_button=self.clear_graphs,
                                           key=None, y_resolution=0.01)

        self.mag_plot_widget.setMinimumSize(250, 200)
        self.acc_plot_widget.setMinimumSize(250, 200)
        self.gyr_plot_widget.setMinimumSize(250, 200)
        self.temp_plot_widget.setMinimumSize(250, 200)

        self.orientation_label = QLabel("""Position your IMU Brick as shown \
in the image above, then press "Save Orientation".""")
        self.orientation_label.setWordWrap(True)
        self.orientation_label.setAlignment(Qt.AlignHCenter)
        self.gl_layout = QVBoxLayout()
        self.gl_layout.addWidget(self.imu_gl)
        self.gl_layout.addWidget(self.orientation_label)

        self.layout_top.addWidget(self.gyr_plot_widget)
        self.layout_top.addWidget(self.acc_plot_widget)
        self.layout_top.addWidget(self.mag_plot_widget)
        self.layout_bottom.addLayout(self.gl_layout)
        self.layout_bottom.addWidget(self.temp_plot_widget)

        self.save_orientation.clicked.connect(self.imu_gl.save_orientation)
        self.calibrate.clicked.connect(self.calibrate_clicked)
        self.led_button.clicked.connect(self.led_clicked)
        self.speed_spinbox.editingFinished.connect(self.speed_finished)

        self.calibrate = None
        self.alive = True

        if self.firmware_version >= (2, 3, 1):
            self.status_led_action = QAction('Status LED', self)
            self.status_led_action.setCheckable(True)
            self.status_led_action.toggled.connect(lambda checked: self.imu.enable_status_led() if checked else self.imu.disable_status_led())
            self.set_configs([(0, None, [self.status_led_action])])
        else:
            self.status_led_action = None

        if self.firmware_version >= (1, 0, 7):
            reset = QAction('Reset', self)
            reset.triggered.connect(self.imu.reset)
            self.set_actions([(0, None, [reset])])

    def restart_gl(self):
        state = self.imu_gl.get_state()
        self.imu_gl.hide()

        self.imu_gl = IMUGLWidget()
        self.imu_gl.setMinimumSize(150, 150)
        self.imu_gl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.gl_layout.addWidget(self.imu_gl)
        self.imu_gl.show()

        self.save_orientation.clicked.connect(self.imu_gl.save_orientation)
        self.imu_gl.set_state(state)

    def start(self):
        if not self.alive:
            return

        self.parent().set_callback_post_untab(lambda x: self.restart_gl())
        self.parent().set_callback_post_tab(lambda x: self.restart_gl())

        if self.firmware_version >= (2, 3, 1):
            async_call(self.imu.is_status_led_enabled, None, self.status_led_action.setChecked, self.increase_error_count)

        self.gl_layout.activate()
        self.cbe_all_data.set_period(100)
        self.cbe_orientation.set_period(100)
        self.cbe_quaternion.set_period(50)
        self.update_timer.start(50)

        async_call(self.imu.get_convergence_speed, None, self.speed_spinbox.setValue, self.increase_error_count)

        self.mag_plot_widget.stop = False
        self.acc_plot_widget.stop = False
        self.gyr_plot_widget.stop = False
        self.temp_plot_widget.stop = False

    def stop(self):
        self.mag_plot_widget.stop = True
        self.acc_plot_widget.stop = True
        self.gyr_plot_widget.stop = True
        self.temp_plot_widget.stop = True

        self.update_timer.stop()
        self.cbe_all_data.set_period(0)
        self.cbe_orientation.set_period(0)
        self.cbe_quaternion.set_period(0)

    def destroy(self):
        self.alive = False
        if self.calibrate:
            self.calibrate.close()

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickIMU.DEVICE_IDENTIFIER

    def all_data_callback(self, data):
        acc_x, acc_y, acc_z, mag_x, mag_y, mag_z, gyr_x, gyr_y, gyr_z, temp = data
        self.acc_x = acc_x
        self.acc_y = acc_y
        self.acc_z = acc_z
        self.mag_x = mag_x
        self.mag_y = mag_y
        self.mag_z = mag_z
        self.gyr_x = gyr_x
        self.gyr_y = gyr_y
        self.gyr_z = gyr_z
        self.temp = temp

    def quaternion_callback(self, data):
        qua_x, qua_y, qua_z, qua_w = data
        self.qua_x = qua_x
        self.qua_y = qua_y
        self.qua_z = qua_z
        self.qua_w = qua_w

    def orientation_callback(self, data):
        roll, pitch, yaw = data
        self.roll = roll
        self.pitch = pitch
        self.yaw = yaw

    def led_clicked(self):
        if 'On' in self.led_button.text().replace('&', ''):
            self.led_button.setText('Turn LEDs Off')
            self.imu.leds_on()
        elif 'Off' in self.led_button.text().replace('&', ''):
            self.led_button.setText('Turn LEDs On')
            self.imu.leds_off()

    def update_data(self):
        self.update_counter += 1

        self.imu_gl.update(self.qua_x, self.qua_y, self.qua_z, self.qua_w)

        if self.update_counter % 2:
            gyr_x = self.gyr_x/14.375
            gyr_y = self.gyr_y/14.375
            gyr_z = self.gyr_z/14.375

            self.acceleration_update(self.acc_x, self.acc_y, self.acc_z)
            self.magnetometer_update(self.mag_x, self.mag_y, self.mag_z)
            self.gyroscope_update(gyr_x, gyr_y, gyr_z)
            self.orientation_update(self.roll, self.pitch, self.yaw)
            self.temperature_update(self.temp)

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

    def calibrate_clicked(self):
        self.stop()
        if self.calibrate is None:
            self.calibrate = CalibrateWindow(self)

        self.calibrate.refresh_values()
        self.calibrate.show()

    def speed_finished(self):
        speed = self.speed_spinbox.value()
        self.imu.set_convergence_speed(speed)
