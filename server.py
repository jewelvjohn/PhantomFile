from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget, QPushButton, QTextEdit
from PySide6.QtCore import Signal
from PySide6.QtWebSockets import QWebSocketServer
from PySide6.QtNetwork import QHostAddress

class ServerWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Server Widget")

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

        # Start the server
        self.server = Server(8080)
        self.server.messageReceived.connect(self.on_message_received)

    def send_message(self):
        # Get the message from the text edit
        message = self.text_edit.toPlainText()

        # Send the message to the server
        self.server.send_message(message)

    def on_message_received(self, message):
        # Append the received message to the text edit
        self.text_edit.append("Received message: " + message)


class Server(QWebSocketServer):
    messageReceived = Signal(str)

    def __init__(self, port, parent=None):
        super().__init__("Server", QWebSocketServer.NonSecureMode, parent)
        self.listen(QHostAddress.Any, port)
        self.newConnection.connect(self.on_new_connection)

    def on_new_connection(self):
        client_socket = self.nextPendingConnection()
        client_socket.textMessageReceived.connect(self.on_text_message_received)
        client_socket.disconnected.connect(self.on_disconnected)

    def on_text_message_received(self, message):
        # Emit the received message signal
        self.messageReceived.emit(message)

    def on_disconnected(self):
        client_socket = self.sender()
        if client_socket:
            client_socket.deleteLater()

if __name__ == "__main__":
    app = QApplication([])
    server_widget = ServerWidget()
    server_widget.show()
    app.exec()