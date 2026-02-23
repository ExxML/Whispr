import json
import os
import sys

from PyQt6.QtWidgets import QApplication

from core.ai_sender import AISender
from core.screenshot_manager import ScreenshotManager
from core.shortcut_manager import ShortcutManager
from ui.main_window import MainWindow
from ui.system_tray import SystemTray


if __name__ == '__main__':
    # Clear chat history on program start
    base_dir = os.getcwd()
    chat_history_path = os.path.join(base_dir, 'src', 'data', 'chat_history.json')
    with open(chat_history_path, 'w') as f:
        json.dump([], f)
    
    app = QApplication(sys.argv)
    screenshot_manager = ScreenshotManager()
    ai_sender = AISender(screenshot_manager)
    main_window = MainWindow(ai_sender)
    shortcut_manager = ShortcutManager(main_window, screenshot_manager)
    tray_icon = SystemTray(main_window, shortcut_manager)
    
    sys.exit(app.exec())