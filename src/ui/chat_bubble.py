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
        
        # First replace Python code blocks with formatted HTML
        formatted_message = self.message
        formatted_message = re.sub(
            r'```python\n(.*?)\n```',
            self._format_code_block,
            formatted_message,
            flags = re.DOTALL
        )
        
        # Format headers
        formatted_message = re.sub(r'^#####\s+(.+?)(<br>|$)', r'<h5>\1</h5>', formatted_message, flags = re.MULTILINE)
        formatted_message = re.sub(r'^####\s+(.+?)(<br>|$)', r'<h4>\1</h4>', formatted_message, flags = re.MULTILINE)
        formatted_message = re.sub(r'^###\s+(.+?)(<br>|$)', r'<h3>\1</h3>', formatted_message, flags = re.MULTILINE)
        formatted_message = re.sub(r'^##\s+(.+?)(<br>|$)', r'<h2>\1</h2>', formatted_message, flags = re.MULTILINE)
        formatted_message = re.sub(r'^#\s+(.+?)(<br>|$)', r'<h1>\1</h1>', formatted_message, flags = re.MULTILINE)
        
        # Replace **text** with <b>text</b>
        formatted_message = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', formatted_message)
        # # Replace `inline code` with formatted HTML
        # formatted_message = re.sub(
        #     r'`([^`]+?)`', 
        #     r'<code style="font-family: monospace; background-color: rgba(255,255,255,0.1); padding: 0.2em 0.4em; border-radius: 3px;">\1</code>', 
        #     formatted_message
        # )
        # Replace newlines with <br> tags (but not inside code blocks)
        # formatted_message = formatted_message.replace('\n', '<br>')
        formatted_message = re.sub(r'(?<!</h[1-5]>)\n(?!<h[1-5]>)', '<br>', formatted_message)
        
        html_message = f'<div style="line-height: 1.2;">{formatted_message}</div>'
        self.message_label.setText(html_message)
    
    def _format_code_block(self, match):
        """Format a Python code block"""
        code = match.group(1)
        # Replace HTML special characters
        code = code.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        
        # Create formatted code block with monospace font and dark background
        formatted_code = (
            '<div style="'
            'background-color: rgba(0, 0, 0, 0.3); '
            'color: rgba(255, 255, 255, 1.0); '
            'font-family: "Cascadia Code", monospace; '
            'white-space: pre-wrap; '
            'word-wrap: break-word; '
            'word-break: break-word; '
            'tab-size: 4; '
            '-moz-tab-size: 4; '
            'text-align: left;' 
            '">'
            f'<code style="white-space: pre-wrap;">{code}</code>'
            '</div>'
        )
        
        return formatted_code
