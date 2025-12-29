import sys
import datetime
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import Qt, QObject, pyqtSlot, pyqtSignal, QAbstractListModel, QModelIndex, QUrl
from PyQt6.QtQml import QQmlApplicationEngine

import config
from client import GotifyClient

# Constants for Model Roles
TitleRole = Qt.ItemDataRole.UserRole + 1
MessageRole = Qt.ItemDataRole.UserRole + 2
DateRole = Qt.ItemDataRole.UserRole + 3

class MessageModel(QAbstractListModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.messages = []

    def rowCount(self, parent=QModelIndex()):
        return len(self.messages)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or index.row() >= len(self.messages):
            return None

        msg = self.messages[index.row()]
        if role == TitleRole:
            return msg["title"]
        elif role == MessageRole:
            return msg["message"]
        elif role == DateRole:
            return msg["date"]
        
        return None

    def roleNames(self):
        return {
            TitleRole: b"title",
            MessageRole: b"message",
            DateRole: b"date"
        }

    def add_message(self, title, message):
        self.beginInsertRows(QModelIndex(), 0, 0) # Insert at top
        date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        self.messages.insert(0, {
            "title": title, 
            "message": message,
            "date": date_str
        })
        self.endInsertRows()

class Backend(QObject):
    connectionStatusChanged = pyqtSignal(bool, arguments=['connected'])
    minimizeRequested = pyqtSignal()

    def __init__(self, model):
        super().__init__()
        self.model = model
        self.client = None
        self.init_client()

    @pyqtSlot()
    def minimize_window(self):
        self.minimizeRequested.emit()

    def init_client(self):
        c = config.load_config()
        if c.get("url") and c.get("token"):
            self.connect_gotify(c["url"], c["token"])

    @pyqtSlot(result='QVariantMap')
    def get_settings(self):
        c = config.load_config()
        return {
            "url": c.get("url", ""),
            "token": c.get("token", "")
        }

    @pyqtSlot(str, str)
    def save_settings(self, url, token):
        config.save_config(url.strip(), token.strip())
        self.connect_gotify(url.strip(), token.strip())

    def connect_gotify(self, url, token):
        if self.client:
            self.client.disconnect()
        
        self.client = GotifyClient(url, token)
        self.client.message_received.connect(self.on_message)
        self.client.connection_status.connect(self.on_status_change)
        self.client.connect()

    def on_status_change(self, connected):
        self.connectionStatusChanged.emit(connected)

    def on_message(self, data):
        title = data.get("title", "Gotify")
        message = data.get("message", "")
        self.model.add_message(title, message)
        
        if hasattr(self, 'tray_callback'):
            self.tray_callback(title, message)

class GotifyApplication(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.setQuitOnLastWindowClosed(False)
        
        self.icon_path = "gotify.png"
        self.setWindowIcon(QIcon(self.icon_path))

        # Model & Backend
        self.message_model = MessageModel()
        self.backend = Backend(self.message_model)
        self.backend.tray_callback = self.show_tray_notification
        self.backend.minimizeRequested.connect(self.on_minimize_requested)

        # QML Engine
        self.engine = QQmlApplicationEngine()
        self.engine.rootContext().setContextProperty("backend", self.backend)
        self.engine.rootContext().setContextProperty("messageModel", self.message_model)
        
        self.engine.load(QUrl.fromLocalFile("main.qml"))

        if not self.engine.rootObjects():
            sys.exit(-1)
            
        self.main_window = self.engine.rootObjects()[0]
        
        # System Tray
        self.setup_tray()

    def on_minimize_requested(self):
        self.main_window.hide()
        self.tray_icon.showMessage("Gotify Client", "Application minimized to tray", QSystemTrayIcon.MessageIcon.Information, 2000)

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
            if self.main_window.isVisible():
                self.main_window.hide()
            else:
                self.show_window()

    def show_tray_notification(self, title, message):
        self.tray_icon.showMessage(title, message, QSystemTrayIcon.MessageIcon.Information, 3000)

    def show_window(self):
        self.main_window.show()
        self.main_window.requestActivate()

    def on_window_closing(self, close):
        # close is a QQuickCloseEvent
        # In newer Qt versions (Qt 6), we might need to handle this differently
        # But for QML ApplicationWindow, 'closing' signal is standard.
        # We want to minimize instead of actually closing.
        close.accepted = False
        self.main_window.hide()
        self.tray_icon.showMessage("Gotify Client", "Application minimized to tray", QSystemTrayIcon.MessageIcon.Information, 2000)

    def quit_app(self):
        if self.backend.client:
            self.backend.client.disconnect()
        self.quit()

if __name__ == "__main__":
    app = GotifyApplication(sys.argv)
    sys.exit(app.exec())
