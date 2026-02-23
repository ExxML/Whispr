import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

class AIManager:
    def __init__(self, screenshot_manager):
        # Load environment variables from the .env file
        base_dir = Path(__file__).resolve().parent.parent.parent
        load_dotenv(base_dir / '.env')
        
        # Initialize Gemini client
        self.client = genai.Client(api_key = os.getenv('GEMINI_API_KEY'))
        
        self.screenshot_manager = screenshot_manager

    def generate_content(self, user_input, on_chunk = None):
        """Generate AI content by streaming from the Gemini model.

        Args:
            user_input (str): The user's input text to send to the model.
            on_chunk (callable, optional): Callback invoked with each text chunk as it streams.

        Returns:
            str: The full generated response text.
        """
        full_response = ""
        # Stream generation
        for chunk in self.client.models.generate_content_stream(
            model = "gemini-2.5-flash",
            contents = [
                user_input
            ],
            config = types.GenerateContentConfig(
                thinking_config = types.ThinkingConfig(thinking_budget = 0)  # Disables thinking
            ),
        ):
            if chunk.text:
                full_response += chunk.text
                print(chunk.text, end = "", flush = True)
                if on_chunk is not None:
                    try:
                        on_chunk(chunk.text)
                    except Exception:
                        pass

        return full_response

    def generate_content_with_screenshot(self, user_input, on_chunk = None):
        """Generate AI content with a screenshot of the primary screen.

        Args:
            user_input (str): The user's input text to send to the model.
            on_chunk (callable, optional): Callback invoked with each text chunk as it streams.

        Returns:
            str: The full generated response text.
        """
        # Take screenshot
        self.screenshot_manager.take_screenshot()

        # Read the screenshot
        base_dir = os.getcwd()
        screenshot_path = os.path.join(base_dir, "src", "data", "cache", "screenshots", "screenshot.png")
        with open(screenshot_path, "rb") as f:
            image_bytes = f.read()

        full_response = ""
        # Stream generation
        for chunk in self.client.models.generate_content_stream(
            model = "gemini-2.5-flash",
            contents = [
                types.Part.from_bytes(
                    data = image_bytes,
                    mime_type = "image/png"
                ),
                user_input
            ],
            config = types.GenerateContentConfig(
                thinking_config = types.ThinkingConfig(thinking_budget = 0)  # Disables thinking
            ),
        ):
            if chunk.text:
                full_response += chunk.text
                print(chunk.text, end = "", flush = True)
                if on_chunk is not None:
                    try:
                        on_chunk(chunk.text)
                    except Exception:
                        pass

        return full_response