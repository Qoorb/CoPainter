from .app import DrawingApp, QApplication
import sys


def main():
    app = QApplication(sys.argv)
    ex = DrawingApp()
    ex.show()
    sys.exit(app.exec())
