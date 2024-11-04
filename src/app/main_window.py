from PyQt6.QtCore import QThreadPool, Qt
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QSizePolicy,
)
from .widgets import DrawingArea, ToolBar, TopBar, ResultArea
from .workers import ImageGeneratorWorker
from .constants import UIConstants
from .error_handling import ErrorHandler
from src.model import Model


class DrawingApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.model = Model()
        self.threadpool = QThreadPool()
        self._init_ui()
        self._setup_connections()

    def _setup_connections(self):
        self.toolbar.generate_button.clicked.connect(self._generate_image)
        self.toolbar.pencil_button.clicked.connect(
            lambda: self.drawing_area.set_tool("pencil")
        )
        self.toolbar.eraser_button.clicked.connect(
            lambda: self.drawing_area.set_tool("eraser")
        )
        self.toolbar.clear_button.clicked.connect(
            self.drawing_area.clear_drawing
        )

    def _init_ui(self):
        self.setWindowTitle("Co-Painter")
        self.setMinimumSize(
            UIConstants.MIN_WINDOW_WIDTH,
            UIConstants.MIN_WINDOW_HEIGHT
        )

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.central_widget.setStyleSheet("background-color: white;")

        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        self.drawing_area = DrawingArea(self)
        self.result_area = ResultArea(self)
        self.toolbar = ToolBar(self)
        self.top_bar = TopBar(self)

        self.drawing_area.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.result_area.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

        main_layout.addWidget(self.top_bar)

        canvas_layout = QHBoxLayout()
        canvas_layout.addWidget(self.drawing_area)
        canvas_layout.addWidget(self.result_area)
        main_layout.addLayout(canvas_layout)

        main_layout.addWidget(
            self.toolbar,
            alignment=Qt.AlignmentFlag.AlignHCenter
        )

    def _generate_image(self):
        style = self.toolbar.styles_box.currentText()
        if style == "(No style)":
            ErrorHandler.show_error(self, "Пожалуйста, выберите стиль")
            return

        self.result_area.show_loading()

        worker = ImageGeneratorWorker(
            self.model.run,
            self.drawing_area.image,
            style
        )

        worker.signals.result.connect(self.result_area.show_result)
        worker.signals.error.connect(
            lambda error: ErrorHandler.handle_generation_error(self, error)
        )
        worker.signals.finished.connect(self.result_area.loading_movie.stop)

        self.threadpool.start(worker)
