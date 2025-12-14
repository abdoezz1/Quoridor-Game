from PySide6.QtWidgets import QMessageBox, QPushButton
from PySide6.QtCore import Qt

def show_message(text):
    box = QMessageBox()
    box.setText(text)
    box.exec()

def show_winner(winner_name, winner_color):
    """
    Display an attractive win message dialog.
    
    Args:
        winner_name: Player name (e.g., "Red", "Blue")
        winner_color: RGB tuple (e.g., (220, 20, 60))
    
    Returns:
        True if user wants to restart, False otherwise
    """
    box = QMessageBox()
    box.setWindowTitle("🏆 Game Over!")
    
    # Create rich text message with color
    color_hex = f"#{winner_color[0]:02x}{winner_color[1]:02x}{winner_color[2]:02x}"
    message = f"""
    <div style='text-align: center; padding: 20px;'>
        <h1 style='color: {color_hex}; font-size: 32px; margin-bottom: 10px;'>
            🎉 {winner_name} Wins! 🎉
        </h1>
        <p style='font-size: 18px; color: #555;'>
            Congratulations on your victory!
        </p>
    </div>
    """
    box.setText(message)
    box.setTextFormat(Qt.RichText)
    
    # Add custom buttons
    restart_button = box.addButton("New Game", QMessageBox.AcceptRole)
    close_button = box.addButton("Close", QMessageBox.RejectRole)
    
    box.setDefaultButton(restart_button)
    box.exec()
    
    # Return True if user clicked restart
    return box.clickedButton() == restart_button
