# -*- coding: utf-8 -*-
"""
IMU Plugin
Copyright (C) 2015 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2015 Matthias Bolte <matthias@tinkerforge.com>

imu_v2_gl_widget.py: IMU 2.0 OpenGL representation

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

from PyQt4.QtOpenGL import QGLWidget

from OpenGL.GL import GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT, GL_DEPTH_TEST, \
                      GL_LESS, GL_MODELVIEW, GL_QUADS, GL_PROJECTION, GL_SMOOTH, \
                      GL_LINES, GL_COMPILE, GL_TRIANGLES, GL_CULL_FACE, glBegin, \
                      glCallList, glClear, glClearColor, glClearDepth, glColor3f, \
                      glDepthFunc, glEnable, glEnd, glEndList, glGenLists, glLoadIdentity, \
                      glMatrixMode, glNewList, glPopMatrix, glPushMatrix, glShadeModel, \
                      glTranslatef, glVertex3fv, glVertex3f, glViewport, glScalef, \
                      glMultMatrixf, glLineWidth
from OpenGL.GLU import gluPerspective

class IMUV2GLWidget(QGLWidget):
    def __init__(self, parent=None, name=None):
        QGLWidget.__init__(self, parent, name)
        self.parent = parent

        self.vertices = [
            (-0.5,-0.5,-0.5),
            (0.5,-0.5,-0.5),
            (0.5,0.5,-0.5),
            (-0.5,0.5,-0.5),
            (-0.5,-0.5,0.5),
            (0.5,-0.5,0.5),
            (0.5,0.5,0.5),
            (-0.5,0.5,0.5)
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

    def update(self, w, x, y, z):
        if self.save_orientation_flag:
            self.rel_x = x
            self.rel_y = y
            self.rel_z = z
            self.rel_w = w
            self.save_orientation_flag = False
            self.has_save_orientation = True
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

        self.updateGL()

    def initializeGL(self):
        glClearColor(0.85, 0.85, 0.85, 1.0)
        glClearDepth(1.0)
        glDepthFunc(GL_LESS)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        glShadeModel(GL_SMOOTH)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        self.display_list = glGenLists(1)
        glNewList(self.display_list, GL_COMPILE)
        glScalef(0.5, 0.5, 0.5)

        # board
        glColor3f(0.0, 0.0, 0.0)
        self.draw_cuboid(4.0, 4.0, 0.16)

        # USB connector
        glPushMatrix()
        glColor3f(0.5, 0.51, 0.58)
        glTranslatef(0.0, -1.6, 0.28)
        self.draw_cuboid(0.75, 0.9, 0.4)
        glPopMatrix()

        # right button
        glPushMatrix()
        glColor3f(0.5, 0.51, 0.58)
        glTranslatef(1.15, -1.85, 0.16)
        self.draw_cuboid(0.4, 0.3, 0.16)
        glColor3f(0.0, 0.0, 0.0)
        glTranslatef(0.0, -0.155, 0.025)
        self.draw_cuboid(0.18, 0.1, 0.08)
        glPopMatrix()

        # left button
        glPushMatrix()
        glColor3f(0.5, 0.51, 0.58)
        glTranslatef(-1.15, -1.85, 0.16)
        self.draw_cuboid(0.4, 0.3, 0.16)
        glColor3f(0.0, 0.0, 0.0)
        glTranslatef(0.0, -0.155, 0.025)
        self.draw_cuboid(0.18, 0.1, 0.08)
        glPopMatrix()

        # left btb top
        glPushMatrix()
        glColor3f(1.0, 1.0, 1.0)
        glTranslatef(-1.65, 0.0, 0.38)
        self.draw_cuboid(0.5, 1.4, 0.9)
        glPopMatrix()

        # right btb top
        glPushMatrix()
        glColor3f(1.0, 1.0, 1.0)
        glTranslatef(1.65, 0.0, 0.38)
        self.draw_cuboid(0.5, 1.4, 0.9)
        glPopMatrix()

        # left btb bottom
        glPushMatrix()
        glColor3f(1.0, 1.0, 1.0)
        glTranslatef(-1.65, 0.0, -0.33)
        self.draw_cuboid(0.5, 1.4, 0.5)
        glPopMatrix()

        # right btb bottom
        glPushMatrix()
        glColor3f(1.0, 1.0, 1.0)
        glTranslatef(1.65, 0.0, -0.33)
        self.draw_cuboid(0.5, 1.4, 0.5)
        glPopMatrix()

        # left bricklet port
        glPushMatrix()
        glColor3f(1.0, 1.0, 1.0)
        glTranslatef(-0.85, 1.8, -0.23)
        self.draw_cuboid(1.2, 0.4, 0.3)
        glPopMatrix()

        # right bricklet port
        glPushMatrix()
        glColor3f(1.0, 1.0, 1.0)
        glTranslatef(0.85, 1.8, -0.23)
        self.draw_cuboid(1.2, 0.4, 0.3)
        glPopMatrix()

        # left direction LED
        glPushMatrix()
        glColor3f(0.0, 0.5, 0.0)
        glTranslatef(-1.05, 1.425, 0.115)
        self.draw_cuboid(0.1, 0.2, 0.07)
        glPopMatrix()

        # top direction LED
        glPushMatrix()
        glColor3f(0.0, 0.5, 0.0)
        glTranslatef(-0.675, 1.8, 0.115)
        self.draw_cuboid(0.2, 0.1, 0.07)
        glPopMatrix()

        # right direction LED
        glPushMatrix()
        glColor3f(0.0, 0.5, 0.0)
        glTranslatef(-0.3, 1.425, 0.115)
        self.draw_cuboid(0.1, 0.2, 0.07)
        glPopMatrix()

        # bottom direction LED
        glPushMatrix()
        glColor3f(0.0, 0.5, 0.0)
        glTranslatef(-0.675, 1.05, 0.115)
        self.draw_cuboid(0.2, 0.1, 0.07)
        glPopMatrix()

        # left y orientation LED
        glPushMatrix()
        glColor3f(0.0, 0.0, 1.0)
        glTranslatef(0.275, 1.7, 0.115)
        self.draw_cuboid(0.1, 0.2, 0.07)
        glPopMatrix()

        # right y orientation LED
        glPushMatrix()
        glColor3f(1.0, 0.0, 0.0)
        glTranslatef(0.425, 1.7, 0.115)
        self.draw_cuboid(0.1, 0.2, 0.07)
        glPopMatrix()

        # top z orientation LED
        glPushMatrix()
        glColor3f(1.0, 0.0, 0.0)
        glTranslatef(0.35, 1.15, 0.115)
        self.draw_cuboid(0.2, 0.1, 0.07)
        glPopMatrix()

        # bottom z orientation LED
        glPushMatrix()
        glColor3f(0.0, 0.0, 1.0)
        glTranslatef(0.35, 1.0, 0.115)
        self.draw_cuboid(0.2, 0.1, 0.07)
        glPopMatrix()

        # top x orientation LED
        glPushMatrix()
        glColor3f(1.0, 0.0, 0.0)
        glTranslatef(1.0, 1.15, 0.115)
        self.draw_cuboid(0.2, 0.1, 0.07)
        glPopMatrix()

        # bottom x orientation LED
        glPushMatrix()
        glColor3f(0.0, 0.0, 1.0)
        glTranslatef(1.0, 1.0, 0.115)
        self.draw_cuboid(0.2, 0.1, 0.07)
        glPopMatrix()

        # top alignment corner
        glPushMatrix()
        glColor3f(1.0, 1.0, 1.0)
        glBegin(GL_TRIANGLES)
        glVertex3f(-2.0, -2.0, 0.081)
        glVertex3f(-1.1, -2.0, 0.081)
        glVertex3f(-2.0, -1.1, 0.081)
        glEnd()
        glPopMatrix()

        # bottom alignment corner
        glPushMatrix()
        glColor3f(1.0, 1.0, 1.0)
        glBegin(GL_TRIANGLES)
        glVertex3f(-2.0, -2.0, -0.081)
        glVertex3f(-2.0, -1.1, -0.081)
        glVertex3f(-1.1, -2.0, -0.081)
        glEnd()
        glPopMatrix()

        # axis
        glPushMatrix()
        glTranslatef(-2.3, -2.3, -0.38)
        glLineWidth(3.0)
        glBegin(GL_LINES)
        glColor3f(1,0,0) # x axis is red
        glVertex3fv((0,0,0))
        glVertex3fv((3.5,0,0))
        glColor3f(0,0.5,0) # y axis is green
        glVertex3fv((0,0,0))
        glVertex3fv((0,3.5,0))
        glColor3f(0,0,1) # z axis is blue
        glVertex3fv((0,0,0))
        glVertex3fv((0,0,3.5))
        glEnd()
        glPopMatrix()

        glEndList()

    def resizeGL(self, width, height):
        if height == 0:
            height = 1

        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, float(width)/float(height), 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)

    # main drawing function.
    def paintGL(self):
        if self.parent.ipcon == None:
            return

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Move Right And Into The Screen
        glLoadIdentity()
        glTranslatef(0.0, 0.0, -5.0)
        glMultMatrixf(self.m)

        glCallList(self.display_list)

    def quad(self, a, b, c, d, n):
        # draw a quad
        glBegin(GL_QUADS)
        glVertex3fv(self.vertices[a])
        glVertex3fv(self.vertices[b])
        glVertex3fv(self.vertices[c])
        glVertex3fv(self.vertices[d])
        glEnd()

    def cube(self):
        # map vertices to faces
        self.quad(0, 3, 2, 1, 5)
        self.quad(2, 3, 7, 6, 1)
        self.quad(4, 7, 3, 0, 3)
        self.quad(1, 2, 6, 5, 0)
        self.quad(7, 4, 5, 6, 2)
        self.quad(5, 4, 0, 1, 4)

    def draw_cuboid(self, x, y, z):
        glPushMatrix()
        glScalef(x, y, z) # size cuboid
        self.cube()
        glPopMatrix()

    def save_orientation(self):
        self.save_orientation_flag = True
