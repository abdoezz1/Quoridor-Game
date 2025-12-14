# Quoridor Game

A strategic board game implementation with AI opponent, built using Python and PySide6.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![PySide6](https://img.shields.io/badge/PySide6-6.5+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 🎮 About the Game

Quoridor is a strategic board game where two players race to reach the opposite side of the board while placing walls to block their opponent.

### Rules
- **Board**: 9×9 grid of cells with wall slots between them
- **Objective**: Be the first player to reach any cell on the opposite baseline
- **Each turn**: Move your pawn OR place a wall (if walls remain)
- **Walls**: Each player has 10 walls; walls span 2 cells and cannot overlap
- **Path Rule**: Walls cannot completely block a player's path to their goal

## ✨ Features

- **Player vs Player** mode
- **Player vs AI** mode with 3 difficulty levels:
  - 🟢 **Easy**: Simple AI (depth 1) - good for beginners
  - 🟡 **Medium**: Balanced AI (depth 2) - moderate challenge
  - 🔴 **Hard**: Advanced AI (depth 3) - very challenging
- **Undo/Redo** functionality (Ctrl+Z / Ctrl+Y)
- **Save/Load** game state (Ctrl+S / Ctrl+O)
- Clean, modern GUI with visual feedback

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/abdoezz1/Quoridor-Game.git
   cd Quoridor-Game
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the game**
   ```bash
   python main.py
   ```

### One-liner (if you have Python installed)
```bash
git clone https://github.com/abdoezz1/Quoridor-Game.git && cd Quoridor-Game && pip install -r requirements.txt && python main.py
```

## 🎯 How to Play

1. **Start**: Choose game mode (PvP or vs AI) and difficulty
2. **Move**: Click on your pawn, then click a highlighted cell to move
3. **Place Wall**: Hover near cell edges to see wall preview, click to place
4. **Win**: Reach the opposite side of the board first!

### Controls
| Action | Control |
|--------|---------|
| New Game | `Ctrl+N` or Menu |
| Save Game | `Ctrl+S` |
| Load Game | `Ctrl+O` |
| Undo | `Ctrl+Z` |
| Redo | `Ctrl+Y` |

## 📁 Project Structure

```
Quoridor-Game/
├── main.py              # Main entry point
├── requirements.txt     # Python dependencies
├── README.md           # This file
│
├── AI/                 # AI opponent logic
│   ├── ai_player.py    # AI player with difficulty levels
│   ├── search.py       # Alpha-Beta search algorithm
│   ├── evaluation.py   # Board evaluation heuristics
│   └── move_generator.py
│
├── core/               # Game logic
│   ├── Board.py        # Game state container
│   ├── player.py       # Player class
│   ├── movement.py     # Pawn movement rules
│   ├── walls.py        # Wall placement logic
│   └── rules.py        # Game constants
│
└── GUI/                # User interface (PySide6)
    ├── main_window.py  # Main window
    ├── game_view.py    # Game view container
    ├── board_widget.py # Board rendering
    ├── widgets/        # UI components
    └── utils/          # GUI utilities
```

## 🤖 AI Algorithm

The AI uses **Minimax with Alpha-Beta Pruning**:

| Difficulty | Depth | Strategy |
|------------|-------|----------|
| Easy | 1 | Greedy, single-ply lookahead |
| Medium | 2 | Alpha-Beta with path heuristic |
| Hard | 3 | Deep search + strategic walls |

**Evaluation Function**:
- Path length difference (A* pathfinding)
- Available wall count bonus
- Positional advantage

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 👥 Authors

- **abdoezz1** - [GitHub Profile](https://github.com/abdoezz1)

## 🙏 Acknowledgments

- Quoridor board game by Mirko Marchesi
- PySide6 (Qt for Python)
