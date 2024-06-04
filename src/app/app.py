from PyQt6.QtCore import Qt, QPoint, QSize
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QPen, QColor, QImage
from PyQt6.QtWidgets import ( 
    QApplication, QMainWindow, QVBoxLayout,
    QHBoxLayout, QWidget, QPushButton,
    QLabel, QFrame, QStackedWidget
    )


class DrawingApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('Co-Painter')

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.central_widget.setStyleSheet("background-color: white;")

        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.stacked_widget = QStackedWidget(self.central_widget)
        main_layout.addWidget(self.stacked_widget)

        self.drawing_area = DrawingArea(self)
        self.drawing_area.setStyleSheet("background-color: white;")

        self.lower_bar = QFrame(self)
        self.lower_bar.setFixedSize(250, 36)
        self.lower_bar.setStyleSheet("background-color: lightgrey; border-radius: 16px;")

        lower_bar_layout = QHBoxLayout(self.lower_bar)
        lower_bar_layout.setContentsMargins(0, 0, 0, 0)

        self.pencil_button = QPushButton(self)
        self.pencil_button.setIcon(QIcon(QPixmap('src/app/assets/pencil_icon.png')))
        self.pencil_button.setIconSize(QSize(24, 24))
        self.pencil_button.setFixedSize(24, 24)
        self.pencil_button.setStyleSheet("border: none;")
        self.pencil_button.clicked.connect(self.drawing_area.use_pencil)

        self.eraser_button = QPushButton(self)
        self.eraser_button.setIcon(QIcon(QPixmap('src/app/assets/eraser_icon.png')))
        self.eraser_button.setIconSize(QSize(24, 24))
        self.eraser_button.setFixedSize(24, 24)
        self.eraser_button.setStyleSheet("border: none;")
        self.eraser_button.clicked.connect(self.drawing_area.use_eraser)

        self.clear_button = QPushButton(self)
        self.clear_button.setIcon(QIcon(QPixmap('src/app/assets/clear_icon.png')))
        self.clear_button.setIconSize(QSize(24, 24))
        self.clear_button.setFixedSize(24, 24)
        self.clear_button.setStyleSheet("border: none;")
        self.clear_button.clicked.connect(self.drawing_area.clear_drawing)

        lower_bar_layout.addWidget(self.pencil_button)
        lower_bar_layout.addWidget(self.eraser_button)
        lower_bar_layout.addWidget(self.clear_button)

        self.canvas_and_toolbar_container = QWidget(self)
        container_layout = QVBoxLayout(self.canvas_and_toolbar_container)
        container_layout.setContentsMargins(0, 0, 0, 0)

        container_layout.addWidget(self.drawing_area)
        container_layout.addWidget(self.lower_bar, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.stacked_widget.addWidget(self.canvas_and_toolbar_container)
        self.stacked_widget.setCurrentIndex(0)

        self.setGeometry(100, 100, 800, 600)
        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        
        self.canvas_and_toolbar_container.move(
            (self.width() - self.canvas_and_toolbar_container.width()) // 2,
            self.height() - self.canvas_and_toolbar_container.height() - 10
        )


class DrawingArea(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.drawing = False
        self.last_point = QPoint()
        self.pen_color = Qt.GlobalColor.black
        self.pen_width = 2
        self.clear_screen = True
        
        self.label = QLabel("Начните творить!", self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("font-size: 24px; color: grey;")

    def paintEvent(self, event):
        canvas = QPainter(self)
        canvas.fillRect(self.rect(), QColor('white'))
        
        if self.clear_screen:
            self.label.setGeometry(self.rect())
            self.label.show()
        else:
            self.label.hide()
        
        canvas.drawImage(self.rect(), self.image)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = True
            self.last_point = event.position().toPoint()
            if self.clear_screen:
                self.clear_screen = False
                self.update()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton and self.drawing:
            painter = QPainter(self.image)
            painter.setPen(QPen(self.pen_color, self.pen_width, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
            painter.drawLine(self.last_point, event.position().toPoint())
            self.last_point = event.position().toPoint()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = False

    def use_pencil(self):
        self.pen_color = Qt.GlobalColor.black
        self.pen_width = 2

    def use_eraser(self):
        self.pen_color = Qt.GlobalColor.white
        self.pen_width = 10

    def clear_drawing(self):
        self.image.fill(Qt.GlobalColor.white)
        self.clear_screen = True
        self.update()

    def resizeEvent(self, event):
        self.image = QImage(self.size(), QImage.Format.Format_RGB32)
        self.image.fill(Qt.GlobalColor.white)
        self.clear_drawing()
        super().resizeEvent(event)

