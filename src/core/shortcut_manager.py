from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer, QPoint, QObject, pyqtSignal
import math
import keyboard

class ShortcutManager(QObject):
    # Signals for safe threading
    move_signal = pyqtSignal(int, int)
    scroll_signal = pyqtSignal(int)
    quit_signal = pyqtSignal()
    screenshot_signal = pyqtSignal()
    clear_chat_signal = pyqtSignal()
    minimize_signal = pyqtSignal()
    generate_content_with_screenshot_signal = pyqtSignal(str, bool)
    
    def __init__(self, overlay, screenshot_manager):
        super().__init__()
        self.overlay = overlay
        self.screenshot_manager = screenshot_manager
        self.is_visible = True
        self.setup_shortcuts()
        self.setup_movement_distances()

        # Connect signals
        self.move_signal.connect(self._start_animation) # Signal needed because QTimers cannot be started from another thread
        self.scroll_signal.connect(self.overlay.chat_area.shortcut_scroll)
        self.quit_signal.connect(self.overlay.quit_app)
        self.screenshot_signal.connect(self.screenshot_manager.take_screenshot)
        self.clear_chat_signal.connect(self.overlay.chat_area.clear_chat)
        self.minimize_signal.connect(self.overlay.hide)
        self.generate_content_with_screenshot_signal.connect(self.overlay.handle_message)

        # Initialize animation
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._animate_step)
        self.animation_active = False
        self.animation_start_pos = None
        self.animation_target_pos = None
        self.animation_progress = 0.0
    
    def setup_shortcuts(self):
        """Setup all keyboard shortcuts with blocking behavior"""
        # Shortcuts:
        # - Ctrl + E to show/hide overlay
        # - Ctrl + D to generate AI output
        # - Ctrl + Alt + <ArrowKeys> to move overlay window
        # - Ctrl + Shift + <Up/Down> to scroll up/down in the overlay window
        # - Ctrl + Shift + Q to quit the application
        keyboard.add_hotkey('Ctrl + E', self.toggle_overlay, suppress = True) # Toggle visibility is always active
        self.register_hotkeys()
    
    def register_hotkeys(self):
        """Register hotkeys that are only active when overlay is visible"""
        keyboard.add_hotkey('Ctrl + Alt + Left', self.move_window_left, suppress = True)
        keyboard.add_hotkey('Ctrl + Alt + Right', self.move_window_right, suppress = True)
        keyboard.add_hotkey('Ctrl + Alt + Up', self.move_window_up, suppress = True)
        keyboard.add_hotkey('Ctrl + Alt + Down', self.move_window_down, suppress = True)
        keyboard.add_hotkey('Ctrl + Shift + Up', self.scroll_up, suppress = True)
        keyboard.add_hotkey('Ctrl + Shift + Down', self.scroll_down, suppress = True)
        keyboard.add_hotkey('Ctrl + Shift + Q', self.close_app, suppress = True)
        keyboard.add_hotkey('Ctrl + Shift + C', self.screenshot, suppress = True)
        keyboard.add_hotkey('Ctrl + Q', self.minimize, suppress = True)
        keyboard.add_hotkey('Ctrl + N', self.clear_chat, suppress = True)
        keyboard.add_hotkey('Ctrl + D', self.generate_with_screenshot, suppress = True)
    
    def unregister_hotkeys(self):
        """Unregister hotkeys that should only work when overlay is visible"""
        keyboard.remove_hotkey('Ctrl + Alt + Left')
        keyboard.remove_hotkey('Ctrl + Alt + Right')
        keyboard.remove_hotkey('Ctrl + Alt + Up')
        keyboard.remove_hotkey('Ctrl + Alt + Down')
        keyboard.remove_hotkey('Ctrl + Shift + Up')
        keyboard.remove_hotkey('Ctrl + Shift + Down')
        keyboard.remove_hotkey('Ctrl + Shift + Q')
        keyboard.remove_hotkey('Ctrl + Shift + C')
        keyboard.remove_hotkey('Ctrl + Q')
        keyboard.remove_hotkey('Ctrl + N')
        keyboard.remove_hotkey('Ctrl + D')
    
    def setup_movement_distances(self):
        """Determine screen geometry and movement distances"""
        self.screen_rect = QApplication.primaryScreen().availableGeometry()
        self.max_move_distance_x = self.screen_rect.width() // 14
        self.max_move_distance_y = self.screen_rect.height() // 14
        self.screen_bounds_offset = 2 # Always keep 2 pixels to screen edge to prevent setGeometry errors
        self.animation_duration = 100 # Animation duration in milliseconds
        self.animation_fps = 120 # Frames per second
        self.animation_frame_time = 1000 // self.animation_fps # Time per frame in ms
    
    def _animate_step(self):
        """Animate one step of movement"""
        # Increment progress
        self.animation_progress += self.animation_frame_time / self.animation_duration
        
        if self.animation_progress >= 1.0:
            # Animation complete
            self.overlay.move(self.animation_target_pos)
            self.animation_timer.stop()
            self.animation_active = False
        else:
            # Ease-out sine motion: sin(t * π/2)
            ease_progress = math.sin(self.animation_progress * math.pi / 2)
            current_x = int(self.animation_start_pos.x() + (self.animation_target_pos.x() - self.animation_start_pos.x()) * ease_progress)
            current_y = int(self.animation_start_pos.y() + (self.animation_target_pos.y() - self.animation_start_pos.y()) * ease_progress)
            self.overlay.move(current_x, current_y)
    
    def _start_animation(self, target_x, target_y):
        """Start animation"""
        self.animation_start_pos = self.overlay.pos()
        self.animation_target_pos = QPoint(target_x, target_y)
        self.animation_progress = 0.0
        self.animation_active = True
        self.animation_timer.start(self.animation_frame_time)

    def toggle_overlay(self):
        """Toggle overlay visibility"""
        if self.is_visible:
            self.overlay.hide()
            self.unregister_hotkeys()
        else:
            self.overlay.show()
            self.overlay.raise_() # Bring to front
            self.register_hotkeys()
        self.is_visible = not self.is_visible
    
    def move_window_left(self):
        """Move overlay window left"""
        if self.animation_active and self.animation_progress < 0.5:
            return
        new_x = max(self.screen_bounds_offset, self.overlay.geometry().x() - self.max_move_distance_x)
        self.move_signal.emit(new_x, self.overlay.geometry().y())
    
    def move_window_right(self):
        """Move overlay window right"""
        if self.animation_active and self.animation_progress < 0.5:
            return
        max_x = self.screen_rect.width() - self.overlay.geometry().width() - self.screen_bounds_offset
        new_x = min(max_x, self.overlay.geometry().x() + self.max_move_distance_x)
        self.move_signal.emit(new_x, self.overlay.geometry().y())
    
    def move_window_up(self):
        """Move overlay window up"""
        if self.animation_active and self.animation_progress < 0.5:
            return
        new_y = max(self.screen_bounds_offset, self.overlay.geometry().y() - self.max_move_distance_y)
        self.move_signal.emit(self.overlay.geometry().x(), new_y)
    
    def move_window_down(self):
        """Move overlay window down"""
        if self.animation_active and self.animation_progress < 0.5:
            return
        max_y = self.screen_rect.height() - self.overlay.geometry().height() - self.screen_bounds_offset
        new_y = min(max_y, self.overlay.geometry().y() + self.max_move_distance_y)
        self.move_signal.emit(self.overlay.geometry().x(), new_y)
    
    def scroll_up(self):
        """Scroll up in the chat area"""
        self.scroll_signal.emit(-100)
    
    def scroll_down(self):
        """Scroll down in the chat area"""
        self.scroll_signal.emit(100)

    def close_app(self):
        """Close the application"""
        self.quit_signal.emit() # Must emit signal to run on main thread
        
    def screenshot(self):
        """Take a screenshot of the primary screen"""
        self.screenshot_signal.emit()
        
    def minimize(self):
        """Minimize the overlay window"""
        self.minimize_signal.emit()
        self.is_visible = False
        self.unregister_hotkeys()
        
    def clear_chat(self):
        """Clear the chat history"""
        self.clear_chat_signal.emit()
        
    def generate_with_screenshot(self):
        """Automatically generate content with screenshot"""
        self.generate_content_with_screenshot_signal.emit(
            """
            Help me solve this programming problem. Be concise.\n
            1. Give me 5 clarification questions to ask about the problem.\n
            2. Give me a concise, point-form plan to approach and solve this problem (including edge cases).\n
            3. Give me a code block with the solution in Python.\n
            4. Give me a concise explanation of the solution.\n
            5. Give me the time and space complexity for the solution.
            """, 
            True # Take a screenshot
        )
