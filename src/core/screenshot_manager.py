from mss import mss
from pathlib import Path

class ScreenshotManager:
    def __init__(self):
        self.screenshots_dir = Path(__file__).parent.parent / 'data' / 'cache' / 'screenshots'
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
        self.sct = mss()

    def take_screenshot(self):
        """
        Takes a screenshot of the primary screen and saves it to the screenshots directory.
        """
        try:
            # Generate filepath
            filepath = self.screenshots_dir / "screenshot.png"
            
            # Get the primary monitor
            monitor = self.sct.monitors[1]  # 0 is all monitors, 1 is primary
            
            # Take screenshot
            screenshot = self.sct.grab(monitor)
            
            # Save the screenshot
            mss.tools.to_png(screenshot.rgb, screenshot.size, output = str(filepath))

        except Exception as e:
            print(f"Screenshot Error taking screenshot: {str(e)}")

        finally:
            self.sct.close()