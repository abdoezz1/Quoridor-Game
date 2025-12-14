from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QToolBar, QMenuBar, QMenu
from PySide6.QtGui import QIcon, QAction, QKeySequence
from PySide6.QtCore import Qt, QSize


class MainWindow(QMainWindow):
    def __init__(self, game_view):
        super().__init__()

        self.setWindowTitle("Quoridor")
        self.game_view = game_view

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

        # Create Menu Bar
        self._create_menu_bar()

        # Create Toolbar
        self._create_toolbar()

    def _create_menu_bar(self):
        """Create the menu bar with File and Game menus."""
        menubar = self.menuBar()

        # File Menu
        file_menu = menubar.addMenu("&File")

        new_game_action = QAction("&New Game...", self)
        new_game_action.setShortcut(QKeySequence("Ctrl+N"))
        new_game_action.triggered.connect(self.game_view.board.signals.newGameRequested.emit)
        file_menu.addAction(new_game_action)

        file_menu.addSeparator()

        save_action = QAction("&Save Game", self)
        save_action.setShortcut(QKeySequence("Ctrl+S"))
        save_action.triggered.connect(self.game_view.board.signals.saveRequested.emit)
        file_menu.addAction(save_action)

        load_action = QAction("&Load Game", self)
        load_action.setShortcut(QKeySequence("Ctrl+O"))
        load_action.triggered.connect(self.game_view.board.signals.loadRequested.emit)
        file_menu.addAction(load_action)

        file_menu.addSeparator()

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence("Alt+F4"))
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit Menu
        edit_menu = menubar.addMenu("&Edit")

        undo_menu_action = QAction("&Undo", self)
        undo_menu_action.setShortcut(QKeySequence("Ctrl+Z"))
        undo_menu_action.triggered.connect(self.game_view.board.signals.undoRequested.emit)
        edit_menu.addAction(undo_menu_action)

        redo_menu_action = QAction("&Redo", self)
        redo_menu_action.setShortcut(QKeySequence("Ctrl+Y"))
        redo_menu_action.triggered.connect(self.game_view.board.signals.redoRequested.emit)
        edit_menu.addAction(redo_menu_action)

        # Expose menu actions
        self.new_game_action = new_game_action
        self.save_action = save_action
        self.load_action = load_action

    def _create_toolbar(self):
        """Create the main toolbar."""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(24, 24))

        # Game actions
        new_game_action = QAction(QIcon("GUI/resources/icons/new.png"), "New Game", self)
        new_game_action.triggered.connect(self.game_view.board.signals.newGameRequested.emit)

        restart_action = QAction(QIcon("GUI/resources/icons/restart.png"), "Restart", self)
        restart_action.triggered.connect(self.game_view.board.signals.restartRequested.emit)

        toolbar.addAction(new_game_action)
        toolbar.addAction(restart_action)
        toolbar.addSeparator()

        # Edit actions
        undo_action = QAction(QIcon("GUI/resources/icons/undo.png"), "Undo", self)
        undo_action.triggered.connect(self.game_view.board.signals.undoRequested.emit)

        redo_action = QAction(QIcon("GUI/resources/icons/redo.png"), "Redo", self)
        redo_action.triggered.connect(self.game_view.board.signals.redoRequested.emit)

        toolbar.addAction(undo_action)
        toolbar.addAction(redo_action)
        toolbar.addSeparator()

        # File actions
        save_action = QAction(QIcon("GUI/resources/icons/save.png"), "Save", self)
        save_action.triggered.connect(self.game_view.board.signals.saveRequested.emit)

        load_action = QAction(QIcon("GUI/resources/icons/load.png"), "Load", self)
        load_action.triggered.connect(self.game_view.board.signals.loadRequested.emit)

        toolbar.addAction(save_action)
        toolbar.addAction(load_action)

        self.addToolBar(toolbar)

        # Expose toolbar actions
        self.restart_action = restart_action
        self.undo_action = undo_action
        self.redo_action = redo_action
        self.save_toolbar_action = save_action
        self.load_toolbar_action = load_action
