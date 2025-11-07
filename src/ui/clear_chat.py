from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QPushButton
import os

class ClearChat(QPushButton):
    def __init__(self, parent, on_click, chat_area):
        super().__init__("", parent)
        self.chat_area = chat_area
        self.setFixedSize(36, 32)
        self.clicked.connect(on_click)
        
        base_dir = os.getcwd()
        assets_dir = os.path.join(base_dir, 'src', 'assets')
        self.light_icon_path = os.path.join(assets_dir, 'clear_chat_button_light.png')
        self.dark_icon_path = os.path.join(assets_dir, 'clear_chat_button_dark.png')
        self.setIcon(QIcon(self.light_icon_path))
        self.setIconSize(QSize(14, 14))
        self.setStyleSheet('''
            QPushButton {
                border: none;
            }
            QPushButton:hover {
                background-color: rgba(255, 77, 69, 0.5);
                border-radius: 0px;
                border-top-left-radius: 8px;
            }
        ''')

    # Override to change icon on hover
    def enterEvent(self, event):
        self.setIcon(QIcon(self.dark_icon_path))
        super().enterEvent(event)

    # Override to change icon when not on hover
    def leaveEvent(self, event):
        self.setIcon(QIcon(self.light_icon_path))
        super().leaveEvent(event)
