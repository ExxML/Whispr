from PyQt6.QtWidgets import QWidget, QLabel, QHBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QFontMetrics

class ChatBubble(QWidget):
    """A chat bubble widget for displaying messages"""
    
    def __init__(self, message, is_user=False, parent=None):
        super().__init__(parent)
        self.message = message
        self.is_user = is_user
        self.initUI()
    
    def initUI(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        
        # Create message label with HTML formatting for line spacing
        html_message = f'<div style="line-height: 1.2;">{self.message}</div>'
        message_label = QLabel(html_message)
        message_label.setTextFormat(Qt.TextFormat.RichText)
        message_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        
        # Set font
        font = QFont("Microsoft JhengHei", 10)
        font.setPointSizeF(10.5)
        message_label.setFont(font)

        # Calculate text width to determine if wrapping is needed
        fm = QFontMetrics(font)
        text_width = fm.horizontalAdvance(self.message) + 8 # additional offset for right spacing
        max_width = 450
        padding = 14  # 7px left + 7px right
        # Only enable word wrap if text exceeds max width
        if text_width + padding > max_width:
            message_label.setWordWrap(True)
            message_label.setFixedWidth(max_width)
        else:
            message_label.setFixedWidth(text_width + padding)
        
        # Style the bubble based on sender
        if self.is_user:
            # User messages: light gray, aligned right
            message_label.setStyleSheet("""
                QLabel {
                    color: #ffffff;
                    border: 1px solid rgba(255, 255, 255, 0.7);
                    border-radius: 10px;
                    padding: 7px 7px 2px 7px;  /* top, right, bottom, left */
                }
            """)
            layout.addStretch()
            layout.addWidget(message_label)
        else:
            # Bot messages: transparent, aligned left
            message_label.setFixedWidth(550)
            layout.addWidget(message_label)
            layout.addStretch()
        
        layout.setSpacing(0)
