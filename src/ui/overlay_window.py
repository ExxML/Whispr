import sys
import ctypes
import signal
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtWidgets import QApplication, QWidget

class Overlay(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        # Config variables
        self.overlay_window_colour = "1E1E1E" # in hex
        self.window_width = 600
        self.window_height = 400

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
        self.setStyleSheet(f"background-color: #{self.overlay_window_colour};")
        self.show()
        
        # Set display affinity to exclude overlay from screen capture (Windows 10+)
        hwnd = int(self.winId())
        WDA_EXCLUDEFROMCAPTURE = 0x00000011
        result = ctypes.windll.user32.SetWindowDisplayAffinity(hwnd, WDA_EXCLUDEFROMCAPTURE)
        if result == 0:
            print("Warning: SetWindowDisplayAffinity failed. May appear in screenshots.")

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

if __name__ == '__main__':
    app = QApplication(sys.argv)
    overlay = Overlay()
    
    ########## ########## ########## Allows Ctrl + C in terminal to exit ########## ########## ##########
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    timer = QTimer()
    timer.timeout.connect(lambda: None)  # Do nothing, just wake up
    timer.start(100)  # Check every 100ms
    ########## ########## ########## ########## ########## ########## ########## ########## ####
    
    sys.exit(app.exec())