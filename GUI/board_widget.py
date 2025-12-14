from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QPen, QColor, QBrush, QPainterPath
from PySide6.QtCore import Qt, QTimer, QPointF
from GUI.utils.signals import BoardSignals
from GUI.utils.constants import BOARD_SIZE, CELL_COLOR, PAWN_COLORS
from GUI.widgets.message_box import show_winner


class BoardWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.signals = BoardSignals()

        # Set white background for the board
        self.setStyleSheet("background-color: white;")

        # Game state (backend will update these)
        self.pawns = {
            "red": (4, 0),
            "blue": (4, 8)
        }
        self.walls = []  # List of (row, col, orientation) tuples

        # Visual state
        self.valid_moves = []  # List of (row, col) tuples for highlighted cells
        self.selected_pawn = None  # Currently selected pawn position (row, col)
        self.preview_wall = None  # (row, col, orientation) for wall preview
        self.hover_cell = None  # (row, col) for cell hover effect

        # Animation state
        self.click_animation_cell = None  # (row, col) for click animation
        self.animation_progress = 0.0  # 0.0 to 1.0
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._update_animation)

        self.setMouseTracking(True)
        self.setFixedSize(540, 540)  # 9x9 board with 60px cells

    # ============ PUBLIC INTERFACE (Backend calls these) ============

    def update_pawns(self, pawns):
        """Update pawn positions. Called by backend."""
        self.pawns = pawns
        self.update()

    def update_walls(self, walls):
        """Update wall positions. Called by backend."""
        self.walls = walls
        self.update()

    def set_valid_moves(self, moves):
        """Show valid move highlights. Called by backend after pawn selection."""
        self.valid_moves = moves
        self.update()

    def clear_valid_moves(self):
        """Clear move highlights."""
        self.valid_moves = []
        self.selected_pawn = None
        self.update()

    def show_winner(self, winner_name):
        """Display win message dialog."""
        winner_color = PAWN_COLORS.get(winner_name.lower(), (100, 100, 100))
        restart = show_winner(winner_name, winner_color)
        if restart:
            self.signals.restartRequested.emit()

    # ============ EVENT HANDLERS ============

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()
        cell = min(w, h) / BOARD_SIZE

        # Draw grid
        self._draw_grid(painter, cell)

        # Draw hover effect
        if self.hover_cell:
            self._draw_hover_effect(painter, cell)

        # Draw valid move highlights
        if self.valid_moves:
            self._draw_valid_moves(painter, cell)

        # Draw walls
        self._draw_walls(painter, cell)

        # Draw wall preview
        if self.preview_wall:
            self._draw_wall_preview(painter, cell)

        # Draw pawns with shadows
        self._draw_pawns(painter, cell)

        # Draw click animation
        if self.click_animation_cell:
            self._draw_click_animation(painter, cell)

    def mouseMoveEvent(self, event):
        """Handle mouse movement for hover effects and wall preview."""
        x = event.position().x()
        y = event.position().y()

        w = self.width()
        h = self.height()
        cell = min(w, h) / BOARD_SIZE

        # Update hover cell
        col = int(x / cell)
        row = int(y / cell)

        if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
            self.hover_cell = (row, col)
        else:
            self.hover_cell = None

        # Calculate wall preview position
        self.preview_wall = self._calculate_wall_position(x, y, cell)

        self.update()

    def mousePressEvent(self, event):
        """Handle mouse clicks."""
        if event.button() == Qt.LeftButton:
            x = event.position().x()
            y = event.position().y()

            w = self.width()
            h = self.height()
            cell = min(w, h) / BOARD_SIZE

            col = int(x / cell)
            row = int(y / cell)

            # Check if wall was clicked FIRST (mutually exclusive with cell click)
            if self.preview_wall:
                r, c, orientation = self.preview_wall
                self.signals.wallPlacementAttempt.emit(r, c, orientation)
                return  # Don't process cell click if wall placement attempted

            # Emit signals based on what was clicked (only if no wall preview)
            if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
                # Cell click - could be pawn selection or movement
                self.signals.cellClicked.emit(x, y)
                self.signals.pawnClicked.emit(row, col)

                # Start click animation
                self.click_animation_cell = (row, col)
                self.animation_progress = 0.0
                self.animation_timer.start(16)  # ~60 FPS

    def leaveEvent(self, event):
        """Clear hover effects when mouse leaves widget."""
        self.hover_cell = None
        self.preview_wall = None
        self.update()

    # ============ DRAWING HELPERS ============

    def _draw_grid(self, painter, cell):
        """Draw the 9x9 grid."""
        pen = QPen(QColor(*CELL_COLOR), 2)
        painter.setPen(pen)

        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                x = c * cell
                y = r * cell
                painter.drawRect(int(x), int(y), int(cell), int(cell))

    def _draw_hover_effect(self, painter, cell):
        """Draw subtle highlight on hovered cell."""
        if not self.hover_cell:
            return

        row, col = self.hover_cell
        x = col * cell
        y = row * cell

        # Semi-transparent yellow highlight
        painter.fillRect(int(x), int(y), int(cell), int(cell),
                        QColor(255, 255, 150, 50))

    def _draw_valid_moves(self, painter, cell):
        """Draw highlights for valid move positions."""
        for row, col in self.valid_moves:
            x = col * cell + cell / 2
            y = row * cell + cell / 2
            radius = cell * 0.25

            # Draw pulsing circle
            painter.setPen(QPen(QColor(50, 205, 50), 3))
            painter.setBrush(QBrush(QColor(144, 238, 144, 100)))
            painter.drawEllipse(
                QPointF(x, y),
                radius,
                radius
            )

    def _draw_walls(self, painter, cell):
        """Draw placed walls."""
        wall_pen = QPen(QColor(139, 69, 19), 8)
        painter.setPen(wall_pen)

        for r, c, orientation in self.walls:
            if orientation == 'h':  # Horizontal wall
                x_start = c * cell
                y_pos = (r + 1) * cell
                x_end = x_start + 2 * cell
                painter.drawLine(int(x_start), int(y_pos), int(x_end), int(y_pos))
            elif orientation == 'v':  # Vertical wall
                x_pos = (c + 1) * cell
                y_start = r * cell
                y_end = y_start + 2 * cell
                painter.drawLine(int(x_pos), int(y_start), int(x_pos), int(y_end))

    def _draw_wall_preview(self, painter, cell):
        """Draw semi-transparent wall preview."""
        if not self.preview_wall:
            return

        r, c, orientation = self.preview_wall

        # Semi-transparent brown
        wall_pen = QPen(QColor(139, 69, 19, 120), 8)
        painter.setPen(wall_pen)

        if orientation == 'h':
            x_start = c * cell
            y_pos = (r + 1) * cell
            x_end = x_start + 2 * cell
            painter.drawLine(int(x_start), int(y_pos), int(x_end), int(y_pos))
        elif orientation == 'v':
            x_pos = (c + 1) * cell
            y_start = r * cell
            y_end = y_start + 2 * cell
            painter.drawLine(int(x_pos), int(y_start), int(x_pos), int(y_end))

    def _draw_pawns(self, painter, cell):
        """Draw pawns with shadow effect."""
        for name, (r, c) in self.pawns.items():
            x = c * cell + cell / 2
            y = r * cell + cell / 2
            radius = cell * 0.35

            # Draw shadow
            shadow_offset = 3
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(QColor(0, 0, 0, 60)))
            painter.drawEllipse(
                int(x - radius + shadow_offset),
                int(y - radius + shadow_offset),
                int(radius * 2),
                int(radius * 2)
            )

            # Draw pawn
            painter.setBrush(QBrush(QColor(*PAWN_COLORS[name])))

            # Add border if selected
            if self.selected_pawn == (r, c):
                painter.setPen(QPen(QColor(255, 215, 0), 3))  # Gold border
            else:
                painter.setPen(QPen(QColor(255, 255, 255), 2))  # White border

            painter.drawEllipse(
                int(x - radius),
                int(y - radius),
                int(radius * 2),
                int(radius * 2)
            )

    def _draw_click_animation(self, painter, cell):
        """Draw expanding circle animation on click."""
        if not self.click_animation_cell:
            return

        row, col = self.click_animation_cell
        x = col * cell + cell / 2
        y = row * cell + cell / 2

        # Expanding circle that fades out
        radius = cell * 0.5 * self.animation_progress
        alpha = int(150 * (1 - self.animation_progress))

        painter.setPen(QPen(QColor(100, 150, 255, alpha), 2))
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(
            QPointF(x, y),
            radius,
            radius
        )

    def _calculate_wall_position(self, x, y, cell):
        """
        Calculate wall position from mouse coordinates based on nearest edge.
        Automatically detects horizontal vs vertical orientation.
        Returns (row, col, orientation) or None.
        """
        # Find which cell we're in
        col_float = x / cell
        row_float = y / cell

        col_int = int(col_float)
        row_int = int(row_float)

        # Make sure we're within bounds
        if not (0 <= row_int < BOARD_SIZE and 0 <= col_int < BOARD_SIZE):
            return None

        # Calculate position within the cell (0.0 to 1.0)
        col_frac = col_float - col_int
        row_frac = row_float - row_int

        # Calculate distance to each edge of the cell
        dist_to_top = row_frac
        dist_to_bottom = 1.0 - row_frac
        dist_to_left = col_frac
        dist_to_right = 1.0 - col_frac

        # Find the closest edge
        min_dist = min(dist_to_top, dist_to_bottom, dist_to_left, dist_to_right)

        # Only show preview if close enough to an edge
        threshold = 0.3  # 30% of cell size
        if min_dist > threshold:
            return None

        # Determine orientation based on which edge is closest
        if min_dist == dist_to_top or min_dist == dist_to_bottom:
            # Closest to horizontal edge → horizontal wall
            if min_dist == dist_to_top and row_int > 0:
                # Top edge → wall above this cell
                wall_row = row_int - 1
                wall_col = col_int
            elif min_dist == dist_to_bottom and row_int < BOARD_SIZE - 1:
                # Bottom edge → wall below this cell
                wall_row = row_int
                wall_col = col_int
            else:
                return None

            # Check if wall can fit (needs 2 cells horizontally)
            if wall_col < BOARD_SIZE - 1:
                return (wall_row, wall_col, 'h')

        else:
            # Closest to vertical edge → vertical wall
            if min_dist == dist_to_left and col_int > 0:
                # Left edge → wall to the left of this cell
                wall_row = row_int
                wall_col = col_int - 1
            elif min_dist == dist_to_right and col_int < BOARD_SIZE - 1:
                # Right edge → wall to the right of this cell
                wall_row = row_int
                wall_col = col_int
            else:
                return None

            # Check if wall can fit (needs 2 cells vertically)
            if wall_row < BOARD_SIZE - 1:
                return (wall_row, wall_col, 'v')

        return None

    def _update_animation(self):
        """Update click animation progress."""
        self.animation_progress += 0.1

        if self.animation_progress >= 1.0:
            self.animation_timer.stop()
            self.click_animation_cell = None
            self.animation_progress = 0.0

        self.update()
