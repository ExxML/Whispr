from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton
from .input_bar import InputBar
from .chat_area import ChatArea
from .clear_chat import ClearChat
import os
import ctypes

class Overlay(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        # Config variables
        self.overlay_window_colour = "1E1E1E" # in hex
        self.window_width = 600
        self.window_height = 600
        self.chat_history_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'chat_history.json')

        # Set window flags for overlay behavior
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )

        # Translucent bg for rounded corners
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Window setup (position overlay at center-top on screen)
        screen_rect = QApplication.primaryScreen().availableGeometry()
        screen_width = screen_rect.width()
        self.setGeometry((screen_width - self.window_width) // 2, 10, self.window_width, self.window_height)
        self.setWindowOpacity(0.8)
        
        # Create main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        self.clear_chat_button = ClearChat(self, self.clear_chat)
        header_layout = QHBoxLayout()
        header_layout.addWidget(self.clear_chat_button)
        header_layout.addStretch(1)
        self.min_btn = QPushButton('–', self)
        self.min_btn.setFixedSize(36, 32)
        self.min_btn.clicked.connect(self.hide)
        self.min_btn.setStyleSheet('''
            QPushButton {
                color: rgba(255, 255, 255, 0.3);
                border: none;
                font-size: 24px;
                font-weight: bold;
                padding-bottom: 3px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.5);
                color: rgba(0, 0, 0, 0.6);
                border-radius: 0px;
            }
        ''')
        self.close_btn = QPushButton('×', self)
        self.close_btn.setFixedSize(36, 32)
        self.close_btn.clicked.connect(self.quit_app)
        self.close_btn.setStyleSheet('''
            QPushButton {
                color: rgba(255, 255, 255, 0.3);
                border: none;
                font-size: 24px;
                font-weight: bold;
                padding-bottom: 3px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: rgba(255, 77, 69, 0.5);
                color: rgba(0, 0, 0, 0.6);
                border-radius: 0px;
                border-top-right-radius: 8px;
            }
        ''')
        header_layout.addWidget(self.min_btn)
        header_layout.addWidget(self.close_btn)
        main_layout.addLayout(header_layout)
        
        # Create and add chat area
        self.chat_area = ChatArea(self)
        main_layout.addWidget(self.chat_area, stretch=1)
        
        # Create and add input bar
        self.input_bar = InputBar(self)
        self.input_bar.message_sent.connect(self.handle_message)
        main_layout.addWidget(self.input_bar)
        
        self.show()
        
        # Set display affinity to exclude overlay from screen capture (Windows 10+)
        hwnd = int(self.winId())
        WDA_EXCLUDEFROMCAPTURE = 0x00000011
        result = ctypes.windll.user32.SetWindowDisplayAffinity(hwnd, WDA_EXCLUDEFROMCAPTURE)
        if result == 0:
            print("Warning: SetWindowDisplayAffinity failed. May appear in screenshots.")
    
    def handle_message(self, message):
        """Handle when a message is sent from the input bar"""
        # Add user message to chat
        self.chat_area.add_message(message, is_user=True)
        self.clear_chat_button.save_message(self.chat_history_path, message, is_user=True)
        
        # TODO: Add bot response logic here
        # For now, add a simple echo response
        bot_response = f"Echo: {message}"
        self.chat_area.add_message(bot_response, is_user=False)
        self.clear_chat_button.save_message(self.chat_history_path, bot_response, is_user=False)
    
    def clear_chat(self):
        """Clear all chat messages from UI and chat_history.json"""
        self.clear_chat_button.clear_chat(self.chat_history_path, self.chat_area)

    def quit_app(self):
        app = QApplication.instance()
        if app is not None:
            app.quit()

    # Override closeEvent to clear chat
    def closeEvent(self, event):
        self.clear_chat()
        super().closeEvent(event)

    # Override paintEvent to render rounded corners on app window
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        # Rounded rectangle background
        rect = self.rect()
        color = QColor(f"#{self.overlay_window_colour}")
        radius = 10
        painter.setBrush(color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(rect, radius, radius)