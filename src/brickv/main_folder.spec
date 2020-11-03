# -*- mode: python -*-

# work-around for https://github.com/pyinstaller/pyinstaller/issues/4064
# Before virtualenv 16.4.0 distutils_path was set to the directory distutils is found in.
# Since virtualenv 16.4.0 distutils_path points to the __init__.py file inside this directory.
# PyInstaller's distutils-hook still expectes the old format; fake it here.
# Also under macOS the distutils_path attribute is not available, but the work-around seems
# to be not necessary here.
import distutils

if hasattr(distutils, 'distutils_path') and distutils.distutils_path.endswith('__init__.py'):
    distutils.distutils_path = os.path.dirname(distutils.distutils_path)

import os
import sys

sys.path.insert(0, '..') # Ensure to use the brickv source, not an installed version
from brickv.pyinstaller_utils import *

utils = PyinstallerUtils(['brickv'])
utils.prepare()

excludes = ['wx', 'gtk+', '_gtkagg', 'gtk', 'gdk', 'gtk2', 'gtk3', 'cairo', 'wayland', 'xinerama', 'share', 'icons', 'atk', 'pango', 'pil', 'PIL',
            '_tkagg',
            'Tkconstants',
            'Tkinter',
            'tcl',
            'pydoc',
            #'email',
            'nose',
            #'inspect',
            #'ctypes.macholib',
            'win32pdh',
            'win32ui',
            'PyOpenGL',
            'OpenGL',
            'PyQt5.Enginio',
            'PyQt5.QAxContainer',
            #'PyQt5.Qt3DAnimation',
            #'PyQt5.Qt3DCore',
            #'PyQt5.Qt3DExtras',
            #'PyQt5.Qt3DInput',
            #'PyQt5.Qt3DLogic',
            #'PyQt5.Qt3DRender',
            'PyQt5.QtAndroidExtras',
            'PyQt5.QtBluetooth',
            'PyQt5.QtChart',
            'PyQt5.QtDBus',
            'PyQt5.QtDataVisualization',
            'PyQt5.QtDesigner',
            'PyQt5.QtHelp',
            'PyQt5.QtLocation',
            #'PyQt5.QtMacExtras',
            'PyQt5.QtMultimedia',
            'PyQt5.QtMultimediaWidgets',
            'PyQt5.QtNetwork',
            'PyQt5.QtNetworkAuth',
            'PyQt5.QtNfc',
            #'PyQt5.QtOpenGL',
            'PyQt5.QtPositioning',
            'PyQt5.QtPrintSupport',
            'PyQt5.QtPurchasing',
            'PyQt5.QtQml',
            'PyQt5.QtQuick',
            'PyQt5.QtQuickWidgets',
            'PyQt5.QtSensors',
            'PyQt5.QtSerialPort',
            'PyQt5.QtSql',
            'PyQt5.QtSvg',
            'PyQt5.QtTest',
            'PyQt5.QtWebChannel',
            'PyQt5.QtWebEngine',
            'PyQt5.QtWebEngineCore',
            'PyQt5.QtWebEngineWidgets',
            'PyQt5.QtWebKit',
            'PyQt5.QtWebKitWidgets',
            'PyQt5.QtWebSockets',
            'PyQt5.QtWinExtras',
            'PyQt5.QtX11Extras',
            'PyQt5.QtXml',
            'PyQt5.QtXmlPatterns']
patterns = ['qt5qml', 'qt5quick', 'qt5network', 'qt5dbus', 'qt5svg', 'qt5websockets',
            'qtqml', 'qtquick', 'qtnetwork', 'qwebp',
            'qjpeg', 'qminimal', 'qoffscreen', 'qwebgl']
hiddenimports = []

a = Analysis(['main.py'], pathex=utils.pathex, excludes=excludes, hiddenimports=hiddenimports)

binaries = utils.strip_binaries(a.binaries, patterns)

pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name=utils.underscore_name + ('.exe' if utils.windows else ''),
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=False,
          console=False,
          icon=utils.icon)

coll = COLLECT(exe,
               binaries,
               a.zipfiles,
               a.datas + utils.datas,
               strip=False,
               upx=False,
               name='')

if utils.macos:
    # CFBundleVersion and CFBundleShortVersionString can be most 18 chars long
    # and have to match this format: \d+\.\d+\.\d+
    app = BUNDLE(coll,
                 name=utils.camel_case_name + '.app',
                 icon=utils.icon,
                 info_plist={
                     'LSMinimumSystemVersion': '10.11', # required for PyQt 5.11.3
                     'CFBundleVersion': utils.version.split('+')[0],
                     'CFBundleShortVersionString': utils.version.split('+')[0],
                     'NSHighResolutionCapable': 'True',
                     'NSSupportsAutomaticGraphicsSwitching': 'True'
                 })

utils.post_generate()
