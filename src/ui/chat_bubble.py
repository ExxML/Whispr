from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QFontMetrics
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QWidget

from ui.ai_formatter import AIFormatter


class ChatBubble(QWidget):
    """A chat bubble widget for displaying messages"""
    
    def __init__(self, message, is_user = False):
        super().__init__()
        self.message = message
        self.is_user = is_user
        self.initUI()
    
    def initUI(self):
        """Initialize the chat bubble UI layout and styling."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        
        # Create message label with HTML formatting
        # Default formatting for user message only (bot message uses formatting in set_bot_message)
        html_message = f'<div style="line-height: 1.4; white-space: pre-wrap;">{self.message}</div>'
        self.message_label = QLabel(html_message)
        self.message_label.setTextFormat(Qt.TextFormat.RichText)
        self.message_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        
        # Set font
        font = QFont("Helvetica", 11)
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
                    padding: 7px 7px 0px 7px;  /* top, right, bottom, left */
                }
            """)

            # Calculate text width to determine if wrapping is needed
            fm = QFontMetrics(font)
            text_width = fm.horizontalAdvance(self.message) + 8 # additional offset for right spacing
            max_width = 400
            total_text_width = text_width + 14 # accounting for 7px left + 7px right padding
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
            self.message_label.setFixedWidth(500)
            layout.addWidget(self.message_label)
            layout.addStretch()
        
        layout.setSpacing(0)

    def set_bot_message(self, message):
        """Format the bot message and set the text as the label.

        Args:
            message (str): The raw bot message text to format and display.
        """
        self.message = message
        self.message_label.setText(AIFormatter.format_message(message))
