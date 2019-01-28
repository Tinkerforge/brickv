# -*- mode: python -*-

import os
import sys
sys.path.append('..')
from brickv.pyinstaller_utils import *

a = Analysis(['main.py'], pathex=[root_path], excludes=excludes, hiddenimports=hiddenimports)

pyz = PYZ(a.pure)

exe = EXE(pyz,
          a.scripts,
          a.binaries + binaries,
          a.zipfiles,
          a.datas + datas,
          [],
          name='brickv.exe' if windows else 'brickv',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=False,
          console=False,
          icon=icon)

if macos:
    app = BUNDLE(exe,
                    name='Brickv.app',
                    icon=icon)

post_generate()
