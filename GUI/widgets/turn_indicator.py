from PySide6.QtWidgets import QLabel
from PySide6.QtGui import QColor

class TurnIndicator(QLabel):
    def __init__(self):
        super().__init__("Turn: Red")
        self.setStyleSheet("font-size: 18px; color: white;")
