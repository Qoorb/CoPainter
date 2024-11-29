from dataclasses import dataclass


@dataclass
class UIConstants:
    MIN_WINDOW_WIDTH = 800
    MIN_WINDOW_HEIGHT = 600
    MIN_CANVAS_SIZE = (300, 300)
    CANVAS_SIZE = (600, 600)
    TOPBAR_HEIGHT = 60


@dataclass
class DrawingConstants:
    PENCIL_WIDTH = 2
    ERASER_WIDTH = 10
    DEFAULT_COLOR = "black"
    BACKGROUND_COLOR = "white"
    CANVAS_SIZE = UIConstants.CANVAS_SIZE


@dataclass
class Styles:
    AVAILABLE_STYLES = [
        "(No style)",
        "Cinematic",
        "3D Model",
        "Anime",
        "Digital Art",
        "Photographic",
        "Pixel art",
        "Fantasy art",
        "Neonpunk",
        "Manga",
    ]
