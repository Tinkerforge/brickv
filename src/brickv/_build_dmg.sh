#!/bin/sh
dot_version=`grep BRICKV_VERSION config_common.py | sed -e 's/BRICKV_VERSION = "\(.*\)"/\1/'`
underscore_version=`printf %s $dot_version | sed -e 's/\./_/g'`
dmg=brickv_macos_$underscore_version.dmg
rm $dmg
hdiutil create -fs HFS+ -volname "Brickv-$dot_version" -srcfolder dist $dmg
