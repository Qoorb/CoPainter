from PyQt6.QtCore import QRunnable, pyqtSlot, QObject, pyqtSignal
from PIL import ImageQt


class GeneratorSignals(QObject):
    result = pyqtSignal(object)
    finished = pyqtSignal()
    error = pyqtSignal(str)


class ImageGeneratorWorker(QRunnable):
    def __init__(self, generator_func, image, style):
        super().__init__()
        self.generator_func = generator_func
        self.image = image
        self.style = style
        self.signals = GeneratorSignals()

    @pyqtSlot()
    def run(self):
        try:
            result = self.generator_func(
                ImageQt.fromqimage(self.image), style_name=self.style
            )
            self.signals.result.emit(result)
        except Exception as e:
            self.signals.error.emit(str(e))
        finally:
            self.signals.finished.emit()
