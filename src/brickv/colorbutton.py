from PyQt5.QtCore import QRect
from PyQt5.QtGui import QPen, QPalette, QPainter, QBrush
from PyQt5.QtWidgets import QPushButton

class ColorButton(QPushButton):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.on = False

    def initialize(self, brightness_color_list, background_color=None, border_color=None, style='rectangular'):
        self.brightness = 0
        self.brightness_pens = [QPen(c) for c in brightness_color_list]
        self.background_pen = QPen(self.palette().color(QPalette.Background) if background_color is None else background_color)
        self.border_pen = QPen(self.palette().color(QPalette.WindowText) if border_color is None else border_color)
        if style in ['rectangular', 'circular']:
            self.style = style
        else:
            raise ValueError("ColorButton style has to be either 'rectangular' or 'circular'")

    def paintEvent(self, _event):
        painter = QPainter(self)

        if self.style == 'rectangular':
            draw_fn = lambda rect, color: painter.drawRect(rect)
            fill_fn = lambda rect, color: painter.fillRect(rect, color)
        elif self.style == 'circular':
            draw_fn = lambda rect, color: painter.drawEllipse(rect)
            def fillEllipse(rect, color):
                painter.setBrush(QBrush(color))
                painter.drawEllipse(rect)
            fill_fn = fillEllipse

        if self.on:
            pen = self.brightness_pens[self.brightness]
        else:
            pen = self.background_pen

        fill_fn(QRect(0, 0, self.width() - 1, self.height() - 1), pen.color())

        painter.setPen(self.border_pen)
        draw_fn(QRect(0, 0, self.width() - 1, self.height() - 1), self.border_pen.color())



    def switch_off(self):
        self.on = False
        self.update()

    def switch_on(self, brightness = None):
        self.on = True
        if brightness is not None:
            self.brightness = brightness
        self.update()

    def set_brightness(self, brightness):
        self.brightness = brightness
