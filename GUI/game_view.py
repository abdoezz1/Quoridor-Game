from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from GUI.widgets.turn_indicator import TurnIndicator
from GUI.widgets.wall_counter import WallCounter
from GUI.board_widget import BoardWidget

class GameView(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        # Top info bar
        info_layout = QHBoxLayout()
        self.turn_indicator = TurnIndicator()
        self.red_walls = WallCounter("Red")
        self.blue_walls = WallCounter("Blue")

        info_layout.addWidget(self.turn_indicator)
        info_layout.addWidget(self.red_walls)
        info_layout.addWidget(self.blue_walls)

        # Board
        self.board = BoardWidget()

        layout.addLayout(info_layout)
        layout.addWidget(self.board)

        self.setLayout(layout)
