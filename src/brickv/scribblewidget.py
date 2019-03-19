"""
Scribble Widget
Copyright (C) 2011-2012 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2014, 2016 Matthias Bolte <matthias@tinkerforge.com>

scribblewidget.py: Scribble Widget Implementation

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

from PyQt5.QtCore import Qt, QSize, QPoint, QRect, pyqtSignal
from PyQt5.QtGui import QImage, QPainter, QPen, QPalette
from PyQt5.QtWidgets import QWidget

class ScribbleWidget(QWidget):
    scribbling_started = pyqtSignal()

    def __init__(self, width, height, scaling_factor, foreground_color, background_color, outline_color=None, enable_grid=True, grid_color=None, parent=None):
        super().__init__(parent)

        self.setAttribute(Qt.WA_StaticContents)
        self.scaling_factor = scaling_factor

        self.setFixedSize(width*scaling_factor + 2, height*scaling_factor + 2) # + 2 for outline
        if outline_color is None:
            self._pen = QPen(self.palette().color(QPalette.WindowText))
        else:
            self._pen = QPen(outline_color)

        self.inner = ScribbleWidget.ScribbleArea(width, height, scaling_factor, foreground_color, background_color, enable_grid, grid_color, self)
        self.inner.move(1, 1)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(self._pen)
        painter.drawRect(QRect(0, 0, self.width() - 1, self.height() - 1))

    def paint_overlay(self, event, painter):
        pass

    def foreground_color(self):
        return self.inner.foreground_color

    def background_color(self):
        return self.inner.background_color

    def set_foreground_color(self, color):
        self.inner.set_foreground_color(color)

    def array_draw(self, r, g, b, scale=1):
        self.inner.array_draw(r, g, b, scale)

    def fill_image(self, color):
        self.inner.fill_image(color)

    def clear_image(self):
        self.inner.clear_image()

    def draw_line_to(self, end_point):
        self.inner.draw_line_to(end_point)

    def image(self):
        return self.inner.image

    class ScribbleArea(QWidget):
        def __init__(self, width, height, scaling_factor, foreground_color, background_color, enable_grid, grid_color, parent):
            super().__init__(parent)

            self.parent = parent
            self.scribbling = 0

            self.width = width
            self.height = height
            self.scaling_factor = scaling_factor
            self.pen_width = 1
            self.foreground_color = foreground_color
            self.background_color = background_color
            self.grid_enabled = enable_grid

            if grid_color is not None:
                self.grid_color = grid_color
            else:
                self.grid_color = self.palette().color(QPalette.Window)

            self.image = QImage(QSize(width, height), QImage.Format_RGB32)

            self.setFixedSize(width*self.scaling_factor, height*self.scaling_factor)
            self.last_point = QPoint()
            self.clear_image()

        def set_foreground_color(self, color):
            self.foreground_color = color

        def array_draw(self, r, g, b, scale=1):
            for i in range(len(r)):
                self.image.setPixel(QPoint(i%self.width, i//self.width), (r[i]*scale << 16) | (g[i]*scale << 8) | b[i]*scale)

            self.update()

        def fill_image(self, color):
            self.image.fill(color)
            self.update()

        def clear_image(self):
            self.image.fill(self.background_color)
            self.update()

        def mousePressEvent(self, event):
            self.parent.scribbling_started.emit()

            if event.button() == Qt.LeftButton:
                self.last_point = event.pos()
                self.scribbling = 1
            elif event.button() == Qt.RightButton:
                self.last_point = event.pos()
                self.scribbling = 2

        def mouseMoveEvent(self, event):
            if (event.buttons() & Qt.LeftButton) and self.scribbling == 1:
                self.draw_line_to(event.pos())
            elif (event.buttons() & Qt.RightButton) and self.scribbling == 2:
                self.draw_line_to(event.pos())

        def mouseReleaseEvent(self, event):
            if event.button() == Qt.LeftButton and self.scribbling == 1:
                self.draw_line_to(event.pos())
                self.scribbling = 0
            elif event.button() == Qt.RightButton and self.scribbling == 2:
                self.draw_line_to(event.pos())
                self.scribbling = 0

        def paintEvent(self, event):
            painter = QPainter(self)
            painter.drawImage(QRect(0, 0, super().width(), super().height()), self.image)

            if self.grid_enabled:
                painter.setPen(QPen(self.grid_color))

                for x in range(1, self.width):
                    painter.drawLine(x * self.scaling_factor, 0, x * self.scaling_factor, super().height())

                for y in range(1, self.height):
                    painter.drawLine(0, y * self.scaling_factor, super().width(), y * self.scaling_factor)

            self.parent.paint_overlay(event, painter)

        def draw_line_to(self, end_point):
            painter = QPainter(self.image)
            painter.setPen(QPen(self.foreground_color if self.scribbling == 1 else self.background_color,
                                self.pen_width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))

            painter.drawLine(QPoint(self.last_point.x()//self.scaling_factor, self.last_point.y()//self.scaling_factor),
                             QPoint(end_point.x()//self.scaling_factor, end_point.y()//self.scaling_factor))

            self.update()
            self.last_point = QPoint(end_point)
