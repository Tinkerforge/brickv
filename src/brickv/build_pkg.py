# -*- coding: utf-8 -*-  
"""
brickv (Brick Viewer) 
Copyright (C) 2011 Olaf Lüke <olaf@tinkerforge.com>
              2011 Bastian Nordmeyer <bastian@tinkerforge.com>

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
#   script copies OpenGL, special libs and plugin_system
#   in dist folder


import config

import sys  
from distutils.core import setup
import os
import glob
import shutil
import matplotlib
 
DESCRIPTION = 'Brick Viewer'
NAME = 'Brickv'

def build_macos_pkg():
    from setuptools import setup, find_packages


    PWD = os.path.dirname(os.path.realpath(__file__))
    RES_PATH = os.path.join(PWD, 'dist', '%s.app' % 'brickv', 'Contents', 'Resources')
    data_files = [
        ("../build_data/macos/", glob.glob(os.path.join(PWD, "../build_data/macos/", "*.nib"))),
        #('/usr/share/applications',['foo.desktop']),
    ]
    packages = find_packages()

    plist = dict(
        CFBundleName = 'Brickv',
        CFBundleShortVersionString = config.BRICKV_VERSION,
        CFBundleGetInfoString = ' '.join(['Brickv', config.BRICKV_VERSION]),
        CFBundleExecutable = 'main',
        CFBundleIdentifier = 'org.tinkerforge.brickv',
        CFBundleIconFile = 'brickv-icon.icns',
        # hide dock icon
    #    LSUIElement = True,
    )

    additional_data_files = matplotlib.get_py2exe_datafiles()
    def visitor(arg, dirname, names):
        for n in names:

            if os.path.isfile(os.path.join(dirname, n)):
                if arg[0] == 'y': #replace first folder name
                    additional_data_files.append((os.path.join(dirname.replace(arg[1],"")) , [os.path.join(dirname, n)]))
                else: # keep full path
                    additional_data_files.append((os.path.join(dirname) , [os.path.join(dirname, n)]))
    
    os.path.walk(os.path.normcase("../build_data/macos/"), visitor, ('y',os.path.normcase("../build_data/macos/")))
    os.path.walk("plugin_system", visitor, ('n',"plugin_system"))
    
    additional_data_files.append( ( os.path.join('.') , [os.path.join('.', 'brickv-icon.png')] ) )
 



    def delete_old():
        BUILD_PATH = os.path.join(PWD, "build")
        DIST_PATH = os.path.join(PWD, "dist")
        if os.path.exists(BUILD_PATH):
            shutil.rmtree(BUILD_PATH)
        if os.path.exists(DIST_PATH):
            shutil.rmtree(DIST_PATH)

    def create_app():
        os.system("python build_all_ui.py")
        apps = [
            {
                "script" : "main.py",
                "plist" : plist,
            }
        ]

        OPTIONS = {'argv_emulation': True, 'iconfile':'../build_data/macos/brickv-icon.icns','site_packages': True, "includes":["atexit", "PyQt4.QtSvg", "sip","PyQt4.Qwt5", "PyQt4.QtCore", "PyQt4.QtGui","numpy.core.multiarray", "PyQt4.QtOpenGL","OpenGL.GL", "ctypes.util", "plot_widget", "pylab", "matplotlib.backends.backend_qt4agg", "scipy.interpolate"],}

        data = data_files + additional_data_files

        setup(
            name = 'brickv',
            version = config.BRICKV_VERSION,
            description = 'Brick Viewer Software',
            author = 'Tinkerforge',
            author_email = 'info@tinkerforge.com',
            platforms = ["Mac OSX"],
            license = "GPL V2",
            url = "http://www.tinkerforge.com",
            scripts = ['main.py'],

            app = apps,
            options = {'py2app': OPTIONS},
            # setup_requires = ['py2app'],
            data_files = data,
            packages = packages,
        )


    def qt_menu_patch():
        src = os.path.join(PWD, '../build_data/macos/', 'qt_menu.nib')
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

#hack: fix wrong position of plugin_system
        src = os.path.join(RES_PATH, "plugin_system")
        dst = os.path.join(RES_PATH, "../MacOS/plugin_system")
        shutil.copytree(src, dst)

        
    ACTION_CREATE = len(sys.argv) == 3 and sys.argv[-1] == "build"

    if ACTION_CREATE:
        delete_old()
        create_app()
        qt_menu_patch()
        run_in_term_patch()
        data_files_patch()
    else:
#create_app()
        print "Usage: python setup.py py2app build"





def build_windows_pkg():
    import py2exe
    os.system("python build_all_ui.py")
    
    data_files = matplotlib.get_py2exe_datafiles()
    def visitor(arg, dirname, names):
        for n in names:

            if os.path.isfile(os.path.join(dirname, n)):
                if arg[0] == 'y': #replace first folder name
                    data_files.append((os.path.join(dirname.replace(arg[1],"")) , [os.path.join(dirname, n)]))
                else: # keep full path
                    data_files.append((os.path.join(dirname) , [os.path.join(dirname, n)]))
    
    os.path.walk(os.path.normcase("../build_data/Windows/"), visitor, ('y',os.path.normcase("../build_data/Windows/")))
    os.path.walk("plugin_system", visitor, ('n',"plugin_system"))
    
    data_files.append( ( os.path.join('.') , [os.path.join('.', 'brickv-icon.png')] ) )
      
    STEXT = '!define BRICKV_VERSION'
    RTEXT = '!define BRICKV_VERSION ' + config.BRICKV_VERSION

    f = open('../build_data/Windows/nsis/brickv_installer_windows.nsi', 'r')
    lines = f.readlines()
    f.close()

    f = open('../build_data/Windows/nsis/brickv_installer_windows.nsi', 'w')
    for line in lines:
        if not line.find(STEXT) == -1:
            line = RTEXT
        f.write(line)
    f.close()

    setup(
          name = NAME,
          description = DESCRIPTION,
          version = config.BRICKV_VERSION,
          data_files = data_files,
          options = {
                    "py2exe":{
                    "dll_excludes":["MSVCP90.dll"], 
                        "includes":["PyQt4.QtSvg", "sip","PyQt4.Qwt5", "PyQt4.QtCore", "PyQt4.QtGui","numpy.core.multiarray", "PyQt4.QtOpenGL","OpenGL.GL", "ctypes.util", "plot_widget", "pylab", "matplotlib.backends.backend_qt4agg", "scipy.interpolate"],
                        "excludes":["_gtkagg", "_tkagg"]
                        }
                    },
          zipfile=None,
          windows = [{'script':'main.py', 'icon_resources':[(0,os.path.normcase("../build_data/Windows/brickv-icon.ico"))]}]
    )
    
    # build nsis
    run = "\"" + os.path.join("C:\Program Files\NSIS\makensis.exe") + "\""
    data = " dist\\nsis\\brickv_installer_windows.nsi"
    print "run:", run
    print "data:", data
    os.system(run + data)

def build_linux_pkg():
    src_path = os.getcwd()
    build_dir = 'build_data/linux/brickv/usr/share/brickv'
    dest_path = os.path.join(os.path.split(src_path)[0], build_dir)
    if os.path.isdir(dest_path):
        shutil.rmtree(dest_path)

    shutil.copytree(src_path, dest_path)
    
    build_data_path = os.path.join(os.path.split(src_path)[0], 'build_data/linux')
    os.chdir(build_data_path)
    os.system('dpkg -b brickv/ brickv-' + config.BRICKV_VERSION + '_all.deb')
    
if __name__ == "__main__":
    if sys.argv[1] == "win":
        sys.argv[1] = "py2exe" # rewrite sys.argv[1] for setup(), want to call py2exe
        build_windows_pkg()
    if sys.argv[1] == "linux":
        build_linux_pkg()
    if sys.argv[1] == "macos":
        sys.argv[1] = "py2app" # rewrite sys.argv[1] for setup(), want to call py2exe
        sys.argv.append("build") # rewrite sys.argv[1] for setup(), want to call py2exe
        build_macos_pkg()
