import json
import os
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize

class ClearChat(QPushButton):
    def __init__(self, parent, on_click):
        super().__init__("", parent)
        self.setFixedSize(32, 32)
        self.clicked.connect(on_click)
        assets_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'clear_chat_button.png')
        self.setIcon(QIcon(assets_path))
        self.setIconSize(QSize(16, 16))
        self.setStyleSheet(
            """
            QPushButton {
                background-color: rgba(255, 255, 255, 0.1);
                color: #FFFFFF;
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 16px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.3);
                border: 1px solid rgba(255, 255, 255, 0.5);
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.15);
            }
            """
        )

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
