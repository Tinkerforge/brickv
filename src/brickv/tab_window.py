# -*- coding: utf-8 -*-
"""
brickv (Brick Viewer)
Copyright (C) 2009-2012 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2012-2014 Matthias Bolte <matthias@tinkerforge.com>
Copyright (C) 2014 Philipp Kroos <philipp.kroos@fh-bielefeld.de>

tab_window.py: Detachable container to be used in a TabBar (e.g. TabWidget)

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

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QDialog, QAbstractButton, QTabBar, QVBoxLayout
from PyQt5.QtGui import QPainter, QIcon

from brickv import config
from brickv.load_pixmap import load_pixmap

class IconButton(QAbstractButton):
    clicked = pyqtSignal()

    def __init__(self, normal_icon, hover_icon, parent=None):
        super().__init__(parent)
        self.normal_icon = normal_icon
        self.hover_icon = hover_icon
        self.setIcon(normal_icon)
        self.setMouseTracking(True)
        self.setFixedSize(16, 16)

    def paintEvent(self, event):
        painter = QPainter(self)

        self.icon().paint(painter, event.rect())

    def sizeHint(self):
        return self.iconSize()

    def enterEvent(self, event):
        self.set_hover_icon()

    def leaveEvent(self, event):
        self.set_normal_icon()

    def mousePressEvent(self, event):
        self.clicked.emit()

    def set_hover_icon(self):
        self.setIcon(self.hover_icon)

    def set_normal_icon(self):
        self.setIcon(self.normal_icon)

class TabWidget(QDialog):
    def __init__(self, tab_window, name):
        super().__init__(None)
        super().setWindowTitle(name)
        self.tab_window = tab_window

     # overrides QDialog.closeEvent
    def closeEvent(self, event):
        self.tab_window.tab()
        event.accept()

    # overrides QDialog.reject
    def reject(self):
        pass # ignore escape key, because QDialog.reject would hide the widget


class TabWindow(QDialog):
    """Detachable widget usable in a TabWidget. The widget can be detached
    from the TabWidget by calling untab(), added to it by calling tab(). If tabbed,
    it has a clickable icon visualizing mouseOver events; on click the button_handler
    of this class is called with the current index in the TabWidget.
    Callbacks called after the tabbing and before the  untabbing events
    can be registered."""

    def __init__(self, tab_widget, name, button_handler, parent=None):
        super().__init__(parent)

        self.tab_widget = tab_widget
        self.name = name
        self.button = None # see tab()
        self.button_handler = button_handler
        self.button_icon_normal = QIcon(load_pixmap('untab-icon-normal.png'))
        self.button_icon_hover = QIcon(load_pixmap('untab-icon-hover.png'))
        self.cb_on_tab = None
        self.cb_on_untab = None
        self.cb_post_tab = None
        self.cb_post_untab = None
        self.parent_dialog = None

    def untab(self):
        index = self.tab_widget.indexOf(self)
        if index > -1:
            if self.cb_on_untab != None:
                self.cb_on_untab(index)

            self.tab_widget.removeTab(index)

            self.parent_dialog = TabWidget(self, self.name + " - " + "Brick Viewer " + config.BRICKV_VERSION)
            layout = QVBoxLayout(self.parent_dialog)
            layout.addWidget(self)
            layout.setContentsMargins(0, 0, 0, 0)

            self.parent_dialog.show()
            self.show()

            if self.cb_post_untab != None:
                self.cb_post_untab(index)

    def tab(self):
        index = self.tab_widget.addTab(self, self.name)
        if self.cb_on_tab != None:
            self.cb_on_tab(index)

        # (re-)instantiating button here because the TabBar takes ownership and
        # destroys it when this TabWindow is untabbed
        self.button = IconButton(self.button_icon_normal, self.button_icon_hover, parent=self)
        self.button.setToolTip('Detach Tab from Brick Viewer')
        self.button.clicked.connect(lambda: self.button_handler(self.tab_widget.indexOf(self)))

        self.tab_widget.tabBar().setTabButton(index, QTabBar.LeftSide, self.button)

        if self.cb_post_tab != None:
            self.cb_post_tab(index)

    def set_callback_on_tab(self, callback):
        self.cb_on_tab = callback

    def set_callback_on_untab(self, callback):
        self.cb_on_untab = callback

    def set_callback_post_untab(self, callback):
        self.cb_post_untab = callback

    def set_callback_post_tab(self, callback):
        self.cb_post_tab = callback
