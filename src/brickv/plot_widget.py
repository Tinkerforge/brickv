# -*- coding: utf-8 -*-
"""
brickv (Brick Viewer)
Copyright (C) 2011 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2014 Matthias Bolte <matthias@tinkerforge.com>

plot_widget.py: Graph for simple value over time representation

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

from PyQt4.QtGui import QVBoxLayout, QHBoxLayout, QWidget, QToolButton, \
                        QPushButton, QPainter, QSizePolicy, QFont, QFontMetrics, \
                        QPixmap, QIcon, QColor, QCursor, QPen
from PyQt4.QtCore import QTimer, Qt, QPointF, QSize
import math
import functools

EPSILON = 0.000001
DEBUG = False

def istr(i):
    return str(int(i))

def fstr(f):
    s = ('%.10f' % f).rstrip('0')

    if s.endswith('.'):
        s += '0'

    return s

def fuzzy_eq(a, b):
    return abs(a - b) < EPSILON

def fuzzy_leq(a, b):
    return a < b or fuzzy_eq(a, b)

def fuzzy_geq(a, b):
    return a > b or fuzzy_eq(a, b)

class Scale:
    def __init__(self, tick_text_font, title_text_font):
        self.axis_line_thickness = 1 # px, fixed

        self.tick_mark_thickness = 1 # px, fixed
        self.tick_mark_size_small = 5 # px, fixed
        self.tick_mark_size_medium = 7 # px, fixed
        self.tick_mark_size_large = 9 # px, fixed

        self.tick_text_font = tick_text_font
        self.tick_text_font_metrics = QFontMetrics(self.tick_text_font)
        self.tick_text_height = self.tick_text_font_metrics.boundingRect('0123456789').height()
        self.tick_text_height_half = int(math.ceil(self.tick_text_height / 2.0))

        self.tick_value_to_str = istr

        self.title_text_font = title_text_font
        self.title_text_font_metrics = QFontMetrics(self.title_text_font)

class XScale(Scale):
    def __init__(self, tick_text_font, title_text_font, title_text):
        Scale.__init__(self, tick_text_font, title_text_font)

        self.tick_mark_to_tick_text = 0 # px, fixed

        self.tick_text_to_title_text = 4 # px, fixed

        self.title_text = title_text
        self.title_text_height = self.title_text_font_metrics.boundingRect(self.title_text).height()
        self.title_text_to_border = 2 # px, fixed

        self.total_height = self.axis_line_thickness + \
                            self.tick_mark_size_large + \
                            self.tick_mark_to_tick_text + \
                            self.tick_text_height + \
                            self.tick_text_to_title_text + \
                            self.title_text_height + \
                            self.title_text_to_border # px, fixed

    def draw(self, painter, factor, tick_value_min, tick_count):
        factor_int = int(math.floor(factor))
        text_flags = Qt.TextDontClip | Qt.AlignHCenter | Qt.AlignBottom

        # axis line
        axis_line_length = int(math.floor(factor * tick_count))

        painter.drawLine(0, 0, axis_line_length - 1, 0)

        # ticks
        tick_text_y = self.axis_line_thickness + \
                      self.tick_mark_size_large + \
                      self.tick_mark_to_tick_text
        tick_text_width = factor_int + self.tick_mark_thickness + factor_int
        tick_text_height = self.tick_text_height

        painter.setFont(self.tick_text_font)

        for i in range(tick_count):
            x = round(factor * i)
            tick_value = int(tick_value_min + i)

            if (tick_value % 5) == 0:
                tick_mark_size = self.tick_mark_size_large
                tick_text_x = x - factor_int

                if DEBUG:
                    painter.fillRect(tick_text_x, tick_text_y,
                                     tick_text_width, tick_text_height,
                                     Qt.yellow)

                painter.drawText(tick_text_x, tick_text_y,
                                 tick_text_width, tick_text_height,
                                 text_flags,
                                 self.tick_value_to_str(tick_value))
            else:
                tick_mark_size = self.tick_mark_size_small

            painter.drawLine(x, 0, x, tick_mark_size)

        # title
        title_text_x = 0
        title_text_y = self.axis_line_thickness + \
                       self.tick_mark_size_large + \
                       self.tick_mark_to_tick_text + \
                       self.tick_text_height + \
                       self.tick_text_to_title_text
        title_text_width = axis_line_length
        title_text_height = self.title_text_height

        if DEBUG:
            painter.fillRect(title_text_x, title_text_y,
                             title_text_width, title_text_height,
                             Qt.yellow)

        painter.setFont(self.title_text_font)
        painter.drawText(title_text_x, title_text_y,
                         title_text_width, title_text_height,
                         text_flags, self.title_text)

class YScale(Scale):
    def __init__(self, tick_text_font, title_text_font, title_text):
        Scale.__init__(self, tick_text_font, title_text_font)

        self.value_min = None # set by update_tick_config
        self.value_max = None # set by update_tick_config

        self.step_size = None # set by update_tick_config
        self.step_subdivision_count = None # set by update_tick_config

        self.tick_mark_to_tick_text = 3 # px, fixed

        self.tick_text_to_title_text = 7 # px, fixed
        self.tick_text_max_width = 10 # px, initial value, calculated in update_tick_config

        self.title_text = title_text
        self.title_text_to_border = 2 # px, fixed
        self.title_text_height = None # set by update_title_text_height
        self.title_text_pixmap = None

        self.total_width = None # set by update_total_width

        self.update_title_text_height(1000)
        self.update_tick_config(-1.0, 1.0, 1.0, 5)

    def update_tick_config(self, value_min, value_max, step_size, step_subdivision_count):
        self.value_min = value_min
        self.value_max = value_max
        self.step_size = step_size
        self.step_subdivision_count = step_subdivision_count

        if fuzzy_geq(self.step_size, 1.0):
            self.tick_value_to_str = istr
        else:
            self.tick_value_to_str = fstr

        value = self.value_min
        tick_text_max_width = self.tick_text_font_metrics.width(self.tick_value_to_str(value))

        while fuzzy_leq(value, self.value_max):
            tick_text_max_width = max(tick_text_max_width, self.tick_text_font_metrics.width(self.tick_value_to_str(value)))
            value += self.step_size

        self.tick_text_max_width = tick_text_max_width

        self.update_total_width()

    def update_title_text_height(self, max_width):
        self.title_text_height = self.title_text_font_metrics.boundingRect(0, 0, max_width, 1000,
                                                                           Qt.TextWordWrap | Qt.AlignHCenter | Qt.AlignTop,
                                                                           self.title_text).height()

        self.update_total_width()

    def update_total_width(self):
        self.total_width = self.axis_line_thickness + \
                           self.tick_mark_size_large + \
                           self.tick_mark_to_tick_text + \
                           self.tick_text_max_width + \
                           self.tick_text_to_title_text + \
                           self.title_text_height + \
                           self.title_text_to_border

    def draw(self, painter, height, factor):
        # axis line
        painter.drawLine(-self.axis_line_thickness, 0, -self.axis_line_thickness, -height + 1)

        # ticks
        painter.setFont(self.tick_text_font)

        tick_text_x = -self.axis_line_thickness - \
                      self.tick_mark_size_large - \
                      self.tick_mark_to_tick_text - \
                      self.tick_text_max_width
        tick_text_width = self.tick_text_max_width
        tick_text_height = self.tick_text_height_half * 2

        value = self.value_min

        while fuzzy_leq(value, self.value_max):
            y = -int(round((value - self.value_min) * factor))

            painter.drawLine(-self.axis_line_thickness, y,
                             -self.axis_line_thickness - self.tick_mark_size_large, y)

            tick_text_y = y - self.tick_text_height_half

            if DEBUG:
                painter.fillRect(tick_text_x, tick_text_y,
                                 tick_text_width, tick_text_height,
                                 Qt.yellow)

            painter.drawText(tick_text_x, tick_text_y, tick_text_width, tick_text_height,
                             Qt.TextDontClip | Qt.AlignRight | Qt.AlignVCenter,
                             self.tick_value_to_str(value))


            for i in range(1, self.step_subdivision_count):
                subvalue = value + (self.step_size * i / self.step_subdivision_count)

                if not fuzzy_leq(subvalue, self.value_max):
                    break

                suby = -int(round((subvalue - self.value_min) * factor))

                if i % 2 == 0 and self.step_subdivision_count % 2 == 0:
                    tick_mark_size = self.tick_mark_size_medium
                else:
                    tick_mark_size = self.tick_mark_size_small

                painter.drawLine(-self.axis_line_thickness, suby,
                                 -self.axis_line_thickness - tick_mark_size, suby)

            value += self.step_size

        # title
        title_width = height
        title_height = self.title_text_height

        if self.title_text_pixmap == None or self.title_text_pixmap.size() != QSize(title_width, title_height):
            self.title_text_pixmap = QPixmap(title_width, title_height)

            if DEBUG:
                self.title_text_pixmap.fill(Qt.yellow)
            else:
                self.title_text_pixmap.fill(QColor(0, 0, 0, 0))

            title_painter = QPainter(self.title_text_pixmap)
            title_painter.setFont(self.title_text_font)
            title_painter.drawText(0, 0, title_width, title_height,
                                  Qt.TextWordWrap | Qt.TextDontClip | Qt.AlignHCenter | Qt.AlignTop,
                                  self.title_text)
            title_painter = None

        painter.save()
        painter.rotate(-90)

        title_x = -1
        title_y = -self.axis_line_thickness - \
                  self.tick_mark_size_large - \
                  self.tick_mark_to_tick_text - \
                  self.tick_text_max_width - \
                  self.tick_text_to_title_text - \
                  title_height

        painter.drawPixmap(title_x, title_y, self.title_text_pixmap)

        painter.restore()

class Plot(QWidget):
    def __init__(self, parent, y_scale_title_text, plots):
        QWidget.__init__(self, parent)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.plots = plots
        self.history_length_x = 20 # seconds
        self.curve_outer_border = 5 # px, fixed
        self.curve_to_scale = 8 # px, fixed
        self.cross_hair_visible = False

        self.tick_text_font = self.font()

        self.title_text_font = self.font()
        self.title_text_font.setPointSize(round(self.title_text_font.pointSize() * 1.2))
        self.title_text_font.setBold(True)

        self.x_scale = XScale(self.tick_text_font, self.title_text_font, 'Time [s]')

        self.y_scale = YScale(self.tick_text_font, self.title_text_font, y_scale_title_text)
        self.y_scale_fixed = False
        self.y_scale_height_offset = max(self.curve_outer_border, self.y_scale.tick_text_height_half) # px, from top

        self.clear_graph()

    # override QWidget.sizeHint
    def sizeHint(self):
        return QSize(600, 300)

    # override QWidget.resizeEvent
    def resizeEvent(self, event):
        height = event.size().height()
        max_width = height - self.y_scale_height_offset - self.x_scale.total_height - self.curve_to_scale

        self.y_scale.update_title_text_height(max_width)

        QWidget.resizeEvent(self, event)

    # override QWidget.paintEvent
    def paintEvent(self, event):
        painter = QPainter(self)
        width = self.width()
        height = self.height()
        curve_width = width - self.y_scale.total_width - self.curve_to_scale - self.curve_outer_border
        curve_height = height - self.y_scale_height_offset - self.x_scale.total_height - self.curve_to_scale

        if DEBUG:
            painter.fillRect(0, 0, width, height, Qt.green)

        # fill canvas
        canvas_x = self.y_scale.total_width + self.curve_to_scale - self.curve_outer_border
        canvas_y = self.y_scale_height_offset - self.curve_outer_border
        canvas_width = self.curve_outer_border + curve_width + self.curve_outer_border
        canvas_height = self.curve_outer_border + curve_height + self.curve_outer_border

        painter.fillRect(canvas_x, canvas_y, canvas_width, canvas_height,
                         QColor(245, 245, 245))

        # draw cross hair at cursor position
        if self.cross_hair_visible:
            p = self.mapFromGlobal(QCursor.pos())
            p_x = p.x()
            p_y = p.y()

            if p_x >= canvas_x and p_x < canvas_x + canvas_width and \
               p_y >= canvas_y and p_y < canvas_y + canvas_height:
                painter.setPen(QPen(QColor(190, 190, 190), 1, Qt.DashLine))
                painter.drawLine(canvas_x, p_y, canvas_x + canvas_width - 1, p_y)
                painter.drawLine(p_x, canvas_y, p_x, canvas_y + canvas_height - 1)

        # draw canvas border
        painter.setPen(QColor(190, 190, 190))
        painter.drawRect(canvas_x, canvas_y, canvas_width - 1, canvas_height - 1) # -1 to accommodate the 1px width of the border

        painter.setPen(Qt.black)

        if DEBUG:
            painter.fillRect(self.y_scale.total_width + self.curve_to_scale,
                             self.y_scale_height_offset,
                             curve_width,
                             curve_height,
                             Qt.cyan)

        # draw scales
        min_y_axis = self.y_scale.value_min
        max_y_axis = self.y_scale.value_max

        factor_x = float(curve_width) / self.history_length_x
        factor_y = float(curve_height - 1) / max(max_y_axis - min_y_axis, EPSILON) # -1 to accommodate the 1px width of the curve

        self.draw_x_scale(painter, factor_x)
        self.draw_y_scale(painter, curve_height, factor_y)

        # draw curves
        if self.min_x != None:
            painter.save()
            painter.translate(self.y_scale.total_width + self.curve_to_scale,
                              self.y_scale_height_offset + curve_height - 1) # -1 to accommodate the 1px width of the curve
            painter.scale(1, -1)

            min_x = self.min_x
            drawLine = painter.drawLine

            for c in range(len(self.curves_x)):
                if not self.curves_visible[c]:
                    continue

                curve_x = self.curves_x[c]
                curve_y = self.curves_y[c]
                last_x = round((curve_x[0] - min_x) * factor_x)
                last_y = round((curve_y[0] - min_y_axis) * factor_y)

                painter.setPen(self.plots[c][1])

                for i in range(1, len(curve_x)):
                    x = round((curve_x[i] - min_x) * factor_x)
                    y = round((curve_y[i] - min_y_axis) * factor_y)

                    drawLine(last_x, last_y, x, y)

                    last_x = x
                    last_y = y

            painter.restore()

    def set_fixed_y_scale(self, value_min, value_max, step_size, step_division_count):
        self.y_scale_fixed = True
        self.y_scale.update_tick_config(value_min, value_max, step_size, step_division_count)

    def get_legend_offset_y(self): # px, from top
        return max(self.y_scale.tick_text_height_half - self.curve_outer_border, 0)

    def draw_x_scale(self, painter, factor):
        offset_x = self.y_scale.total_width + self.curve_to_scale
        offset_y = self.height() - self.x_scale.total_height

        if self.min_x != None:
            min_x = self.min_x
        else:
            min_x = 0

        painter.save()
        painter.translate(offset_x, offset_y)

        self.x_scale.draw(painter, factor, min_x, self.history_length_x)

        painter.restore()

    def draw_y_scale(self, painter, height, factor):
        offset_x = self.y_scale.total_width
        offset_y = self.height() - self.x_scale.total_height - self.curve_to_scale - 1

        painter.save()
        painter.translate(offset_x, offset_y)

        self.y_scale.draw(painter, height, factor)

        painter.restore()

    # NOTE: assumes that x is a timestamp in seconds that constantly grows
    def add_data(self, c, x, y):
        if self.type_y == None:
            self.type_y = type(y)

        x = float(x)
        y = float(y)

        last_min_y = self.min_y
        last_max_y = self.max_y

        if self.min_x == None:
            self.min_x = x

        if self.curves_visible[c]:
            if self.min_y == None:
                self.min_y = y
            else:
                self.min_y = min(self.min_y, y)

            if self.max_y == None:
                self.max_y = y
            else:
                self.max_y = max(self.max_y, y)

        self.curves_x[c].append(x)
        self.curves_y[c].append(y)

        if self.curves_min_x[c] == None:
            self.curves_min_x[c] = x

        if self.curves_min_y[c] == None:
            self.curves_min_y[c] = y
        else:
            self.curves_min_y[c] = min(self.curves_min_y[c], y)

        if self.curves_max_y[c] == None:
            self.curves_max_y[c] = y
        else:
            self.curves_max_y[c] = max(self.curves_max_y[c], y)

        if len(self.curves_x[c]) > 0 and (self.curves_x[c][-1] - self.curves_x[c][0]) >= self.history_length_x:
            self.curves_x[c] = self.curves_x[c][10:] # remove first second
            self.curves_y[c] = self.curves_y[c][10:] # remove first second

            if len(self.curves_x[c]) > 0:
                self.curves_min_x[c] = self.curves_x[c][0]
            else:
                self.curves_min_x[c] = None

            self.curves_min_y[c] = min(self.curves_y[c])
            self.curves_max_y[c] = max(self.curves_y[c])

            self.update_min_x_min_max_y()

        if self.curves_visible[c] and (last_min_y != self.min_y or last_max_y != self.max_y):
            self.update_min_max_y_axis()

        self.update()

    def update_min_x_min_max_y(self):
        self.min_x = min(self.curves_min_x)

        if sum(map(int, self.curves_visible)) > 0:
            self.min_y = min([curve_min_y for k, curve_min_y in enumerate(self.curves_min_y) if self.curves_visible[k]])
            self.max_y = max([curve_max_y for k, curve_max_y in enumerate(self.curves_max_y) if self.curves_visible[k]])
        else:
            self.min_y = None
            self.max_y = None

    def update_min_max_y_axis(self):
        if self.min_y == None or self.max_y == None:
            min_y = -1.0
            max_y = 1.0
        else:
            min_y = self.min_y
            max_y = self.max_y

        delta_y = abs(max_y - min_y)

        # if there is no delta then force some to get a y-axis with some ticks
        if delta_y < EPSILON:
            delta_y = 2.0
            min_y -= 1.0
            max_y += 1.0

        # start with the biggest power of 10 that is smaller than delta-y
        axis_y_step_size = 10.0 ** math.floor(math.log(delta_y, 10.0))
        axis_y_step_divisions = 5

        # the divisors are chosen in way to produce the sequence
        # 100.0, 50.0, 20.0, 10.0, 5.0, 2.0, 1.0, 0.5, 0.2, 0.1, 0.05 etc
        divisors = [2.0, 2.5, 2.0]
        divisions = [5, 4, 5]
        d = 0

        if self.type_y == int:
            min_axis_y_step_size = 1.0
        else:
            min_axis_y_step_size = EPSILON

        # decrease y-axis step-size until it divides delta-y in 4 or more parts
        while fuzzy_geq(axis_y_step_size / divisors[d % len(divisors)], min_axis_y_step_size) \
              and delta_y / axis_y_step_size < 4.0:
            axis_y_step_size /= divisors[d % len(divisors)]
            axis_y_step_divisions = divisions[d % len(divisions)]
            d += 1

        if d == 0:
            # if no division occurred in the first while loop then add 1
            # to d to counter the d -= 1 in the next while loop
            d += 1

        # increase y-axis step-size until it divides delta-y in 8 or less parts
        while delta_y / axis_y_step_size > 8.0:
            axis_y_step_divisions = divisions[d % len(divisions)]
            d -= 1
            axis_y_step_size *= divisors[d % len(divisors)]

        # ensure that the y-axis endpoints are multiple of the step-size
        self.min_y_axis = math.floor(min_y / axis_y_step_size) * axis_y_step_size
        self.max_y_axis = math.ceil(max_y / axis_y_step_size) * axis_y_step_size

        # fix rounding (?) errors from floor/ceil scaling
        while fuzzy_leq(self.min_y_axis + axis_y_step_size, min_y):
            self.min_y_axis += axis_y_step_size

        while fuzzy_geq(self.max_y_axis - axis_y_step_size, max_y):
            self.max_y_axis -= axis_y_step_size

        # if the y-axis endpoints are identical then force them 4 steps apart
        if fuzzy_eq(self.min_y_axis, self.max_y_axis):
            self.min_y_axis -= 2.0 * axis_y_step_size
            self.max_y_axis += 2.0 * axis_y_step_size

        self.axis_y_step_size = axis_y_step_size
        self.axis_y_step_divisions = axis_y_step_divisions

        if not self.y_scale_fixed:
            self.y_scale.update_tick_config(self.min_y_axis, self.max_y_axis, self.axis_y_step_size, self.axis_y_step_divisions)

    def show_curve(self, c, show):
        if self.curves_visible[c] == show:
            return

        last_min_y = self.min_y
        last_max_y = self.max_y

        self.curves_visible[c] = show

        self.update_min_x_min_max_y()

        if last_min_y != self.min_y or last_max_y != self.max_y:
            self.update_min_max_y_axis()

        self.update()

    def clear_graph(self):
        self.curves_visible = [] # per curve visibility
        self.curves_x = [] # per curve x values
        self.curves_y = [] # per curve y values
        self.curves_min_x = [] # per curve minimum x value
        self.curves_min_y = [] # per curve minimum y value
        self.curves_max_y = [] # per curve maximum y value
        self.min_x = None # minimum x value over all curves
        self.min_y = None # minimum y value over all curves
        self.max_y = None # maximum y value over all curves
        self.min_y_axis = None
        self.max_y_axis = None
        self.axis_y_step_size = None
        self.axis_y_step_divisions = None
        self.axis_y_to_str = istr
        self.type_y = None

        for plot in self.plots:
            self.curves_visible.append(True)
            self.curves_x.append([])
            self.curves_y.append([])
            self.curves_min_x.append(None)
            self.curves_min_y.append(None)
            self.curves_max_y.append(None)

        self.update()

class PlotWidget(QWidget):
    def __init__(self, y_scale_title_text, plots, clear_button=None, parent=None):
        QWidget.__init__(self, parent)

        self.setMinimumSize(300, 250)

        self.stop = True
        self.plot = Plot(self, y_scale_title_text, plots)
        self.set_fixed_y_scale = self.plot.set_fixed_y_scale
        self.plot_buttons = []
        self.first_show = True

        if clear_button == None:
            self.clear_button = QPushButton('Clear Graph')
        else:
            self.clear_button = clear_button

        self.clear_button.clicked.connect(self.clear_clicked)

        vlayout = QVBoxLayout(self)
        vlayout.setContentsMargins(0, 0, 0, 0)

        if len(plots) > 1:
            hlayout = QHBoxLayout()
            hlayout.setContentsMargins(0, 0, 0, 0)

            button_layout = QVBoxLayout()
            button_layout.setContentsMargins(0, 0, 0, 0)
            button_layout.addSpacing(self.plot.get_legend_offset_y())

            for i, plot in enumerate(plots):
                pixmap = QPixmap(10, 1)
                QPainter(pixmap).fillRect(0, 0, 10, 1, plot[1])

                button = QToolButton(self)
                button.setText(plot[0])
                button.setIcon(QIcon(pixmap))
                button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
                button.setCheckable(True)
                button.setChecked(True)
                button.toggled.connect(functools.partial(self.plot.show_curve, i))

                self.plot_buttons.append(button)

                button_layout.addWidget(button)

            button_layout.addStretch(1)

            hlayout.addWidget(self.plot)
            hlayout.addLayout(button_layout)

            vlayout.addLayout(hlayout)
        else:
            vlayout.addWidget(self.plot)

        if clear_button == None:
            vlayout.addWidget(self.clear_button)

        self.counter = 0
        self.update_funcs = []

        for plot in plots:
            self.update_funcs.append(plot[2])

        self.timer = QTimer()
        self.timer.timeout.connect(self.add_new_data)
        self.timer.start(100)

    # overrides QWidget.showEvent
    def showEvent(self, event):
        QWidget.showEvent(self, event)

        if self.first_show:
            self.first_show = False

            if len(self.plot_buttons) > 0:
                widths = []

                for plot_button in self.plot_buttons:
                    widths.append(plot_button.width())

                width = max(widths)

                for plot_button in self.plot_buttons:
                    size = plot_button.minimumSize()

                    size.setWidth(width)

                    plot_button.setMinimumSize(size)

    def add_new_data(self):
        if self.stop:
            return

        for i, update_func in enumerate(self.update_funcs):
            value = update_func()

            if value != None:
                self.plot.add_data(i, self.counter / 10.0, value)

        self.counter += 1

    def clear_clicked(self):
        self.plot.clear_graph()
        self.counter = 0
