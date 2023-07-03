from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget, QPushButton, QTextEdit
from PySide6.QtWebSockets import QWebSocket
from PySide6.QtCore import QUrl

class ClientWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Client Widget")

        # Create a text edit widget to display server messages
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)

        # Create a button to send a message to the server
        self.send_button = QPushButton("Send Message")
        self.send_button.clicked.connect(self.send_message)

        # Layout the widgets
        layout = QVBoxLayout()
        layout.addWidget(self.text_edit)
        layout.addWidget(self.send_button)
        self.setLayout(layout)

        # Connect to the server
        self.client = QWebSocket()
        self.client.connected.connect(self.on_connected)
        self.client.textMessageReceived.connect(self.on_text_message_received)
        self.client.disconnected.connect(self.on_disconnected)
        self.client.open(QUrl("ws://localhost:8080"))

    def send_message(self):
        # Get the message from the text edit
        message = self.text_edit.toPlainText()

        # Send the message to the server
        self.client.sendTextMessage(message)

    def on_connected(self):
        self.text_edit.append("Connected to server")

    def on_text_message_received(self, message):
        self.text_edit.append("Received message: " + message)

    def on_disconnected(self):
        self.text_edit.append("Disconnected from server")


if __name__ == "__main__":
    app = QApplication([])
    client_widget = ClientWidget()
    client_widget.show()
    app.exec()