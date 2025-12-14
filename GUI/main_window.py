from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QToolBar
from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import Qt, QSize

class MainWindow(QMainWindow):
    def __init__(self, game_view):
        super().__init__()

        self.setWindowTitle("Quoridor")

        # Load stylesheet
        try:
            with open("GUI/resources/qss/style.qss", "r") as f:
                self.setStyleSheet(f.read())
        except FileNotFoundError:
            pass  # Stylesheet not found, continue without it

        # Central Widget
        container = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(game_view, alignment=Qt.AlignCenter)
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Toolbar
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(24, 24))

        restart_action = QAction(QIcon("GUI/resources/icons/restart.png"), "Restart", self)
        undo_action = QAction(QIcon("GUI/resources/icons/undo.png"), "Undo", self)

        toolbar.addAction(restart_action)
        toolbar.addAction(undo_action)
        self.addToolBar(toolbar)

        # Connect actions to board signals
        restart_action.triggered.connect(game_view.board.signals.restartRequested.emit)
        undo_action.triggered.connect(game_view.board.signals.undoRequested.emit)

        # Expose actions
        self.restart_action = restart_action
        self.undo_action = undo_action
