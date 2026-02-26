from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QWidget

from ui.ai_formatter import format_message


class ChatBubble(QWidget):
    """A chat bubble widget for displaying messages"""
    
    def __init__(self, message, is_user=False):
        super().__init__()
        self.message = message
        self.is_user = is_user
        self._initUI()
    
    def _initUI(self) -> None:
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
                    border-radius: 8px;
                    padding: 5px 4px -3px 5px;  /* top, right, bottom, left */
                }
            """)  # padding adjusted to visually center text within the bubble

            # Let Qt estimate the natural width of the message, then word wrap if necessary
            natural_width = self.message_label.sizeHint().width()
            max_width = 400

            if natural_width > max_width:
                self.message_label.setFixedWidth(max_width)
                self.message_label.setWordWrap(True)
            else:
                self.message_label.setFixedWidth(natural_width)

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

    def set_bot_message(self, message: str) -> None:
        """Format the bot message and set the text as the label.

        Args:
            message (str): The raw bot message text to format and display.
        """
        self.message = message
        self.message_label.setText(format_message(message))
