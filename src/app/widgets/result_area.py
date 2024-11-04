from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QMovie, QPixmap
from ..constants import UIConstants


class ResultArea(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
        self.loading_movie = QMovie("src/app/assets/processing.gif")
        self.setMinimumSize(*UIConstants.MIN_CANVAS_SIZE)

    def _init_ui(self):
        self.setStyleSheet(
            "background-color: white; "
            "border: 1px solid #29be46; "
            "font-size: 24px; color: grey;"
        )
        self.setFixedSize(*UIConstants.CANVAS_SIZE)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setText("Здесь будет результат!")

    def show_loading(self):
        self.setMovie(self.loading_movie)
        self.loading_movie.start()

    def show_result(self, image):
        self.clear()
        self.setPixmap(QPixmap.fromImage(image))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.pixmap() and not self.pixmap().isNull():
            self.setPixmap(
                self.pixmap().scaled(
                    self.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
