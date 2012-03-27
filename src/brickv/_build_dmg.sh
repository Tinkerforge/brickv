#!/bin/sh
rm Brickv.dmg
hdiutil create -fs HFS+ -volname Brickv -srcfolder dist Brickv.dmg

