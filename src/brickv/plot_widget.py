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
    return a < b or abs(a - b) < EPSILON

def fuzzy_geq(a, b):
    return a > b or abs(a - b) < EPSILON

class Plot(QWidget):
    def __init__(self, parent, axis_y_name, plots, axis_scales):
        QWidget.__init__(self, parent)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.plots = plots
        self.history_length_x = 20 # seconds
        self.curve_outer_border = 5 # px
        self.cross_hair_visible = False

        self.tick_size_small = 5 # px
        self.tick_size_medium = 7 # px
        self.tick_size_large = 9 # px
        self.tick_to_text_x = 1 # px
        self.tick_to_text_y = 3 # px
        self.tick_font = self.font()
        self.tick_font_metrics = QFontMetrics(self.tick_font)
        self.tick_font_height = self.tick_font_metrics.boundingRect('0123456789').height()
        self.tick_font_height_half = int(math.ceil(self.tick_font_height / 2.0))
        self.tick_font_max_width = 10 # px, just an initial value, dynamically calculated based on y-axis ticks

        self.axis_x_name = 'Time [s]'
        self.axis_x_name_to_tick_text = 4 # px
        self.axis_x_name_to_border = 2 # px
        self.axis_y_name = axis_y_name
        self.axis_y_name_to_tick_text = 7 # px
        self.axis_y_name_to_border = 2 # px
        self.axis_font = self.font()
        self.axis_font.setPointSize(round(self.axis_font.pointSize() * 1.2))
        self.axis_font.setBold(True)
        self.axis_font_metrics = QFontMetrics(self.axis_font)
        self.axis_x_font_height = self.axis_font_metrics.boundingRect(self.axis_x_name).height()
        self.axis_y_font_height = 16 # px, just an initial value, dynamically calculated based on y-axis name
        self.axis_y_name_pixmap = None

        self.fixed_min_y_axis = None
        self.fixed_max_y_axis = None
        self.axis_y_fixed = False
        self.axis_y_fixed_step_size = None
        self.axis_y_fixed_step_divisions = None

        self.axis_x_height = self.tick_size_large + self.tick_to_text_x + self.tick_font_height + \
                             self.axis_x_name_to_tick_text + self.axis_x_font_height + self.axis_x_name_to_border
        self.axis_y_width = 50 # px, just an initial value, dynamically calculated based on y-axis ticks
        self.axis_y_height_offset = max(self.curve_outer_border, self.tick_font_height_half) # px, from top
        self.axis_to_curve = 8 # px

        self.clear_graph()

    # override QWidget.sizeHint
    def sizeHint(self):
        return QSize(600, 300)

    # override QWidget.resizeEvent
    def resizeEvent(self, event):
        height = event.size().height()
        axis_y_name_width = height - self.axis_y_height_offset - self.axis_x_height - self.axis_to_curve
        self.axis_y_font_height = self.axis_font_metrics.boundingRect(0, 0, axis_y_name_width, 1000,
                                                                      Qt.TextWordWrap | Qt.AlignHCenter | Qt.AlignTop,
                                                                      self.axis_y_name).height()

        self.update_axis_y_width()

        QWidget.resizeEvent(self, event)

    # override QWidget.paintEvent
    def paintEvent(self, event):
        painter = QPainter(self)
        width = self.width()
        height = self.height()
        curve_width = width - self.axis_y_width - self.axis_to_curve - self.curve_outer_border
        curve_height = height - self.axis_y_height_offset - self.axis_x_height - self.axis_to_curve

        if DEBUG:
            painter.fillRect(0, 0, width, height, Qt.green)

        # fill canvas
        canvas_x = self.axis_y_width + self.axis_to_curve - self.curve_outer_border
        canvas_y = self.axis_y_height_offset - self.curve_outer_border
        canvas_width = curve_width + 2 * self.curve_outer_border
        canvas_height = curve_height + 2 * self.curve_outer_border

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
            painter.fillRect(self.axis_y_width + self.axis_to_curve,
                             self.axis_y_height_offset,
                             curve_width,
                             curve_height,
                             Qt.cyan)

        # draw scales
        scale_x = float(curve_width) / self.history_length_x

        if self.min_x != None:
            if self.axis_y_fixed:
                min_y_axis = self.fixed_min_y_axis
                max_y_axis = self.fixed_max_y_axis
            else:
                min_y_axis = self.min_y_axis
                max_y_axis = self.max_y_axis

            scale_y = float(curve_height - 1) / max(max_y_axis - min_y_axis, EPSILON) # -1 to accommodate the 1px width of the curve
        else:
            scale_y = 1.0

        self.draw_axis_x(painter, curve_width, scale_x)
        self.draw_axis_y(painter, curve_height, scale_y)

        # draw curves
        if self.min_x != None:
            painter.save()
            painter.translate(self.axis_y_width + self.axis_to_curve,
                              self.axis_y_height_offset + curve_height - 1) # -1 to accommodate the 1px width of the curve
            painter.scale(1, -1)

            min_x = self.min_x
            drawLine = painter.drawLine

            for c in range(len(self.curves_x)):
                if not self.curves_visible[c]:
                    continue

                curve_x = self.curves_x[c]
                curve_y = self.curves_y[c]
                last_x = round((curve_x[0] - min_x) * scale_x)
                last_y = round((curve_y[0] - min_y_axis) * scale_y)

                painter.setPen(self.plots[c][1])

                for i in range(1, len(curve_x)):
                    x = round((curve_x[i] - min_x) * scale_x)
                    y = round((curve_y[i] - min_y_axis) * scale_y)

                    drawLine(last_x, last_y, x, y)

                    last_x = x
                    last_y = y

            painter.restore()

    def set_fixed_y_axis(self, minimum, maximum, step_size, step_divisions):
        self.fixed_min_y_axis = float(minimum)
        self.fixed_max_y_axis = float(maximum)
        self.axis_y_fixed = True
        self.axis_y_fixed_step_size = float(step_size)
        self.axis_y_fixed_step_divisions = int(step_divisions)

    def get_legend_offset_y(self): # px, from top
        return max(self.tick_font_height_half - self.curve_outer_border, 0)

    def draw_axis_x(self, painter, curve_width, scale_x):
        offset_x = self.axis_y_width + self.axis_to_curve
        offset_y = self.height() - self.axis_x_height
        scale_x_int = math.floor(scale_x)

        painter.drawLine(offset_x, offset_y, offset_x + curve_width - 1, offset_y)

        if self.min_x != None:
            min_x = self.min_x
        else:
            min_x = 0

        painter.setFont(self.tick_font)

        for i in range(self.history_length_x):
            x = offset_x + round(i * scale_x)
            s = int(min_x + i)

            if (s % 5) == 0:
                time_x = x - scale_x_int
                time_y = offset_y + self.tick_size_large
                time_width = scale_x_int * 2 + 1 # +1 to accommodate the 1px width of the tick
                time_height = self.tick_to_text_x + self.tick_font_height

                if DEBUG:
                    painter.fillRect(time_x, time_y, time_width, time_height, Qt.yellow)

                painter.drawLine(x, offset_y, x, offset_y + self.tick_size_large)
                painter.drawText(time_x, time_y, time_width, time_height,
                                 Qt.TextDontClip | Qt.AlignHCenter | Qt.AlignBottom, istr(s))
            else:
                painter.drawLine(x, offset_y, x, offset_y + self.tick_size_small)

        name_x = offset_x
        name_y = offset_y + self.tick_size_large + self.tick_to_text_x + self.tick_font_height + self.axis_x_name_to_tick_text
        name_width = curve_width
        name_height = self.axis_x_font_height

        if DEBUG:
            painter.fillRect(name_x, name_y, name_width, name_height, Qt.yellow)

        painter.setFont(self.axis_font)
        painter.drawText(name_x, name_y, name_width, name_height,
                         Qt.TextDontClip | Qt.AlignHCenter | Qt.AlignBottom,
                         self.axis_x_name)

    def draw_axis_y(self, painter, curve_height, scale_y):
        offset_x = self.axis_y_width - 1 # -1 to accommodate the 1px width of the axis
        offset_y = self.height() - self.axis_x_height - self.axis_to_curve - 1

        if self.axis_y_fixed:
            min_y_axis = self.fixed_min_y_axis
            max_y_axis = self.fixed_max_y_axis
            axis_y_step_size = self.axis_y_fixed_step_size
            axis_y_step_divisions = self.axis_y_fixed_step_divisions
        else:
            if self.min_y_axis != None:
                min_y_axis = self.min_y_axis
            else:
                min_y_axis = -1.0

            if self.max_y_axis != None:
                max_y_axis = self.max_y_axis
            else:
                max_y_axis = 1.0

            if self.axis_y_step_size != None:
                axis_y_step_size = self.axis_y_step_size
            else:
                axis_y_step_size = 1.0

            if self.axis_y_step_divisions != None:
                axis_y_step_divisions = self.axis_y_step_divisions
            else:
                axis_y_step_divisions = 5

        # draw axis line
        painter.drawLine(offset_x, offset_y, offset_x, offset_y - curve_height + 1) # +1 to accommodate the 1px width of the curve

        y_axis = min_y_axis

        if DEBUG:
            painter.fillRect(0, 0, self.axis_y_name_to_border, curve_height, Qt.darkGreen)
            painter.fillRect(self.axis_y_name_to_border + self.axis_y_font_height, 0,
                             self.axis_y_name_to_tick_text, curve_height, Qt.darkGreen)

        # draw ticks
        painter.setFont(self.tick_font)

        while fuzzy_leq(y_axis, max_y_axis):
            y = offset_y - int(round((y_axis - min_y_axis) * scale_y))

            painter.drawLine(offset_x - self.tick_size_large, y, offset_x, y)

            tick_text_x = 0
            tick_text_y = y - self.tick_font_height_half
            tick_text_width = offset_x - self.tick_size_large - self.tick_to_text_y
            tick_text_height = self.tick_font_height_half * 2

            if DEBUG:
                painter.fillRect(tick_text_x, tick_text_y, tick_text_width, tick_text_height, Qt.cyan)
                painter.fillRect(tick_text_x + tick_text_width - self.tick_font_max_width, tick_text_y,
                                 self.tick_font_max_width, tick_text_height, QColor(255,0,0,64))

            painter.drawText(tick_text_x, tick_text_y, tick_text_width, tick_text_height,
                             Qt.TextDontClip | Qt.AlignRight | Qt.AlignVCenter,
                             self.axis_y_to_str(y_axis))

            for i in range(1, axis_y_step_divisions):
                sub_y_axis = y_axis + (axis_y_step_size * i / axis_y_step_divisions)

                if not fuzzy_leq(sub_y_axis, max_y_axis):
                    break

                y = offset_y - int(round((sub_y_axis - min_y_axis) * scale_y))

                if i % 2 == 0 and axis_y_step_divisions % 2 == 0:
                    tick_size = self.tick_size_medium
                else:
                    tick_size = self.tick_size_small

                painter.drawLine(offset_x - tick_size, y, offset_x, y)

            y_axis += axis_y_step_size

        # draw name
        name_width = curve_height
        name_height = self.axis_y_font_height

        if self.axis_y_name_pixmap == None or self.axis_y_name_pixmap.size() != QSize(name_width, name_height):
            self.axis_y_name_pixmap = QPixmap(name_width, name_height)
            self.axis_y_name_pixmap.fill(QColor(0, 0, 0, 0))

            name_painter = QPainter(self.axis_y_name_pixmap)
            name_painter.setFont(self.axis_font)
            name_painter.drawText(0, 0, name_width, name_height,
                                  Qt.TextWordWrap | Qt.TextDontClip | Qt.AlignHCenter | Qt.AlignTop,
                                  self.axis_y_name)
            name_painter = None

        painter.save()
        painter.rotate(-90)

        name_x = -offset_y - 1
        name_y = self.axis_y_name_to_border

        painter.drawPixmap(name_x, name_y, self.axis_y_name_pixmap)

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

        # find maximum tick text width
        if fuzzy_geq(self.axis_y_step_size, 1.0):
            self.axis_y_to_str = istr
        else:
            self.axis_y_to_str = fstr

        y_axis = self.min_y_axis
        tick_font_max_width = self.tick_font_metrics.width(self.axis_y_to_str(y_axis))

        while fuzzy_leq(y_axis, self.max_y_axis):
            tick_font_max_width = max(tick_font_max_width, self.tick_font_metrics.width(self.axis_y_to_str(y_axis)))
            y_axis += self.axis_y_step_size

        self.tick_font_max_width = tick_font_max_width

        self.update_axis_y_width()

    def update_axis_y_width(self):
        self.axis_y_width = self.tick_size_large + self.tick_to_text_y + self.tick_font_max_width + \
                            self.axis_y_name_to_tick_text + self.axis_y_font_height + self.axis_y_name_to_border + 1 # +1 to accommodate the 1px width of the axis

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
    def __init__(self, y_axis_name, plots, clear_button=None, parent=None, axis_scales=None):
        QWidget.__init__(self, parent)

        self.setMinimumSize(300, 250)

        self.stop = True
        self.plot = Plot(self, y_axis_name, plots, axis_scales)
        self.set_fixed_y_axis = self.plot.set_fixed_y_axis
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
