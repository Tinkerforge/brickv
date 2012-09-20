# -*- coding: utf-8 -*-  
"""
brickv (Brick Viewer) 
Copyright (C) 2011 Olaf Lüke <olaf@tinkerforge.com>

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

from PyQt4.QtGui import QVBoxLayout, QWidget, QPushButton
from PyQt4.QtCore import QTimer

import PyQt4.Qwt5 as Qwt
class Plot(Qwt.QwtPlot):
    def __init__(self, y_axis, plot_list, *args):
        Qwt.QwtPlot.__init__(self, *args)
     
        self.setAxisTitle(Qwt.QwtPlot.xBottom, 'Time [s]')
        self.setAxisTitle(Qwt.QwtPlot.yLeft, y_axis)
        
        self.has_legend = plot_list[0][0] != ''
        
        if self.has_legend: 
            legend = Qwt.QwtLegend()
            legend.setItemMode(Qwt.QwtLegend.CheckableItem)
            self.insertLegend(legend, Qwt.QwtPlot.RightLegend)
        
        self.setAutoReplot(True)
        
        self.curve = []
        
        self.data_x = []
        self.data_y = []
        
        for x in plot_list:
            c = Qwt.QwtPlotCurve(x[0])
            self.curve.append(c)
            self.data_x.append([])
            self.data_y.append([])
        
            c.attach(self)
            c.setPen(x[1])
            self.show_curve(c, True)
        
        if self.has_legend: 
            self.legendChecked.connect(self.show_curve)
        
    def show_curve(self, item, on):
        item.setVisible(on)
        if self.has_legend:
            widget = self.legend().find(item)
            if isinstance(widget, Qwt.QwtLegendItem):
                widget.setChecked(on)
        self.replot()
           

    def add_data(self, i, data_x, data_y):
        self.data_x[i].append(data_x)
        self.data_y[i].append(data_y)
        if len(self.data_x[i]) == 1200: # 2 minutes
            self.data_x[i] = self.data_x[i][10:]
            self.data_y[i] = self.data_y[i][10:]
        
        self.curve[i].setData(self.data_x[i], self.data_y[i])
        
    def clear_graph(self):
        for i in range(len(self.data_x)):
            self.data_x[i] = []
            self.data_y[i] = []
            
class PlotWidget(QWidget):
    def __init__(self, y_axis, plot_list, clear_button = None, parent = None):
        QWidget.__init__(self, parent)
        
        self.stop = True
        
        self.plot = Plot(y_axis, plot_list)

        if clear_button is None:
            self.clear_button = QPushButton('Clear Graph')
        else:
            self.clear_button = clear_button

        self.clear_button.pressed.connect(self.clear_pressed)
        
        layout = QVBoxLayout(self)
        layout.addWidget(self.plot)

        if clear_button is None:
            layout.addWidget(self.clear_button)
        
        self.counter = 0
        self.update_func = []
        
        for pl in plot_list:
            self.update_func.append(pl[2])
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(100)
        
    def update(self):
        if self.stop:
            return
        
        for i in range(len(self.update_func)):
            self.plot.add_data(i, self.counter/10.0, self.update_func[i]())
            
        self.counter += 1
            
    def clear_pressed(self):
        self.plot.clear_graph()
        self.counter = 0
