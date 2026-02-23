import os

from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QMenu, QSystemTrayIcon

class SystemTray(QSystemTrayIcon):
    def __init__(self, overlay_window, shortcut_manager = None, parent = None):
        # Set icon
        base_dir = os.getcwd()
        icon_path = os.path.join(base_dir, 'src', 'assets', 'blank.ico')
        icon = QIcon(icon_path)
        
        super().__init__(icon, parent)
        self.setToolTip('Whispr')
        self.overlay_window = overlay_window
        self.shortcut_manager = shortcut_manager

        # Quit action
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.quit_app)
        
        # Add actions to menu
        self.menu = QMenu()
        self.menu.addAction(quit_action)
        
        # Set the context menu
        self.setContextMenu(self.menu)
        
        # Connect the activated signal (click) to toggle the window
        self.activated.connect(self.on_tray_activated)

        self.show()
    
    def on_tray_activated(self, reason):
        """Handle system tray icon activation events.

        Args:
            reason (QSystemTrayIcon.ActivationReason): The reason the tray icon was activated.
        """
        # Show/Hide on left click
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.overlay_window.toggle_window_visibility()
    
    def quit_app(self):
        """Quit the application via the overlay window."""
        self.overlay_window.quit_app()
