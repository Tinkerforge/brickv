# -*- mode: python -*-

import os
import sys
sys.path.append('..')
from brickv.pyinstaller_utils import *

a = Analysis(['main.py'],pathex=pathex, excludes=excludes, hiddenimports=hiddenimports)

pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='brickv.exe' if windows else 'brickv',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=False,
          console=False,
          icon=icon)

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas + datas,
               strip=False,
               upx=False,
               name='')
if macos:
    app = BUNDLE(coll,
                    name='Brickv.app',
                    icon=icon)

post_generate()
