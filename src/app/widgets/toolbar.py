from PyQt6.QtWidgets import QFrame, QHBoxLayout, QPushButton, QComboBox
from PyQt6.QtCore import QSize
from PyQt6.QtGui import QIcon, QPixmap
from ..constants import Styles


class ToolBar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(350, 36)
        self.setStyleSheet("background-color: #29be46; border-radius: 16px;")
        self._init_ui()

    def _init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.styles_box = self._create_styles_box()
        self.pencil_button = self._create_tool_button("pencil_icon.png")
        self.eraser_button = self._create_tool_button("eraser_icon.png")
        self.clear_button = self._create_tool_button("clear_icon.png")
        self.generate_button = self._create_tool_button("generate_icon.png")

        layout.addWidget(self.styles_box)
        layout.addWidget(self.pencil_button)
        layout.addWidget(self.eraser_button)
        layout.addWidget(self.clear_button)
        layout.addWidget(self.generate_button)

    def _create_tool_button(self, icon_name):
        button = QPushButton(self)
        button.setIcon(QIcon(QPixmap(f"src/app/assets/{icon_name}")))
        button.setIconSize(QSize(24, 24))
        button.setFixedSize(24, 24)
        button.setStyleSheet("border: none;")
        return button

    def _create_styles_box(self):
        styles_box = QComboBox(self)
        styles_box.addItems(Styles.AVAILABLE_STYLES)
        styles_box.setFixedSize(120, 24)
        styles_box.setStyleSheet(
            """
            QComboBox {
                background-color: white;
                border: 1px solid #29be46;
                border-radius: 12px;
                padding-left: 10px;
                color: grey;
            }
            QComboBox::drop-down {
                border: none;
                width: 24px;
            }
            QComboBox::down-arrow {
                image: url(src/app/assets/arrow_down.png);
                width: 12px;
                height: 12px;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                border: 1px solid #29be46;
                border-radius: 12px;
                selection-background-color: #e6f3e8;
                color: grey;
            }
        """
        )
        return styles_box
