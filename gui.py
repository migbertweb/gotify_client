import sys
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QListWidget, 
                             QLabel, QLineEdit, QPushButton, QDialog, QSystemTrayIcon, 
                             QMenu, QApplication, QMessageBox)
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import Qt
import config
from client import GotifyClient

class ConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gotify Settings")
        self.layout = QVBoxLayout()

        self.layout.addWidget(QLabel("Server URL:"))
        self.url_input = QLineEdit()
        self.layout.addWidget(self.url_input)

        self.layout.addWidget(QLabel("Client Token:"))
        self.token_input = QLineEdit()
        self.layout.addWidget(self.token_input)

        save_btn = QPushButton("Save & Connect")
        save_btn.clicked.connect(self.save)
        self.layout.addWidget(save_btn)

        self.setLayout(self.layout)
        self.load_settings()

    def load_settings(self):
        c = config.load_config()
        self.url_input.setText(c.get("url", ""))
        self.token_input.setText(c.get("token", ""))

    def save(self):
        url = self.url_input.text().strip()
        token = self.token_input.text().strip()
        config.save_config(url, token)
        self.accept()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gotify Client")
        self.resize(400, 600)
        
        # Load Icon
        self.icon_path = "gotify.png"
        self.setWindowIcon(QIcon(self.icon_path))

        # Central Widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Status Label
        self.status_label = QLabel("Disconnected")
        self.status_label.setStyleSheet("color: red;")
        layout.addWidget(self.status_label)

        # Message List
        self.msg_list = QListWidget()
        layout.addWidget(self.msg_list)

        # Menu
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.open_settings)
        file_menu.addAction(settings_action)

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.quit_app)
        file_menu.addAction(exit_action)

        # System Tray
        self.setup_tray()

        # Client
        self.client = None
        self.init_client()

    def setup_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon(self.icon_path))

        tray_menu = QMenu()
        show_action = QAction("Show", self)
        show_action.triggered.connect(self.show_window)
        tray_menu.addAction(show_action)

        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.quit_app)
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.tray_activated)
        self.tray_icon.show()

    def tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            if self.isVisible():
                self.hide()
            else:
                self.show_window()

    def init_client(self):
        c = config.load_config()
        if c["url"] and c["token"]:
            self.connect_gotify(c["url"], c["token"])
        else:
            self.open_settings()

    def open_settings(self):
        dialog = ConfigDialog(self)
        if dialog.exec():
            c = config.load_config()
            self.connect_gotify(c["url"], c["token"])

    def connect_gotify(self, url, token):
        if self.client:
            self.client.disconnect()
        
        self.client = GotifyClient(url, token)
        self.client.message_received.connect(self.on_message)
        self.client.connection_status.connect(self.on_status_change)
        self.client.connect()

    def on_status_change(self, connected):
        if connected:
            self.status_label.setText("Connected")
            self.status_label.setStyleSheet("color: green;")
        else:
            self.status_label.setText("Disconnected")
            self.status_label.setStyleSheet("color: red;")

    def on_message(self, data):
        title = data.get("title", "Gotify")
        message = data.get("message", "")
        formatted = f"{title}: {message}"
        self.msg_list.addItem(formatted)
        
        # Show system notification via Tray
        self.tray_icon.showMessage(title, message, QSystemTrayIcon.MessageIcon.Information, 3000)

    def show_window(self):
        self.show()
        self.activateWindow()

    def closeEvent(self, event):
        # Minimize to tray instead of closing
        event.ignore()
        self.hide()
        self.tray_icon.showMessage("Gotify Client", "Application minimized to tray", QSystemTrayIcon.MessageIcon.Information, 2000)

    def quit_app(self):
        if self.client:
            self.client.disconnect()
        QApplication.quit()
