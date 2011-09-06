# package builder for brickv
#
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
    
    os.path.walk("..\build_data\Windows\\", visitor, ('y',"..\build_data\Windows\\"))
    os.path.walk("plugin_system", visitor, ('n',"plugin_system"))
    
    setup(
          name = NAME,
          description = DESCRIPTION,
          version = '1.00.00',
          data_files = data_files,
          options = {
                    "py2exe":{
                        "dll_excludes":["MSVCP90.dll"], 
                        "includes":["PyQt4.QtSvg", "sip","PyQt4.Qwt5", "PyQt4.QtCore", "PyQt4.QtGui","numpy.core.multiarray", "PyQt4.QtOpenGL","OpenGL.GL", "ctypes.util", "plot_widget", "pylab", "matplotlib.backends.backend_qt4agg", "scipy.interpolate"],
                        "excludes":["_gtkagg", "_tkagg"]
                        }
                    },
          zipfile=None,
          windows = [{'script':'main.py'}]
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
    os.system('dpkg -b brickv/ brickv-1.0_all.deb')
    
if __name__ == "__main__":
    if sys.argv[1] == "win":
        sys.argv[1] = "py2exe" # rewrite sys.argv[1] for setup(), want to call py2exe
        build_windows_pkg()
    if sys.argv[1] == "linux":
        build_linux_pkg()
