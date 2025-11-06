from PyQt6.QtCore import QObject
from PyQt6.QtWidgets import QApplication
import os

class ScreenshotManager(QObject):
    def __init__(self):
        super().__init__()
        self.screenshots_dir = os.path.join(
            os.path.dirname(__file__), '..', 'data', 'cache', 'screenshots'
        )
        os.makedirs(self.screenshots_dir, exist_ok = True)

    def take_screenshot(self):
        """
        Takes a screenshot of the primary screen and saves it to the screenshots directory.
        """
        try:
            # Generate filepath
            filepath = os.path.join(self.screenshots_dir, "screenshot.png")
            
            # Get primary screen
            screen = QApplication.primaryScreen()
            if not screen:
                print("Screenshot Error: Could not get primary screen")
                
            # Take screenshot
            screenshot = screen.grabWindow(0)
            if screenshot.isNull():
                print("Screenshot Error: Failed to take screenshot")
                
            # Save screenshot
            if not screenshot.save(filepath, 'PNG'):
                print(f"Screenshot Error: Failed to save screenshot to {filepath}")

        except Exception as e:
            print(f"Screenshot Error taking screenshot: {str(e)}")