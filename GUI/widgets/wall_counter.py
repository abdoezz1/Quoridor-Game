from PySide6.QtWidgets import QLabel

class WallCounter(QLabel):
    def __init__(self, player):
        super().__init__(f"{player} walls: 10")
        self.setStyleSheet("font-size: 16px; color: white;")
