from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication
from ui.overlay_window import Overlay
import sys
import signal


if __name__ == '__main__':
    app = QApplication(sys.argv)
    overlay = Overlay()
    
    ########## ########## ########## Allows Ctrl + C in terminal to exit ########## ########## ##########
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    timer = QTimer()
    timer.timeout.connect(lambda: None)  # Do nothing, just wake up
    timer.start(100)  # Check every 100ms
    ########## ########## ########## ########## ########## ########## ########## ########## ####
    
    sys.exit(app.exec())