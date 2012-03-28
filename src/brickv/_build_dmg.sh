#!/bin/sh
rm Brickv.dmg
rm -rf dist/Brickv.app/Contents/Resources/lib/python2.6/matplotlib/tests
hdiutil create -fs HFS+ -volname Brickv -srcfolder dist Brickv.dmg

