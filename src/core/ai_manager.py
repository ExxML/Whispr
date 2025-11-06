import os
from pathlib import Path
from google import genai
from google.genai import types
from dotenv import load_dotenv

class AIManager:
    def __init__(self):
        # Load environment variables from the .env file
        load_dotenv(Path(__file__).parent.parent.parent / '.env')
        
        # Initialize Gemini client
        self.client = genai.Client(api_key = os.getenv('GEMINI_API_KEY'))

    def generate_content(self, user_input):
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

        return full_response

    def generate_content_with_screenshot(self, user_input):
        # Read the screenshot
        with open("./src/data/cache/screenshots/screenshot.png", "rb") as f:
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

        return full_response