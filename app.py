from PySide6.QtWidgets import QApplication
from GUI.main_window import MainWindow
from GUI.game_view import GameView

app = QApplication([])

view = GameView()
window = MainWindow(view)
window.show()

app.exec()
