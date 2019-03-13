# -*- coding: utf-8 -*-
"""
IMU Plugin
Copyright (C) 2010-2012 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2015 Matthias Bolte <matthias@tinkerforge.com>

imu_gl_widget.py: IMU OpenGL representation

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

# Workaround a strange OpenGL problem that affects some but not all Qt5 OpenGL
# versions. For example libqt5opengl5 5.9.1+dfsg-10ubuntu1 in Ubuntu is affected.
#
# If the problem occurs then the following messages are printed upon opening the
# plugin widget that contains the OpenGL widget. The whole Brick Viewer window
# turns black as a result.
#
#  QOpenGLShaderProgram: could not create shader program
#  QOpenGLShader: could not create shader
#  Could not link shader program:
#
# Manually loading libGL.so here fixes the problem.

if sys.platform.startswith('linux'):
    libGL_path = ctypes.util.find_library('GL')

    if libGL_path != None:
        libGL = ctypes.CDLL(libGL_path, mode=ctypes.RTLD_GLOBAL)

import math
from PyQt5.QtWidgets import QOpenGLWidget
from PyQt5.QtGui import QOpenGLContext, QOpenGLVersionProfile, QSurfaceFormat

class IMUGLWidget(QOpenGLWidget):
    def __init__(self, parent=None):
        super().__init__(self, parent)

        surface_format = QSurfaceFormat()
        surface_format.setSamples(16)
        QOpenGLWidget.setFormat(self, surface_format)

        self.profile = QOpenGLVersionProfile()
        self.profile.setVersion(2, 1)

        self.parent = parent

        self.vertices = [
            (-0.5, -0.5, -0.5),
            (0.5, -0.5, -0.5),
            (0.5, 0.5, -0.5),
            (-0.5, 0.5, -0.5),
            (-0.5, -0.5, 0.5),
            (0.5, -0.5, 0.5),
            (0.5, 0.5, 0.5),
            (-0.5, 0.5, 0.5)
        ]

        self.normals = [
            (1, 0, 0),
            (0, 1, 0),
            (0, 0, 1),
            (-1, 0, 0),
            (0, -1, 0),
            (0, 0, -1),
        ]

        self.m = [[1, 0, 0, 0],
                  [0, 1, 0, 0],
                  [0, 0, 1, 0],
                  [0, 0, 0, 1]]

        self.rel_x = 0
        self.rel_y = 0
        self.rel_z = 0
        self.rel_w = 0

        self.save_orientation_flag = False
        self.has_save_orientation = False
        self.display_list = None
        self.initialized = False

    def get_state(self):
        return self.save_orientation_flag, self.rel_x, self.rel_y, self.rel_z, self.rel_w, self.has_save_orientation, self.initialized

    def set_state(self, tup):
        self.save_orientation_flag, self.rel_x, self.rel_y, self.rel_z, self.rel_w, self.has_save_orientation, self.initialized = tup

    def update(self, x, y, z, w):
        if self.save_orientation_flag:
            self.rel_x = x
            self.rel_y = y
            self.rel_z = z
            self.rel_w = w
            self.save_orientation_flag = False
            self.has_save_orientation = True
            if self.parent is not None:
                self.parent.orientation_label.hide()

        if not self.has_save_orientation:
            return

        # conjugate
        x = -x
        y = -y
        z = -z

        wn = w * self.rel_w - x * self.rel_x - y * self.rel_y - z * self.rel_z
        xn = w * self.rel_x + x * self.rel_w + y * self.rel_z - z * self.rel_y
        yn = w * self.rel_y - x * self.rel_z + y * self.rel_w + z * self.rel_x
        zn = w * self.rel_z + x * self.rel_y - y * self.rel_x + z * self.rel_w

        x = xn
        y = yn
        z = zn
        w = wn

        xx = x * x
        yy = y * y
        zz = z * z
        xy = x * y
        xz = x * z
        yz = y * z
        wx = w * x
        wy = w * y
        wz = w * z

        self.m = [[1.0 - 2.0*(yy + zz), 2.0*(xy - wz), 2.0*(xz + wy), 0.0],
                  [2.0*(xy + wz), 1.0 - 2.0*(xx + zz), 2.0*(yz - wx), 0.0],
                  [2.0*(xz - wy), 2.0*(yz + wx), 1.0 - 2.0*(xx + yy), 0.0],
                  [0.0, 0.0, 0.0, 1.0]]

        QOpenGLWidget.update(self)

    def initializeGL(self):
        self.gl = self.context().versionFunctions(self.profile)
        if not self.initialized:
            self.gl.initializeOpenGLFunctions()
            self.initialized = True

        gl = self.gl
        gl.glClearColor(0.85, 0.85, 0.85, 1.0)
        gl.glClearDepth(1.0)
        gl.glDepthFunc(gl.GL_LESS)
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glEnable(gl.GL_CULL_FACE)

        gl.glShadeModel(gl.GL_SMOOTH)
        gl.glEnable(gl.GL_NORMALIZE)
        gl.glEnable(gl.GL_COLOR_MATERIAL)
        gl.glColorMaterial(gl.GL_FRONT, gl.GL_AMBIENT_AND_DIFFUSE)
        gl.glLightfv(gl.GL_LIGHT0, gl.GL_POSITION, (0.0, 0.0, 1.0, 0.0))
        gl.glEnable(gl.GL_LIGHT0)

        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()

        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()

        if self.display_list is not None:
            gl.glDeleteLists(self.display_list, 1)

        self.display_list = gl.glGenLists(1)
        gl.glNewList(self.display_list, gl.GL_COMPILE)
        gl.glScalef(0.5, 0.5, 0.5)

        gl.glEnable(gl.GL_LIGHTING)

        # board
        gl.glColor3f(0.0, 0.0, 0.0)
        self.draw_cuboid(4.0, 4.0, 0.16)

        # USB connector
        gl.glPushMatrix()
        gl.glColor3f(0.5, 0.51, 0.58)
        gl.glTranslatef(0.0, -1.6, 0.28)
        self.draw_cuboid(0.75, 0.9, 0.4)
        gl.glPopMatrix()

        # right button
        gl.glPushMatrix()
        gl.glColor3f(0.5, 0.51, 0.58)
        gl.glTranslatef(1.15, -1.85, 0.16)
        self.draw_cuboid(0.4, 0.3, 0.16)
        gl.glColor3f(0.0, 0.0, 0.0)
        gl.glTranslatef(0.0, -0.155, 0.025)
        self.draw_cuboid(0.18, 0.1, 0.08)
        gl.glPopMatrix()

        # left button
        gl.glPushMatrix()
        gl.glColor3f(0.5, 0.51, 0.58)
        gl.glTranslatef(-1.15, -1.85, 0.16)
        self.draw_cuboid(0.4, 0.3, 0.16)
        gl.glColor3f(0.0, 0.0, 0.0)
        gl.glTranslatef(0.0, -0.155, 0.025)
        self.draw_cuboid(0.18, 0.1, 0.08)
        gl.glPopMatrix()

        # left btb top
        gl.glPushMatrix()
        gl.glColor3f(1.0, 1.0, 1.0)
        gl.glTranslatef(-1.65, 0.0, 0.38)
        self.draw_cuboid(0.5, 1.4, 0.6)
        gl.glPopMatrix()

        # right btb top
        gl.glPushMatrix()
        gl.glColor3f(1.0, 1.0, 1.0)
        gl.glTranslatef(1.65, 0.0, 0.38)
        self.draw_cuboid(0.5, 1.4, 0.6)
        gl.glPopMatrix()

        # left btb bottom
        gl.glPushMatrix()
        gl.glColor3f(1.0, 1.0, 1.0)
        gl.glTranslatef(-1.65, 0.0, -0.33)
        self.draw_cuboid(0.5, 1.4, 0.5)
        gl.glPopMatrix()

        # right btb bottom
        gl.glPushMatrix()
        gl.glColor3f(1.0, 1.0, 1.0)
        gl.glTranslatef(1.65, 0.0, -0.33)
        self.draw_cuboid(0.5, 1.4, 0.5)
        gl.glPopMatrix()

        # left bricklet port
        gl.glPushMatrix()
        gl.glColor3f(1.0, 1.0, 1.0)
        gl.glTranslatef(-0.85, 1.8, -0.23)
        self.draw_cuboid(1.2, 0.4, 0.3)
        gl.glPopMatrix()

        # right bricklet port
        gl.glPushMatrix()
        gl.glColor3f(1.0, 1.0, 1.0)
        gl.glTranslatef(0.85, 1.8, -0.23)
        self.draw_cuboid(1.2, 0.4, 0.3)
        gl.glPopMatrix()

        # left direction LED
        gl.glPushMatrix()
        gl.glColor3f(0.0, 0.5, 0.0)
        gl.glTranslatef(-1.05, 1.425, 0.115)
        self.draw_cuboid(0.1, 0.2, 0.07)
        gl.glPopMatrix()

        # top direction LED
        gl.glPushMatrix()
        gl.glColor3f(0.0, 0.5, 0.0)
        gl.glTranslatef(-0.675, 1.8, 0.115)
        self.draw_cuboid(0.2, 0.1, 0.07)
        gl.glPopMatrix()

        # right direction LED
        gl.glPushMatrix()
        gl.glColor3f(0.0, 0.5, 0.0)
        gl.glTranslatef(-0.3, 1.425, 0.115)
        self.draw_cuboid(0.1, 0.2, 0.07)
        gl.glPopMatrix()

        # bottom direction LED
        gl.glPushMatrix()
        gl.glColor3f(0.0, 0.5, 0.0)
        gl.glTranslatef(-0.675, 1.05, 0.115)
        self.draw_cuboid(0.2, 0.1, 0.07)
        gl.glPopMatrix()

        # left y orientation LED
        gl.glPushMatrix()
        gl.glColor3f(0.0, 0.0, 1.0)
        gl.glTranslatef(0.275, 1.7, 0.115)
        self.draw_cuboid(0.1, 0.2, 0.07)
        gl.glPopMatrix()

        # right y orientation LED
        gl.glPushMatrix()
        gl.glColor3f(1.0, 0.0, 0.0)
        gl.glTranslatef(0.425, 1.7, 0.115)
        self.draw_cuboid(0.1, 0.2, 0.07)
        gl.glPopMatrix()

        # top z orientation LED
        gl.glPushMatrix()
        gl.glColor3f(1.0, 0.0, 0.0)
        gl.glTranslatef(0.35, 1.15, 0.115)
        self.draw_cuboid(0.2, 0.1, 0.07)
        gl.glPopMatrix()

        # bottom z orientation LED
        gl.glPushMatrix()
        gl.glColor3f(0.0, 0.0, 1.0)
        gl.glTranslatef(0.35, 1.0, 0.115)
        self.draw_cuboid(0.2, 0.1, 0.07)
        gl.glPopMatrix()

        # top x orientation LED
        gl.glPushMatrix()
        gl.glColor3f(1.0, 0.0, 0.0)
        gl.glTranslatef(1.0, 1.15, 0.115)
        self.draw_cuboid(0.2, 0.1, 0.07)
        gl.glPopMatrix()

        # bottom x orientation LED
        gl.glPushMatrix()
        gl.glColor3f(0.0, 0.0, 1.0)
        gl.glTranslatef(1.0, 1.0, 0.115)
        self.draw_cuboid(0.2, 0.1, 0.07)
        gl.glPopMatrix()

        # top alignment corner
        gl.glPushMatrix()
        gl.glColor3f(1.0, 1.0, 1.0)
        gl.glBegin(gl.GL_TRIANGLES)
        gl.glNormal3f(0.0, 0.0, 1.0)
        gl.glVertex3f(-2.0, -2.0, 0.081)
        gl.glVertex3f(-1.1, -2.0, 0.081)
        gl.glVertex3f(-2.0, -1.1, 0.081)
        gl.glEnd()
        gl.glPopMatrix()

        # bottom alignment corner
        gl.glPushMatrix()
        gl.glColor3f(1.0, 1.0, 1.0)
        gl.glBegin(gl.GL_TRIANGLES)
        gl.glNormal3f(0.0, 0.0, -1.0)
        gl.glVertex3f(-2.0, -2.0, -0.081)
        gl.glVertex3f(-2.0, -1.1, -0.081)
        gl.glVertex3f(-1.1, -2.0, -0.081)
        gl.glEnd()
        gl.glPopMatrix()

        gl.glDisable(gl.GL_LIGHTING)

        # axis
        gl.glPushMatrix()
        gl.glTranslatef(-2.3, -2.3, -0.38)
        gl.glLineWidth(3.0)
        gl.glBegin(gl.GL_LINES)
        gl.glColor3f(1,0,0) # x axis is red
        gl.glVertex3f(0,0,0)
        gl.glVertex3f(3,0,0)
        gl.glColor3f(0,0.5,0) # y axis is green
        gl.glVertex3f(0,0,0)
        gl.glVertex3f(0,3,0)
        gl.glColor3f(0,0,1) # z axis is blue
        gl.glVertex3f(0,0,0)
        gl.glVertex3f(0,0,3)
        gl.glEnd()
        gl.glLineWidth(1.0)
        gl.glPopMatrix()

        gl.glEndList()

    def perspective(self, fov_y, aspect, z_near, z_far):
        f_height = math.tan(fov_y / 2 * (math.pi/180)) * z_near
        f_width = f_height * aspect
        self.gl.glFrustum(-f_width, f_width, -f_height, f_height, z_near, z_far)

    def resizeGL(self, width, height):
        if height == 0:
            height = 1
        gl = self.gl

        gl.glViewport(0, 0, width, height)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        self.perspective(45.0, float(width)/float(height), 0.1, 100.0)
        gl.glMatrixMode(gl.GL_MODELVIEW)

    # main drawing function.
    def paintGL(self):
        gl = self.gl

        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        # Move Right And Into The Screen
        gl.glLoadIdentity()
        gl.glTranslatef(0.0, 0.0, -5.0)
        gl.glMultMatrixf([item for line in self.m for item in line]) # call with flattened list of lists

        gl.glCallList(self.display_list)

    def quad(self, a, b, c, d, n):
        # draw a quad
        gl = self.gl

        gl.glBegin(gl.GL_QUADS)
        gl.glNormal3fv(self.normals[n])
        gl.glVertex3fv(self.vertices[a])
        gl.glVertex3fv(self.vertices[b])
        gl.glVertex3fv(self.vertices[c])
        gl.glVertex3fv(self.vertices[d])
        gl.glEnd()

    def cube(self):
        # map vertices to faces
        self.quad(0, 3, 2, 1, 5)
        self.quad(2, 3, 7, 6, 1)
        self.quad(4, 7, 3, 0, 3)
        self.quad(1, 2, 6, 5, 0)
        self.quad(7, 4, 5, 6, 2)
        self.quad(5, 4, 0, 1, 4)

    def draw_cuboid(self, x, y, z):
        gl = self.gl

        gl.glPushMatrix()
        gl.glScalef(x, y, z) # size cuboid
        self.cube()
        gl.glPopMatrix()

    def save_orientation(self):
        self.save_orientation_flag = True
