import glob
import os

import mss


class ScreenshotManager():
    """Handles capturing screenshots of the primary screen."""

    def __init__(self):
        base_dir = os.getcwd()
        self.screenshots_dir = os.path.join(base_dir, "src", "data", "cache", "screenshots")
        os.makedirs(self.screenshots_dir, exist_ok=True)  # Ensure the folder exists
        self._screenshot_count = 0

    def take_screenshot(self) -> str:
        """Take a screenshot of the primary screen and save it to the screenshots directory.

        Returns:
            str: The filepath of the saved screenshot, or an empty string on failure.
        """
        try:
            filename = f"screenshot{self._screenshot_count}.png"
            filepath = os.path.join(self.screenshots_dir, filename)

            # Create a new mss instance for each call (thread-safe)
            with mss.mss() as sct:
                # Screenshot the primary monitor
                monitor = sct.monitors[1]  # 0 is all monitors, 1 is primary
                screenshot = sct.grab(monitor)
                mss.tools.to_png(screenshot.rgb, screenshot.size, output=str(filepath))

            self._screenshot_count += 1
            return filepath

        except Exception as e:
            print(f"Error taking screenshot: {str(e)}")
            return ""

    def clear_screenshots(self) -> None:
        """Delete all screenshots from the screenshots directory and reset the counter."""
        try:
            pattern = os.path.join(self.screenshots_dir, "screenshot*.png")
            for filepath in glob.glob(pattern):
                os.remove(filepath)
        except Exception as e:
            print(f"Error clearing screenshots: {str(e)}")

        self._screenshot_count = 0