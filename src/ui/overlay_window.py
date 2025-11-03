from PyQt6.QtCore import Qt, QTimer, QPoint
from PyQt6.QtGui import QPainter, QColor, QPen
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton
from .input_bar import InputBar
from .chat_area import ChatArea
from .clear_chat import ClearChat
import os
import ctypes
from ctypes import wintypes

class Overlay(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        # Config variables
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
        self.setGeometry((screen_rect.width() - self.window_width) // 2, 2, self.window_width, self.window_height)
        
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
        main_layout.addWidget(self.chat_area, stretch = 1)
        
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
        
        # Setup timer to raise overlay so it is always visible (certain Windows operations override the stay on top hint)
        self._visibility_timer = QTimer(self)
        self._visibility_timer.setInterval(1000)
        self._visibility_timer.timeout.connect(self.ensure_window_visible)
        self._visibility_timer.start()

    def ensure_window_visible(self):
        try:
            if not self._is_topmost_window():
                self.raise_()
        except Exception:
            pass

    def _is_topmost_window(self) -> bool:
        try:
            screen = QApplication.primaryScreen()
            rect = self.frameGeometry()
            scale = screen.devicePixelRatio()
            ga_root = 2
            self_hwnd = int(self.winId())
            self_root = ctypes.windll.user32.GetAncestor(wintypes.HWND(self_hwnd), ga_root)
            padding = 15
            corners = [
                rect.topLeft() + QPoint(padding, padding),
                rect.topRight() + QPoint(-padding, padding),
                rect.bottomLeft() + QPoint(padding, -padding),
                rect.bottomRight() + QPoint(-padding, -padding)
            ]
            for corner in corners:
                pt = wintypes.POINT(int(corner.x() * scale), int(corner.y() * scale))
                hwnd_at_pt = ctypes.windll.user32.WindowFromPoint(pt)
                if hwnd_at_pt:
                    target_root = ctypes.windll.user32.GetAncestor(wintypes.HWND(hwnd_at_pt), ga_root)
                    if int(self_root) != int(target_root):
                        return False
            return True
        except Exception:
            return True
    
    def handle_message(self, message):
        """Handle when a message is sent from the input bar"""
        # Add user message to chat
        self.chat_area.add_message(message, is_user = True)
        self.clear_chat_button.save_message(self.chat_history_path, message, is_user = True)
        
        # TODO: Add bot response logic here
        # For now, add a simple echo response
        bot_response = f"Echo: {message}"
        self.chat_area.add_message(bot_response, is_user = False)
        self.clear_chat_button.save_message(self.chat_history_path, bot_response, is_user = False)
    
    def clear_chat(self):
        """Clear all chat messages from UI and chat_history.json"""
        self.clear_chat_button.clear_chat(self.chat_history_path, self.chat_area)

    def quit_app(self):
        self.clear_chat()
        app = QApplication.instance()
        if app is not None:
            app.quit()

    # Override mousePressEvent to automatically set focus to input field
    def mousePressEvent(self, event):
        self.input_bar.input_field.setFocus()
        super().mousePressEvent(event)

    # Override paintEvent to draw app window
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect()
        radius = 10
        
        # Draw window with rounded corners
        r, g, b, a = (20, 20, 20, 0.7)
        color = QColor(r, g, b, int(255 * a))
        painter.setBrush(color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(rect, radius, radius)
        
        # Draw window border
        border_width = 1
        border_rect = rect.adjusted(border_width, border_width, -border_width, -border_width)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor(255, 255, 255, int(255 * 0.15)), border_width))
        painter.drawRoundedRect(border_rect, radius, radius)