#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
brickv (Brick Viewer)
Copyright (C) 2009-2013 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2013-2015 Matthias Bolte <matthias@tinkerforge.com>

main.py: Entry file for Brick Viewer

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
if (sys.hexversion & 0xFF000000) != 0x03000000:
    print('Python 3.x required')
    sys.exit(1)

import os
import logging
import locale

def prepare_package(package_name):
    # from http://www.py2exe.org/index.cgi/WhereAmI
    if hasattr(sys, 'frozen'):
        program_path = os.path.dirname(os.path.realpath(sys.executable))
    else:
        program_path = os.path.dirname(os.path.realpath(__file__))

    # add program_path so OpenGL is properly imported
    sys.path.insert(0, program_path)

    # allow the program to be directly started by calling 'main.py'
    # without '<package_name>' being in the path already
    if package_name not in sys.modules:
        head, tail = os.path.split(program_path)

        if head not in sys.path:
            sys.path.insert(0, head)

        if not hasattr(sys, 'frozen'):
            # load and inject in modules list, this allows to have the source in a
            # directory named differently than '<package_name>'
            sys.modules[package_name] = __import__(tail, globals(), locals())

prepare_package('brickv')

from PyQt5.QtCore import QEvent, pyqtSignal, Qt
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QTextBrowser, \
                            QPushButton, QWidget, QLabel, QCheckBox, QHBoxLayout, \
                            QMessageBox, QSplashScreen

from brickv import config
from brickv.async_call import ASYNC_EVENT, async_event_handler
from brickv.load_pixmap import load_pixmap

from brickv.bindings.ip_connection import Error
import traceback
import html
import queue
import threading
import subprocess
from copy import deepcopy

logging.basicConfig(level=config.LOGGING_LEVEL,
                    format=config.LOGGING_FORMAT,
                    datefmt=config.LOGGING_DATEFMT)

class ExceptionReporter:
    def __init__(self, argv):
        self.argv = argv
        self.error_queue = queue.Queue()
        self.error_spawn = threading.Thread(target=self.error_spawner, daemon=True)
        self.error_spawn.start()
        sys.excepthook = self.exception_hook

    def error_spawner(self):
        ignored = []
        while True:
            error = self.error_queue.get()

            hash_ = hash(error)
            if hash_ in ignored:
                continue

            # Either sys.executable is /path/to/python, then run calls /path/to/python /path/to/main.py --error-report,
            # or sys.executable is brickv[.exe], then the --error-report flag ensures, that the path to main.py is ignored.
            show_again = bool(subprocess.run([sys.executable, os.path.realpath(__file__), "--error-report"] + self.argv, input=error, universal_newlines=True).returncode)
            if not show_again:
                ignored.append(hash_)

    def exception_hook(self, exctype, value, tb):
        traceback.print_exception(etype=exctype, value=value, tb=tb)

        message = "".join(traceback.format_exception(etype=exctype, value=value, tb=tb))
        self.error_queue.put(message)

class BrickViewer(QApplication):
    object_creator_signal = pyqtSignal(object)
    infos_changed_signal = pyqtSignal(str) # uid

    def __init__(self, *args, **kwargs):
        QApplication.__init__(self, *args, **kwargs)

        self.object_creator_signal.connect(self.object_creator_slot)
        self.setWindowIcon(QIcon(load_pixmap('brickv-icon.png')))

    def object_creator_slot(self, object_creator):
        object_creator.create()

    def notify(self, receiver, event):
        if event.type() > QEvent.User and event.type() == ASYNC_EVENT:
            async_event_handler()

        return QApplication.notify(self, receiver, event)

def error_report_main():
    error_message = sys.stdin.read()
    error_message = "<pre>{}</pre>".format(html.escape(error_message).replace("\n", "<br>"))
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle('Error - Brick Viewer ' + config.BRICKV_VERSION)

    widget = QWidget()
    window.setCentralWidget(widget)
    widget.setLayout(QHBoxLayout())

    icon = QLabel()
    icon.setPixmap(QMessageBox.standardIcon(QMessageBox.Critical))
    icon.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
    widget.layout().addWidget(icon)

    right_widget = QWidget()
    right_widget.setLayout(QVBoxLayout())

    label = QLabel("Please report this error to <a href='mailto:info@tinkerforge.com'>info@tinkerforge.com</a>.\nIf you know what caused the error and can fix it, please report it anyway. This allows us to improve the error messages.")
    label.setWordWrap(True)
    label.setOpenExternalLinks(True)
    right_widget.layout().addWidget(label)

    tb = QTextBrowser()
    tb.setHtml(error_message)
    right_widget.layout().addWidget(tb)

    cbox = QCheckBox("Show this message again")
    cbox.setChecked(True)
    right_widget.layout().addWidget(cbox)

    btn = QPushButton("OK")
    btn.clicked.connect(lambda event: app.exit())
    right_widget.layout().addWidget(btn)

    widget.layout().addWidget(right_widget)
    window.show()
    window.setMinimumSize(640, 400)
    app.exec_()
    return int(cbox.isChecked())

def main():
    try:
        locale.setlocale(locale.LC_ALL, '')
    except locale.Error:
        pass # ignore this as it might fail on macOS, we'll fallback to UTF-8 in that case

    if config.get_use_fusion_gui_style():
        sys.argv += ['-style', 'fusion']

    if '--error-report' in sys.argv:
        sys.exit(error_report_main())

    # Catch all uncaught exceptions and show an error message for them.
    # PyQt5 does not silence exceptions in slots (as did PyQt4), so there
    # can be slots which try to (for example) send requests but don't wrap
    # them in an async call with error handling.
    ExceptionReporter(deepcopy(sys.argv)) # Deep copy because QApplication (i.e. BrickViewer) constructor parses away Qt args and we want to know the style.

    # importing the MainWindow after creating the QApplication instance triggers this warning
    #
    #  Qt WebEngine seems to be initialized from a plugin. Please set Qt::AA_ShareOpenGLContexts
    #  using QCoreApplication::setAttribute before constructing QGuiApplication.
    #
    # do what the warnings says to avoid it
    QApplication.setAttribute(Qt.AA_ShareOpenGLContexts)

    brick_viewer = BrickViewer(sys.argv)
    splash = QSplashScreen(load_pixmap('splash.png'), Qt.WindowStaysOnTopHint)
    splash.show()
    splash.showMessage('Starting Brick Viewer ' + config.BRICKV_VERSION, Qt.AlignHCenter | Qt.AlignBottom, Qt.white)
    brick_viewer.processEvents()

    from brickv.mainwindow import MainWindow
    main_window = MainWindow()
    main_window.show()
    splash.finish(main_window)

    sys.exit(brick_viewer.exec_())

if __name__ == "__main__":
    main()
