class GUIController:
    """
    Connects GUI <-> Backend game logic.
    GUI does not implement logic itself.
    """

    def __init__(self, board_widget, game):
        """
        game: backend game logic instance
        """
        self.board = board_widget
        self.game = game

        # Connect signals
        self.board.signals.cellClicked.connect(self.handle_cell_click)

    def handle_cell_click(self, x, y):
        row, col = self.pixel_to_cell(x, y)

        # Example: ask game if this move is valid
        if self.game.is_valid_pawn_move(row, col):
            self.game.move_pawn_to(row, col)
            self.update_board()

    def pixel_to_cell(self, x, y):
        cell_size = min(self.board.width(), self.board.height()) / 9
        col = int(x // cell_size)
        row = int(y // cell_size)
        return row, col

    def update_board(self):
        # Pull updated state from game logic
        self.board.pawns = self.game.get_pawn_positions()
        self.board.walls = self.game.get_walls()
        self.board.update()
