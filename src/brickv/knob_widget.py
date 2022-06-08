# -*- coding: utf-8 -*-
"""
brickv (Brick Viewer)
Copyright (C) 2014-2015, 2017 Matthias Bolte <matthias@tinkerforge.com>
Copyright (C) 2021 Erik Fleckstein <erik@tinkerforge.com>

knob_widget.py: Round slider

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

import math

from PyQt5.QtCore import Qt, QPoint, QPointF
from PyQt5.QtWidgets import QWidget, QSizePolicy
from PyQt5.QtGui import QPainter, QColor, QPen, QFontMetrics, QRadialGradient, QPolygonF

EPSILON = 0.000001
DEBUG = False

class KnobWidget(QWidget):
    STYLE_ROUND = 1
    STYLE_NEEDLE = 2

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

        self.minimum_value = -100
        self.maximum_value = 100
        self.value_range = self.maximum_value - self.minimum_value
        self.total_angle = 200 # degree
        self.pressed = False
        self.scale_visible = True
        self.scale_arc_visible = True
        self.scale_text_visible = True
        self.scale_step_size = 10
        self.scale_step_divisions = 2
        self.knob_radius = 20 # px
        self.knob_style = KnobWidget.STYLE_ROUND
        self.dynamic_resize = False
        self.dynamic_knob_radius = None
        self.needle_base_radius = 7 # px
        self.needle_color = Qt.red
        self.knob_to_scale = 4 # px
        self.knob_scaleless_to_border = 1 # px, applied if scale not visible
        self.base_color = QColor(245, 245, 245)
        self.base_color_pressed = Qt.red
        self.mark_color = Qt.black
        self.border_color = QColor(190, 190, 190)
        self.tick_size_large = 9 # px
        self.tick_size_small = 5 # px
        self.tick_to_text = 4 # px
        self.text_to_border = 2 # px
        self.text_radius = None
        self.title_text = None
        self.value = self.value_range / 2
        self.value_factor = float(self.value - self.minimum_value) / self.value_range
        self.font_metrics = QFontMetrics(self.font())

        self.recalculate_size()

    # override QWidget.resizeEvent
    def resizeEvent(self, event):
        QWidget.resizeEvent(self, event)

        self.recalculate_size()

    # override QWidget.paintEvent
    # Disable pylint warning for knob_radius (which can not be None, as it is read from
    # self.dynamic_knob_radius if self.dynamic_resize, which, when set first recalculates
    # the dynamic_knob_radius, and then calls update
    #pylint: disable=invalid-unary-operand-type
    def paintEvent(self, _event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        width = self.width()
        height = self.height()

        if self.dynamic_resize:
            knob_radius = self.dynamic_knob_radius
        else:
            knob_radius = self.knob_radius

        # ensure that the center point is in the middle of a pixel to ensure
        # that exact vertial and horizantal ticks are drawn exactly 1px wide
        x = math.floor(width / 2.0) + 0.5
        y = math.floor(height / 2.0) + 0.5

        if DEBUG:
            painter.fillRect(0, 0, width, height, Qt.yellow)

        painter.translate(x, y)

        if self.knob_style == KnobWidget.STYLE_NEEDLE:
            r = min(x, y) - 1

            painter.setPen(Qt.white)
            painter.setBrush(Qt.white)
            painter.drawEllipse(QPoint(0, 0), r, r)

        angle = self.value_factor * self.total_angle - (self.total_angle / 2.0)

        # draw base knob or needle spike
        if self.knob_style == KnobWidget.STYLE_ROUND:
            painter.setPen(self.border_color)

            if self.pressed:
                gradient = QRadialGradient(0, 0, knob_radius)
                gradient.setColorAt(0, self.base_color_pressed)
                gradient.setColorAt(0.85, self.base_color)
                gradient.setColorAt(1, self.base_color)

                painter.setBrush(gradient)
            else:
                painter.setBrush(self.base_color)

            painter.drawEllipse(QPoint(0, 0), knob_radius, knob_radius)
        elif self.knob_style == KnobWidget.STYLE_NEEDLE:
            painter.save()
            painter.rotate(angle)
            painter.setPen(self.needle_color)
            painter.setBrush(self.needle_color)

            needle = QPolygonF()
            needle.append(QPointF(self.needle_base_radius * 0.6, 0))
            needle.append(QPointF(0, -knob_radius))
            needle.append(QPointF(-self.needle_base_radius * 0.6, 0))

            painter.drawPolygon(needle)
            painter.restore()

        # draw knob mark or needle base
        if self.knob_style == KnobWidget.STYLE_ROUND:
            painter.save()
            painter.rotate(angle)
            painter.setPen(QPen(self.mark_color, 2))
            painter.drawLine(0, int(-knob_radius * 0.4), 0, int(-knob_radius * 0.8))
            painter.restore()
        elif self.knob_style == KnobWidget.STYLE_NEEDLE:
            painter.setPen(self.border_color)
            painter.setBrush(self.base_color)
            painter.drawEllipse(QPoint(0, 0), self.needle_base_radius, self.needle_base_radius)

        if self.scale_visible:
            painter.setPen(Qt.black)

            # draw scale arc
            if self.scale_arc_visible:
                painter.drawArc(-knob_radius - self.knob_to_scale,
                                -knob_radius - self.knob_to_scale,
                                knob_radius * 2 + self.knob_to_scale * 2,
                                knob_radius * 2 + self.knob_to_scale * 2,
                                int((90 + self.total_angle / 2) * 16), -self.total_angle * 16)

            # draw scale ticks
            def value_to_angle(value):
                return (float(value - self.minimum_value) / self.value_range) * self.total_angle - (self.total_angle / 2.0)

            value = self.minimum_value

            while value <= self.maximum_value:
                angle = value_to_angle(value)

                painter.save()
                painter.rotate(value_to_angle(value))
                painter.drawLine(0, int(-knob_radius - self.knob_to_scale),
                                 0, int(-knob_radius - self.knob_to_scale - self.tick_size_large))

                if self.scale_text_visible:
                    p = painter.worldTransform().map(QPoint(0, int(-knob_radius - \
                                                               self.knob_to_scale - \
                                                               self.tick_size_large - \
                                                               self.tick_to_text - \
                                                               self.text_radius)))

                painter.restore()

                if self.scale_text_visible:
                    if DEBUG:
                        painter.save()
                        painter.setPen(QColor(255, 0, 0, 50))
                        painter.setBrush(QColor(255, 0, 0, 50))
                        painter.drawEllipse(QPoint(p.x() - x, p.y() - y),
                                            self.text_radius, self.text_radius)
                        painter.restore()

                    painter.drawText(int(p.x() - x - 30), int(p.y() - y - 30), 60, 60,
                                     int(Qt.TextDontClip | Qt.AlignHCenter | Qt.AlignVCenter),
                                     str(value))

                for i in range(1, self.scale_step_divisions):
                    sub_value = value + (float(self.scale_step_size) * i) / self.scale_step_divisions

                    if sub_value > self.maximum_value:
                        break

                    painter.save()
                    painter.rotate(value_to_angle(sub_value))
                    painter.drawLine(0,int(-knob_radius - self.knob_to_scale),
                                     0,int(-knob_radius - self.knob_to_scale - self.tick_size_small))
                    painter.restore()

                value += self.scale_step_size

        if self.title_text != None:
            painter.drawText(int(-knob_radius), int(knob_radius - 30),
                             int(knob_radius * 2), 60,
                             int(Qt.TextDontClip | Qt.AlignHCenter | Qt.AlignVCenter),
                             self.title_text)

    def recalculate_size(self):
        if self.scale_visible:
            if self.scale_text_visible:
                text_width = 0
                text_height = 0
                value = self.minimum_value

                while value <= self.maximum_value:
                    text_rect = self.font_metrics.boundingRect(str(value))
                    text_width = max(text_width, text_rect.width())
                    text_height = max(text_height, text_rect.height())
                    value += self.scale_step_size

                self.text_radius = math.sqrt((text_width / 2.0) ** 2 + (text_height / 2.0) ** 2)
            else:
                self.text_radius = 0

            additional_radius = self.knob_to_scale + \
                                self.tick_size_large + \
                                self.tick_to_text + \
                                self.text_radius * 2 + \
                                self.text_to_border
        else:
            additional_radius = self.knob_scaleless_to_border

        diameter = int((self.knob_radius + additional_radius) * 2)

        self.setMinimumSize(diameter, diameter)

        if self.dynamic_resize:
            radius = min(self.width(), self.height()) / 2
            self.dynamic_knob_radius = radius - additional_radius

    def set_scale_visible(self, visible):
        self.scale_visible = visible

        self.recalculate_size()
        self.update()

    def set_scale_arc_visible(self, visible):
        self.scale_arc_visible = visible

        self.update()

    def set_scale_text_visible(self, visible):
        self.scale_text_visible = visible

        self.recalculate_size()
        self.update()

    def set_total_angle(self, total_angle):
        self.total_angle = max(min(total_angle, 360), 1)

        self.recalculate_size()
        self.set_value(self.value)

    def set_pressed(self, pressed):
        self.pressed = pressed

        self.update()

    def set_range(self, minimum_value, maximum_value):
        self.minimum_value = minimum_value
        self.maximum_value = maximum_value

        # Don't allow min=max value, otherwise we have a value_range of 0 which
        # results in division by zero in some parts of the code
        if maximum_value == minimum_value:
            self.maximum_value = maximum_value + 1
        else:
            self.maximum_value = maximum_value

        self.value_range = self.maximum_value - self.minimum_value

        self.recalculate_size()
        self.set_value(self.value)

    def set_knob_radius(self, radius):
        self.knob_radius = max(1, radius)

        self.recalculate_size()
        self.update()

    def set_knob_style(self, style):
        self.knob_style = style

        self.update()

    def set_dynamic_resize_enabled(self, enable):
        self.dynamic_resize = enable

        if self.dynamic_resize:
            self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        else:
            self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

        self.recalculate_size()
        self.update()

    def set_scale(self, scale_step_size, scale_step_divisions):
        self.scale_step_size = max(EPSILON, scale_step_size)
        self.scale_step_divisions = scale_step_divisions

        self.recalculate_size()
        self.update()

    def set_title_text(self, text):
        self.title_text = text

        self.update()

    def set_value(self, value):
        self.value = max(min(value, self.maximum_value), self.minimum_value)
        self.value_factor = float(self.value - self.minimum_value) / self.value_range

        self.update()

    def get_value(self):
        return self.value
