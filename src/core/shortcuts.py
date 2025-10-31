import keyboard

class ShortcutManager:
    def __init__(self, overlay):
        self.overlay = overlay
        self.is_visible = True
        self.setup_shortcuts()
    
    def setup_shortcuts(self):
        """Setup all keyboard shortcuts with blocking behavior"""
        # Shortcuts:
        # - Ctrl + L to show/hide overlay
        # - Ctrl + D to generate AI output
        # - Ctrl + Alt + <ArrowKeys> to move overlay window
        # - Ctrl + Shift + <UpArrow/DownArrow> to scroll up/down in the overlay window
        keyboard.add_hotkey('Ctrl + L', self.toggle_overlay, suppress = True)
    
    def toggle_overlay(self):
        """Toggle overlay visibility"""
        if self.is_visible:
            self.overlay.hide()
            self.is_visible = False
        else:
            self.overlay.show()
            self.overlay.raise_() # Bring to front
            self.is_visible = True