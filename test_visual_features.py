"""
Quick test to demonstrate all visual features.
Run this to see walls, valid moves, and test the win dialog.
"""

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from GUI.main_window import MainWindow
from GUI.game_view import GameView

app = QApplication([])

# Create GUI
view = GameView()
window = MainWindow(view)

# Add some walls to demonstrate wall rendering
view.board.update_walls([
    (2, 3, 'h'),  # Horizontal wall
    (5, 2, 'v'),  # Vertical wall
    (0, 6, 'h'),  # Another horizontal
])

# Show valid moves for demonstration
view.board.set_valid_moves([
    (3, 0),  # Three possible moves
    (5, 0),
    (4, 1)
])

# Test signal connections
def on_pawn_click(row, col):
    print(f"✓ Pawn clicked at: ({row}, {col})")

def on_wall_attempt(row, col, orientation):
    print(f"✓ Wall placement: ({row}, {col}, {orientation})")
    # Add the wall to the board
    current_walls = view.board.walls.copy()
    current_walls.append((row, col, orientation))
    view.board.update_walls(current_walls)

view.board.signals.pawnClicked.connect(on_pawn_click)
view.board.signals.wallPlacementAttempt.connect(on_wall_attempt)

# Show window
window.show()

# Optional: Uncomment to test win dialog after 2 seconds
# def show_win():
#     view.board.show_winner("Red")
# QTimer.singleShot(2000, show_win)

print("\n" + "="*50)
print("✨ QUORIDOR GUI - VISUAL FEATURES DEMO")
print("="*50)
print("\n🎯 Try these interactions:")
print("  • Hover over cells → See yellow highlight")
print("  • Hover near edges → See wall preview (brown)")
print("  • Click cells → See expanding blue animation")
print("  • Green circles → Valid move indicators")
print("  • Notice pawn shadows for depth")
print("  • Click near edges → Place walls")
print("\n📝 Watch console for signal outputs")
print("="*50 + "\n")

app.exec()
