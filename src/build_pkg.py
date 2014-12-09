# -*- coding: utf-8 -*-
"""
brickv (Brick Viewer)
Copyright (C) 2012-2014 Matthias Bolte <matthias@tinkerforge.com>
Copyright (C) 2011 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2011 Bastian Nordmeyer <bastian@tinkerforge.com>

build_pkg.py: Package builder for Brick Viewer

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

# Windows:
#   dependencies:
#       pythonxy (2.6)
#       py2exe
#       nsis
#       win redistributables vcredist under winxp
#
#   run build scripts in all folders
#   run python build_pkg.py win to build the windows exe
#   final data is stored in folder "dist"
#
#   script copies OpenGL, special libs in dist folder

import os
import sys
import base64
from distutils.core import setup
import glob
import shutil
import struct
import brickv.config

DESCRIPTION = 'Brick Viewer'
NAME = 'Brickv'

def generate_plugin_images():
    image_files = []
    def image_visitor(arg, dirname, names):
        for name in names:
            if os.path.isfile(os.path.join(dirname, name)):
                _, ext = os.path.splitext(name)
                ext = ext[1:]

                if ext in ['bmp', 'png', 'jpg']:
                    image_files.append([os.path.join(dirname, name).replace('\\', '/').replace('brickv/', ''), ext])

    os.path.walk(os.path.join('brickv', 'plugin_system'), image_visitor, None)

    images = open(os.path.join('brickv', 'plugin_images.py'), 'wb')
    images.write('image_data = {\n')

    for image_file in image_files:
        image_data = base64.b64encode(file(os.path.join('brickv', image_file[0]), 'rb').read())
        images.write("'{0}': ['{1}', '{2}'],\n".format(image_file[0], image_file[1], image_data))

    images.write('}\n')
    images.close()

def build_macosx_pkg():
    from setuptools import setup, find_packages

    PWD = os.path.dirname(os.path.realpath(__file__))
    RES_PATH = os.path.join(PWD, 'dist', 'brickv.app', 'Contents', 'Resources')
    data_files = [("build_data/macosx/", glob.glob(os.path.join(PWD, "build_data/macosx/", "*.nib")))]
    packages = find_packages()

    plist = dict(
        CFBundleName = 'Brickv',
        CFBundleShortVersionString = brickv.config.BRICKV_VERSION,
        CFBundleGetInfoString = ' '.join(['Brickv', brickv.config.BRICKV_VERSION]),
        CFBundleExecutable = 'main',
        CFBundleIdentifier = 'com.tinkerforge.brickv',
        CFBundleIconFile = 'brickv-icon.icns',
    )

    def visitor(arg, dirname, names):
        for n in names:
            if os.path.isfile(os.path.join(dirname, n)):
                if arg[0]: # replace first folder name
                    data_files.append((os.path.join(dirname.replace(arg[1],"")) , [os.path.join(dirname, n)]))
                else: # keep full path
                    data_files.append((os.path.join(dirname), [os.path.join(dirname, n)]))

    os.path.walk(os.path.normcase("build_data/macosx/"), visitor, (True, os.path.normcase("build_data/macosx/")))
    data_files.append((os.path.join('.'), [os.path.join('.', 'brickv', 'brickv-icon.png')]))
    data_files.append((os.path.join('.'), [os.path.join('.', 'brickv', 'tab-default-icon.png')]))
    data_files.append((os.path.join('.'), [os.path.join('.', 'brickv', 'tab-mouse-over-icon.png')]))
    data_files.append((os.path.join('.'), [os.path.join('.', 'brickv', 'file-icon.png')]))
    data_files.append((os.path.join('.'), [os.path.join('.', 'brickv', 'folder-icon.png')]))
    data_files.append((os.path.join('.'), [os.path.join('.', 'brickv', 'dialog-warning.png')]))

    def delete_old():
        BUILD_PATH = os.path.join(PWD, "build")
        DIST_PATH = os.path.join(PWD, "dist")
        if os.path.exists(BUILD_PATH):
            shutil.rmtree(BUILD_PATH)
        if os.path.exists(DIST_PATH):
            shutil.rmtree(DIST_PATH)

    def create_app():
        os.system("python build_all_ui.py")

        generate_plugin_images()

        apps = [{"script": "brickv/main.py", "plist": plist}]

        OPTIONS = {'argv_emulation' : True,
                   'iconfile' : 'build_data/macosx/brickv-icon.icns',
                   'site_packages' : True,
                   'includes' : ["atexit",
                                 "sip",
                                 "PyQt4.QtCore",
                                 "PyQt4.QtGui",
                                 "PyQt4.QtOpenGL",
                                 "PyQt4.QtSvg",
                                 "PyQt4.Qwt5",
                                 "OpenGL.GL",
                                 "numpy.core.multiarray",
                                 "ctypes.util",
                                 "serial",
                                 "colorsys",
                                ],
                   'excludes' : ['scipy',
                                 'distutils',
                                 'setuptools',
                                 'email',
                                 'matplotlib',
                                 'PyQt4.QtDeclarative',
                                 'PyQt4.QtDesigner',
                                 'PyQt4.QtHelp',
                                 'PyQt4.QtMultimedia',
                                 'PyQt4.QtNetwork',
                                 'PyQt4.QtScript',
                                 'PyQt4.QtScriptTools',
                                 'PyQt4.QtSql',
                                 'PyQt4.QtTest',
                                 'PyQt4.QtWebKit',
                                 'PyQt4.QtXml',
                                 'PyQt4.QtXmlPatterns']}

        setup(
            name = 'brickv',
            version = brickv.config.BRICKV_VERSION,
            description = 'Brick Viewer Software',
            author = 'Tinkerforge',
            author_email = 'info@tinkerforge.com',
            platforms = ["Mac OSX"],
            license = "GPL v2",
            url = "http://www.tinkerforge.com",
            scripts = ['brickv/main.py'],
            app = apps,
            options = {'py2app': OPTIONS},
            data_files = data_files,
            packages = packages,
        )

    def qt_menu_patch():
        src = os.path.join(PWD, 'build_data', 'macosx', 'qt_menu.nib')
        dst = os.path.join(RES_PATH, 'qt_menu.nib')
        if not os.path.exists(dst):
            shutil.copytree(src, dst)

    _RUN_IN_TERM_PATCH = """import os
import sys

os.environ['RESOURCEPATH'] = os.path.dirname(os.path.realpath(__file__))

"""

    def run_in_term_patch():
        BOOT_FILE_PATH = os.path.join(RES_PATH, "__boot__.py")
        with open(BOOT_FILE_PATH) as f:
            old = f.read()

        new = _RUN_IN_TERM_PATCH + old

        with open(BOOT_FILE_PATH, 'w') as f:
            f.write(new)

    def data_files_patch():
        for item in data_files:
            if isinstance(item, tuple):
                folder_name = item[0]
            else:
                folder_name = item

            src = os.path.join(PWD, folder_name)
            dst = os.path.join(RES_PATH, folder_name)
            if not os.path.exists(dst):
                shutil.copytree(src, dst)

    ACTION_CREATE = len(sys.argv) == 3 and sys.argv[-1] == "build"

    if ACTION_CREATE:
        delete_old()
        create_app()
        qt_menu_patch()
        run_in_term_patch()
        data_files_patch()
    else:
        print "Usage: python setup.py py2app build"

# https://github.com/rfk/www.rfk.id.au/blob/master/content/blog/entry/code-signing-py2exe/index.html
def sign_py2exe(exepath):
    # First, sign a *copy* of the file so that we know its final size.
    execopy = os.path.join(os.path.dirname(exepath),
                           "temp-" + os.path.basename(exepath))
    shutil.copy2(exepath, execopy)
    os.system('X:\\sign.bat ' + execopy)

    # Figure out the size of the appended signature.
    comment_size = os.stat(execopy).st_size - os.stat(exepath).st_size
    os.unlink(execopy)

    # Write the correct comment size as the last two bytes of the file.
    with open(exepath, "r+") as f:
        f.seek(-2, os.SEEK_END)
        f.write(struct.pack("<H", comment_size))

    # Now we can sign the file for real.
    os.system('X:\\sign.bat ' + exepath)

def build_windows_pkg():
    PWD = os.path.dirname(os.path.realpath(__file__))
    BUILD_PATH = os.path.join(PWD, "build")
    DIST_PATH = os.path.join(PWD, "dist")
    if os.path.exists(BUILD_PATH):
        shutil.rmtree(BUILD_PATH)
    if os.path.exists(DIST_PATH):
        shutil.rmtree(DIST_PATH)

    import py2exe
    os.system("python build_all_ui.py")

    data_files = []
    def visitor(arg, dirname, names):
        for n in names:
            if os.path.isfile(os.path.join(dirname, n)):
                if arg[0]: # replace first folder name
                    data_files.append((os.path.join(dirname.replace(arg[1],"")), [os.path.join(dirname, n)]))
                else: # keep full path
                    data_files.append((os.path.join(dirname), [os.path.join(dirname, n)]))

    os.path.walk(os.path.normcase("build_data/windows/"), visitor, (True, os.path.normcase("build_data/windows/")))
    data_files.append((os.path.join('.'), [os.path.join('.', 'brickv', 'brickv-icon.png')]))
    data_files.append((os.path.join('.'), [os.path.join('.', 'brickv', 'tab-default-icon.png')]))
    data_files.append((os.path.join('.'), [os.path.join('.', 'brickv', 'tab-mouse-over-icon.png')]))
    data_files.append((os.path.join('.'), [os.path.join('.', 'brickv', 'file-icon.png')]))
    data_files.append((os.path.join('.'), [os.path.join('.', 'brickv', 'folder-icon.png')]))
    data_files.append((os.path.join('.'), [os.path.join('.', 'brickv', 'dialog-warning.png')]))

    generate_plugin_images()

    setup(name = NAME,
          description = DESCRIPTION,
          version = brickv.config.BRICKV_VERSION,
          data_files = data_files,
          options = {
                    "py2exe" : {
                    "dll_excludes" : ["MSVCP90.dll"],
                    "includes" : ["sip",
                                  "PyQt4.QtCore",
                                  "PyQt4.QtGui",
                                  "PyQt4.QtOpenGL",
                                  "PyQt4.QtSvg",
                                  "PyQt4.Qwt5",
                                  "OpenGL.GL",
                                  "numpy.core.multiarray",
                                  "ctypes.util",
                                  "serial",
                                  "colorsys",
                                  "win32com.client",
                                  "win32con",
                                  "winerror",
                                  "pywintypes",
                                  "win32file",
                                  "win32api"],
                    "excludes" : ["config_linux",
                                  "config_macosx",
                                  "_gtkagg",
                                  "_tkagg",
                                  "Tkconstants",
                                  "Tkinter",
                                  "tcl",
                                  "pydoc",
                                  "email",
                                  "nose",
                                  "inspect",
                                  "ctypes.macholib",
                                  "win32pdh",
                                  "win32ui"]
                    }
                    },
          zipfile = None,
          windows = [{'script' : 'brickv/main.py',
                      'icon_resources' : [(0, os.path.normcase("build_data/windows/brickv-icon.ico"))],
                      'dest_base' : 'brickv'
                     }]
    )

    # FIXME: doesn't work yet
    #if os.path.exists('X:\\sign.bat'):
    #    sign_py2exe('dist\\brickv.exe')

    # build nsis
    lines = []
    for line in file('build_data/windows/nsis/brickv_installer.nsi.template', 'rb').readlines():
        line = line.replace('<<BRICKV_DOT_VERSION>>', brickv.config.BRICKV_VERSION)
        line = line.replace('<<BRICKV_UNDERSCORE_VERSION>>', brickv.config.BRICKV_VERSION.replace('.', '_'))
        lines.append(line)
    file('dist/nsis/brickv_installer.nsi', 'wb').writelines(lines)

    os.system('"C:\\Program Files\\NSIS\\makensis.exe" dist\\nsis\\brickv_installer.nsi')

    dist_nsis_dir = os.path.join(os.getcwd(), 'dist', 'nsis')
    installer = 'brickv_windows_{0}.exe'.format(brickv.config.BRICKV_VERSION.replace('.', '_'))

    if os.path.exists(installer):
        os.unlink(installer)

    shutil.move(os.path.join(dist_nsis_dir, installer), os.getcwd())

    if os.path.exists('X:\\sign.bat'):
        os.system('X:\\sign.bat ' + installer)


def build_linux_pkg():
    if os.geteuid() != 0:
        sys.stderr.write("build_pkg for Linux has to be started as root, exiting\n")
        sys.exit(1)

    print('building brickv package')

    os.system("python build_all_ui.py")

    generate_plugin_images()

    src_path = os.path.join(os.getcwd(), 'brickv')
    build_dir = os.path.join('build_data', 'linux', 'brickv', 'usr', 'share', 'brickv')
    dest_path = os.path.join(os.getcwd(), build_dir)
    if os.path.isdir(dest_path):
        shutil.rmtree(dest_path)

    shutil.copytree(src_path, dest_path)

    build_data_path = os.path.join(os.getcwd(), 'build_data', 'linux')
    os.chdir(build_data_path)

    STEXT = 'Version:'
    RTEXT = 'Version: {0}\n'.format(brickv.config.BRICKV_VERSION)

    f = open(os.path.join('brickv', 'DEBIAN', 'control'), 'rb')
    lines = f.readlines()
    f.close()

    f = open(os.path.join('brickv', 'DEBIAN', 'control'), 'wb')
    for line in lines:
        if not line.find(STEXT) == -1:
            line = RTEXT
        f.write(line)
    f.close()

    os.system('find brickv/usr -type f -path *.pyc -exec rm {} \;')
    os.system('find brickv/usr -type d -exec chmod 0755 {} \;')

    os.system('chown -R root:root brickv/usr')
    os.system('dpkg -b brickv/ brickv-' + brickv.config.BRICKV_VERSION + '_all.deb')
    os.system('chown -R `logname`:`logname` brickv/usr')


BRICK_FLASH_CMD_VERSION = '1.0.0'

def build_linux_cmd_pkg():
    if os.geteuid() != 0:
        sys.stderr.write("build_pkg for Linux has to be started as root, exiting\n")
        sys.exit(1)

    print('building brick-flash-cmd package')

    src_path = os.path.join(os.getcwd(), 'brickv')
    dest_path = os.path.join(os.getcwd(), 'build_data', 'linux', 'brick-flash-cmd', 'usr', 'bin')

    if os.path.exists(dest_path):
        shutil.rmtree(dest_path)
    os.makedirs(dest_path)

    f = open(os.path.join(src_path, 'brick-flash-cmd.template'), 'rb')
    template = f.read()
    f.close()

    f = open(os.path.join(src_path, 'samba.py'), 'rb')
    samba_lines = f.readlines()
    f.close()

    while len(samba_lines) > 0 and not samba_lines[0].startswith('#### skip here for brick-flash-cmd ####'):
        del samba_lines[0]

    if len(samba_lines) > 0 and samba_lines[0].startswith('#### skip here for brick-flash-cmd ####'):
        del samba_lines[0]

    template = template.replace('#### insert samba module here ####', ''.join(samba_lines))

    f = open(os.path.join(dest_path, 'brick-flash-cmd'), 'wb')
    f.write(template)
    f.close()

    build_data_path = os.path.join(os.getcwd(), 'build_data', 'linux')
    os.chdir(build_data_path)

    STEXT = 'Version:'
    RTEXT = 'Version: {0}\n'.format(BRICK_FLASH_CMD_VERSION)

    f = open(os.path.join('brick-flash-cmd', 'DEBIAN', 'control'), 'rb')
    lines = f.readlines()
    f.close()

    f = open(os.path.join('brick-flash-cmd', 'DEBIAN', 'control'), 'wb')
    for line in lines:
        if not line.find(STEXT) == -1:
            line = RTEXT
        f.write(line)
    f.close()

    os.system('chmod 0755 brick-flash-cmd/usr/bin/brick-flash-cmd')
    os.system('find brick-flash-cmd/usr -type d -exec chmod 0755 {} \;')
    os.system('chown -R root:root brick-flash-cmd/usr')
    os.system('dpkg -b brick-flash-cmd/ brick-flash-cmd-' + BRICK_FLASH_CMD_VERSION + '_all.deb')
    os.system('chown -R `logname`:`logname` brick-flash-cmd/usr')


# call python build_pkg.py to build the windows/linux/macosx package
if __name__ == "__main__":
    full_argv = sys.argv[:]
    if len(sys.argv) > 1:
        sys.argv = sys.argv[:1]

    if sys.platform.startswith('linux'):
        if len(full_argv) > 1 and full_argv[1] == 'cmd':
            build_linux_cmd_pkg()
        else:
            build_linux_pkg()
    elif sys.platform == 'win32':
        sys.argv.append('py2exe') # set sys.argv[1] for setup(), want to call py2exe
        build_windows_pkg()
    elif sys.platform == 'darwin':
        sys.argv.append('py2app') # set sys.argv[1] for setup(), want to call py2app
        sys.argv.append('build')
        build_macosx_pkg()
    else:
        print "error: unsupported platform: " + sys.platform
