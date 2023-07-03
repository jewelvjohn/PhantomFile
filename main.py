import os
import sys
import tqdm
import time
import socket

from PySide6.QtWidgets import (QApplication, QWidget, 
                               QLabel, QPushButton, 
                               QVBoxLayout, QHBoxLayout, 
                               QTextEdit, QStackedLayout)
from PySide6.QtCore import Qt

class MainWindow(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.resize(640, 480)
        self.setWindowTitle("Stratosphere AI")
        self.setStyleSheet("QWidget {background: rgb(40, 40, 40);}")

        self.initialize_ui()

    def initialize_ui(self):
        # Openning UI

        self.stacked_layout = QStackedLayout()

        intro_widget = self.intro_ui()
        self.stacked_layout.addWidget(intro_widget)

        send_widget = self.send_ui()
        self.stacked_layout.addWidget(send_widget)

        # recieve_widget = self.send_ui()
        # self.stacked_layout.addWidget(recieve_widget)

        self.main_layout = QVBoxLayout()
        self.main_layout.addLayout(self.stacked_layout)

        self.setLayout(self.main_layout)

    def intro_page(self):
        self.stacked_layout.setCurrentIndex(0)

    def send_page(self):
        self.stacked_layout.setCurrentIndex(1)

    def intro_ui(self):
        client_header = QLabel("Client")
        client_header.setStyleSheet(
                                    """
                                    QLabel
                                    {
                                        color: #CCCCCC; 
                                        font-size: 15px; 
                                        font-weight: 850;
                                        padding: 8px 8px;
                                    }
                                    """
                                )
        client_header.setAlignment(Qt.AlignCenter)

        server_header = QLabel("Server")
        server_header.setStyleSheet(
                                    """
                                    QLabel
                                    {
                                        color: #CCCCCC; 
                                        font-size: 15px; 
                                        font-weight: 850;
                                        padding: 8px 8px;
                                    }
                                    """
                                )
        server_header.setAlignment(Qt.AlignCenter)
        
        send_button = QPushButton("SEND")
        send_button.setFixedSize(200, 80)
        send_button.clicked.connect(self.send_page)
        send_button.setStyleSheet(
                                    """
                                    QPushButton {
                                        font-size: 15px;
                                        font-weight: 800;
                                        background-color: #335033;
                                        border: 0px solid #555555;
                                        border-radius: 5px;
                                        color: #CCCCCC;
                                        padding: 8px 8px;
                                    }
                                    
                                    QPushButton:hover {
                                        background-color: #151515;
                                        border: 1px solid #555555;
                                    }
                                    
                                    QPushButton:pressed {
                                        background-color: #444444;
                                        border: 2px solid #777777;
                                    }
                                    """
                                )
        
        recieve_button = QPushButton("RECIEVE")
        recieve_button.setFixedSize(200, 80)
        # recieve_button.clicked.connect(self.recieve_ui)
        recieve_button.setStyleSheet(
                                    """
                                    QPushButton {
                                        font-size: 15px;
                                        font-weight: 800;
                                        background-color: #335033;
                                        border: 0px solid #555555;
                                        border-radius: 5px;
                                        color: #CCCCCC;
                                        padding: 8px 8px;
                                    }
                                    
                                    QPushButton:hover {
                                        background-color: #151515;
                                        border: 1px solid #555555;
                                    }
                                    
                                    QPushButton:pressed {
                                        background-color: #444444;
                                        border: 2px solid #777777;
                                    }
                                    """
                                )

        send_button_layout = QVBoxLayout()
        send_button_layout.setAlignment(Qt.AlignCenter)
        send_button_layout.addWidget(client_header)
        send_button_layout.addSpacing(10)
        send_button_layout.addWidget(send_button)

        recieve_button_layout = QVBoxLayout()
        recieve_button_layout.setAlignment(Qt.AlignCenter)
        recieve_button_layout.addWidget(server_header)
        recieve_button_layout.addSpacing(10)
        recieve_button_layout.addWidget(recieve_button)

        intro_layout = QHBoxLayout()
        intro_layout.setAlignment(Qt.AlignCenter)
        intro_layout.addLayout(send_button_layout)
        intro_layout.addSpacing(40)
        intro_layout.addLayout(recieve_button_layout)

        intro_widget = QWidget()
        intro_widget.setLayout(intro_layout)

        return intro_widget

    def send_ui(self):
        header = QLabel("Select file")
        header.setStyleSheet(
                                    """
                                    QLabel
                                    {
                                        color: #CCCCCC; 
                                        font-size: 15px; 
                                        font-weight: 850;
                                        padding: 8px 8px;
                                    }
                                    """
                                )
        header.setAlignment(Qt.AlignCenter)

        self.file_textbox = QTextEdit()
        self.file_textbox.setMaximumHeight(50)
        self.file_textbox.setStyleSheet(
                                    """
                                    QTextEdit
                                    {
                                        background-color: #151515; 
                                        color: #CCCCCC; 
                                        border-radius: 10px; 
                                        padding: 8px 8px;
                                    }
                                    """
                                )
        
        back_button = QPushButton("BACK")
        back_button.setFixedSize(130, 40)
        back_button.clicked.connect(self.intro_page)
        back_button.setStyleSheet(
                                    """
                                    QPushButton {
                                        font-size: 15px;
                                        font-weight: 800;
                                        background-color: #335033;
                                        border: 0px solid #555555;
                                        border-radius: 5px;
                                        color: #CCCCCC;
                                        padding: 8px 8px;
                                    }
                                    
                                    QPushButton:hover {
                                        background-color: #151515;
                                        border: 1px solid #555555;
                                    }
                                    
                                    QPushButton:pressed {
                                        background-color: #444444;
                                        border: 2px solid #777777;
                                    }
                                    """
                                )
        
        send_button = QPushButton("SEND")
        send_button.setFixedSize(130, 40)
        # send_button.clicked.connect(self.disconnect)
        send_button.setStyleSheet(
                                    """
                                    QPushButton {
                                        font-size: 15px;
                                        font-weight: 800;
                                        background-color: #335033;
                                        border: 0px solid #555555;
                                        border-radius: 5px;
                                        color: #CCCCCC;
                                        padding: 8px 8px;
                                    }
                                    
                                    QPushButton:hover {
                                        background-color: #151515;
                                        border: 1px solid #555555;
                                    }
                                    
                                    QPushButton:pressed {
                                        background-color: #444444;
                                        border: 2px solid #777777;
                                    }
                                    """
                                )

        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignCenter)
        button_layout.addWidget(back_button)
        button_layout.addSpacing(20)
        button_layout.addWidget(send_button)

        send_layout = QVBoxLayout()
        send_layout.addWidget(header)
        send_layout.addWidget(self.file_textbox)
        send_layout.addSpacing(10)
        send_layout.addLayout(button_layout)

        send_widget = QWidget()
        send_widget.setLayout(send_layout)

        return send_widget

    # Sender
    def send(self, host: str, port: int, file_path: str):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        file = open(file_path, "rb")

        while True:
            try:
                client.connect((host, port))
                print("Connected to server")
                break
            except ConnectionRefusedError:
                print("Connection refused. Retrying in 2 seconds...")
                time.sleep(2)

        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)


        (tm_year, tm_mon, tm_mday, tm_hour, tm_min, tm_sec, tm_wday, tmyday, tm_isdst) = time.localtime()
        name_mark = "PF ["+ str(tm_mday) +"-"+ str(tm_mon) +"-"+ str(tm_year) +"]" + "["+ str(tm_hour) +"-"+ str(tm_min) +"-"+ str(tm_sec) +"] "

        reciever_file = name_mark + file_name

        client.send(reciever_file.encode())
        client.send(str(file_size).encode())

        data = file.read()
        client.sendall(data)

        client.close()
        file.close()

    # Reciever
    def recieve(self, host: str, port: int):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((host, port))
        server.listen()

        print("Server listening on {}:{}".format(host, port))
        client, client_addr = server.accept()

        print("Client connected: ", client_addr)

        file_name = client.recv(1024).decode()
        file_size = client.recv(1024).decode()
        file_dir = input("Enter the save path: ")
        file_dir = file_dir + file_name

        done = False

        progress = tqdm.tqdm(unit="B", unit_scale=True, unit_divisor=1000, total=int(file_size))
        progress_percentage = 0

        while not done:
            data = client.recv(1024)
            if progress_percentage >= 100:
                print("Successfully recieved")

                done = True
            else:
                with open(file_dir, 'ab') as file:
                    file.write(data)
            progress.update(1024)
            progress_percentage = (progress.n / progress.total) * 100

        client.close()
        server.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow(app)
    window.show()
    app.exec()