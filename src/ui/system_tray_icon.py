from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
import os

class SystemTrayIcon(QSystemTrayIcon):
    def __init__(self, overlay_window, shortcut_manager = None, parent = None):
        # Set icon
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'Whispr.ico')
        icon = QIcon(icon_path)
        
        super().__init__(icon, parent)
        self.setToolTip('Whispr')
        self.overlay_window = overlay_window
        self.shortcut_manager = shortcut_manager

        # Toggle overlay visibility action
        self.toggle_action = QAction("Show/Hide", self)
        self.toggle_action.triggered.connect(self.shortcut_manager.toggle_overlay)
        
        # Quit action
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.quit_app)
        
        # Add actions to menu
        self.menu = QMenu()
        self.menu.addAction(self.toggle_action)
        self.menu.addAction(quit_action)
        
        # Set the context menu
        self.setContextMenu(self.menu)
        
        # Connect the activated signal (click) to toggle the window
        self.activated.connect(self.on_tray_activated)

        self.show()
    
    def on_tray_activated(self, reason):
        # Show/Hide on left click
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.shortcut_manager.toggle_overlay()
    
    def quit_app(self):
        self.overlay_window.quit_app()
