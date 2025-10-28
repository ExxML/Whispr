import json
import os
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize

class ClearChat(QPushButton):
    def __init__(self, parent, on_click):
        super().__init__("", parent)
        self.setFixedSize(36, 32)
        self.clicked.connect(on_click)
        assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets')
        self.light_icon_path = os.path.join(assets_dir, 'clear_chat_button_light.png')
        self.dark_icon_path = os.path.join(assets_dir, 'clear_chat_button_dark.png')
        self.setIcon(QIcon(self.light_icon_path))
        self.setIconSize(QSize(14, 14))
        self.setStyleSheet('''
            QPushButton {
                border: none;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.5);
                border-radius: 0px;
                border-top-left-radius: 8px;
            }
        ''')

    def save_message(self, chat_history_path, message, is_user):
        """Save a message to chat_history.json"""
        try:
            with open(chat_history_path, 'r') as f:
                history = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            history = []

        history.append({
            "message": message,
            "is_user": is_user
        })

        with open(chat_history_path, 'w') as f:
            json.dump(history, f, indent=2)


    def clear_chat(self, chat_history_path, chat_area):
        """Clear all chat messages from UI and chat_history.json"""
        # Clear UI
        chat_area.clear_messages()

        # Clear JSON file
        with open(chat_history_path, 'w') as f:
            json.dump([], f)

    # Override to change icon on hover
    def enterEvent(self, event):
        self.setIcon(QIcon(self.dark_icon_path))
        super().enterEvent(event)

    # Override to change icon when not on hover
    def leaveEvent(self, event):
        self.setIcon(QIcon(self.light_icon_path))
        super().leaveEvent(event)
