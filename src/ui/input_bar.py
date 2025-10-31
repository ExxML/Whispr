from PyQt6.QtGui import QFont
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLineEdit

class InputBar(QWidget):
    """Input bar with text field and send button"""
    
    # Signal emitted when a message is sent
    message_sent = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
    
    def initUI(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 6, 12, 12)
        layout.setSpacing(8)
        
        # Create text input field
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("How can I help you?")
        self.input_field.returnPressed.connect(self.send_message)
        
        # Set font
        font = QFont("Microsoft JhengHei", 10)
        self.input_field.setFont(font)
        self.input_field.setMinimumHeight(32)
        
        # Style the input field
        self.input_field.setStyleSheet("""
            QLineEdit {
                background-color: rgba(255, 255, 255, 0.15);
                color: #FFFFFF;
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 16px;
                padding: 6px 10px;
            }
            QLineEdit:focus {
                border: 1px solid rgba(255, 255, 255, 0.5);
                background-color: rgba(255, 255, 255, 0.2);
            }
            QLineEdit::placeholder {
                color: rgba(255, 255, 255, 0.5);
            }
        """)
        
        # Add widgets to layout
        layout.addWidget(self.input_field)
    
    def send_message(self):
        """Send the message and clear the input field"""
        message = self.input_field.text().strip()
        if message:
            self.message_sent.emit(message)
            self.input_field.clear()
            self.input_field.setFocus()
    
    def set_enabled(self, enabled):
        """Enable or disable the input bar"""
        self.input_field.setEnabled(enabled)
