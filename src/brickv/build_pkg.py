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
    import shutil
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
