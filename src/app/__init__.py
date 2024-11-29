from .main_window import DrawingApp
from PyQt6.QtWidgets import QApplication
import sys


def main():
    app = QApplication(sys.argv)
    ex = DrawingApp()
    ex.show()
    sys.exit(app.exec())
