from PyQt6.QtWidgets import QMessageBox


class ErrorHandler:
    @staticmethod
    def show_error(parent, message):
        QMessageBox.critical(
            parent,
            "Ошибка",
            message,
            QMessageBox.StandardButton.Ok
        )

    @staticmethod
    def handle_generation_error(parent, error_message):
        ErrorHandler.show_error(
            parent, f"Ошибка при генерации изображения: {error_message}"
        )
