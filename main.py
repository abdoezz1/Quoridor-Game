import sys
import json
from datetime import datetime
from pathlib import Path

from PySide6.QtWidgets import QApplication, QFileDialog, QMessageBox
from PySide6.QtCore import Qt, QTimer

# Core game logic imports
from core.Board import Board
from core.player import Player
from core.walls import place_wall, is_wall_placement_valid
from core.rules import is_inside
from core.movement import _apply_move

# AI imports
from AI.ai_player import AIPlayer
from AI.move_generator import generate_pawn_moves

# GUI imports
from GUI.main_window import MainWindow
from GUI.game_view import GameView
from GUI.widgets.game_dialog import NewGameDialog


class QuoridorGame:
    """
    Main game controller that connects GUI with game logic.
    Supports both 2-player and vs AI modes.
    """

    def __init__(self, view: GameView, window: MainWindow):
        self.view = view
        self.window = window
        self.board_widget = view.board

        # Game settings
        self.vs_ai = False
        self.ai_difficulty = 'medium'

        # Initialize backend game (2-player mode, no AI)
        self.game = Board(vs_ai=False)

        # Track selected pawn for movement
        self.selected_pawn = None

        # Move history for undo functionality
        self.move_history = []

        # Redo history for redo functionality
        self.redo_history = []

        # AI move timer (to add delay for better UX)
        self.ai_timer = QTimer()
        self.ai_timer.setSingleShot(True)
        self.ai_timer.timeout.connect(self._execute_ai_move)

        # Connect signals
        self._connect_signals()

        # Show game mode dialog on startup
        QTimer.singleShot(100, self._show_new_game_dialog)

    def _connect_signals(self):
        """Connect GUI signals to game logic handlers."""
        self.board_widget.signals.pawnClicked.connect(self._on_cell_clicked)
        self.board_widget.signals.wallPlacementAttempt.connect(self._on_wall_placement)
        self.board_widget.signals.restartRequested.connect(self._restart_game)
        self.board_widget.signals.undoRequested.connect(self._undo_move)
        self.board_widget.signals.redoRequested.connect(self._redo_move)
        self.board_widget.signals.saveRequested.connect(self._save_game)
        self.board_widget.signals.loadRequested.connect(self._load_game)
        self.board_widget.signals.newGameRequested.connect(self._show_new_game_dialog)

    def _show_new_game_dialog(self):
        """Show dialog to select game mode and difficulty."""
        dialog = NewGameDialog(self.window)
        if dialog.exec():
            settings = dialog.get_settings()
            self._start_new_game(settings['vs_ai'], settings['difficulty'])
        else:
            # If cancelled on startup, start default PvP game
            if not hasattr(self, '_game_started'):
                self._start_new_game(False, 'medium')
        self._game_started = True

    def _start_new_game(self, vs_ai: bool, difficulty: str):
        """Start a new game with specified settings."""
        self.vs_ai = vs_ai
        self.ai_difficulty = difficulty

        # Create new game board
        self.game = Board(vs_ai=vs_ai, ai_difficulty=difficulty)

        # Reset state
        self.selected_pawn = None
        self.move_history = []
        self.redo_history = []
        self.board_widget.walls = []

        # Update window title
        mode = f"vs AI ({difficulty.capitalize()})" if vs_ai else "Player vs Player"
        self.window.setWindowTitle(f"Quoridor - {mode}")

        # Update display
        self._update_display()

    def _update_display(self):
        """Sync GUI with current game state."""
        # Update pawn positions (convert from 17×17 grid to 9×9 display)
        p1_display = (self.game.p1.pos[0] // 2, self.game.p1.pos[1] // 2)
        p2_display = (self.game.p2.pos[0] // 2, self.game.p2.pos[1] // 2)

        self.board_widget.update_pawns({
            "red": p1_display,   # Player 1 (bottom, starts at row 8)
            "blue": p2_display   # Player 2 (top, starts at row 0)
        })

        # Update turn indicator
        current = "Red" if self.game.current_turn == self.game.p1 else "Blue"
        if self.vs_ai and self.game.current_turn == self.game.p2:
            current = "Blue (AI)"
        self.view.turn_indicator.set_turn(current)

        # Update wall counters
        self.view.red_walls.set_count(self.game.p1.available_walls)
        self.view.blue_walls.set_count(self.game.p2.available_walls)

        # Clear selection
        self.board_widget.clear_valid_moves()

    def _on_cell_clicked(self, row: int, col: int):
        """Handle cell click - either select pawn or move to cell."""
        # Ignore clicks during AI turn
        if self.vs_ai and self.game.current_turn == self.game.p2:
            return

        current_player = self.game.current_turn
        player_display_pos = (current_player.pos[0] // 2, current_player.pos[1] // 2)

        # Check if clicking on current player's pawn
        if (row, col) == player_display_pos:
            self._select_pawn(current_player)
            return

        # If pawn is selected and clicking on valid move
        if self.selected_pawn is not None:
            if (row, col) in self.board_widget.valid_moves:
                self._move_pawn(row, col)
            else:
                # Deselect if clicking elsewhere
                self.selected_pawn = None
                self.board_widget.clear_valid_moves()

    def _select_pawn(self, player):
        """Select pawn and show valid moves."""
        self.selected_pawn = player
        valid_moves = self._get_valid_moves(player)
        self.board_widget.set_valid_moves(valid_moves)

    def _get_valid_moves(self, player) -> list:
        """
        Get all valid moves for the player in display coordinates.
        Uses AI/move_generator.py for consistent move generation.
        """
        # Get pawn moves from AI module (returns moves in 17x17 coords)
        pawn_moves = generate_pawn_moves(self.game, player)
        
        # Convert from 17×17 to 9×9 display coordinates
        valid = []
        for move_type, position in pawn_moves:
            if move_type == "pawn":
                display_row = position[0] // 2
                display_col = position[1] // 2
                valid.append((display_row, display_col))
        
        return valid

    def _move_pawn(self, row: int, col: int):
        """
        Move current player's pawn to the specified cell.
        Uses player.move_to_position() from core/player.py which delegates to core/movement.py.
        """
        player = self.game.current_turn

        # Save state for undo
        old_y, old_x = player.pos[0], player.pos[1]
        
        # Convert to 17×17 coordinates
        new_y, new_x = row * 2, col * 2

        # Use player's move_to_position method (delegates to core/movement.py)
        success = player.move_to_position(new_y, new_x)
        
        if not success:
            QMessageBox.warning(self.window, "Invalid Move", "Cannot move to this position!")
            return

        # Record move in history for undo
        self.move_history.append({
            'type': 'move',
            'player_id': player.id,
            'old_pos': (old_y, old_x),
            'new_pos': (new_y, new_x)
        })
        self.redo_history.clear()

        # Check for win
        if self._check_win(player):
            winner = "Red" if player == self.game.p1 else "Blue"
            self._update_display()
            self.board_widget.show_winner(winner)
            return

        # Switch turn
        self.game.switch_turn()
        self.selected_pawn = None
        self._update_display()

        # Trigger AI move if vs AI mode
        if self.vs_ai and self.game.current_turn == self.game.p2:
            self.ai_timer.start(500)  # 500ms delay for better UX

    def _execute_ai_move(self):
        """Execute the AI's move."""
        if not self.vs_ai or self.game.current_turn != self.game.p2:
            return

        # Save state before AI move for undo
        ai_player = self.game.p2
        old_pos = (ai_player.pos[0], ai_player.pos[1])
        old_walls = ai_player.available_walls

        # Execute AI move
        success = ai_player.ai_move()

        if success:
            # Determine what kind of move was made
            new_pos = (ai_player.pos[0], ai_player.pos[1])

            if new_pos != old_pos:
                # Pawn move
                self.move_history.append({
                    'type': 'move',
                    'player_id': 2,
                    'old_pos': old_pos,
                    'new_pos': new_pos
                })
            elif ai_player.available_walls < old_walls:
                # Wall placement - find the new wall
                # (For simplicity, we'll mark this as a special AI wall move)
                self.move_history.append({
                    'type': 'ai_wall',
                    'player_id': 2,
                    'walls_before': old_walls
                })

            self.redo_history.clear()

            # Rebuild GUI walls from board state
            self._rebuild_gui_walls()

            # Check for AI win
            if self._check_win(ai_player):
                self._update_display()
                self.board_widget.show_winner("Blue (AI)")
                return

            self._update_display()

    def _rebuild_gui_walls(self):
        """Rebuild GUI walls list from board state."""
        walls = []
        dim = self.game.dimBoard
        board = self.game.board

        for y in range(1, dim - 1, 2):
            for x in range(0, dim, 2):
                # Check horizontal walls
                if board[y, x] != 0 and x + 2 < dim and board[y, x + 1] != 0 and board[y, x + 2] != 0:
                    display_row = (y - 1) // 2
                    display_col = x // 2
                    wall = (display_row, display_col, 'h')
                    if wall not in walls:
                        walls.append(wall)

        for y in range(0, dim, 2):
            for x in range(1, dim - 1, 2):
                # Check vertical walls
                if board[y, x] != 0 and y + 2 < dim and board[y + 1, x] != 0 and board[y + 2, x] != 0:
                    display_row = y // 2
                    display_col = (x - 1) // 2
                    wall = (display_row, display_col, 'v')
                    if wall not in walls:
                        walls.append(wall)

        self.board_widget.walls = walls

    def _check_win(self, player) -> bool:
        """
        Check if player has reached their objective row.
        Uses player.objective from core/player.py.
        """
        return player.pos[0] == player.objective

    def _on_wall_placement(self, row: int, col: int, orientation: str):
        """
        Handle wall placement attempt.
        Uses is_wall_placement_valid and place_wall from core/walls.py.
        """
        # Ignore during AI turn
        if self.vs_ai and self.game.current_turn == self.game.p2:
            return

        player = self.game.current_turn

        if player.available_walls <= 0:
            QMessageBox.warning(self.window, "Invalid Move", "No walls remaining!")
            return

        if orientation == 'h':
            wall_y = row * 2 + 1
            wall_x = col * 2
        else:
            wall_y = row * 2
            wall_x = col * 2 + 1

        # Use core/walls.py for placement (place_wall validates internally)
        if place_wall(self.game, wall_y, wall_x, player):
            self.move_history.append({
                'type': 'wall',
                'player_id': player.id,
                'wall_y': wall_y,
                'wall_x': wall_x,
                'orientation': orientation,
                'display_pos': (row, col, orientation)
            })
            self.redo_history.clear()

            # Note: place_wall already decrements available_walls
            self.board_widget.walls.append((row, col, orientation))

            self.game.switch_turn()
            self._update_display()

            # Trigger AI move if vs AI mode
            if self.vs_ai and self.game.current_turn == self.game.p2:
                self.ai_timer.start(500)
        else:
            # Wall placement failed - show error message
            QMessageBox.warning(self.window, "Invalid Move", "Cannot place wall here!")

    def _restart_game(self):
        """Reset the game to initial state with same settings."""
        self._start_new_game(self.vs_ai, self.ai_difficulty)

    def _undo_move(self):
        """Undo the last move."""
        if not self.move_history:
            return

        last_move = self.move_history.pop()
        self.redo_history.append(last_move)

        player = self.game.p1 if last_move['player_id'] == 1 else self.game.p2

        if last_move['type'] == 'move':
            old_y, old_x = last_move['old_pos']
            
            # Use _apply_move from core/movement.py to restore position
            _apply_move(player, old_y, old_x)

        elif last_move['type'] == 'wall':
            wall_y = last_move['wall_y']
            wall_x = last_move['wall_x']
            orientation = last_move['orientation']

            self._remove_wall_from_board(wall_y, wall_x, orientation)
            player.available_walls += 2  # Restore 2 walls on undo

            display_pos = last_move['display_pos']
            if display_pos in self.board_widget.walls:
                self.board_widget.walls.remove(display_pos)

        self.game.switch_turn()
        self.selected_pawn = None
        self._update_display()

    def _remove_wall_from_board(self, wall_y: int, wall_x: int, orientation: str):
        """
        Remove a wall from the backend board grid.
        Clears all 3 cells (2 segments + connector) as defined in core/walls.py.
        """
        if orientation == 'h':
            # Horizontal wall: same row, spans 3 columns
            self.game.board[wall_y, wall_x] = 0
            self.game.board[wall_y, wall_x + 1] = 0  # connector
            self.game.board[wall_y, wall_x + 2] = 0
        else:
            # Vertical wall: same column, spans 3 rows
            self.game.board[wall_y, wall_x] = 0
            self.game.board[wall_y + 1, wall_x] = 0  # connector
            self.game.board[wall_y + 2, wall_x] = 0

    def _redo_move(self):
        """Redo a previously undone move."""
        if not self.redo_history:
            return

        redo_move = self.redo_history.pop()
        player = self.game.p1 if redo_move['player_id'] == 1 else self.game.p2

        if redo_move['type'] == 'move':
            new_y, new_x = redo_move['new_pos']
            
            # Use _apply_move from core/movement.py to apply position
            _apply_move(player, new_y, new_x)

        elif redo_move['type'] == 'wall':
            wall_y = redo_move['wall_y']
            wall_x = redo_move['wall_x']
            orientation = redo_move['orientation']
            display_pos = redo_move['display_pos']

            self._apply_wall_to_board(wall_y, wall_x, orientation)
            player.available_walls -= 2  # Each wall costs 2
            self.board_widget.walls.append(display_pos)

        self.move_history.append(redo_move)
        self.game.switch_turn()
        self.selected_pawn = None
        self._update_display()

    def _apply_wall_to_board(self, wall_y: int, wall_x: int, orientation: str):
        """
        Apply a wall to the backend board grid.
        Uses same wall codes as defined in core/rules.py.
        """
        from core.rules import HORIZONTAL_CONNECTOR_CODE, VERTICAL_CONNECTOR_CODE
        
        if orientation == 'h':
            # Horizontal wall: same row, spans 3 columns
            self.game.board[wall_y, wall_x] = 1
            self.game.board[wall_y, wall_x + 1] = HORIZONTAL_CONNECTOR_CODE  # connector
            self.game.board[wall_y, wall_x + 2] = 1
        else:
            # Vertical wall: same column, spans 3 rows
            self.game.board[wall_y, wall_x] = 1
            self.game.board[wall_y + 1, wall_x] = VERTICAL_CONNECTOR_CODE  # connector
            self.game.board[wall_y + 2, wall_x] = 1

    # ==================== SAVE/LOAD FUNCTIONALITY ====================

    def _save_game(self):
        """Save current game state to a JSON file."""
        filepath, _ = QFileDialog.getSaveFileName(
            self.window,
            "Save Game",
            f"quoridor_save_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "JSON Files (*.json)"
        )

        if not filepath:
            return

        try:
            # Helper function to convert numpy types to Python native types
            def convert_to_native(obj):
                """Recursively convert numpy types to Python native types for JSON serialization."""
                import numpy as np
                if isinstance(obj, np.integer):
                    return int(obj)
                elif isinstance(obj, np.floating):
                    return float(obj)
                elif isinstance(obj, np.ndarray):
                    return obj.tolist()
                elif isinstance(obj, dict):
                    return {k: convert_to_native(v) for k, v in obj.items()}
                elif isinstance(obj, (list, tuple)):
                    return [convert_to_native(item) for item in obj]
                return obj

            game_state = {
                'version': '1.0',
                'timestamp': datetime.now().isoformat(),
                'settings': {
                    'vs_ai': self.vs_ai,
                    'ai_difficulty': self.ai_difficulty,
                },
                'board': {
                    'grid': self.game.board.tolist(),
                    'dim': int(self.game.dimBoard),
                },
                'players': {
                    'p1': {
                        'pos': [int(x) for x in self.game.p1.pos],
                        'walls': int(self.game.p1.available_walls),
                        'objective': int(self.game.p1.objective),
                    },
                    'p2': {
                        'pos': [int(x) for x in self.game.p2.pos],
                        'walls': int(self.game.p2.available_walls),
                        'objective': int(self.game.p2.objective),
                    },
                },
                'current_turn': 1 if self.game.current_turn == self.game.p1 else 2,
                'gui_walls': self.board_widget.walls,
                'move_history': convert_to_native(self.move_history),
            }

            with open(filepath, 'w') as f:
                json.dump(game_state, f, indent=2)

            QMessageBox.information(
                self.window,
                "Game Saved",
                f"Game saved successfully to:\n{filepath}"
            )

        except Exception as e:
            QMessageBox.critical(
                self.window,
                "Save Error",
                f"Failed to save game:\n{str(e)}"
            )

    def _load_game(self):
        """Load game state from a JSON file."""
        filepath, _ = QFileDialog.getOpenFileName(
            self.window,
            "Load Game",
            "",
            "JSON Files (*.json)"
        )

        if not filepath:
            return

        try:
            with open(filepath, 'r') as f:
                game_state = json.load(f)

            # Validate version
            if game_state.get('version') != '1.0':
                raise ValueError("Incompatible save file version")

            # Restore settings
            self.vs_ai = game_state['settings']['vs_ai']
            self.ai_difficulty = game_state['settings']['ai_difficulty']

            # Create new game with same settings
            self.game = Board(vs_ai=self.vs_ai, ai_difficulty=self.ai_difficulty)

            # Restore board state
            import numpy as np
            self.game.board = np.array(game_state['board']['grid'])

            # Restore player states
            self.game.p1.pos[0] = game_state['players']['p1']['pos'][0]
            self.game.p1.pos[1] = game_state['players']['p1']['pos'][1]
            self.game.p1.available_walls = game_state['players']['p1']['walls']

            self.game.p2.pos[0] = game_state['players']['p2']['pos'][0]
            self.game.p2.pos[1] = game_state['players']['p2']['pos'][1]
            self.game.p2.available_walls = game_state['players']['p2']['walls']

            # Restore current turn
            self.game.current_turn = self.game.p1 if game_state['current_turn'] == 1 else self.game.p2

            # Restore GUI walls
            self.board_widget.walls = [tuple(w) for w in game_state['gui_walls']]

            # Restore move history
            self.move_history = game_state.get('move_history', [])
            # Convert tuples back from lists
            for move in self.move_history:
                if 'old_pos' in move:
                    move['old_pos'] = tuple(move['old_pos'])
                if 'new_pos' in move:
                    move['new_pos'] = tuple(move['new_pos'])
                if 'display_pos' in move:
                    move['display_pos'] = tuple(move['display_pos'])

            self.redo_history = []
            self.selected_pawn = None

            # Update window title
            mode = f"vs AI ({self.ai_difficulty.capitalize()})" if self.vs_ai else "Player vs Player"
            self.window.setWindowTitle(f"Quoridor - {mode}")

            self._update_display()

            QMessageBox.information(
                self.window,
                "Game Loaded",
                "Game loaded successfully!"
            )

        except Exception as e:
            QMessageBox.critical(
                self.window,
                "Load Error",
                f"Failed to load game:\n{str(e)}"
            )


def main():
    """Main entry point for Quoridor."""
    app = QApplication(sys.argv)

    # Create GUI
    view = GameView()
    window = MainWindow(view)

    # Initialize game controller
    game = QuoridorGame(view, window)

    # Keep reference to prevent garbage collection
    window.game = game

    # Show window
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
