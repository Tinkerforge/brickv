# -*- coding: utf-8 -*-  
"""
IMU Plugin
Copyright (C) 2015 Olaf Lüke <olaf@tinkerforge.com>

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

from OpenGL.GL import GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT, GL_DEPTH_TEST, GL_LESS, GL_MODELVIEW, GL_POLYGON, GL_PROJECTION, GL_SMOOTH, glBegin, glClear, glClearColor, glClearDepth, glColor3f, glDepthFunc, glEnable, glEnd, glLoadIdentity, glMatrixMode, glPopMatrix, glPushMatrix, glShadeModel, glTranslatef, glVertex3fv, glViewport, glScalef, glMultMatrixf, GL_LINES, glLineWidth
from OpenGL.GLU import gluPerspective

class IMUV2GLWidget(QGLWidget):
    def __init__(self, parent=None, name=None):
        QGLWidget.__init__(self, parent, name)
        self.parent = parent
        
#        col = parent.palette().background().color()
#        self.color_background = (col.redF(), col.greenF(), col.blueF(), 1.0)
        self.color_background = (0.85, 0.85, 0.85, 1.0)
        self.color_led_red = (1.0, 0.0, 0.0)
        self.color_led_green = (0.0, 1.0, 0.0)
        self.color_board = (0.0, 0.7, 0.0)
        self.color_connector = (0.0, 0.0, 0.0)
        
        self.vertices = (
            (-1.0,-1.0,-1.0),
            (1.0,-1.0,-1.0),
            (1.0,1.0,-1.0), 
            (-1.0,1.0,-1.0), 
            (-1.0,-1.0,1.0),
            (1.0,-1.0,1.0), 
            (1.0,1.0,1.0), 
            (-1.0,1.0,1.0)
        )
        
        self.pins = [(-0.8, -0.9), (-0.8, -0.65), (-0.8, -0.4), 
                     (-0.6, -0.9), (-0.6, -0.65), (-0.6, -0.4),
                     (0.9, 0.8), (0.65, 0.8), (0.4, 0.8), (0.15, 0.8), 
                     (0.9, 0.6), (0.65, 0.6), (0.4, 0.6), (0.15, 0.6)]

        self.m = [[1, 0, 0, 0], 
                  [0, 1, 0, 0],
                  [0, 0, 1, 0],
                  [0, 0, 0, 1]]

        self.rel_x = 0
        self.rel_y = 0
        self.rel_z = 0
        self.rel_w = 0
        
        self.save_orientation_flag = False
        
    def update(self, x, y, z, w):
        if self.save_orientation_flag:
            self.rel_x = x
            self.rel_y = y
            self.rel_z = z
            self.rel_w = w
            self.save_orientation_flag = False
            self.parent.orientation_label.setText("")
            self.parent.orientation_label.setFixedHeight(0)
        
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
        glClearColor(*self.color_background)    
        glClearDepth(1.0)                   
        glDepthFunc(GL_LESS)                
        glEnable(GL_DEPTH_TEST)             
        glShadeModel(GL_SMOOTH)             
        
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()                    
    
        glMatrixMode(GL_MODELVIEW)
    
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
        glLoadIdentity()
        
        # Move Right And Into The Screen
        glTranslatef(0.0, 0.0, -5.0) 

        glMultMatrixf(self.m)
        
        # Draw board
        glColor3f(*self.color_board)
        glColor3f(0.0, 0.0, 0.0)
        self.draw_cuboid(1.0, 1.0, 0.1)
     
        # Draw USB connector
        glColor3f(0.5, 0.51, 0.58)
        glPushMatrix()
        glTranslatef(0.0, -0.8, 0.2)
        self.draw_cuboid(0.2, 0.25, 0.1)
        glPopMatrix()
        
        # Draw button right
        glPushMatrix()
        glColor3f(0.5, 0.51, 0.58)
        glTranslatef(0.65, -0.95, 0.125)
        self.draw_cuboid(0.1, 0.075, 0.05)
        glColor3f(0.0, 0.0, 0.0)
        glTranslatef(0.0, -0.075, 0.0)
        self.draw_cuboid(0.05, 0.025, 0.045)
        glPopMatrix()
        
        # Draw button left
        glPushMatrix()
        glColor3f(0.5, 0.51, 0.58)
        glTranslatef(-0.65, -0.95, 0.125)
        self.draw_cuboid(0.1, 0.075, 0.05)
        glColor3f(0.0, 0.0, 0.0)
        glTranslatef(0.0, -0.075, 0.0)
        self.draw_cuboid(0.05, 0.025, 0.045)
        glPopMatrix()
        
        # Draw btb left top
        glPushMatrix()
        glColor3f(1.0, 1.0, 1.0)
        glTranslatef(-0.75, 0.0, 0.25)
        self.draw_cuboid(0.13, 0.5, 0.15)
        glPopMatrix()
        
        # Draw btb right top
        glPushMatrix()
        glColor3f(1.0, 1.0, 1.0)
        glTranslatef(0.75, 0.0, 0.25)
        self.draw_cuboid(0.13, 0.5, 0.15)
        glPopMatrix()
        
        # Draw btb left bottom
        glPushMatrix()
        glColor3f(1.0, 1.0, 1.0)
        glTranslatef(-0.75, 0.0, -0.2)
        self.draw_cuboid(0.13, 0.5, 0.1)
        glPopMatrix()
        
        # Draw btb right bottom
        glPushMatrix()
        glColor3f(1.0, 1.0, 1.0)
        glTranslatef(0.75, 0.0, -0.2)
        self.draw_cuboid(0.13, 0.5, 0.1)
        glPopMatrix()
        
        # Draw bricklet port left
        glPushMatrix()
        glColor3f(1.0, 1.0, 1.0)
        glTranslatef(-0.425, 0.9, -0.125)
        self.draw_cuboid(0.325, 0.1, 0.05)
        glPopMatrix()
        
                
        # Draw bricklet port right
        glPushMatrix()
        glColor3f(1.0, 1.0, 1.0)
        glTranslatef(0.425, 0.9, -0.125)
        self.draw_cuboid(0.325, 0.1, 0.05)
        glPopMatrix()
        
        # Draw Axis
        glPushMatrix()
        glTranslatef(-1.2, -1.2, -0.3)
        glLineWidth(5.0)
        
        glBegin(GL_LINES)
        glColor3f(1,0,0) # x axis is red
        glVertex3fv((0,0,0))
        glVertex3fv((2,0,0))
        glColor3f(0,0.5,0) # y axis is green
        glVertex3fv((0,0,0))
        glVertex3fv((0,2,0))
        glColor3f(0,0,1) # z axis is blue
        glVertex3fv((0,0,0))
        glVertex3fv((0,0,2))
        glEnd()
        
        glPopMatrix()
        
    def polygon(self, a, b, c, d):
        # draw a polygon
        glBegin(GL_POLYGON)
        glVertex3fv(self.vertices[a])
        glVertex3fv(self.vertices[b])
        glVertex3fv(self.vertices[c])
        glVertex3fv(self.vertices[d])
        glEnd()

    def cube(self):
        # map vertices to faces
        self.polygon(0, 3, 2, 1)
        self.polygon(2, 3, 7, 6)
        self.polygon(4, 7, 3, 0)
        self.polygon(1, 2, 6, 5)
        self.polygon(7, 4, 5, 6)
        self.polygon(5, 4, 0, 1)

    def draw_cuboid(self, x, y, z):
        glPushMatrix()
        glScalef(x, y, z) # size cuboid
        self.cube()
        glPopMatrix()

    def save_orientation(self):
        self.save_orientation_flag = True
