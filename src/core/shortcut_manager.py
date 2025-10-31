from PyQt6.QtWidgets import QApplication
import keyboard

class ShortcutManager:
    def __init__(self, overlay):
        self.overlay = overlay
        self.is_visible = True
        self.setup_shortcuts()
        self.setup_movement_distances()
    
    def setup_shortcuts(self):
        """Setup all keyboard shortcuts with blocking behavior"""
        # Shortcuts:
        # - Ctrl + E to show/hide overlay
        # - Ctrl + D to generate AI output
        # - Ctrl + Alt + <ArrowKeys> to move overlay window
        # - Ctrl + Shift + <UpArrow/DownArrow> to scroll up/down in the overlay window
        keyboard.add_hotkey('Ctrl + E', self.toggle_overlay, suppress = True)
        keyboard.add_hotkey('Ctrl + Alt + Left', self.move_window_left, suppress = True)
        keyboard.add_hotkey('Ctrl + Alt + Right', self.move_window_right, suppress = True)
        keyboard.add_hotkey('Ctrl + Alt + Up', self.move_window_up, suppress = True)
        keyboard.add_hotkey('Ctrl + Alt + Down', self.move_window_down, suppress = True)
    
    def toggle_overlay(self):
        """Toggle overlay visibility"""
        if self.is_visible:
            self.overlay.hide()
            self.is_visible = False
        else:
            self.overlay.show()
            self.overlay.raise_() # Bring to front
            self.is_visible = True
    
    def setup_movement_distances(self):
        """Determine screen geometry and movement distances"""
        self.screen_rect = QApplication.primaryScreen().availableGeometry()
        self.max_move_distance_x = self.screen_rect.width() // 10
        self.max_move_distance_y = self.screen_rect.height() // 10
        self.screen_bounds_offset = 2 # Always keep 2 pixels to screen edge to prevent setGeometry errors
    
    def move_window_left(self):
        """Move overlay window left"""
        new_x = max(self.screen_bounds_offset, self.overlay.geometry().x() - self.max_move_distance_x)
        self.overlay.move(new_x, self.overlay.geometry().y())
    
    def move_window_right(self):
        """Move overlay window right"""
        max_x = self.screen_rect.width() - self.overlay.geometry().width() - self.screen_bounds_offset
        new_x = min(max_x, self.overlay.geometry().x() + self.max_move_distance_x)
        self.overlay.move(new_x, self.overlay.geometry().y())
    
    def move_window_up(self):
        """Move overlay window up"""
        new_y = max(self.screen_bounds_offset, self.overlay.geometry().y() - self.max_move_distance_y)
        self.overlay.move(self.overlay.geometry().x(), new_y)
    
    def move_window_down(self):
        """Move overlay window down"""
        max_y = self.screen_rect.height() - self.overlay.geometry().height() - self.screen_bounds_offset
        new_y = min(max_y, self.overlay.geometry().y() + self.max_move_distance_y)
        self.overlay.move(self.overlay.geometry().x(), new_y)