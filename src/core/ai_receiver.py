import threading

from PyQt6.QtCore import QObject, pyqtSignal


class AIReceiver(QObject):
    """Handles AI response streaming and chat area updates."""

    # Signals for cross-thread communication
    # Using threading instead of QThread due to compilation issues with Nuitka
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    progress = pyqtSignal(str)

    def __init__(self, ai_sender, chat_area):
        super().__init__()
        self.ai_sender = ai_sender
        self.chat_area = chat_area
        self._thread = None
        self._stop_flag = threading.Event() # Stop flag in case a new user message is sent while a bot message is being streamed
        self._message = None
        self._take_screenshot = False

        # Connect signals to response handlers once
        self.progress.connect(self.on_response_chunk)
        self.finished.connect(self.on_response_ready)
        self.error.connect(self.on_response_error)

    def handle_message(self, message: str, take_screenshot: bool = False) -> None:
        """Handle a user message by displaying it and starting AI generation.

        Args:
            message (str): The user's message text.
            take_screenshot (bool): Whether to include a screenshot with the request.
        """
        # If there's an active thread, stop it
        if self._thread is not None and self._thread.is_alive():
            self._stop_flag.set()

            # Finalize the interrupted stream
            if self.chat_area._streaming_bubble is not None:
                self.chat_area.finalize_assistant_stream()

        # Reset stop flag for new message
        self._stop_flag = threading.Event()
        self._message = message
        self._take_screenshot = take_screenshot

        # Immediately add user's message to the chat area
        self.chat_area.add_message(message, is_user=True)

        # Start new thread
        self._thread = threading.Thread(target=self.run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Signal the thread to stop."""
        self._stop_flag.set()

    def is_stopped(self) -> bool:
        """Check if stop has been requested.

        Returns:
            bool: True if the thread has been signaled to stop.
        """
        return self._stop_flag.is_set()

    def run(self) -> None:
        """Execute AI content generation and emit progress and completion signals."""
        try:
            if self._take_screenshot:
                response = self.ai_sender.generate_content_with_screenshot(self._message, self._on_chunk)
            else:
                response = self.ai_sender.generate_content(self._message, self._on_chunk)

            # Only emit finished if we weren't stopped
            if not self.is_stopped():
                self.finished.emit(response)

        except Exception as e:
            # Only emit error if we weren't stopped
            if not self.is_stopped():
                self.error.emit(str(e))

    def _on_chunk(self, text: str) -> None:
        """Handle a streamed text chunk by emitting it to the UI thread.

        Args:
            text (str): The text chunk received from the AI stream.
        """
        # Emit chunk text to UI thread only if not stopped
        if text and not self.is_stopped():
            self.progress.emit(text)

    def on_response_ready(self) -> None:
        """Handle successful AI response."""
        # Finalize streaming bubble
        self.chat_area.finalize_assistant_stream()

    def on_response_error(self, error: str) -> None:
        """Handle AI response error.

        Args:
            error (str): The error message from the AI response.
        """
        error_msg = f"Error generating response: {error}"
        # Finalize any in-progress stream, then add error as a separate message
        if self.chat_area._streaming_bubble is not None:
            self.chat_area.finalize_assistant_stream()
        self.chat_area.add_message(error_msg, is_user=False)

    def on_response_chunk(self, chunk: str) -> None:
        """Stream chunk text into the current assistant bubble.

        Args:
            chunk (str): Text chunk from the AI response stream.
        """
        # Lazily create the assistant bubble only when first chunk arrives
        if self.chat_area._streaming_bubble is None:
            self.chat_area.start_assistant_stream()
        self.chat_area.append_to_stream(chunk)
