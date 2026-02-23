import ctypes
from ctypes import wintypes

from PyQt6.QtCore import QPoint, Qt, QTimer
from PyQt6.QtGui import QColor, QPainter, QPen
from PyQt6.QtWidgets import QApplication, QHBoxLayout, QPushButton, QVBoxLayout, QWidget

from .chat_area import ChatArea
from .clear_chat_button import ClearChatButton
from .input_bar import InputBar
from core.ai_receiver import AIReceiver


class MainWindow(QWidget):
    """Main application window containing the chat area, input bar, and title bar buttons."""

    def __init__(self, ai_sender):
        super().__init__()
        self.initUI()
        self.worker = AIReceiver(ai_sender, self.chat_area)
        
    def initUI(self):
        """Initialize the main window UI layout and components."""
        # Config variables
        self.window_width = 550
        self.window_height = 600

        # Set window flags for main window behavior
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
            # Qt.WindowType.WindowTransparentForInput # Click-through
        )

        # Translucent bg for rounded corners
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Prevent cursor from changing when hovering over the window
        self.setAttribute(Qt.WidgetAttribute.WA_SetCursor, False)
        self.unsetCursor()
        
        # Window setup (position main window at center-top on screen)
        screen_rect = QApplication.primaryScreen().availableGeometry()
        self.setGeometry((screen_rect.width() - self.window_width) // 2, 2, self.window_width, self.window_height)
        
        # Create main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create chat area
        self.chat_area = ChatArea(self)
        
        # Create input bar
        self.input_bar = InputBar(self)

        # Create and add title bar buttons
        self.clear_chat_button = ClearChatButton(self, self.chat_area.clear_chat, self.chat_area)
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

        # Add chat area
        main_layout.addWidget(self.chat_area, stretch = 1)

        # Add input bar
        self.input_bar.message_sent.connect(lambda msg: self.worker.handle_message(msg, take_screenshot = False))
        main_layout.addWidget(self.input_bar)

        # Unset cursor for all child widgets to preserve system cursor
        self._unset_cursor_recursive(self)
        
        self.show()
        
        # Set display affinity to exclude main window from screen capture (Windows 10+)
        hwnd = int(self.winId())
        WDA_EXCLUDEFROMCAPTURE = 0x00000011
        result = ctypes.windll.user32.SetWindowDisplayAffinity(hwnd, WDA_EXCLUDEFROMCAPTURE)
        if result == 0:
            print("Warning: SetWindowDisplayAffinity failed. May appear in screenshots.")
        
        # Setup timer to raise main window so it is always visible (certain Windows operations override the stay on top hint)
        self._visibility_timer = QTimer(self)
        self._visibility_timer.setInterval(1000)
        self._visibility_timer.timeout.connect(self.ensure_window_visible)
        self._visibility_timer.start()

    # Set cursor as default texture regardless of where it is hovering on the main window
    def _unset_cursor_recursive(self, widget):
        """Recursively unset cursor for a widget and all its children.

        Args:
            widget (QWidget): The widget to unset the cursor for.
        """
        widget.setAttribute(Qt.WidgetAttribute.WA_SetCursor, False)
        widget.unsetCursor()
        for child in widget.findChildren(QWidget):
            child.setAttribute(Qt.WidgetAttribute.WA_SetCursor, False)
            child.unsetCursor()

    def ensure_window_visible(self):
        """Raise the main window if it is no longer the topmost window."""
        try:
            if not self._is_topmost_window():
                self.raise_()
        except Exception:
            pass

    def _is_topmost_window(self):
        """Check if the main window is the topmost window at its corner positions.

        Returns:
            bool: True if the main window is topmost at all sampled points.
        """
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

    def toggle_window_visibility(self):
        """Toggle the main window between visible and hidden states."""
        if self.isVisible():
            self.hide()
        else:
            self.show()
            self.raise_()  # Bring to front

    def quit_app(self):
        """Quit the application, stopping any active worker and clearing chat."""
        # Stop any active worker
        if self.worker is not None:
            self.worker.stop()
        
        self.chat_area.clear_chat()
        app = QApplication.instance()
        if app is not None:
            app.quit()

    # Override mousePressEvent to automatically set focus to input field
    def mousePressEvent(self, event):
        """Handle mouse press events by setting focus to the input field.

        Args:
            event (QMouseEvent): The mouse press event.
        """
        self.input_bar.input_field.setFocus()
        super().mousePressEvent(event)

    # Override paintEvent to draw app window
    def paintEvent(self, _event):
        """Paint the main window with rounded corners and a border."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect()
        radius = 10
        
        # Draw window with rounded corners
        r, g, b, a = (20, 20, 20, 0.6)
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