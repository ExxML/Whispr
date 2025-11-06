from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QFontMetrics
from PyQt6.QtWidgets import QWidget, QLabel, QHBoxLayout
import re

class ChatBubble(QWidget):
    """A chat bubble widget for displaying messages"""
    
    def __init__(self, message, is_user = False, parent = None):
        super().__init__(parent)
        self.message = message
        self.is_user = is_user
        self.initUI()
    
    def initUI(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        
        # Create message label with HTML formatting
        html_message = f'<div style="line-height: 1.2;">{self.message}</div>'
        self.message_label = QLabel(html_message)
        self.message_label.setTextFormat(Qt.TextFormat.RichText)
        self.message_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        
        # Set font
        font = QFont("Microsoft JhengHei", 10)
        font.setPointSizeF(10.5)
        self.message_label.setFont(font)
        
        # Style the bubble based on sender
        if self.is_user:
            # User messages: light gray, aligned right
            self.message_label.setStyleSheet("""
                QLabel {
                    color: rgba(255, 255, 255, 1.0);
                    background-color: transparent;
                    border: 1px solid rgba(255, 255, 255, 1.0);
                    border-radius: 10px;
                    padding: 6px 7px 3px 7px;  /* top, right, bottom, left */
                }
            """)

            # Calculate text width to determine if wrapping is needed
            fm = QFontMetrics(font)
            text_width = fm.horizontalAdvance(self.message) + 8 # additional offset for right spacing
            max_width = 450
            total_text_width = text_width + 14 # 7px left + 7px right padding
            # Set max width if text length exceeds max width
            if total_text_width > max_width:
                if total_text_width > max_width + 5:
                    # Only enable word wrap if text is long enough (prevents excessive top/bottom padding when text length is just above max width)
                    self.message_label.setWordWrap(True)
                self.message_label.setFixedWidth(max_width)
            else:
                # If text is one line
                self.message_label.setFixedWidth(total_text_width)

            layout.addStretch()
            layout.addWidget(self.message_label)
        else:
            # Bot messages: transparent, aligned left
            self.message_label.setStyleSheet("""
                QLabel {
                    color: rgba(255, 255, 255, 1.0);
                    background-color: transparent;
                }
            """)
            self.message_label.setWordWrap(True)
            self.message_label.setFixedWidth(550)
            layout.addWidget(self.message_label)
            layout.addStretch()
        
        layout.setSpacing(0)

    def set_message(self, message):
        # Parse markdown formatting in the generated response
        self.message = message

        # Replace **text** with <b>text</b>
        formatted_message = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', self.message)
        # Replace newlines with <br> tags
        formatted_message = formatted_message.replace('\n', '<br>')
        
        html_message = f'<div style="line-height: 1.2;">{formatted_message}</div>'
        self.message_label.setText(html_message)
