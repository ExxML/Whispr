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
        
        # Create message label
        message_label = QLabel(self.message)
        message_label.setWordWrap(True)
        message_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        
        # Set font
        font = QFont("Microsoft JhengHei", 10)
        message_label.setFont(font)
        
        # Set maximum width for text wrapping
        message_label.setMaximumWidth(600)
        
        # Style the bubble based on sender
        if self.is_user:
            # User messages: light gray, aligned right
            message_label.setStyleSheet("""
                QLabel {
                    background-color: rgba(255, 255, 255, 0.7);
                    color: #000000;
                    border-radius: 15px;
                    padding: 6px 10px;
                }
            """)
            layout.addStretch()
            layout.addWidget(message_label)
        else:
            # Bot messages: transparent, aligned left
            layout.addWidget(message_label)
            layout.addStretch()
        
        layout.setSpacing(0)
