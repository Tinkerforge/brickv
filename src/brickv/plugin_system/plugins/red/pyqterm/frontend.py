# -*- coding: utf-8 -*-
import time

import sys

from PyQt5.QtCore import QRect, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QClipboard, QPainter, QFont, QBrush, QColor, QPen, QPixmap, QContextMenuEvent
from PyQt5.QtWidgets import QApplication, QWidget

from .backend import SerialSession

DEBUG = False

class TerminalWidget(QWidget):

    foreground_color_map = {
        0: "#000",
        1: "#b00",
        2: "#0b0",
        3: "#bb0",
        4: "#66F",
        5: "#b0b",
        6: "#0bb",
        7: "#bbb",
        8: "#666",
        9: "#f00",
        10: "#0f0",
        11: "#ff0",
        12: "#00f",  # concelaed
        13: "#f0f",
        14: "#000",  # negative
        15: "#fff",  # default
    }
    background_color_map = {
        0: "#000",
        1: "#b00",
        2: "#0b0",
        3: "#bb0",
        4: "#00b",
        5: "#b0b",
        6: "#0bb",
        7: "#bbb",
        12: "#aaa",  # cursor
        14: "#000",  # default
        15: "#fff",  # negative
    }
    keymap = {
        Qt.Key_Backspace: chr(127),
        Qt.Key_Escape: chr(27),
        Qt.Key_AsciiTilde: "~~",
        Qt.Key_Up: "~A",
        Qt.Key_Down: "~B",
        Qt.Key_Left: "~D",
        Qt.Key_Right: "~C",
        Qt.Key_PageUp: "~1",
        Qt.Key_PageDown: "~2",
        Qt.Key_Home: "~H",
        Qt.Key_End: "~F",
        Qt.Key_Insert: "~3",
        Qt.Key_Delete: "~4",
        Qt.Key_F1: "~a",
        Qt.Key_F2: "~b",
        Qt.Key_F3:  "~c",
        Qt.Key_F4:  "~d",
        Qt.Key_F5:  "~e",
        Qt.Key_F6:  "~f",
        Qt.Key_F7:  "~g",
        Qt.Key_F8:  "~h",
        Qt.Key_F9:  "~i",
        Qt.Key_F10:  "~j",
        Qt.Key_F11:  "~k",
        Qt.Key_F12:  "~l",
    }

    session_closed = pyqtSignal()

    def __init__(self, parent=None, command="/bin/bash",font_size=14):
        super(TerminalWidget, self).__init__(parent)
        self._columns = 80
        self._rows = 24
        self._char_width = [0]*(self._columns+1)
        self._char_height = [0]*(self._rows+1)

        self.setFocusPolicy(Qt.StrongFocus)
        self.setAutoFillBackground(False)
        self.setAttribute(Qt.WA_OpaquePaintEvent, True)
        self.setCursor(Qt.IBeamCursor)
        font_name = "Monospace"
        if sys.platform == 'darwin':
            font_name = "Courier"
        font = QFont(font_name)
        font.setStyleHint(QFont.TypeWriter)
        font.setPixelSize(font_size)
        self.setFont(font)
        self._session = None
        self._last_update = 0
        self._screen = []
        self._text = []
        self._cursor_rect = None
        self._cursor_col = 0
        self._cursor_row = 0
        self._dirty = False
        self._blink = False
        self._press_pos = None
        self._selection = None
        self._clipboard = QApplication.clipboard()
        self._pixmap = None

    def execute(self, command):
        self._update_metrics()
        self._session = SerialSession(command, self)
        self._session.start()
        self._timer_id = None
        # start timer either with high or low priority
        if self.hasFocus():
            self.focusInEvent(None)
        else:
            self.focusOutEvent(None)

    def send(self, s):
        self._session.write(s)

    def stop(self):
        self._session.close()

    def setFont(self, font):
        super(TerminalWidget, self).setFont(font)
        self._update_metrics()

    def closeEvent(self, event):
        if self._session == None:
            return
        self._session.close()

    def focusNextPrevChild(self, next):
        if self._session == None:
            return True
        return False

    def timerEvent(self, event):
        if self.hasFocus():
            self._blink = not self._blink
        self.update_screen()

    def _update_metrics(self):
        fm = self.fontMetrics()

        for i in range(self._columns+1):
            self._char_width[i] = fm.width(' '*i)
        for i in range(self._rows+1):
            self._char_height[i] = fm.height()*(i+1)

    def _update_cursor_rect(self):
        cx, cy = self._pos2pixel(self._cursor_col, self._cursor_row)
        self._cursor_rect = QRect(cx, cy, self._char_width[1], self._char_height[0])

    def _reset(self):
        self.setMinimumHeight(self._char_height[self._rows-1])
        self.setMaximumHeight(self._char_height[self._rows-1])
        self.setMinimumWidth(self._char_width[self._columns])
        self.setMaximumWidth(self._char_width[self._columns])

        if self._session == None:
            self._dirty = True
            self.repaint()
            return

        self._dirty = True
        self._update_metrics()
        self._update_cursor_rect()
        self.resizeEvent(None)
        self.repaint()
        self.update_screen()
        self.repaint()

    @pyqtSlot()
    def update_screen(self):
        if self._session == None:
            return

        # max 25 fps
        new_update = time.time()
        if (new_update - self._last_update) < 0.040:
            return

        self._last_update = new_update

        old_screen = self._screen
        (self._cursor_col, self._cursor_row), self._screen = self._session.dump()
        self._update_cursor_rect()
        if old_screen != self._screen:
            self._dirty = True

        self.repaint()

    def paintEvent(self, event):
        # the original code tried to be clever about painting an caching. it
        # only painted the screen if it was dirty. for the redraws when the
        # dirty flag was not set it relyed on the OS not the clear the cash.
        # but this does not work (at least on macOS). instead of caching in
        # the OS cache the screen in a pixmap to have full control over it
        if self._pixmap == None or self.size() != self._pixmap.size():
            self._pixmap = QPixmap(self.size())
            self._dirty = True

        if self._dirty:
            self._dirty = False

            pixmap_painter = QPainter(self._pixmap)
            pixmap_painter.setFont(self.font())

            self._paint_screen(pixmap_painter)

        painter = QPainter(self)
        painter.drawPixmap(0, 0, self._pixmap)

        # We don't use the blinky cursor for now
#        if self._cursor_rect is not None and self._selection is None:
#            self._paint_cursor(painter)
        if self._selection:
            self._paint_selection(painter)
            self._dirty = True

    def _pixel2pos(self, x, y):
        col = int(round(x / (self._char_width[self._columns]/float(self._columns))))
        row = int(round(y / (self._char_height[self._rows]/float(self._rows))))
        return col, row

    def _pos2pixel(self, col, row):
        x = self._char_width[col]
        if row == 0:
            y = 0
        else:
            y = self._char_height[row-1]
        return x, y

    def _paint_cursor(self, painter):
        if self._blink:
            color = "#aaa"
        else:
            color = "#fff"
        painter.setPen(QPen(QColor(color)))
        painter.drawRect(self._cursor_rect)
        self._cursor_rect = None

    def _paint_screen(self, painter):
        # Speed hacks: local name lookups are faster
        vars().update(QColor=QColor, QBrush=QBrush, QPen=QPen, QRect=QRect)
        background_color_map = self.background_color_map
        foreground_color_map = self.foreground_color_map
        painter_drawText = painter.drawText
        painter_fillRect = painter.fillRect
        painter_setPen = painter.setPen
        align = Qt.AlignTop | Qt.AlignLeft
        # set defaults
        background_color = background_color_map[14]
        foreground_color = foreground_color_map[15]
        brush = QBrush(QColor(background_color))
        painter_fillRect(self.rect(), brush)
        pen = QPen(QColor(foreground_color))
        painter_setPen(pen)
        y = 0
        text = []
        text_append = text.append
        for row, line in enumerate(self._screen):
            col = 0
            text_line = ""
            for item in line:
                if isinstance(item, str):
                    x = self._char_width[col]
                    length = len(item)
                    rect = QRect(
                        x, y, x + self._char_width[length], y + self._char_height[0])
                    painter_fillRect(rect, brush)
                    painter_drawText(rect, align, item)
                    col += length
                    text_line += item
                else:
                    foreground_color_idx, background_color_idx, underline_flag = item
                    foreground_color = foreground_color_map[
                        foreground_color_idx]
                    background_color = background_color_map[
                        background_color_idx]
                    pen = QPen(QColor(foreground_color))
                    brush = QBrush(QColor(background_color))
                    painter_setPen(pen)
            y += self._char_height[0]
            text_append(text_line)
        self._text = text

    def _paint_selection(self, painter):
        pcol = QColor(200, 200, 200, 50)
        pen = QPen(pcol)
        bcol = QColor(230, 230, 230, 50)
        brush = QBrush(bcol)
        painter.setPen(pen)
        painter.setBrush(brush)
        if self._selection != None:
            for (start_col, start_row, end_col, end_row) in self._selection:
                x, y = self._pos2pixel(start_col, start_row)
                width, height = self._pos2pixel(
                    end_col - start_col, end_row - start_row)
                rect = QRect(x, y, width, height)
                painter.fillRect(rect, brush)

    def zoom_in(self):
        font = self.font()
        font.setPixelSize(font.pixelSize() + 2)
        self.setFont(font)
        self._reset()

    def zoom_out(self):
        font = self.font()
        font.setPixelSize(font.pixelSize() - 2)
        self.setFont(font)
        self._reset()

    return_pressed = pyqtSignal()

    def keyPressEvent(self, event):
        if self._session == None:
            return

        text = event.text()
        key = event.key()
        modifiers = event.modifiers()
        ctrl = modifiers == Qt.ControlModifier
        if ctrl and key == Qt.Key_Plus:
            self.zoom_in()
        elif ctrl and key == Qt.Key_Minus:
                self.zoom_out()
        else:
            if text and key != Qt.Key_Backspace:
                self.send(text)
            else:
                s = self.keymap.get(key)
                if s:
                    self.send(s.encode("utf-8"))
                elif DEBUG:
                    print("Unknown key combination")
                    print("Modifiers: " + str(modifiers))
                    print("Key: " + str(key))
                    for name in dir(Qt):
                        if not name.startswith("Key_"):
                            continue
                        value = getattr(Qt, name)
                        if value == key:
                            print("Symbol: Qt.%s" % name)
                    print("Text: %r" % text)
        event.accept()
        if key in (Qt.Key_Enter, Qt.Key_Return):
            self.return_pressed.emit()

    def mousePressEvent(self, event):
        if self._session == None:
            return

        button = event.button()
        if button == Qt.RightButton:
            ctx_event = QContextMenuEvent(QContextMenuEvent.Mouse, event.pos())
            self.contextMenuEvent(ctx_event)
            self._press_pos = None
        elif button == Qt.LeftButton:
            self._press_pos = event.pos()
            self._selection = None
            self.update_screen()
        elif button == Qt.MiddleButton:
            self._press_pos = None
            self._selection = None
            text = self._clipboard.text(QClipboard.Selection)
            self.send(text.encode("utf-8"))

    def mouseReleaseEvent(self, QMouseEvent):
        pass

    def _selection_rects(self, start_pos, end_pos):
        sx, sy = start_pos.x(), start_pos.y()
        start_col, start_row = self._pixel2pos(sx, sy)
        ex, ey = end_pos.x(), end_pos.y()
        end_col, end_row = self._pixel2pos(ex, ey)
        if start_row == end_row:
            if ey > sy or end_row == 0:
                end_row += 1
            else:
                end_row -= 1
        if start_col == end_col:
            if ex > sx or end_col == 0:
                end_col += 1
            else:
                end_col -= 1
        if start_row > end_row:
            start_row, end_row = end_row, start_row
        if start_col > end_col:
            start_col, end_col = end_col, start_col

        if start_col > 80:
            start_col = 80
        if end_col > 80:
            end_col = 80
        if start_col < 0:
            start_col = 0
        if end_col < 0:
            end_col = 0

        if start_row > 24:
            start_row = 24
        if end_row > 24:
            end_row = 24
        if start_row < 0:
            start_row = 0
        if end_row < 0:
            end_row = 0

        return [(start_col, start_row, end_col, end_row)]

    def text(self, rect=None):
        if rect is None:
            return "\n".join(self._text)
        else:
            text = []
            (start_col, start_row, end_col, end_row) = rect
            for row in range(start_row, end_row):
                text.append(self._text[row][start_col:end_col])
            return text

    def text_selection(self):
        text = []
        if self._selection != None:
            for (start_col, start_row, end_col, end_row) in self._selection:
                for row in range(start_row, end_row):
                    text.append(self._text[row][start_col:end_col])
        return "\n".join(text)

    def column_count(self):
        return self._columns

    def row_count(self):
        return self._rows

    def copy_selection_to_clipboard(self):
        sel = self.text_selection()
        self._clipboard.setText(sel, QClipboard.Clipboard)

    def mouseMoveEvent(self, event):
        if self._session == None:
            return

        if self._press_pos:
            move_pos = event.pos()
            self._selection = self._selection_rects(self._press_pos, move_pos)

            sel = self.text_selection()
            if DEBUG:
                print("%r copied to xselection" % sel)
            self._clipboard.setText(sel, QClipboard.Selection)

            self.update_screen()

    def mouseDoubleClickEvent(self, event):
        if self._session == None:
            return

        self._press_pos = None
        # double clicks create a selection for the word under the cursor
        pos = event.pos()
        x, y = pos.x(), pos.y()
        col, row = self._pixel2pos(x, y)
        line = self._text[row]
        # find start of word
        start_col = col
        found_left = 0
        while start_col > 0:
            char = line[start_col]
            if not char.isalnum() and char not in ("_",):
                found_left = 1
                break
            start_col -= 1
        # find end of word
        end_col = col
        found_right = 0
        while end_col < self._columns:
            char = line[end_col]
            if not char.isalnum() and char not in ("_",):
                found_right = 1
                break
            end_col += 1
        self._selection = [
            (start_col + found_left, row, end_col - found_right + 1, row + 1)]

        sel = self.text_selection()
        if DEBUG:
            print("%r copied to xselection" % sel)
        self._clipboard.setText(sel, QClipboard.Selection)

        self.update_screen()
