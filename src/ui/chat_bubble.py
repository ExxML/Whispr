from PyQt6.QtWidgets import QWidget, QLabel, QHBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

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
        
        # Create message label with HTML for better line spacing
        # Replace newlines with <br> and wrap in HTML with line height
        html_message = self.message.replace('\n', '<br>')
        message_label = QLabel(f'<div style="line-height: 1.25;">{html_message}</div>')
        message_label.setWordWrap(True)
        message_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        
        # Set font
        font = QFont("Microsoft JhengHei", 10)
        message_label.setFont(font)
        
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
            message_label.setMinimumWidth(min(len(self.message), 450))
            message_label.setMaximumWidth(450)
            layout.addStretch()
            layout.addWidget(message_label)
        else:
            # Bot messages: transparent, aligned left
            message_label.setMinimumWidth(550)
            message_label.setMaximumWidth(550)
            layout.addWidget(message_label)
            layout.addStretch()
        
        layout.setSpacing(0)
