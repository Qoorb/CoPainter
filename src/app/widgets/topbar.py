from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QSizePolicy
from PyQt6.QtSvgWidgets import QSvgWidget
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt


class TopBar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("padding: 5px 20px;")
        self.setFixedHeight(60)
        self._init_ui()

    def _init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        self.logo = QSvgWidget("src/app/assets/test.svg")
        self.logo.setFixedSize(350, 50)

        self.separator = QLabel()
        separator_pixmap = QPixmap("src/app/assets/line.png")
        self.separator.setPixmap(separator_pixmap.scaled(40, 40))
        self.separator.setFixedWidth(40)

        self.title = QLabel("Нейро-Мольберт")
        self.title.setStyleSheet("font-size: 24px; color: grey;")
        self.title.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
        )

        layout.addWidget(
            self.logo,
            0,
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
        )
        layout.addWidget(
            self.separator,
            0,
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
        )
        layout.addWidget(
            self.title,
            0,
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
        )
        layout.addStretch()
