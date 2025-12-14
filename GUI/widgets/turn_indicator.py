from PySide6.QtWidgets import QLabel
from PySide6.QtGui import QColor


class TurnIndicator(QLabel):
    def __init__(self):
        super().__init__("Turn: Red")
        self.setStyleSheet("font-size: 18px; font-weight: bold; color: white;")

    def set_turn(self, player_name: str):
        """Update the turn indicator to show current player."""
        color = "#E63946" if player_name == "Red" else "#467C9E"
        self.setText(f"Turn: {player_name}")
        self.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {color};")
