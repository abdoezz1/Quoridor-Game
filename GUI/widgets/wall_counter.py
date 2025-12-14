from PySide6.QtWidgets import QLabel


class WallCounter(QLabel):
    def __init__(self, player):
        super().__init__(f"{player} walls: 10")
        self.player = player
        self.setStyleSheet("font-size: 16px; color: white;")

    def set_count(self, count: int):
        """Update the wall count display."""
        self.setText(f"{self.player} walls: {count}")
