# -*- coding: utf-8 -*-
#
# Copyright (C) 2011 Loic Jaquemet loic.jaquemet+python@gmail.com
#


# Taken from Haystack project (GPL): http://pydoc.net/Python/haystack/0.15/
# Copyright (C) 2015 Olaf Lüke <olaf@tinkerforge.com>
#
# Changes for Brick Viewer:
#
# * Make qhexedit file compatible to newer Qt versions:
#  * Replace QString with str
#  * Replace s.length() with len(s)
# * Replace QTextStream by str
# * Remove unused parts
# * Small bugfixes
#  * Add missing self.'s
#  * Fix typos in variable names
# * Fix indentation errors
# * Allow font to be set through constructor
# * Remove unnecessary menu options
# * Consider \n, \r and \t to be not printable in hex view
# * Fix bug with every second highlight getting grey
# * Use writeData on QBuffer directly instead of using QByteArray
# * Remove QBuffer and QIODevice and replace it by str
# * Remove Font picker

import string

from PyQt5.Qt import Qt
from PyQt5.QtGui import QFontMetrics, QClipboard, QPen, QPainter
from PyQt5.QtWidgets import QMenu, QApplication, QAbstractScrollArea, QAction

#where is QtGlobal ?
def qBound(mini, value, maxi):
    return max(mini, min(value, maxi))

class QHexeditWidget(QAbstractScrollArea):
    highlightingNone = 0
    highlightingData = 1
    highlightingAscii = 2

    def __init__(self, font, parent=None):
        super().__init__(parent)
        self.data = ""
        self.row_width = 16
        self.word_width = 1
        self.address_color = Qt.blue
        self.show_hex = True
        self.show_ascii = True
        self.show_address = True
        self.origin = 0
        self.address_offset = 0
        self.selection_start = -1
        self.selection_end = -1
        self.highlighting = self.highlightingNone
        self.even_word = Qt.blue
        self.non_printable_text = Qt.red
        self.unprintable_char = '.'
        self.show_line1 = True
        self.show_line2 = True
        self.show_line3 = False
        self.show_address_separator = True
        self.setFont(font)
        self.setShowAddressSeparator(True)
        return

    def setShowAddressSeparator(self, value):
        self.show_address_separator = value
        self.updateScrollbars()
        return

    def formatAddress(self, address):
        return self.format_address(address, self.show_address_separator)

    def format_address(self, address, showSep=False):
        if showSep:
            sep = ':'
        else:
            sep = ''

        return str("%04x%s%04x" % (address, sep, address + 0x10))

    def is_printable(self, ch):
        return (ch in string.printable) and (not ch in ('\n', '\r', '\t', '\x0b', '\x0c'))

    '''
    Name: add_toggle_action_to_menu(QMenu *menu, const str &caption, bool checked, QObject *receiver, const char *slot)
    Desc: convenience function used to add a checkable menu item to the context menu
    '''
    def add_toggle_action_to_menu(self, menu, caption, checked, call):
        action = QAction(caption, menu)
        action.setCheckable(True)
        action.setChecked(checked)
        menu.addAction(action)
        action.toggled.connect(call)
        return action


    def repaint(self):
        self.viewport().repaint()
        return

    '''
    Name: dataSize() const
    Desc: returns how much data we are viewing
    '''
    def dataSize(self):
        return len(self.data)

    '''
    Name: setFont(const QFont &f)
    Desc: overloaded version of setFont, calculates font metrics for later
    '''
    def setFont(self, f):
        # recalculate all of our metrics/offsets
        fm = QFontMetrics(f)
        self.font_width = fm.width('X')
        self.font_height = fm.height()
        self.updateScrollbars()
        # TODO: assert that we are using a fixed font & find out if we care?
        QAbstractScrollArea.setFont(self, f)
        return

    '''
    Name: createStandardContextMenu()
    Desc: creates the 'standard' context menu for the widget
    '''
    def createStandardContextMenu(self):
        menu = QMenu(self)

        self.add_toggle_action_to_menu(menu, str("Show A&ddress"), self.show_address, self.setShowAddress)
        self.add_toggle_action_to_menu(menu, str("Show &Hex"), self.show_hex, self.setShowHexDump)
        self.add_toggle_action_to_menu(menu, str("Show &ASCII"), self.show_ascii, self.setShowAsciiDump)

        menu.addSeparator()
        menu.addAction(str("&Copy Selection To Clipboard"), self.mnuCopy)
        return menu

    '''
    Name: contextMenuEvent(QContextMenuEvent *event)
    Desc: default context menu event, simply shows standard menu
    '''
    def contextMenuEvent(self, event):
        menu = self.createStandardContextMenu()
        menu.exec_(event.globalPos())
        del menu
        return


    '''
    Name: mnuCopy()
    Desc:
    '''
    def mnuCopy(self):
        if not self.hasSelectedText():
            return

        ss = ""
        # current actual offset (in bytes)
        chars_per_row = self.bytesPerRow()
        offset = self.verticalScrollBar().value() * chars_per_row

        if self.origin != 0:
            if offset > 0:
                offset += self.origin
                offset -= self.chars_per_row

        end = max(self.selection_start, self.selection_end)
        start = min(self.selection_start, self.selection_end)
        data_size = self.dataSize()

        # offset now refers to the first visible byte
        while offset < end:
            if (offset + chars_per_row) > start:
                row_data = self.data[offset:chars_per_row + offset]

                if row_data is not None:
                    if self.show_address:
                        address_rva = self.address_offset + offset
                        addressBuffer = self.formatAddress(address_rva)

                        ss += str(addressBuffer)
                        ss += '|'
                    if self.show_hex:
                        ss = self.drawHexDumpToBuffer(ss, offset, data_size, row_data)
                        ss += "|"
                    if self.show_ascii:
                        ss = self.drawAsciiDumpToBuffer(ss, offset, data_size, row_data)
                        ss += "|"
                ss += "\n"
            offset += chars_per_row
        QApplication.clipboard().setText(ss)
        QApplication.clipboard().setText(ss, QClipboard.Selection)
        return

    '''
    Name: clear()
    Desc: clears all data from the view
    '''
    def clear(self):
        self.data = ""
        self.repaint()
        return

    '''
    Name: hasSelectedText() const
    Desc: returns true if any text is selected
    '''
    def hasSelectedText(self):
        return not (self.selection_start == -1 or self.selection_end == -1)

    '''
    Name: isInViewableArea(int index) const
    Desc: returns true if the word at the given index is in the viewable area
    '''
    def isInViewableArea(self, index):
        firstViewableWord = self.verticalScrollBar().value() * self.row_width
        viewableLines = self.viewport().height() // self.font_height
        viewableWords = viewableLines * self.row_width
        lastViewableWord = firstViewableWord + viewableWords
        return index >= firstViewableWord and index < lastViewableWord

    '''
    Name: keyPressEvent(QKeyEvent *event)
    Desc:
    '''
    def keyPressEvent(self, event):
        if event.modifiers() & Qt.ControlModifier:
            key = event.key()
            if key == Qt.Key_A:
                self.selectAll()
                self.repaint()
            elif key == Qt.Key_Home:
                self.scrollTo(0)
            elif key == Qt.Key_End:
                self.scrollTo(self.dataSize() - self.bytesPerRow())
            elif key == Qt.Key_Down:
                while True:
                    offset = self.verticalScrollBar().value() * self.bytesPerRow()
                    if self.origin != 0:
                        if offset > 0:
                            offset += self.origin
                            offset -= self.bytesPerRow()
                    if offset + 1 < self.dataSize():
                        self.scrollTo(offset + 1)
                    #return so we don't pass on the key event
                    return
            elif key == Qt.Key_Up:
                while True:
                    offset = self.verticalScrollBar().value() * self.bytesPerRow()
                    if self.origin != 0:
                        if offset > 0:
                            offset += self.origin
                            offset -= self.bytesPerRow()
                    if offset > 0:
                        self.scrollTo(offset - 1)
                    #return so we don't pass on the key event
                    return
        QAbstractScrollArea.keyPressEvent(self, event)
        return

    '''
    Name: line3() const
    Desc: returns the x coordinate of the 3rd line
    '''
    def line3(self):
        if self.show_ascii:
            elements = self.bytesPerRow()
            return self.asciiDumpLeft() + (elements * self.font_width) + (self.font_width // 2)
        else:
            return self.line2()

    '''
    Name: line2() const
    Desc: returns the x coordinate of the 2nd line
    '''
    def line2(self):
        if self.show_hex:
            elements = self.row_width * (self.charsPerWord() + 1) - 1
            return self.hexDumpLeft() + (elements * self.font_width) + (self.font_width // 2)
        else:
            return self.line1()


    '''
    Name: line1() const
    Desc: returns the x coordinate of the 1st line
    '''
    def line1(self):
        if self.show_address:
            return self.addressLen() * self.font_width + 3 * self.font_width // 4
        else:
            return 0


    '''
    Name: hexDumpLeft() const
    Desc: returns the x coordinate of the hex-dump field left edge
    '''
    def hexDumpLeft(self):
        return self.line1() + (self.font_width // 2)

    '''
    Name: asciiDumpLeft() const
    Desc: returns the x coordinate of the ascii-dump field left edge
    '''
    def asciiDumpLeft(self):
        return self.line2() + (self.font_width // 2)

    '''
    Name: charsPerWord() const
    Desc: returns how many characters each word takes up
    '''
    def charsPerWord(self):
        return self.word_width * 2

    '''
    Name: addressLen() const
    Desc: returns the lenth in characters the address will take up
    '''
    def addressLen(self):
        addressLength = 8
        if self.show_address_separator:
            return addressLength + 1
        return addressLength + 0


    '''
    Name: updateScrollbars()
    Desc: recalculates scrollbar maximum value base on lines total and lines viewable
    '''
    def updateScrollbars(self):
        sz = self.dataSize()
        bpr = self.bytesPerRow()
        if sz % bpr:
            horn = 1
        else:
            horn = 0
        self.verticalScrollBar().setMaximum(max(0, sz // bpr + horn - self.viewport().height() // self.font_height))
        self.horizontalScrollBar().setMaximum(max(0, (self.line3() - self.viewport().width()) // self.font_width))
        return


    '''
    Name: scrollTo( offset)
    Desc: scrolls view to given byte offset
    '''
    def scrollTo(self, offset):
        bpr = self.bytesPerRow()
        self.origin = offset % bpr
        address = offset // bpr

        self.updateScrollbars()

        if self.origin != 0:
            address += 1

        self.verticalScrollBar().setValue(address)
        self.repaint()
        return

    def setSelected(self, start, length):
        self.selection_start = start
        self.selection_end = self.selection_start + length
        self.repaint()


    '''
    Name: setShowAddress(bool show)
    Desc: sets if we are to display the address column
    '''
    def setShowAddress(self, show):
        self.show_address = show
        self.updateScrollbars()
        self.repaint()
        return

    '''
    Name: setShowHexDump(bool show)
    Desc: sets if we are to display the hex-dump column
    '''
    def setShowHexDump(self, show):
        self.show_hex = show
        self.updateScrollbars()
        self.repaint()
        return

    '''
    Name: setShowAsciiDump(bool show)
    Desc: sets if we are to display the ascii-dump column
    '''
    def setShowAsciiDump(self, show):
        self.show_ascii = show
        self.updateScrollbars()
        self.repaint()
        return

    '''
    Name: setRowWidth(int rowWidth)
    Desc: sets the row width (units is words)
    '''
    def setRowWidth(self, rowWidth):
        self.row_width = rowWidth
        self.updateScrollbars()
        self.repaint()
        return

    '''
    Name: setWordWidth(int wordWidth)
    Desc: sets how many bytes represent a word
    '''
    def setWordWidth(self, wordWidth):
        self.word_width = wordWidth
        self.updateScrollbars()
        self.repaint()
        return

    '''
    Name: bytesPerRow() const
    '''
    def bytesPerRow(self):
        return self.row_width * self.word_width


    '''
    Name: pixelToWord(int x, int y) const
    '''
    def pixelToWord(self, x, y):

        if self.highlighting == self.highlightingData:
            # the right edge of a box is kinda quirky, so we pretend there is one
            # extra character there
            x = qBound(self.line1(), x, self.line2() + self.font_width)

            # the selection is in the data view portion
            x -= self.line1()

            # scale x/y down to character from pixels
            if x % self.font_width >= self.font_width // 2:
                x = x // self.font_width + 1
            else:
                x = x // self.font_width
            y //= self.font_height

            # make x relative to rendering mode of the bytes
            x //= (self.charsPerWord() + 1)
        elif self.highlighting == self.highlightingAscii:
            x = qBound(self.asciiDumpLeft(), x, self.line3())

            # the selection is in the ascii view portion
            x -= self.asciiDumpLeft()

            # scale x/y down to character from pixels
            x //= self.font_width
            y //= self.font_height

            # make x relative to rendering mode of the bytes
            x //= self.word_width
        else:
            pass

        # starting offset in bytes
        start_offset = self.verticalScrollBar().value() * self.bytesPerRow()

        # take into account the origin
        if self.origin != 0:
            if start_offset > 0:
                start_offset += self.origin
                start_offset -= self.bytesPerRow()

        # convert byte offset to word offset, rounding up
        start_offset //= self.word_width

        if (self.origin % self.word_width) != 0:
            start_offset += 1

        word = ((y * self.row_width) + x) + start_offset

        return word


    '''
    Name: mouseDoubleClickEvent(QMouseEvent *event)
    '''
    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            x = event.x() + self.horizontalScrollBar().value() * self.font_width
            y = event.y()
            if x >= self.line1() and x < self.line2():
                self.highlighting = self.highlightingData
                offset = self.pixelToWord(x, y)
                byte_offset = offset * self.word_width
                if self.origin:
                    if self.origin % self.word_width:
                        byte_offset -= self.word_width - (self.origin % self.word_width)
                self.selection_start = byte_offset
                self.selection_end = self.selection_start + self.word_width
                self.repaint()
        return


    '''
    Name: mousePressEvent(QMouseEvent *event)
    '''
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            x = event.x() + self.horizontalScrollBar().value() * self.font_width
            y = event.y()

            if x < self.line2():
                self.highlighting = self.highlightingData
            elif x >= self.line2():
                self.highlighting = self.highlightingAscii

            offset = self.pixelToWord(x, y)
            byte_offset = offset * self.word_width
            if self.origin:
                if self.origin % self.word_width:
                    byte_offset -= self.word_width - (self.origin % self.word_width)
            if offset < self.dataSize():
                self.selection_start = self.selection_end = byte_offset
            else:
                self.selection_start = self.selection_end = -1
            self.repaint()
        return

    '''
    Name: mouseMoveEvent(QMouseEvent *event)
    '''
    def mouseMoveEvent(self, event):
        if self.highlighting != self.highlightingNone:
            x = event.x() + self.horizontalScrollBar().value() * self.font_width
            y = event.y()

            offset = self.pixelToWord(x, y)

            if self.selection_start != -1:
                if offset == -1:
                    self.selection_end = (self.row_width - self.selection_start) + self.selection_start
                else:
                    byte_offset = (offset * self.word_width)
                    if self.origin:
                        if self.origin % self.word_width:
                            byte_offset -= self.word_width - (self.origin % self.word_width)
                    self.selection_end = byte_offset
                if self.selection_end < 0:
                    self.selection_end = 0
                if not self.isInViewableArea(self.selection_end):
                    # TODO: scroll to an appropriate location
                    pass
            self.repaint()
        return

    '''
    Name: mouseReleaseEvent(QMouseEvent *event)
    '''
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.highlighting = self.highlightingNone
        return

    def appendData(self, data):
        self.data += data
        self.deselect()
        self.updateScrollbars()
        slider = self.verticalScrollBar()
        slider.setSliderPosition(slider.maximum())
        self.repaint()

    '''
    Name: resizeEvent(QResizeEvent *)
    '''
    def resizeEvent(self, _event):
        self.updateScrollbars()
        return

    '''
    Name: setAddressOffset(address_t offset)
    '''
    def setAddressOffset(self, offset):
        self.address_offset = offset
        return

    '''
    Name: isSelected(int index) const
    '''
    def isSelected(self, index):
        ret = False
        if index < self.dataSize():
            if self.selection_start != self.selection_end:
                if self.selection_start < self.selection_end:
                    ret = (self.selection_start <= index < self.selection_end)
                else:
                    ret = (self.selection_end <= index < self.selection_start)
        return ret

    '''
    Name: drawAsciiDumpToBuffer(QTextStream &stream, offset, int size, const QByteArray &row_data) const
    '''
    def drawAsciiDumpToBuffer(self, stream, offset, size, row_data):
        # i is the byte index
        chars_per_row = self.bytesPerRow()
        for i in range(0, chars_per_row):
            index = offset + i
            if index < size:
                if self.isSelected(index):
                    ch = row_data[i]
                    if self.is_printable(ch):
                        stream += str(ch)
                    else:
                        stream += str(self.unprintable_char)
                else:
                    stream += ' '

            else:
                break
        return stream

    '''
    Name: format_bytes(const C &data_ref, int index) const
    Desc: formats bytes in a way that's suitable for rendering in a hexdump
                having self as a separate function serves two purposes.
                #1 no code duplication between the buffer and QPainter versions
                #2 self encourages NRVO of the return value more than an integrated
    '''
    def format_bytes(self, row_data, index):
        #union:
        #    quint64 q
        #    quint32 d
        #    quint16 w
        #    quint8    b
        value = 0
        byte_buffer = [0]*32
        if self.word_width == 1:
            value |= (ord(row_data[index + 0]) & 0xff)
            byte_buffer = "%02x" % value
        elif self.word_width == 2:
            value |= (ord(row_data[index + 0]) & 0xff)
            value |= (ord(row_data[index + 1]) & 0xff) << 8
            byte_buffer = "%04x" % value
        elif self.word_width == 4:
            value |= (ord(row_data[index + 0]) & 0xff)
            value |= (ord(row_data[index + 1]) & 0xff) << 8
            value |= (ord(row_data[index + 2]) & 0xff) << 16
            value |= (ord(row_data[index + 3]) & 0xff) << 24
            byte_buffer = "%08x" % value
        elif self.word_width == 8:
            # we need the cast to ensure that it won't assume 32-bit
            # and drop bits shifted more that 31
            value |= (ord(row_data[index + 0]) & 0xff)
            value |= (ord(row_data[index + 1]) & 0xff) << 8
            value |= (ord(row_data[index + 2]) & 0xff) << 16
            value |= (ord(row_data[index + 3]) & 0xff) << 24
            value |= (ord(row_data[index + 4]) & 0xff) << 32
            value |= (ord(row_data[index + 5]) & 0xff) << 40
            value |= (ord(row_data[index + 6]) & 0xff) << 48
            value |= (ord(row_data[index + 7]) & 0xff) << 56
            byte_buffer = "%016x" % value
        return byte_buffer

    '''
    Name: drawHexDumpToBuffer(QTextStream &stream,    offset, int size, const QByteArray &row_data) const
    '''
    def drawHexDumpToBuffer(self, stream, offset, size, row_data):
        # i is the word we are currently rendering
        for i in range(0, self.row_width):
            # index of first byte of current 'word'
            index = offset + (i * self.word_width)
            # equal <=, not < because we want to test the END of the word we
            # about to render, not the start, it's allowed to end at the very last
            # byte
            if index + self.word_width <= size:
                byteBuffer = str(self.format_bytes(row_data, i * self.word_width))
                if self.isSelected(index):
                    stream += byteBuffer
                else:
                    stream += ' ' * len(byteBuffer)
                if i != (self.row_width - 1):
                    stream += ' '
            else:
                break

        return stream

    '''
    Name: drawHexDump(QPainter &painter, offset, row, int size, int &word_count, const QByteArray &row_data) const
    '''
    def drawHexDump(self, painter, offset, row, size, word_count, row_data):
        hex_dump_left = self.hexDumpLeft()
        # i is the word we are currently rendering
        for i in range(0, self.row_width):
            # index of first byte of current 'word'
            index = offset + (i * self.word_width)
            # equal <=, not < because we want to test the END of the word we
            # about to render, not the start, it's allowed to end at the very last
            # byte
            if index + self.word_width <= size:
                byteBuffer = str(self.format_bytes(row_data, i * self.word_width))
                drawLeft = hex_dump_left + (i * (self.charsPerWord() + 1) * self.font_width)
                if self.isSelected(index):
                    painter.fillRect(
                        drawLeft,
                        row,
                        self.charsPerWord() * self.font_width,
                        self.font_height,
                        self.palette().highlight()
                    )

                    # should be highlight the space between us and the next word?
                    if i != (self.row_width - 1):
                        if self.isSelected(index + 1):
                            painter.fillRect(
                                drawLeft + self.font_width,
                                row,
                                self.charsPerWord() * self.font_width,
                                self.font_height,
                                self.palette().highlight()
                                )
                    painter.setPen(QPen(self.palette().highlightedText().color()))
                else:
                    painter.setPen(QPen(self.even_word))
                    painter.setPen(QPen(self.palette().text().color()))

                painter.drawText(
                    drawLeft,
                    row,
                    len(byteBuffer) * self.font_width,
                    self.font_height,
                    Qt.AlignTop,
                    byteBuffer
                    )

                word_count += 1
            else:
                break
        return

    '''
    Name: drawAsciiDump(QPainter &painter, offset, row, int size, const QByteArray &row_data) const
    '''
    def drawAsciiDump(self, painter, offset, row, size, row_data):
        ascii_dump_left = self.asciiDumpLeft()

        # i is the byte index
        chars_per_row = self.bytesPerRow()
        for i in range(0, chars_per_row):
            index = offset + i
            if index < size:
                ch = row_data[i]
                drawLeft = ascii_dump_left + i * self.font_width
                printable = self.is_printable(ch)
                # drawing a selected character
                if self.isSelected(index):
                    painter.fillRect(
                        drawLeft,
                        row,
                        self.font_width,
                        self.font_height,
                        self.palette().highlight()
                        )
                    painter.setPen(QPen(self.palette().highlightedText().color()))
                else:
                    if printable:
                        painter.setPen(QPen(self.palette().text().color()))
                    else:
                        painter.setPen(QPen(self.non_printable_text))
                if printable:
                    byteBuffer = str(ch)
                else:
                    byteBuffer = str(self.unprintable_char)
                painter.drawText(
                    drawLeft,
                    row,
                    self.font_width,
                    self.font_height,
                    Qt.AlignTop,
                    byteBuffer
                    )
            else:
                break
        return

    '''
    Name: paintEvent(QPaintEvent *)
    '''
    def paintEvent(self, event):
        painter = QPainter(self.viewport())
        painter.translate(-self.horizontalScrollBar().value() * self.font_width, 0)
        word_count = 0

        # pixel offset of self row
        row = 0
        chars_per_row = self.bytesPerRow()
        # current actual offset (in bytes)
        offset = self.verticalScrollBar().value() * chars_per_row

        if self.origin != 0:
            if offset > 0:
                offset += self.origin
                offset -= chars_per_row
            else:
                self.origin = 0
                self.updateScrollbars()

        data_size = self.dataSize()
        widget_height = self.height()

        while (row + self.font_height < widget_height) and (offset < data_size):
            row_data = self.data[offset:chars_per_row+offset]
            if row_data is not None: # != '' ?
                if self.show_address:
                    address_rva = self.address_offset + offset
                    addressBuffer = self.formatAddress(address_rva)
                    painter.setPen(QPen(self.address_color))
                    painter.drawText(0, row, len(addressBuffer) * (self.font_width+1), self.font_height, Qt.AlignTop, addressBuffer)

                painter.setPen(QPen(Qt.black))
                if self.show_hex:
                    self.drawHexDump(painter, offset, row, data_size, word_count, row_data)
                if self.show_ascii:
                    self.drawAsciiDump(painter, offset, row, data_size, row_data)
            offset += chars_per_row
            row += self.font_height

        painter.setPen(QPen(self.palette().shadow().color()))

        if self.show_address and self.show_line1:
            line1_x = self.line1()
            painter.drawLine(int(line1_x), 0, int(line1_x), widget_height)

        if self.show_hex and self.show_line2:
            line2_x = self.line2()
            painter.drawLine(int(line2_x), 0, int(line2_x), widget_height)

        if self.show_ascii and self.show_line3:
            line3_x = self.line3()
            painter.drawLine(int(line3_x), 0, int(line3_x), widget_height)

        return

    '''
    Name: selectAll()
    '''
    def selectAll(self):
        self.selection_start = 0
        self.selection_end = self.dataSize()
        return

    '''
    Name: deselect()
    '''
    def deselect(self):
        self.selection_start = -1
        self.selection_end = -1
        return

    '''
    Name: allBytes() const
    '''
    def allBytes(self):
        return self.data

    '''
    Name: selectedBytes() const
    '''
    def selectedBytes(self):
        if self.hasSelectedText():
            s = min(self.selection_start, self.selection_end)
            e = max(self.selection_start, self.selection_end)
            self.data.seek(s)
            return self.data[s:e]
        return []

    '''
    Name: selectedBytesAddress() const
    '''
    def selectedBytesAddress(self):
        select_base = min(self.selection_start, self.selection_end)
        return select_base + self.address_offset

    '''
    Name: selectedBytesSize() const
    '''
    def selectedBytesSize(self):
        if self.selection_end > self.selection_start:
            ret = self.selection_end - self.selection_start
        else:
            ret = self.selection_start - self.selection_end
        return ret

    '''
    Name: addressOffset() const
    '''
    def addressOffset(self):
        return self.address_offset

    '''
    Name: showHexDump() const
    '''
    def showHexDump(self):
        return self.show_hex

    '''
    Name: showAddress() const
    '''
    def showAddress(self):
        return self.show_address

    '''
    Name: showAsciiDump() const
    '''
    def showAsciiDump(self):
        return self.show_ascii

    '''
    Name: showComments() const
    '''
    def mshowComments(self):
        return self.show_comments

    '''
    Name: wordWidth() const
    '''
    def wordWidth(self):
        return self.word_width

    '''
    Name: rowWidth() const
    '''
    def rowWidth(self):
        return self.row_width

    '''wf
    Name: firstVisibleAddress() const
    '''
    def firstVisibleAddress(self):
        # current actual offset (in bytes)
        chars_per_row = self.bytesPerRow()
        offset = self.verticalScrollBar().value() * chars_per_row
        if self.origin != 0:
            if offset > 0:
                offset += self.origin
                offset -= chars_per_row
        return offset + self.addressOffset()
