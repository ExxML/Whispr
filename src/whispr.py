from PyQt6.QtWidgets import QApplication
from ui.overlay_window import Overlay
from core.ai_manager import AIManager
from core.shortcut_manager import ShortcutManager
from core.screenshot_manager import ScreenshotManager
import os
import sys
import json

if __name__ == '__main__':
    # Clear chat history on program start
    chat_history_path = os.path.join(os.path.dirname(__file__), 'data', 'chat_history.json')
    with open(chat_history_path, 'w') as f:
        json.dump([], f)
    
    app = QApplication(sys.argv)
    screenshot_manager = ScreenshotManager()
    ai_manager = AIManager(screenshot_manager)
    overlay = Overlay(ai_manager)
    shortcut_manager = ShortcutManager(overlay, screenshot_manager)
    
    sys.exit(app.exec())