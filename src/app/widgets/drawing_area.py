from PyQt6.QtCore import Qt, QPoint, pyqtSignal
from PyQt6.QtGui import QPainter, QPen, QColor, QImage
from PyQt6.QtWidgets import QWidget
from ..constants import DrawingConstants, UIConstants


class DrawingArea(QWidget):
    drawing_started = pyqtSignal()
    drawing_finished = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_attributes()
        self._init_ui()
        self.setMinimumSize(*UIConstants.MIN_CANVAS_SIZE)

    def _init_attributes(self):
        self.drawing = False
        self.last_point = QPoint()
        self.pen_color = QColor(DrawingConstants.DEFAULT_COLOR)
        self.pen_width = DrawingConstants.PENCIL_WIDTH
        self.clear_screen = True
        self.image = self._create_blank_image()

    def _init_ui(self):
        self.setStyleSheet(
            """
            QWidget {
                background-color: white;
            }
        """
        )

    def _create_blank_image(self):
        image = QImage(self.size(), QImage.Format.Format_RGB32)
        image.fill(QColor(DrawingConstants.BACKGROUND_COLOR))
        return image

    def set_tool(self, tool_type):
        if tool_type == "pencil":
            self.pen_color = QColor(DrawingConstants.DEFAULT_COLOR)
            self.pen_width = DrawingConstants.PENCIL_WIDTH
        elif tool_type == "eraser":
            self.pen_color = QColor(DrawingConstants.BACKGROUND_COLOR)
            self.pen_width = DrawingConstants.ERASER_WIDTH

    def clear_drawing(self):
        self.image = self._create_blank_image()
        self.clear_screen = True
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = True
            self.last_point = event.pos()
            self.clear_screen = False
            self.drawing_started.emit()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton and self.drawing:
            painter = QPainter(self.image)
            painter.setPen(
                QPen(self.pen_color, self.pen_width, Qt.PenStyle.SolidLine)
            )
            painter.drawLine(self.last_point, event.pos())
            self.last_point = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.drawing:
            self.drawing = False
            self.drawing_finished.emit()

    def paintEvent(self, event):
        painter = QPainter(self)

        painter.drawImage(self.rect(), self.image)

        pen = QPen(QColor("#29be46"))
        painter.setPen(pen)
        painter.drawRect(0, 0, self.width() - 1, self.height() - 1)

        if self.clear_screen:
            painter.setPen(QColor("grey"))
            font = painter.font()
            font.setPointSize(24)
            painter.setFont(font)
            painter.drawText(
                self.rect(), Qt.AlignmentFlag.AlignCenter, "Начните творить!"
            )

    def resizeEvent(self, event):
        super().resizeEvent(event)
        new_image = QImage(self.size(), QImage.Format.Format_RGB32)
        new_image.fill(QColor(DrawingConstants.BACKGROUND_COLOR))

        painter = QPainter(new_image)
        if hasattr(self, "image"):
            painter.drawImage(self.rect(), self.image)
        painter.end()

        self.image = new_image
        self.update()
