from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication
from ui.overlay_window import Overlay
import sys
import signal
import json
import os

if __name__ == '__main__':
    # Clear chat history on program start
    chat_history_path = os.path.join(os.path.dirname(__file__), 'data', 'chat_history.json')
    with open(chat_history_path, 'w') as f:
        json.dump([], f)
    
    app = QApplication(sys.argv)
    overlay = Overlay()
    
    ########## ########## ########## Allows Ctrl + C in terminal to exit ########## ########## ##########
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    timer = QTimer()
    timer.timeout.connect(lambda: None)  # Do nothing, just wake up
    timer.start(100)  # Check every 100ms
    ########## ########## ########## ########## ########## ########## ########## ########## ####
    
    sys.exit(app.exec())