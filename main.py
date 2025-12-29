#!/usr/bin/env python3
import sys
from PyQt6.QtWidgets import QApplication
from gui import MainWindow

def main():
    app = QApplication(sys.argv)
    
    # Don't close when the last window is closed (since we minimize to tray)
    app.setQuitOnLastWindowClosed(False)

    window = MainWindow()
    if not window.client.url or not window.client.token:
        window.show() # Show if config is needed
    else:
        # Start minimized or shown? Let's show it by default so user knows it's running
        window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
