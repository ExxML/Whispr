from PyQt6.QtWidgets import QApplication
from ui.overlay_window import Overlay
from core.shortcuts import ShortcutManager
import os
import sys
import json

if __name__ == '__main__':
    # Clear chat history on program start
    chat_history_path = os.path.join(os.path.dirname(__file__), 'data', 'chat_history.json')
    with open(chat_history_path, 'w') as f:
        json.dump([], f)
    
    app = QApplication(sys.argv)
    overlay = Overlay()
    shortcut_manager = ShortcutManager(overlay)
    
    sys.exit(app.exec())