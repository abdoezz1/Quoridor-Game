"""
Game Mode Selection Dialog
==========================
Allows users to select game mode and AI difficulty.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGroupBox,
    QRadioButton, QComboBox, QLabel, QPushButton,
    QButtonGroup
)
from PySide6.QtCore import Qt


class NewGameDialog(QDialog):
    """Dialog for selecting game mode and AI difficulty."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("New Game")
        self.setModal(True)
        self.setMinimumWidth(300)

        self.game_mode = "pvp"  # Default: Player vs Player
        self.ai_difficulty = "medium"  # Default difficulty

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Game Mode Selection
        mode_group = QGroupBox("Game Mode")
        mode_layout = QVBoxLayout()

        self.mode_button_group = QButtonGroup(self)

        self.pvp_radio = QRadioButton("Player vs Player")
        self.pvp_radio.setChecked(True)
        self.pva_radio = QRadioButton("Player vs AI")

        self.mode_button_group.addButton(self.pvp_radio, 0)
        self.mode_button_group.addButton(self.pva_radio, 1)

        mode_layout.addWidget(self.pvp_radio)
        mode_layout.addWidget(self.pva_radio)
        mode_group.setLayout(mode_layout)

        # AI Difficulty Selection
        self.difficulty_group = QGroupBox("AI Difficulty")
        diff_layout = QVBoxLayout()

        self.difficulty_combo = QComboBox()
        self.difficulty_combo.addItems(["Easy", "Medium", "Hard"])
        self.difficulty_combo.setCurrentText("Medium")

        # Difficulty descriptions
        self.diff_description = QLabel()
        self.diff_description.setWordWrap(True)
        self.diff_description.setStyleSheet("color: gray; font-size: 11px;")
        self._update_difficulty_description("Medium")

        diff_layout.addWidget(self.difficulty_combo)
        diff_layout.addWidget(self.diff_description)
        self.difficulty_group.setLayout(diff_layout)
        self.difficulty_group.setEnabled(False)  # Disabled by default (PvP mode)

        # Buttons
        button_layout = QHBoxLayout()

        self.start_button = QPushButton("Start Game")
        self.start_button.setDefault(True)
        self.cancel_button = QPushButton("Cancel")

        button_layout.addStretch()
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.cancel_button)

        # Add to main layout
        layout.addWidget(mode_group)
        layout.addWidget(self.difficulty_group)
        layout.addStretch()
        layout.addLayout(button_layout)

        # Connect signals
        self.pva_radio.toggled.connect(self._on_mode_changed)
        self.difficulty_combo.currentTextChanged.connect(self._update_difficulty_description)
        self.start_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

    def _on_mode_changed(self, checked):
        """Enable/disable difficulty selection based on mode."""
        self.difficulty_group.setEnabled(checked)

    def _update_difficulty_description(self, difficulty):
        """Update the difficulty description text."""
        descriptions = {
            "Easy": "Simple AI - Looks 1 move ahead.\nGood for beginners learning the game.",
            "Medium": "Balanced AI - Uses Alpha-Beta pruning (depth 2).\nProvides a moderate challenge.",
            "Hard": "Advanced AI - Deep search with strategic walls (depth 3).\nVery challenging opponent."
        }
        self.diff_description.setText(descriptions.get(difficulty, ""))

    def get_settings(self):
        """Return the selected game settings."""
        return {
            'vs_ai': self.pva_radio.isChecked(),
            'difficulty': self.difficulty_combo.currentText().lower()
        }


class SaveLoadDialog(QDialog):
    """Simple save/load confirmation dialog."""
    pass  # File dialogs are handled natively
