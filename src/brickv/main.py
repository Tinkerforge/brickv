#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
brickv (Brick Viewer)
Copyright (C) 2009-2013 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2013-2015 Matthias Bolte <matthias@tinkerforge.com>
Copyright (C) 2020 Erik Fleckstein <erik@tinkerforge.com>

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

import datetime
from tzlocal import get_localzone
import os
import logging
import locale
import traceback
import html
import queue
import threading
import subprocess
from copy import deepcopy

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

from PyQt5.QtCore import QEvent, pyqtSignal, Qt, QSysInfo
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QTextBrowser, \
                            QPushButton, QWidget, QLabel, QCheckBox, QHBoxLayout, \
                            QMessageBox, QSplashScreen

# QOperatingSystemVersion is only available sice Qt 5.9
try:
    from PyQt5.QtCore import QOperatingSystemVersion
    q_os_version_available = True
except:
    q_os_version_available = False

from brickv import config
from brickv.async_call import ASYNC_EVENT, async_event_handler
from brickv.load_pixmap import load_pixmap

logging.basicConfig(level=config.LOGGING_LEVEL,
                    format=config.LOGGING_FORMAT,
                    datefmt=config.LOGGING_DATEFMT)

brickv_version = [(0, 0, 0), (0, 0, 0)]

class ExceptionReporter:
    def __init__(self, argv):
        self.argv = argv
        self.error_queue = queue.Queue()
        self.error_spawn = threading.Thread(target=self.error_spawner, daemon=True)
        self.error_spawn.start()
        self.main_window = None
        sys.excepthook = self.exception_hook
        if sys.version_info >= (3,8,0):
            threading.excepthook = lambda args: self.exception_hook(*args)
        else:
            self.install_thread_excepthook()

    def install_thread_excepthook(self):
        """
        Workaround for sys.excepthook thread bug
        From https://bugs.python.org/issue1230540#msg91244
        """
        init_old = threading.Thread.__init__
        def init(self, *args, **kwargs):
            init_old(self, *args, **kwargs)
            run_old = self.run
            def run_with_except_hook(*args, **kw):
                try:
                    run_old(*args, **kw)
                except (KeyboardInterrupt, SystemExit):
                    raise
                except:
                    # Add self (i.e. the thread that raised the error) to behave like to python 3.8's threading.excepthook
                    sys.excepthook(*sys.exc_info(), thread=self)
            self.run = run_with_except_hook
        threading.Thread.__init__ = init

    def set_main_window(self, main_window):
        self.main_window = main_window

    def get_python_thread_stack_traces(self):
        thread_names = {thread.ident: thread.name for thread in threading.enumerate()}

        result = []
        for thread_id, stack in sys._current_frames().items():
            template = 'Thread {} (Name: {}):\n{}'
            name = thread_names.get(thread_id, 'unknown')
            stack_trace = ''.join(traceback.format_stack(stack))
            result.append(template.format(thread_id, name, stack_trace))
        return result

    def get_os_name(self):
        global q_os_version_available
        try:
            os_name = QSysInfo.prettyProductName()

            if q_os_version_available:
                ver = QOperatingSystemVersion.current()
                if ver.name() != '':
                    os_name += ' {} '.format(ver.name())
                if ver.segmentCount() > 2:
                    os_name += '{}.{}.{}'.format(ver.majorVersion(), ver.minorVersion(), ver.microVersion())
                elif ver.segmentCount == 2:
                    os_name += '{}.{}'.format(ver.majorVersion(), ver.minorVersion())
                elif ver.segmentCount == 1:
                    os_name += '{}'.format(ver.majorVersion())

            kernel_name = QSysInfo.kernelType() + ' ' + QSysInfo.kernelVersion()
            if os_name != kernel_name:
                os_name += ' ({})'.format(kernel_name)
            return os_name
        except Exception as e:
            return 'unknown OS - PLEASE EXPLAIN IF SENDING REPORT.'

    def error_spawner(self):
        ignored = []
        while True:
            time_occured, exctype, value, tb, thread = self.error_queue.get()
            error = "".join(traceback.format_exception(etype=exctype, value=value, tb=tb))

            hash_ = hash(error)
            if hash_ in ignored:
                continue

            label_suffix = ''

            if brickv_version[1] == (0, 0, 0):
                label_suffix += '<br/><br/><b>Your Brick Viewer version is {}, however it is unknown if a newer version is available.</b> Please <a href="https://www.tinkerforge.com/en/doc/Downloads.html#tools">check for updates</a> before reporting this error.'.format(config.BRICKV_FULL_VERSION)

            elif brickv_version[0] < brickv_version[1]:
                label_suffix += '<br/><br/><b>Your Brick Viewer version is {}, however {}.{}.{} is available.</b> Please update and try again before reporting this error.'.format(config.BRICKV_FULL_VERSION, *brickv_version[1])

            prefix = 'Brick Viewer {} on {}\nException raised at {}'.format(config.BRICKV_FULL_VERSION, self.get_os_name(), time_occured)
            if thread is not None:
                prefix += ' by Thread {}'.format(thread.ident)
                if thread.name is not None:
                    prefix += ' (Name: {})'.format(thread.name)
            print(prefix)

            prefix = label_suffix + '!!!' + prefix

            traceback.print_exception(etype=exctype, value=value, tb=tb)

            report_message = prefix + '\n\n' + error + '\nActive Threads:\n\n' + '\n\n'.join(self.get_python_thread_stack_traces())

            # Either sys.executable is /path/to/python, then run calls /path/to/python /path/to/main.py --error-report,
            # or sys.executable is brickv[.exe], then the --error-report flag ensures, that the path to main.py is ignored.
            show_again = bool(subprocess.run([sys.executable, os.path.realpath(__file__), "--error-report"] + self.argv, input=report_message, universal_newlines=True).returncode)
            if not show_again:
                ignored.append(hash_)

    def exception_hook(self, exctype, value, tb, thread=None):
        try:
            tz = get_localzone()
        except:
            tz = None
        self.error_queue.put((datetime.datetime.now(tz=tz).isoformat(), exctype, value, tb, thread))

class BrickViewer(QApplication):
    object_creator_signal = pyqtSignal(object)
    info_changed_signal = pyqtSignal(str) # uid

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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
    label_suffix, error_message = error_message.split('!!!')
    error_message = "<pre>{}</pre>".format(html.escape(error_message).replace("\n", "<br>"))

    app = QApplication(sys.argv)

    if sys.platform == 'darwin':
        # workaround macOS QTBUG-61562
        from brickv.mac_pasteboard_mime_fixed import MacPasteboardMimeFixed
        mac_pasteboard_mime_fixed = MacPasteboardMimeFixed()

    window = QMainWindow()
    window.setWindowTitle('Error - Brick Viewer ' + config.BRICKV_VERSION)
    window.setWindowIcon(QIcon(load_pixmap('brickv-icon.png')))

    widget = QWidget()
    window.setCentralWidget(widget)
    widget.setLayout(QHBoxLayout())

    icon = QLabel()
    icon.setPixmap(QMessageBox.standardIcon(QMessageBox.Critical))
    icon.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
    widget.layout().addWidget(icon)

    right_widget = QWidget()
    right_widget.setLayout(QVBoxLayout())
    right_widget.layout().setContentsMargins(0, 0, 0, 0)

    label = QLabel("Please report this error to <a href='mailto:info@tinkerforge.com'>info@tinkerforge.com</a>.<br/>" +
                   "Please also report what you tried to do, when the error was reported.<br/><br/>" +
                   "If you know what caused the error and could work around it, please report it anyway. This allows us to improve the error messages.{}".format(label_suffix))
    label.setWordWrap(True)
    label.setOpenExternalLinks(True)
    right_widget.layout().addWidget(label)

    tb = QTextBrowser()
    tb.setHtml(error_message)
    right_widget.layout().addWidget(tb)

    cbox = QCheckBox("Show this message again")
    cbox.setChecked(True)
    right_widget.layout().addWidget(cbox)

    btn = QPushButton("Close")
    btn.clicked.connect(lambda event: app.exit())
    right_widget.layout().addWidget(btn)

    widget.layout().addWidget(right_widget)
    window.setMinimumSize(640, 400)
    window.resize(950, 600)
    window.show()

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
    argv = deepcopy(sys.argv) # Deep copy because QApplication (i.e. BrickViewer) constructor parses away Qt args and we want to know the style.
    if '--no-error-reporter' not in sys.argv:
        ExceptionReporter(argv)

    # Exceptions that happen before the event loop runs (f.e. syntax errors) kill the brickv so fast, that the error reporter thread
    # (which is daemonized) can not report the error before it is killed. Report them manually.
    try:
        # importing the MainWindow after creating the QApplication instance triggers this warning
        #
        #  Qt WebEngine seems to be initialized from a plugin. Please set Qt::AA_ShareOpenGLContexts
        #  using QCoreApplication::setAttribute before constructing QGuiApplication.
        #
        # do what the warnings says to avoid it
        QApplication.setAttribute(Qt.AA_ShareOpenGLContexts)

        brick_viewer = BrickViewer(sys.argv)

        if sys.platform == 'darwin':
            # workaround macOS QTBUG-61562
            from brickv.mac_pasteboard_mime_fixed import MacPasteboardMimeFixed
            mac_pasteboard_mime_fixed = MacPasteboardMimeFixed()

        splash = QSplashScreen(load_pixmap('splash.png'), Qt.WindowStaysOnTopHint)
        splash.show()

        message = 'Starting Brick Viewer ' + config.BRICKV_FULL_VERSION

        # FIXME: Need int cast for alignment here, because of an API design bug
        #        in Qt. The alignment parameter has type int but should have type
        #        Qt.Alignment. Because of this Python 3.8 reports a deprecation
        #        warning about implicit int casts being removed in the future.
        splash.showMessage(message, int(Qt.AlignHCenter | Qt.AlignBottom), Qt.white)

        brick_viewer.processEvents()

        from brickv.mainwindow import MainWindow

        main_window = MainWindow(brickv_version)
        main_window.show()

        splash.finish(main_window)
    except:
        if '--no-error-reporter' in sys.argv:
            raise

        etype, value, tb = sys.exc_info()
        error = "".join(traceback.format_exception(etype, value, tb))
        error = "!!!The following error is fatal. Exiting now.\n\n" + error

        traceback.print_exception(etype, value, tb)

        try:
            splash.close()
        except:
            pass

        # Either sys.executable is /path/to/python, then run calls /path/to/python /path/to/main.py --error-report,
        # or sys.executable is brickv[.exe], then the --error-report flag ensures, that the path to main.py is ignored.
        subprocess.run([sys.executable, os.path.realpath(__file__), "--error-report"] + argv, input=error, universal_newlines=True)
        sys.exit(1)

    sys.exit(brick_viewer.exec_())

if __name__ == "__main__":
    main()
