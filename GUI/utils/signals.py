from PySide6.QtCore import QObject, Signal

class BoardSignals(QObject):
    cellClicked = Signal(float, float)  # (x, y) pixel coordinates
    pawnClicked = Signal(int, int)  # (row, col) grid coordinates
    wallPlacementAttempt = Signal(int, int, str)  # (row, col, orientation)
    restartRequested = Signal()
    undoRequested = Signal()
