from ui.overlay_window import Overlay
from core.ai_manager import AIManager
from core.shortcut_manager import ShortcutManager
from core.screenshot_manager import ScreenshotManager
from PyQt6.QtWidgets import QApplication
import os
import sys
import json

if __name__ == '__main__':
    # Clear chat history on program start
    base_dir = os.getcwd()
    chat_history_path = os.path.join(base_dir, 'src', 'data', 'chat_history.json')
    with open(chat_history_path, 'w') as f:
        json.dump([], f)
    
    app = QApplication(sys.argv)
    screenshot_manager = ScreenshotManager()
    ai_manager = AIManager(screenshot_manager)
    overlay = Overlay(ai_manager)
    shortcut_manager = ShortcutManager(overlay, screenshot_manager)
    
    sys.exit(app.exec())