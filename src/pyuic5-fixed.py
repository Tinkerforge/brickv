#!/usr/bin/env python3

# The pyuic5 tool drops the contents margins of layout widgets, but some versions
# of pyuic5 have a bug that makes it identify normal widgets as layout widgets
# resulting in broken layouts. The brickv .ui files were created based on PyQt4.
# To avoid having to chase down all the places where the broken pyuic5 erroneously
# drops contents margins of normal widgets just monkey patch pyuic5 to pretend
# that there are no layout widgets at all to get back to the old pyuic4 behavior.

import PyQt5.uic.uiparser as uiparser

class FixedWidgetStack(uiparser.WidgetStack):
    def topIsLayoutWidget(self):
        return False

uiparser.WidgetStack = FixedWidgetStack

import PyQt5.uic.pyuic as pyuic

if __name__ == '__main__':
    pyuic.main()
