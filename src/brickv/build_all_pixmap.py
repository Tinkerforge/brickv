# -*- coding: utf-8 -*-
"""
brickv (Brick Viewer)
Copyright (C) 2012 Matthias Bolte <matthias@tinkerforge.com>

build_all_pixmap.py: Image converter for Brick Viewer

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
import os
from base64 import b64encode
from PyQt4.QtGui import QApplication
from PyQt4.QtGui import QPixmap

import_str = """from sys import platform
from base64 import b64decode
from PyQt4.QtGui import QImage, QPixmap

"""

get_image_str = """
def get_{0}():
    if platform == 'win32':
        return QPixmap('{1}')
    else:
        return QPixmap.fromImage(QImage(b64decode(data), width, height, format))
"""

def convert_images():
    file_url = os.path.abspath(__file__).replace(__file__, '')
    for f in os.walk(file_url):
        #print repr(f)
        for k in f[2]:
            if k.endswith('.gif'):
                p = os.path.join(f[0], k)
                print 'converting ' + p

                image = QPixmap(p).toImage()
                t = open(os.path.join(f[0], k.replace('.gif', '_pixmap')) + '.py', 'wb')

                t.write(import_str)

                t.write('width = {0}\n'.format(image.width()))
                t.write('height = {0}\n'.format(image.height()))
                t.write('format = {0}\n'.format(image.format()))

                bits = b64encode(image.bits().asstring(image.byteCount()))

                if len(bits) <= 67:
                    t.write('data = {0}\n'.format(bits))
                else:
                    t.write("data = '{0}' + \\\n".format(bits[:67]))
                    bits = bits[67:]
                    while len(bits) > 0:
                        if len(bits) > 74:
                            t.write("'{0}' + \\\n".format(bits[:74]))
                        else:
                            t.write("'{0}'\n".format(bits[:74]))
                        bits = bits[74:]

                t.write(get_image_str.format(k.replace('.gif', '_pixmap'), os.path.join(f[0], k).replace(file_url, '').replace('\\', '/')))
                t.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    convert_images()
