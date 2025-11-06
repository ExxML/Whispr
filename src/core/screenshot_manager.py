import mss
from pathlib import Path

class ScreenshotManager:
    def __init__(self):
        self.screenshots_dir = Path(__file__).parent.parent / 'data' / 'cache' / 'screenshots'
        self.screenshots_dir.mkdir(parents = True, exist_ok = True)
        self.sct = mss.mss()

    def take_screenshot(self):
        """
        Takes a screenshot of the primary screen and saves it to the screenshots directory.
        """
        try:
            filepath = self.screenshots_dir / "screenshot.png"
            
            # Screenshot the primary monitor
            monitor = self.sct.monitors[1]  # 0 is all monitors, 1 is primary
            screenshot = self.sct.grab(monitor)
            mss.tools.to_png(screenshot.rgb, screenshot.size, output = str(filepath))

        except Exception as e:
            print(f"Screenshot Error taking screenshot: {str(e)}")