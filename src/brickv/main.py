#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
brickv (Brick Viewer)
Copyright (C) 2009-2013 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2013-2015 Matthias Bolte <matthias@tinkerforge.com>
Copyright (C) 2020-2022 Erik Fleckstein <erik@tinkerforge.com>

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
import platform
import urllib.parse
import time
import argparse
import io

def prepare_package(package_name):
    # from http://www.py2exe.org/index.cgi/WhereAmI
    if getattr(sys, 'frozen', False):
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

        if not getattr(sys, 'frozen', False):
            # load and inject in modules list, this allows to have the source in a
            # directory named differently than '<package_name>'
            sys.modules[package_name] = __import__(tail, globals(), locals())

prepare_package('brickv')

from PyQt5.Qt import PYQT_VERSION_STR
from PyQt5.QtCore import QEvent, pyqtSignal, Qt, QSysInfo, QT_VERSION_STR, QUrl
from PyQt5.QtGui import QIcon, QDesktopServices, QPalette
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QTextBrowser, \
                            QPushButton, QWidget, QLabel, QCheckBox, QHBoxLayout, \
                            QSplashScreen, QSizePolicy, QMessageBox

# QOperatingSystemVersion is only available since Qt 5.9
try:
    from PyQt5.QtCore import QOperatingSystemVersion
    q_os_version_available = True
except:
    q_os_version_available = False

from brickv import config
from brickv.async_call import ASYNC_EVENT, async_event_handler
from brickv.load_pixmap import load_pixmap
from brickv.ui_errorreporter import Ui_ErrorReporter
from brickv.utils import get_save_file_name, get_home_path

logging.basicConfig(level=config.LOGGING_LEVEL,
                    format=config.LOGGING_FORMAT,
                    datefmt=config.LOGGING_DATEFMT)

brickv_version = [(0, 0, 0), (0, 0, 0)]

class ExceptionReporter:
    def __init__(self):
        self.start_time = time.monotonic()
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
            return platform.platform()

    def error_spawner(self):
        ignored = []
        while True:
            time_occured, exctype, value, tb, thread = self.error_queue.get()
            error = "".join(traceback.format_exception(exctype, value=value, tb=tb))

            hash_ = hash(error)
            if hash_ in ignored:
                continue

            label_suffix = ''

            if brickv_version[1] == (0, 0, 0):
                label_suffix += '<br/><br/><b>Your Brick Viewer version is {}, however it is unknown if a newer version is available.</b> Please <a href="https://www.tinkerforge.com/en/doc/Downloads.html#tools">check for updates</a> before reporting this error.'.format(config.BRICKV_FULL_VERSION)

            elif brickv_version[0] < brickv_version[1]:
                label_suffix += '<br/><br/><b>Your Brick Viewer version is {}, however {}.{}.{} is available.</b> Please update and try again before reporting this error.'.format(config.BRICKV_FULL_VERSION, *brickv_version[1])

            runtime = str(datetime.timedelta(seconds=time.monotonic() - self.start_time))
            prefix = 'Brick Viewer {} on\n{}\nPyQt {}\nQt {}\nPython {}\nSystem language: {}\n\nException raised at {}\nBrick Viewer ran for {}\n'.format(
                config.BRICKV_FULL_VERSION,
                self.get_os_name(),
                PYQT_VERSION_STR,
                QT_VERSION_STR,
                sys.version.replace("\n", ""),
                locale.getdefaultlocale()[0],
                time_occured,
                runtime)

            if thread is not None:
                prefix += ' by Thread {}'.format(thread.ident)
                if thread.name is not None:
                    prefix += ' (Name: {})'.format(thread.name)
            print(prefix)

            prefix = label_suffix + '!!!' + prefix

            traceback.print_exception(exctype, value=value, tb=tb)
            print("")

            report_message = prefix + '\n' + error + '\nActive Threads:\n\n' + '\n\n'.join(self.get_python_thread_stack_traces())

            # Either sys.executable is /path/to/python, then run calls /path/to/python /path/to/main.py --error-report,
            # or sys.executable is brickv[.exe], then the --error-report flag ensures, that the path to main.py is ignored.
            rc = subprocess.run([sys.executable, os.path.realpath(__file__), "--error-report"], input=report_message, universal_newlines=True).returncode

            show_again = rc & 1 == 1
            exit_requested = rc & 2 == 2

            if exit_requested:
                QApplication.exit(1)
                return

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

        if sys.platform == 'darwin' and config.get_use_fusion_gui_style():
            # workaround macOS QTBUG-75321
            p = self.palette()
            p.setColor(QPalette.ButtonText, p.color(QPalette.WindowText))
            self.setPalette(p)

    def object_creator_slot(self, object_creator):
        object_creator.create()

    def notify(self, receiver, event):
        if event.type() > QEvent.User and event.type() == ASYNC_EVENT:
            async_event_handler()

        return QApplication.notify(self, receiver, event)

class ErrorReporter(QMainWindow, Ui_ErrorReporter):
    def closeEvent(self, event):
        QApplication.exit(int(self.check_show_again.isChecked()))

def error_report_main(qapplication_argv):
    error_message = sys.stdin.read()

    if len(error_message) == 0:
        # FIXME: for some unknown reason it can happen that stdin is empty
        label_suffix = ''
        error_message = 'An unknown error occurred!'
    elif '!!!' in error_message:
        label_suffix, error_message = error_message.split('!!!')

    formatted_error_message = "<pre>{}</pre>".format(html.escape(error_message).replace("\n", "<br>"))

    app = QApplication(qapplication_argv)

    if sys.platform == 'darwin':
        # workaround macOS QTBUG-61562
        from brickv.mac_pasteboard_mime_fixed import MacPasteboardMimeFixed
        mac_pasteboard_mime_fixed = MacPasteboardMimeFixed()

    window = ErrorReporter()
    window.setupUi(window)
    window.setWindowTitle('Error - ' + config.BRICKV_TITLE)
    window.setWindowIcon(QIcon(load_pixmap('brickv-icon.png')))

    mail_url = 'mailto:info@tinkerforge.com?subject=Brickv Error Report&body=PLEASE ALSO DESCRIBE WHAT YOU TRIED TO DO AT THE TIME THE ERROR OCCURRED.{}'.format(urllib.parse.quote("\n\n"+error_message))
    title = "<b>Please report this error to <a href='{}'>info@tinkerforge.com</a>.<b>".format(mail_url)
    description = "You can either save the report to a text file by clicking the <b>Save</b> button below and email the file to us or you can click the <b>Email</b> button below to prepopulate an email in your email program.<br><br>" + \
                  "Please also describe what you tried to do at the time the error occurred.<br/><br/>" + \
                  "If you know what caused the error and could work around it, please tell us anyway. This allows us to improve the robustness of Brick Viewer.{}".format(label_suffix)

    window.label_title.setText(title)
    window.label_description.setText(description)

    def save():
        date = datetime.datetime.now().replace(microsecond=0).isoformat().replace('T', '_').replace(':', '-')
        filename = get_save_file_name(window, 'Save Report To File', os.path.join(get_home_path(), 'brickv_error_report_{}.txt'.format(date)))

        if len(filename) == 0:
            return

        try:
            with open(filename, 'w') as f:
                f.write(error_message)
        except Exception as e:
            QMessageBox.critical(window, 'Save Report To File',
                                 'Could not save report to file:\n\n' + str(e),
                                 QMessageBox.Ok)

    window.button_save.clicked.connect(save)
    window.button_email.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(mail_url)))
    window.text_error.setHtml(formatted_error_message)
    window.check_show_again.setChecked(True)
    window.button_close.clicked.connect(lambda event: app.exit(int(window.check_show_again.isChecked())))

    def close_and_exit():
        app.exit(int(window.check_show_again.isChecked()) + 2)

    window.button_close_and_exit.clicked.connect(lambda event: close_and_exit())

    window.setMinimumSize(640, 400)
    window.resize(800, 800)
    window.show()

    return app.exec_()

def stdio_wrapper(qapplication_argv, func):
    if not getattr(sys, 'frozen', False) or sys.platform.startswith('linux'):
        return func()
    else:
        # frozen programs on Windows and macOS have no stdio properly attached.
        # capture stdio output and show it in a message box instead
        stdio = io.StringIO()

        old_stdout = sys.stdout
        old_stderr = sys.stderr

        sys.stdout = stdio
        sys.stderr = stdio

        try:
            return func()
        except SystemExit:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

            app = QApplication(qapplication_argv)
            app.setWindowIcon(QIcon(load_pixmap('brickv-icon.png')))

            mbox = QMessageBox(QMessageBox.NoIcon, config.BRICKV_TITLE, stdio.getvalue().strip(), buttons=QMessageBox.Ok)
            QWidget.setWindowTitle(mbox, config.BRICKV_TITLE) # macOS UI guidelines forbid message box window titles, ignore these guidelines
            mbox.exec_()

            raise

def main(dev_mode):
    try:
        locale.setlocale(locale.LC_ALL, '')
    except locale.Error:
        pass # ignore this as it might fail on macOS, we'll fallback to UTF-8 in that case

    qapplication_argv = [sys.argv[0]]

    if config.get_use_fusion_gui_style():
        qapplication_argv += ['-style', 'fusion']

    if '--error-report' in sys.argv:
        # special handle --error-report option for the "brickv[.exe] /path/to/main.py --error-report"
        # case were the /path/to/main.py has to be ignored. also the --error-report flag is for internal
        # usage anyway, so no need for argparse niceness
        sys.exit(error_report_main(qapplication_argv))

    parser = argparse.ArgumentParser(prog='brickv', description=config.BRICKV_TITLE)

    parser.add_argument('-v', '--version', action='version', version=config.BRICKV_VERSION)
    parser.add_argument('host', nargs='?', help='connect to given host')
    parser.add_argument('-p', '--port', type=int, help='port for given host [default: 4223]', default=4223)
    parser.add_argument('-s', '--secret', help='secret for given host [default: disabled]')
    parser.add_argument('-r', '--remember-secret', action='store_true', help='remember secret for given host [default: disabled]')
    parser.add_argument('--no-dev-mode', action='store_true', help='disable Python dev mode [default: disabled]')
    parser.add_argument('--no-error-reporter', action='store_true', help='disable error reporter [default: enabled]')

    args = stdio_wrapper(qapplication_argv, lambda: parser.parse_args(sys.argv[1:]))

    if not args.no_dev_mode and dev_mode and not sys.flags.dev_mode:
        sys.exit(subprocess.run([sys.executable, '-X', 'dev', '-W', 'error', '-B', '-X', 'pycache_prefix=__dev_mode_pycache__'] + sys.argv).returncode)

    # Catch all uncaught exceptions and show an error message for them.
    # PyQt5 does not silence exceptions in slots (as did PyQt4), so there
    # can be slots which try to (for example) send requests but don't wrap
    # them in an async call with error handling.
    if not args.no_error_reporter:
        ExceptionReporter()

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

        brick_viewer = BrickViewer(qapplication_argv)

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

        main_window = MainWindow(brickv_version, args.host, args.port, args.secret, args.remember_secret)
        main_window.show()

        splash.finish(main_window)
    except:
        if args.no_error_reporter:
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
        subprocess.run([sys.executable, os.path.realpath(__file__), "--error-report"], input=error, universal_newlines=True)
        sys.exit(1)

    sys.exit(brick_viewer.exec_())

if __name__ == "__main__":
    main(not getattr(sys, 'frozen', False))
