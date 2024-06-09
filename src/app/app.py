from PyQt6.QtCore import Qt, QPoint, QSize, QRunnable, pyqtSlot, QThreadPool, QObject, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QPen, QColor, QImage, QMovie
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout,
    QHBoxLayout, QWidget, QPushButton,
    QLabel, QFrame, QStackedWidget,
    QComboBox
)

from PIL import ImageQt
from src.model import Model


class WorkerSignals(QObject):

    result = pyqtSignal(object)
    finished = pyqtSignal()


class Worker(QRunnable):

    def __init__(self, generate_result, img, draw_style):
        super(Worker, self).__init__()
        self.generate_result = generate_result
        self.img = img
        self.draw_style = draw_style
        self.signals = WorkerSignals()
        
    @pyqtSlot()
    def run(self):
        result = self.generate_result(ImageQt.fromqimage(self.img), style_name=self.draw_style)
        self.signals.result.emit(result)
        self.signals.finished.emit()


class DrawingApp(QMainWindow):

    def __init__(self):
        super(DrawingApp, self).__init__()
        self.model = Model()
        self.draw_style = '(No style)'
        self.initUI()
        self.threadpool = QThreadPool()

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
        self.drawing_area.setStyleSheet("background-color: white; border: 1px solid #29be46;")
        self.drawing_area.setFixedSize(600, 600)

        self.result_area = QLabel(self)
        self.result_area.setStyleSheet("background-color: white; border: 1px solid #29be46; font-size: 24px; color: grey;")
        self.result_area.setFixedSize(600, 600)
        self.result_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.result_area.setText("Здесь будет результат!")

        self.movie = QMovie("src/app/assets/processing.gif")
        
        self.top_bar = QFrame(self)
        self.top_bar.setStyleSheet('padding-left: 20px;')

        header_layout = QHBoxLayout(self.top_bar)
        header_layout.setContentsMargins(0, 0, 0, 0)

        self.logo_area = QLabel()
        self.logo_area.setPixmap(QPixmap('src/app/assets/logo.png').scaled(250, 100, Qt.AspectRatioMode.KeepAspectRatio))
        
        self.sep_area = QLabel()
        self.sep_area.setPixmap(QPixmap('src/app/assets/line.png'))

        self.name_area = QLabel(self)
        self.name_area.setStyleSheet("font-size: 24px; color: grey;")
        self.name_area.setText("Нейро-Мольберт")

        header_layout.addWidget(self.logo_area)
        header_layout.addWidget(self.sep_area)
        header_layout.addWidget(self.name_area)

        canvas_layout = QHBoxLayout()
        canvas_layout.addWidget(self.drawing_area, alignment=Qt.AlignmentFlag.AlignHCenter)
        canvas_layout.addWidget(self.result_area, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.styles_box = QComboBox()
        self.styles_box.addItems([
            '(No style)', 'Cinematic', '3D Model',
            'Anime', 'Digital Art', 'Photographic',
            'Pixel art', 'Fantasy art', 'Neonpunk',
            'Manga'
            ])
        self.styles_box.setStyleSheet("border: none;")
        self.styles_box.setFixedSize(144, 24)
        self.styles_box.activated.connect(self.change_style)

        self.lower_bar = QFrame(self)
        self.lower_bar.setFixedSize(350, 36)
        self.lower_bar.setStyleSheet("background-color: #29be46; border-radius: 16px;")

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

        self.show_result_button = QPushButton(self)
        self.show_result_button.setIcon(QIcon(QPixmap('src/app/assets/generate_icon.png')))
        self.show_result_button.setIconSize(QSize(24, 24))
        self.show_result_button.setFixedSize(24, 24)
        self.show_result_button.setStyleSheet("border: none;")
        self.show_result_button.clicked.connect(self.generate_image)
        self.show_result_button.clicked.connect(self.processing)

        lower_bar_layout.addWidget(self.styles_box)
        lower_bar_layout.addWidget(self.pencil_button)
        lower_bar_layout.addWidget(self.eraser_button)
        lower_bar_layout.addWidget(self.clear_button)
        lower_bar_layout.addWidget(self.show_result_button)

        self.canvas_and_toolbar_container = QWidget(self)
        container_layout = QVBoxLayout(self.canvas_and_toolbar_container)
        container_layout.setContentsMargins(0, 0, 0, 0)

        container_layout.addWidget(self.top_bar, alignment=Qt.AlignmentFlag.AlignLeft)
        container_layout.addLayout(canvas_layout)
        container_layout.addWidget(self.lower_bar, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.stacked_widget.addWidget(self.canvas_and_toolbar_container)
        self.stacked_widget.setCurrentIndex(0)

        self.setGeometry(100, 100, 1200, 700)
        self.showFullScreen()

    def resizeEvent(self, event):
        super().resizeEvent(event)

        self.canvas_and_toolbar_container.move(
            (self.width() - self.canvas_and_toolbar_container.width()) // 2,
            self.height() - self.canvas_and_toolbar_container.height() - 10
        )

    def change_style(self, _): # We receive the index, but don't use it.
        self.draw_style = self.styles_box.currentText()

    def processing(self):
        self.result_area.setMovie(self.movie)
        self.movie.start()

    def update_result(self, output):
        self.result_area.clear()
        self.result_area.setPixmap(QPixmap.fromImage(ImageQt.toqimage(output.convert("RGBA"))))

    def generate_image(self):
        worker = Worker(self.model.run, self.drawing_area.image, self.draw_style)
        worker.signals.result.connect(self.update_result)
        self.threadpool.start(worker)

        self.show_result_button.setEnabled(False)
        worker.signals.finished.connect(
            lambda: self.show_result_button.setEnabled(True)
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

        self.image = QImage(self.size(), QImage.Format.Format_RGB32)
        self.image.fill(Qt.GlobalColor.white)

    def paintEvent(self, event):
        canvas = QPainter(self)
        canvas.fillRect(self.rect(), QColor('white'))

        if self.clear_screen:
            self.label.setGeometry(self.rect())
            self.label.show()
        else:
            self.label.hide()

        canvas.drawImage(self.rect(), self.image)

        pen = QPen(Qt.GlobalColor.lightGray)
        pen.setWidth(1)
        canvas.setPen(pen)
        canvas.drawRect(self.rect().adjusted(0, 0, -1, -1))

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
