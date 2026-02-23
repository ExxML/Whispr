import json
import os

from PyQt6.QtCore import QAbstractAnimation, QEasingCurve, QPropertyAnimation, Qt, QTimer
from PyQt6.QtWidgets import QScrollArea, QVBoxLayout, QWidget

from .chat_bubble import ChatBubble

class ChatArea(QScrollArea):
    """Scrollable chat area for displaying message history"""
    
    def __init__(self, parent = None):
        super().__init__(parent)
        self.initUI()
        self._init_scroll_animation()
        base_dir = os.getcwd()
        self.chat_history_path = os.path.join(base_dir, 'src', 'data', 'chat_history.json')
        self._streaming_bubble = None
        self._streaming_text = ""
        
    def initUI(self):
        """Initialize the chat area UI layout, scroll settings, and styling."""
        # Configure scroll area
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Create container widget for messages
        self.chat_container = QWidget()
        self.chat_container.setStyleSheet('background-color: transparent;')
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.setContentsMargins(3, 3, 3, 3)
        self.chat_layout.addStretch()
        
        # Set the container as the scroll area's widget
        self.setWidget(self.chat_container)
        
        # Style the scroll area
        self.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background-color: rgba(255, 255, 255, 0.1);
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background-color: rgba(255, 255, 255, 0.3);
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: rgba(255, 255, 255, 0.5);
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
    
    def _init_scroll_animation(self):
        """Initialize smooth scrolling animation"""
        self._scroll_anim = QPropertyAnimation(self.verticalScrollBar(), b"value", self)
        self._scroll_anim.setEasingCurve(QEasingCurve.Type.OutQuad)
    
    def add_message(self, message, is_user):
        """Add a new message to the chat area.

        Args:
            message (str): The message text to display.
            is_user (bool): Whether the message is from the user.
        """
        # Remove the stretch before adding new message
        self.chat_layout.takeAt(self.chat_layout.count() - 1)
        
        # Create and add the chat bubble
        bubble = ChatBubble(message, is_user)
        self.chat_layout.addWidget(bubble)
        
        # Add stretch back at the end
        self.chat_layout.addStretch()
        
        # Save the message to chat history
        self.save_message(message, is_user)
        
        # Force scroll to bottom after a delay
        if is_user:
            QTimer.singleShot(400, lambda: self._animate_to(self.verticalScrollBar().maximum() - 10, 100))
    
    def start_assistant_stream(self):
        """Create an assistant bubble to stream content into (not saved until finalized)."""
        if self._streaming_bubble is not None:
            return
        # Remove stretch, add empty assistant bubble, then add stretch back
        self.chat_layout.takeAt(self.chat_layout.count() - 1)
        self._streaming_bubble = ChatBubble("", is_user = False)
        self._streaming_text = ""
        self.chat_layout.addWidget(self._streaming_bubble)
        self.chat_layout.addStretch()
    
    def append_to_stream(self, chunk_text):
        """Append text to the current streaming assistant bubble.

        Args:
            chunk_text (str): The text chunk to append to the stream.
        """
        if self._streaming_bubble is None:
            return
        self._streaming_text += chunk_text
        self._streaming_bubble.set_bot_message(self._streaming_text)
    
    def finalize_assistant_stream(self):
        """Persist the streamed assistant message and clear streaming state."""
        if self._streaming_bubble is None:
            return
        # Save final message
        self.save_message(self._streaming_text, is_user = False)
        # Clear streaming state
        self._streaming_bubble = None
        self._streaming_text = ""
        
    def save_message(self, message, is_user):
        """Save a message to chat_history.json.

        Args:
            message (str): The message text to save.
            is_user (bool): Whether the message is from the user.
        """
        try:
            with open(self.chat_history_path, 'r') as f:
                history = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            history = []

        history.append({
            "message": message,
            "is_user": is_user
        })

        with open(self.chat_history_path, 'w') as f:
            json.dump(history, f, indent = 2)
    
    def clear_chat(self):
        """Clear all messages from the chat area"""
        # Remove all widgets except the stretch
        while self.chat_layout.count() > 1:
            item = self.chat_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Clear chat history (JSON file)
        with open(self.chat_history_path, 'w') as f:
            json.dump([], f)
    
    def shortcut_scroll(self, amount):
        """Scroll the chat area by a specified amount.

        Args:
            amount (int): The pixel amount to scroll (positive for down, negative for up).
        """
        scrollbar = self.verticalScrollBar()
        target = scrollbar.value() + amount
        duration = 100
        self._animate_to(target, duration)
    
    def _animate_to(self, target, duration):
        """Animate scrollbar to target position.

        Args:
            target (int): The target scroll position.
            duration (int): The animation duration in milliseconds.
        """
        anim = self._scroll_anim
        if anim.state() == QAbstractAnimation.State.Running:
            anim.stop()
        sb = self.verticalScrollBar()
        target = max(sb.minimum(), min(target, sb.maximum()))
        anim.setTargetObject(sb)
        anim.setStartValue(sb.value())
        anim.setEndValue(target)
        anim.setDuration(duration)
        anim.start()
