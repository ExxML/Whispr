from PyQt6.QtWidgets import QScrollArea, QWidget, QVBoxLayout
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QAbstractAnimation
from .chat_bubble import ChatBubble

class ChatArea(QScrollArea):
    """Scrollable chat area for displaying message history"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        self._init_scroll_animation()
        
    def initUI(self):
        # Configure scroll area
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Create container widget for messages
        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.setContentsMargins(3, 3, 3, 3)
        self.chat_layout.setSpacing(0)
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
    
    def add_message(self, message, is_user=False):
        """Add a new message to the chat area"""
        # Remove the stretch before adding new message
        self.chat_layout.takeAt(self.chat_layout.count() - 1)
        
        # Create and add the chat bubble
        bubble = ChatBubble(message, is_user)
        self.chat_layout.addWidget(bubble)
        
        # Add stretch back at the end
        self.chat_layout.addStretch()
        
        # Scroll to bottom with smooth animation
        QTimer.singleShot(50, self.scroll_to_bottom)
    
    def scroll_to_bottom(self):
        """Smoothly scroll to the bottom of the chat area"""
        scrollbar = self.verticalScrollBar()
        self._animate_to(scrollbar.maximum(), 100)
    
    def clear_messages(self):
        """Clear all messages from the chat area"""
        # Remove all widgets except the stretch
        while self.chat_layout.count() > 1:
            item = self.chat_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
    
    def shortcut_scroll(self, amount):
        """Scroll the chat area by a specified amount"""
        scrollbar = self.verticalScrollBar()
        target = scrollbar.value() + amount
        duration = 100
        self._animate_to(target, duration)
    
    def _animate_to(self, target, duration):
        """Animate scrollbar to target position"""
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
