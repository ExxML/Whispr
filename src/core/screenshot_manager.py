import os

import mss

class ScreenshotManager:
    def __init__(self):
        base_dir = os.getcwd()
        self.screenshots_dir = os.path.join(base_dir, 'src', 'data', 'cache', 'screenshots')
        os.makedirs(self.screenshots_dir, exist_ok = True)  # Ensure the folder exists

    def take_screenshot(self):
        """
        Takes a screenshot of the primary screen and saves it to the screenshots directory.
        """
        try:
            filepath = os.path.join(self.screenshots_dir, 'screenshot.png')
            
            # Create a new mss instance for each call (thread-safe)
            with mss.mss() as sct:
                # Screenshot the primary monitor
                monitor = sct.monitors[1]  # 0 is all monitors, 1 is primary
                screenshot = sct.grab(monitor)
                mss.tools.to_png(screenshot.rgb, screenshot.size, output = str(filepath))

        except Exception as e:
            print(f"Error taking screenshot: {str(e)}")