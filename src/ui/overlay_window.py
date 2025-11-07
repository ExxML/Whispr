from PyQt6.QtGui import QPainter, QColor, QPen
from PyQt6.QtCore import Qt, QTimer, QPoint, QObject, pyqtSignal
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton
from .input_bar import InputBar
from .chat_area import ChatArea
from .clear_chat import ClearChat
from ctypes import wintypes
import ctypes
import threading

class AIThread(QObject):
    """Separate thread for AI response streaming"""
    # Separate thread is needed because Qt requires all GUI operations to happen on the main thread
    # Using threading instead of QThread due to compilation issues with Nuitka
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    progress = pyqtSignal(str)
    
    def __init__(self, ai_manager, message, take_screenshot = False):
        super().__init__()
        self.ai_manager = ai_manager
        self.message = message
        self.take_screenshot = take_screenshot
        self._thread = None
        self._stop_flag = threading.Event() # Stop flag in case a new user message is sent while a bot message is being streamed
    
    def start(self):
        self._thread = threading.Thread(target = self.run, daemon = True)
        self._thread.start()
    
    def stop(self):
        """Signal the thread to stop"""
        self._stop_flag.set()
    
    def is_stopped(self):
        """Check if stop has been requested"""
        return self._stop_flag.is_set()
    
    def run(self):
        try:
            if self.take_screenshot:
                response = self.ai_manager.generate_content_with_screenshot(self.message, self._on_chunk)
            else:
                response = self.ai_manager.generate_content(self.message, self._on_chunk)
            
            # Only emit finished if we weren't stopped
            if not self.is_stopped():
                self.finished.emit(response)
        
        except Exception as e:
            # Only emit error if we weren't stopped
            if not self.is_stopped():
                self.error.emit(str(e))
    
    def _on_chunk(self, text):
        # Emit chunk text to UI thread only if not stopped
        if text and not self.is_stopped():
            self.progress.emit(text)

class Overlay(QWidget):
    def __init__(self, ai_manager):
        super().__init__()
        self.initUI()
        self.ai_manager = ai_manager
        self.worker = None
        
    def initUI(self):
        # Config variables
        self.window_width = 550
        self.window_height = 600

        # Set window flags for overlay behavior
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
        
        # Window setup (position overlay at center-top on screen)
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
        self.clear_chat_button = ClearChat(self, self.chat_area.clear_chat, self.chat_area)
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
        self.input_bar.message_sent.connect(lambda msg: self.handle_message(msg, take_screenshot = True))
        main_layout.addWidget(self.input_bar)

        # Unset cursor for all child widgets to preserve system cursor
        self._unset_cursor_recursive(self)
        
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

    # Set cursor as default texture regardless of where it is hovering on the overlay
    def _unset_cursor_recursive(self, widget):
        """Recursively unset cursor for widget and all its children"""
        widget.setAttribute(Qt.WidgetAttribute.WA_SetCursor, False)
        widget.unsetCursor()
        for child in widget.findChildren(QWidget):
            child.setAttribute(Qt.WidgetAttribute.WA_SetCursor, False)
            child.unsetCursor()

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

    def handle_message(self, message, take_screenshot = False):
        """Handle a user message"""
        # If there's an active worker, stop it and disconnect signals
        if self.worker is not None:
            self.worker.stop()
            try:
                self.worker.progress.disconnect()
                self.worker.finished.disconnect()
                self.worker.error.disconnect()
            except TypeError:
                # Signals already disconnected
                pass
            
            # Finalize the interrupted stream
            if self.chat_area._streaming_bubble is not None:
                self.chat_area.finalize_assistant_stream()
        
        # Immediately add user's message to the chat area
        self.chat_area.add_message(message, is_user = True)
        
        # Prepare streaming assistant bubble
        self.chat_area.start_assistant_stream()
        
        # Create and start worker thread
        self.worker = AIThread(self.ai_manager, message, take_screenshot)
        self.worker.progress.connect(self.on_response_chunk)
        self.worker.finished.connect(self.on_response_ready)
        self.worker.error.connect(self.on_response_error)
        self.worker.start()

        self.chat_area.scroll_to_bottom()

    def on_response_ready(self):
        """Handle successful AI response"""
        # Finalize streaming bubble and re-enable input
        self.chat_area.finalize_assistant_stream()
        
    def on_response_error(self, error):
        """Handle AI response error"""
        error_msg = f"Error generating response: {error}"
        # Finalize any in-progress stream, then add error as a separate message
        if self.chat_area._streaming_bubble is not None:
            self.chat_area.finalize_assistant_stream()
        self.chat_area.add_message(error_msg, is_user = False)

    def on_response_chunk(self, chunk):
        """Stream chunk text into the current assistant bubble"""
        self.chat_area.append_to_stream(chunk)

    def quit_app(self):
        # Stop any active worker
        if self.worker is not None:
            self.worker.stop()
        
        self.chat_area.clear_chat()
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