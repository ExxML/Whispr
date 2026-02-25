import mimetypes
import os
from pathlib import Path
from typing import Callable

from dotenv import load_dotenv
from google import genai
from google.genai import types


class AISender():
    """Handles sending user input to Gemini."""

    def __init__(self):
        # Load environment variables from the .env file
        base_dir = Path(__file__).resolve().parent.parent.parent
        load_dotenv(base_dir / ".env")

        # Initialize Gemini client
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    def generate_content_stream(
        self,
        user_input: str,
        attachments: list[str] | None = None,
        on_chunk: Callable[[str], None] | None = None
    ) -> str:
        """Generate and stream AI content with attachments, if any.

        Args:
            user_input (str): The user's input text to send to the model.
            attachments (list[str], optional): List of file paths to attach to the request.
            on_chunk (callable, optional): Callback invoked with each text chunk as it streams.

        Returns:
            str: The full generated response text.
        """
        # Build content parts from attachments
        contents: list[types.Part | str] = []
        for filepath in attachments or []:
            mime_type = mimetypes.guess_type(filepath)[0] or "application/octet-stream"
            with open(filepath, "rb") as f:
                contents.append(
                    types.Part.from_bytes(data=f.read(), mime_type=mime_type)
                )
        contents.append(user_input)

        full_response = ""
        # Stream generation
        for chunk in self.client.models.generate_content_stream(
            model="gemini-2.5-flash",
            contents=contents,
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_budget=0)  # Disables thinking
            ),
        ):
            if chunk.text:
                full_response += chunk.text
                print(chunk.text, end="", flush=True)
                if on_chunk is not None:
                    try:
                        on_chunk(chunk.text)
                    except Exception:
                        pass

        return full_response