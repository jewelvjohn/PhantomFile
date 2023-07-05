import os
import sys
import cv2
import tqdm
import time
import socket

from PySide6.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, 
                               QVBoxLayout, QHBoxLayout, QTextEdit, QStackedLayout,
                               QFileDialog, QFileDialog, QFileIconProvider, 
                               QSizePolicy, QGraphicsView, QGraphicsScene, 
                               QGraphicsPixmapItem, QProgressBar)
from PySide6.QtGui import QIcon, QPixmap, QPainter, QImage, QColor, QMouseEvent, QTransform
from PySide6.QtCore import Qt, QFileInfo, QThread, Signal, QPoint, QTimer

class RotatingImage(QGraphicsView):
    steps = 1
    interval = 10

    def __init__(self, image: str, w: int, h: int, steps=None, interval=None):
        super().__init__()

        if steps is not None:
            self.steps = steps

        if interval is not None:
            self.interval = interval

        self.scene = QGraphicsScene()
        self.setScene(self.scene)

        self.pixmap_item = QGraphicsPixmapItem()
        self.pixmap_item.setTransformationMode(Qt.SmoothTransformation)
        self.pixmap_item.setShapeMode(QGraphicsPixmapItem.BoundingRectShape)
        self.scene.addItem(self.pixmap_item)

        pixmap = QPixmap(image).scaled(w, h, Qt.AspectRatioMode.KeepAspectRatio, Qt.SmoothTransformation)
        self.pixmap_item.setPixmap(pixmap)

        self.start_animation()

    def start_animation(self):
        self.rotation_angle = 0
        self.rotation_timer = QTimer()
        self.rotation_timer.timeout.connect(self.update_rotation)
        self.rotation_timer.start(self.interval)  # Adjust the interval (in milliseconds) to control the rotation speed

    def update_rotation(self):
        self.rotation_angle += self.steps
        pixmap_width = self.pixmap_item.pixmap().width()
        pixmap_height = self.pixmap_item.pixmap().height()
        transform = QTransform().translate(pixmap_width / 2, pixmap_height / 2).rotate(self.rotation_angle).translate(-pixmap_width / 2, -pixmap_height / 2)
        self.pixmap_item.setTransform(transform)

    def stop_animation(self):
        self.rotation_timer.stop()

class Progressbar_Widget(QWidget):
    def __init__(self):
        super().__init__()

        self.current_data = QLabel("0 B")
        self.maximum_data = QLabel("0 B")
        self.percentage = QLabel("0 %")
        self.progressbar = QProgressBar()
        self.file_size = 0

        self.percentage.setAlignment(Qt.AlignLeft)
        self.percentage.setStyleSheet(
            """
                QLabel
                {
                    color: #CCCCCC;
                    font-size: 16px;
                    font-weight: 650;
                }
            """
        )

        self.current_data.setAlignment(Qt.AlignRight)
        self.current_data.setStyleSheet(
            """
                QLabel
                {
                    color: #CCCCCC;
                    font-size: 16px;
                    font-weight: 650;
                }
            """
        )

        self.maximum_data.setAlignment(Qt.AlignLeft)
        self.maximum_data.setStyleSheet(
            """
                QLabel
                {
                    color: #CCCCCC;
                    font-size: 16px;
                    font-weight: 650;
                }
            """
        )

        self.progressbar.setFixedHeight(20)
        self.progressbar.setRange(0, 100)
        self.progressbar.setValue(0)

        slash = QLabel("/")
        slash.setAlignment(Qt.AlignVCenter)
        slash.setStyleSheet(
            """
                QLabel
                {
                    color: #CCCCCC;
                    font-size: 16px;
                    font-weight: 650;
                }
            """
        )

        data_layout = QHBoxLayout()
        data_layout.addWidget(self.current_data)
        data_layout.setAlignment(self.current_data, Qt.AlignRight | Qt.AlignVCenter)
        data_layout.addWidget(slash)
        data_layout.setAlignment(slash, Qt.AlignVCenter)
        data_layout.addWidget(self.maximum_data)
        data_layout.setAlignment(self.maximum_data, Qt.AlignLeft | Qt.AlignVCenter)

        text_layout = QHBoxLayout()
        text_layout.addSpacing(5)
        text_layout.addWidget(self.percentage)
        text_layout.setAlignment(self.percentage, Qt.AlignBottom | Qt.AlignLeft)
        text_layout.addLayout(data_layout)
        text_layout.setAlignment(data_layout, Qt.AlignBottom | Qt.AlignRight)
        text_layout.addSpacing(5)

        progressbar_layout = QVBoxLayout()
        progressbar_layout.setAlignment(Qt.AlignCenter)
        progressbar_layout.addLayout(text_layout)
        progressbar_layout.addWidget(self.progressbar)

        self.setLayout(progressbar_layout)

    def set_red_theme(self):
        self.progressbar.setStyleSheet(
            """
                QProgressBar 
                {
                    color: transparent;
                    background-color: #151515;
                    border: 1px solid #444444;
                    border-radius: 10px;
                    padding: 5px 5px;
                }
                
                QProgressBar::chunk 
                {
                    background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #AA4040, stop:1 #4040AA);
                    border-radius: 4px;
                }
            """
        )

    def set_green_theme(self):
        self.progressbar.setStyleSheet(
            """
                QProgressBar 
                {
                    color: transparent;
                    background-color: #151515;
                    border: 1px solid #444444;
                    border-radius: 10px;
                    padding: 5px 5px;
                }
                
                QProgressBar::chunk 
                {
                    background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #7010AA, stop:1 #40AA40);
                    border-radius: 4px;
                }
            """
        )

    def set_progress(self, value):
        if value <= self.progressbar.maximum():    
            self.progressbar.setValue(value)
            self.percentage.setText(str(value) + " %")

    def set_maximum_data(self, value):
        self.file_size = value
        file_size = self.format_file_size(value)
        self.maximum_data.setText(file_size)

    def set_current_data(self, value):
        file_size = self.format_file_size(value)
        self.current_data.setText(file_size)

        if self.file_size:
            percentage = (value / self.file_size) * 100
            percentage = round(percentage, 2)
            self.set_progress(percentage)

    @staticmethod
    def format_file_size(size):
        units = ['B', 'KB', 'MB', 'GB', 'TB']
        index = 0
        while size >= 1024 and index < len(units) - 1:
            size /= 1024
            index += 1
        return f"{size:.2f} {units[index]}"

class SenderThread(QThread):
    connectionEstablished = Signal()
    progressChanged = Signal(int)
    fileRecieved = Signal()
    fileSend = Signal()

    def __init__(self, host: str, port: int, file_path: str):
        super().__init__()

        self.host = host
        self.port = port
        self.file_path = file_path
        self.stop_request = False

    def stop(self):
        self.stop_request = True

    def run(self):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        file = open(self.file_path, "rb")

        while True:
            if self.stop_request:
                return
            try:
                client.connect((self.host, self.port))
                self.connectionEstablished.emit()
                break
            except ConnectionRefusedError:
                print("Connection refused. Retrying in 2 seconds...")
                time.sleep(2)

        file_name = os.path.basename(self.file_path)
        file_size = os.path.getsize(self.file_path)


        (tm_year, tm_mon, tm_mday, tm_hour, tm_min, tm_sec, _, _, _) = time.localtime()
        name_mark = "PF ["+ str(tm_mday) +"-"+ str(tm_mon) +"-"+ str(tm_year) +"]" + "["+ str(tm_hour) +"-"+ str(tm_min) +"-"+ str(tm_sec) +"] "

        reciever_file = name_mark + file_name

        client.send(reciever_file.encode())
        client.send(str(file_size).encode())

        data = file.read()
        client.sendall(data)
        self.fileSend.emit()

        client.close()
        file.close()

        # self.progressChanged.emit(i)
        self.fileRecieved.emit() 

class ReceiverThread(QThread):
    connectionEstablished = Signal()
    progressChanged = Signal(int)
    fileRecieved = Signal()
    fileSize = Signal(int)

    def __init__(self, host: str, port: int, file_path: str):
        super().__init__()
        self.host = host
        self.port = port
        self.file_path = file_path

    def run(self):
        os.makedirs(self.file_path, exist_ok=True)

        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.host, self.port))
        server.listen()

        print("Server listening on {}:{}".format(self.host, self.port))
        client, client_addr = server.accept()

        print("Client connected: ", client_addr)
        self.connectionEstablished.emit()

        file_name = client.recv(1024).decode()
        file_size = int(client.recv(1024).decode())
        self.file_path = self.file_path + "/" + file_name

        self.fileSize.emit(file_size)

        done = False

        progress = tqdm.tqdm(unit="B", unit_scale=True, unit_divisor=1000, total=int(file_size))
        progress_percentage = 0

        while not done:
            data = client.recv(1024)
            if progress_percentage >= 100:
                print("Successfully recieved")

                done = True
            else:
                with open(self.file_path, 'ab') as file:
                    file.write(data)
            progress.update(1024)
            progress_percentage = (progress.n / progress.total) * 100
            self.progressChanged.emit(progress.pos)

        client.close()
        server.close()

        self.fileRecieved.emit()

class MainWindow(QWidget):
    save_path = str()
    sending_file_path = str()

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.setFixedSize(650, 400)
        self.setWindowFlags(Qt.FramelessWindowHint)

        self.draggable_area = self.rect()
        self.offset = QPoint()
        self.dragging = False
        self.draggable = True

        self.initialize_ui()
        self.initialize_settings()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton and self.draggable and self.draggable_area.contains(event.position().toPoint()):
            self.dragging = True
            self.offset = event.position().toPoint()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.dragging:
            self.move(self.mapToParent(event.position().toPoint() - self.offset))

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton and self.dragging:
            self.dragging = False

    def initialize_settings(self):
        self.settings_path = "files/settings.jwl"
        if(os.path.isfile(self.settings_path)):
            with open(self.settings_path, 'r') as file:
                data = file.read()
                if(data == ""):
                    self.reset_settings()
                else:
                    self.refresh_settings()
        else:
            self.reset_settings()

    def reset_settings(self):
        home = os.path.expanduser("~")
        home = home.replace("\\", '/')
        saves = home +"/"+ "Downloads/Phantom Files"
        os.makedirs(saves, exist_ok=True)

        self.host = "127.0.0.1"
        self.port = 9999
        self.save_path = saves

        data = f"{self.host},{self.port},{self.save_path}"

        with open(self.settings_path, "w") as file:
            file.write(data)
        self.refresh_settings()

    def update_settings(self):
        ip_addr = self.host_textbox.toPlainText()
        port = int(self.port_textbox.toPlainText())
        save_path = self.saves_textbox.toPlainText()

        data = f"{ip_addr},{port},{save_path}"

        with open(self.settings_path, "w") as file:
            file.write(data)
        self.refresh_settings()
        self.main_page()

    def refresh_settings(self):
        with open(self.settings_path, 'r') as file:
            data = file.read()
            addr, port, saves = data.split(",")
            os.makedirs(saves, exist_ok=True)

            self.host = addr
            self.port = int(port)
            self.save_path = saves

            self.host_textbox.setPlainText(self.host)
            self.port_textbox.setPlainText(str(self.port))
            self.saves_textbox.setPlainText(self.save_path)

    def initialize_ui(self):
        self.setStyleSheet(
                                """
                                QWidget 
                                {
                                    background-color: #282828;
                                }
                                """
                            )
        
        titlebar = self.titlebar_ui()
        self.draggable_area = titlebar.rect()

        self.stacked_layout = QStackedLayout()

        intro_widget = self.main_ui()
        self.stacked_layout.addWidget(intro_widget)

        settings_widget = self.settings_ui()
        self.stacked_layout.addWidget(settings_widget)

        send_widget = self.sender_ui()
        self.stacked_layout.addWidget(send_widget)

        sending_widget = self.sending_ui()
        self.sender_connecting_state()
        self.stacked_layout.addWidget(sending_widget)

        receiver_widget = self.receiver_ui()
        self.stacked_layout.addWidget(receiver_widget)

        # recieve_widget = self.send_ui()
        # self.stacked_layout.addWidget(recieve_widget)

        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(titlebar)
        self.main_layout.addLayout(self.stacked_layout)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(self.main_layout)

    def main_page(self):
        self.stacked_layout.setCurrentIndex(0)

    def settings_page(self):
        self.refresh_settings()
        self.stacked_layout.setCurrentIndex(1)

    def sender_page(self):
        self.stacked_layout.setCurrentIndex(2)

    def sending_page(self):
        self.sender_connecting_state()
        self.stacked_layout.setCurrentIndex(3)

    def receiver_page(self):
        self.receiver_connecting_state()
        self.stacked_layout.setCurrentIndex(4)

    def titlebar_ui(self):
        app_icon = QPixmap("files/icon.png")
        app_icon = app_icon.scaled(30, 30, Qt.AspectRatioMode.KeepAspectRatio, Qt.SmoothTransformation)

        icon_label = QLabel()
        icon_label.setPixmap(app_icon)
        icon_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        title_label = QLabel("Phantom File")
        title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        title_label.setStyleSheet(
                                    """
                                    QLabel
                                    {
                                        color: #CCCCCC; 
                                        font-size: 16px; 
                                        font-weight: 550;
                                    }
                                    """
                                )

        close_icon = QPixmap("files/close.png")

        close_button = QPushButton()
        close_button.setIcon(close_icon)
        close_button.setFixedSize(20, 20)
        close_button.clicked.connect(self.close)
        close_button.setStyleSheet(
                                    """
                                    QPushButton {
                                        font-size: 15px;
                                        font-weight: 800;
                                        padding: 8px 8px;
                                        border-radius: 5px;

                                        background-color: #151515;
                                        border: 1px solid #555555;
                                        color: #CCCCCC;
                                    }
                                    
                                    QPushButton:hover {
                                        background-color: #AA4040;
                                        border: 0px solid #555555;
                                        color: #101010;
                                    }
                                    
                                    QPushButton:pressed {
                                        background-color: #444444;
                                        border: 2px solid #777777;
                                        color: #CCCCCC;
                                    }
                                    """
                                )

        minimize_icon = QPixmap("files/minimize.png")

        minimize_button = QPushButton()
        minimize_button.setIcon(minimize_icon)
        minimize_button.setFixedSize(20, 20)
        minimize_button.clicked.connect(self.showMinimized)
        minimize_button.setStyleSheet(
                                    """
                                    QPushButton {
                                        font-size: 15px;
                                        font-weight: 800;
                                        padding: 8px 8px;
                                        border-radius: 5px;

                                        background-color: #151515;
                                        border: 1px solid #555555;
                                        color: #CCCCCC;
                                    }
                                    
                                    QPushButton:hover {
                                        background-color: #80AA80;
                                        border: 0px solid #555555;
                                        color: #101010;
                                    }
                                    
                                    QPushButton:pressed {
                                        background-color: #444444;
                                        border: 2px solid #777777;
                                        color: #CCCCCC;
                                    }
                                    """
                                )

        title_layout = QHBoxLayout()
        title_layout.addWidget(icon_label)
        title_layout.setAlignment(icon_label, Qt.AlignRight | Qt.AlignVCenter)
        title_layout.addSpacing(5)
        title_layout.addWidget(title_label)
        title_layout.setAlignment(title_label, Qt.AlignLeft | Qt.AlignVCenter)

        button_layout = QHBoxLayout()
        button_layout.addWidget(minimize_button)
        button_layout.setAlignment(minimize_button, Qt.AlignRight | Qt.AlignVCenter)
        button_layout.addSpacing(5)
        button_layout.addWidget(close_button)
        button_layout.setAlignment(close_button, Qt.AlignLeft | Qt.AlignVCenter)

        titlebar_layout = QHBoxLayout()
        titlebar_layout.addSpacing(5)
        titlebar_layout.addLayout(title_layout)
        titlebar_layout.setAlignment(title_layout, Qt.AlignLeft | Qt.AlignVCenter)
        titlebar_layout.addLayout(button_layout)
        titlebar_layout.setAlignment(button_layout, Qt.AlignRight | Qt.AlignVCenter)
        titlebar_layout.addSpacing(5)

        titlebar_widget = QWidget()
        titlebar_widget.setFixedHeight(40)
        titlebar_widget.setLayout(titlebar_layout)
        titlebar_widget.setStyleSheet(
                                        """
                                            QWidget {
                                                border-radius: 0px;
                                                background-color: #151515;
                                            }
                                        """
                                    )

        return titlebar_widget

    def main_ui(self):
        dummy_header = QLabel("")
        dummy_header.setAlignment(Qt.AlignRight)

        client_header = QLabel("(Client)")
        client_header.setStyleSheet(
                                    """
                                    QLabel
                                    {
                                        color: #808080; 
                                        font-size: 15px; 
                                        font-weight: 600;
                                        padding: 8px 8px;
                                    }
                                    """
                                )
        client_header.setAlignment(Qt.AlignCenter)

        server_header = QLabel("(Server)")
        server_header.setStyleSheet(
                                    """
                                    QLabel
                                    {
                                        color: #808080; 
                                        font-size: 15px; 
                                        font-weight: 600;
                                        padding: 8px 8px;
                                    }
                                    """
                                )
        server_header.setAlignment(Qt.AlignCenter)
        
        settings_icon = QPixmap("files/gear.png")

        settings_button = QPushButton()
        settings_button.setIcon(settings_icon)
        settings_button.clicked.connect(self.settings_page)
        settings_button.setStyleSheet(
                                    """
                                    QPushButton {
                                        font-size: 15px;
                                        font-weight: 800;
                                        padding: 8px 8px;
                                        border-radius: 5px;

                                        background-color: #151515;
                                        border: 1px solid #555555;
                                        color: #CCCCCC;
                                    }
                                    
                                    QPushButton:hover {
                                        background-color: #80AA80;
                                        border: 0px solid #555555;
                                        color: #101010;
                                    }
                                    
                                    QPushButton:pressed {
                                        background-color: #444444;
                                        border: 2px solid #777777;
                                        color: #CCCCCC;
                                    }
                                    """
                                )

        sender_button = QPushButton("SENDER")
        sender_button.setFixedSize(200, 80)
        sender_button.clicked.connect(self.sender_page)
        sender_button.setStyleSheet(
                                    """
                                    QPushButton {
                                        font-size: 15px;
                                        font-weight: 800;
                                        padding: 8px 8px;
                                        border-radius: 5px;

                                        background-color: #151515;
                                        border: 1px solid #555555;
                                        color: #CCCCCC;
                                    }
                                    
                                    QPushButton:hover {
                                        background-color: #AA8080;
                                        border: 0px solid #555555;
                                        color: #101010;
                                    }
                                    
                                    QPushButton:pressed {
                                        background-color: #444444;
                                        border: 2px solid #777777;
                                        color: #CCCCCC;
                                    }
                                    """
                                )
        
        receiver_button = QPushButton("RECEIVER")
        receiver_button.setFixedSize(200, 80)
        receiver_button.clicked.connect(self.receive)
        receiver_button.setStyleSheet(
                                    """
                                    QPushButton {
                                        font-size: 15px;
                                        font-weight: 800;
                                        padding: 8px 8px;
                                        border-radius: 5px;

                                        background-color: #151515;
                                        border: 1px solid #555555;
                                        color: #CCCCCC;
                                    }
                                    
                                    QPushButton:hover {
                                        background-color: #8080AA;
                                        border: 0px solid #555555;
                                        color: #101010;
                                    }
                                    
                                    QPushButton:pressed {
                                        background-color: #444444;
                                        border: 2px solid #777777;
                                        color: #CCCCCC;
                                    }
                                    """
                                )

        note = QLabel("Note - Generally server side runs first, even though this application is designed to handle any order of execution")
        note.setStyleSheet(
                                    """
                                    QLabel
                                    {
                                        color: #808080; 
                                        font-size: 15px; 
                                        font-weight: 600;
                                        padding: 8px 8px;
                                    }
                                    """
                                )
        note.setAlignment(Qt.AlignCenter)
        note.setWordWrap(True)

        send_button_layout = QVBoxLayout()
        send_button_layout.setAlignment(Qt.AlignCenter)
        send_button_layout.addWidget(sender_button)
        send_button_layout.addWidget(client_header)

        receive_button_layout = QVBoxLayout()
        receive_button_layout.setAlignment(Qt.AlignCenter)
        receive_button_layout.addWidget(receiver_button)
        receive_button_layout.addWidget(server_header)

        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignCenter)
        button_layout.addLayout(send_button_layout)
        button_layout.addSpacing(20)
        button_layout.addLayout(receive_button_layout)

        header_layout = QHBoxLayout()
        header_layout.addWidget(settings_button)
        header_layout.addWidget(dummy_header)
        header_layout.setAlignment(settings_button, Qt.AlignLeft)
        header_layout.setAlignment(dummy_header, Qt.AlignRight)

        main_layout = QVBoxLayout()
        main_layout.addLayout(header_layout)
        main_layout.setAlignment(header_layout, Qt.AlignTop)
        main_layout.addSpacing(20)
        main_layout.addLayout(button_layout)
        main_layout.setAlignment(button_layout, Qt.AlignCenter)
        main_layout.addSpacing(20)
        main_layout.addWidget(note)
        main_layout.setAlignment(note, Qt.AlignBottom)

        main_widget = QWidget()
        main_widget.setLayout(main_layout)

        return main_widget

    def settings_ui(self):
        header = QLabel("Settings")
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet(
                                    """
                                    QLabel
                                    {
                                        color: #CCCCCC; 
                                        font-size: 20px; 
                                        font-weight: 600;
                                        padding: 8px 8px;
                                    }
                                    """
                                )

        saves_button = QPushButton("...")
        saves_button.setFixedSize(45, 45)
        saves_button.clicked.connect(self.saves_folder_dialog)
        saves_button.setStyleSheet(
                                    """
                                    QPushButton {
                                        font-size: 15px;
                                        font-weight: 800;
                                        padding: 8px 8px;
                                        border-radius: 5px;

                                        background-color: #151515;
                                        border: 1px solid #555555;
                                        color: #CCCCCC;
                                    }
                                    
                                    QPushButton:hover {
                                        background-color: #80AA80;
                                        border: 0px solid #555555;
                                        color: #101010;
                                    }
                                    
                                    QPushButton:pressed {
                                        background-color: #444444;
                                        border: 2px solid #777777;
                                        color: #CCCCCC;
                                    }
                                    """
                                )

        cancel_button = QPushButton("CANCEL")
        cancel_button.setFixedSize(130, 40)
        cancel_button.clicked.connect(self.main_page)
        cancel_button.setStyleSheet(
                                    """
                                    QPushButton {
                                        font-size: 15px;
                                        font-weight: 800;
                                        padding: 8px 8px;
                                        border-radius: 5px;

                                        background-color: #151515;
                                        border: 1px solid #555555;
                                        color: #CCCCCC;
                                    }
                                    
                                    QPushButton:hover {
                                        background-color: #80AA80;
                                        border: 0px solid #555555;
                                        color: #101010;
                                    }
                                    
                                    QPushButton:pressed {
                                        background-color: #444444;
                                        border: 2px solid #777777;
                                        color: #CCCCCC;
                                    }
                                    """
                                )
        
        apply_button = QPushButton("ACCEPT")
        apply_button.setFixedSize(130, 40)
        apply_button.clicked.connect(self.update_settings)
        apply_button.setStyleSheet(
                                    """
                                    QPushButton {
                                        font-size: 15px;
                                        font-weight: 800;
                                        padding: 8px 8px;
                                        border-radius: 5px;

                                        background-color: #151515;
                                        border: 1px solid #555555;
                                        color: #CCCCCC;
                                    }
                                    
                                    QPushButton:hover {
                                        background-color: #80AA80;
                                        border: 0px solid #555555;
                                        color: #101010;
                                    }
                                    
                                    QPushButton:pressed {
                                        background-color: #444444;
                                        border: 2px solid #777777;
                                        color: #CCCCCC;
                                    }
                                    """
                                )

        saves_caption = QLabel("Save Location")
        saves_caption.setAlignment(Qt.AlignVCenter)
        saves_caption.setFixedWidth(125)
        saves_caption.setStyleSheet(
                                    """
                                    QLabel
                                    {
                                        color: #A0A0A0; 
                                        font-size: 14px; 
                                        font-weight: 500;
                                        padding: 8px 8px;
                                    }
                                    """
                                )

        self.saves_textbox = QTextEdit()
        self.saves_textbox.setAlignment(Qt.AlignCenter)
        self.saves_textbox.setFixedHeight(45)
        self.saves_textbox.setStyleSheet(
                                    """
                                    QTextEdit
                                    {
                                        background-color: #202020; 
                                        color: #CCCCCC; 
                                        border: 1px solid #555555;
                                        border-radius: 5px;
                                        padding: 6px 6px;
                                    }
                                    """
                                )

        host_caption = QLabel("Host Address")
        host_caption.setAlignment(Qt.AlignVCenter)
        host_caption.setFixedWidth(120)
        host_caption.setStyleSheet(
                                    """
                                    QLabel
                                    {
                                        color: #A0A0A0; 
                                        font-size: 14px; 
                                        font-weight: 500;
                                        padding: 8px 8px;
                                    }
                                    """
                                )

        self.host_textbox = QTextEdit()
        self.host_textbox.setAlignment(Qt.AlignCenter)
        self.host_textbox.setFixedHeight(45)
        self.host_textbox.setStyleSheet(
                                    """
                                    QTextEdit
                                    {
                                        background-color: #202020; 
                                        color: #CCCCCC; 
                                        border: 1px solid #555555;
                                        border-radius: 5px;
                                        padding: 6px 6px;
                                    }
                                    """
                                )

        port_caption = QLabel("Port Number")
        port_caption.setAlignment(Qt.AlignVCenter)
        port_caption.setFixedWidth(120)
        port_caption.setStyleSheet(
                                    """
                                    QLabel
                                    {
                                        color: #A0A0A0; 
                                        font-size: 14px; 
                                        font-weight: 500;
                                        padding: 8px 8px;
                                    }
                                    """
                                )

        self.port_textbox = QTextEdit()
        self.port_textbox.setAlignment(Qt.AlignCenter)
        self.port_textbox.setFixedHeight(45)
        self.port_textbox.setStyleSheet(
                                    """
                                    QTextEdit
                                    {
                                        background-color: #202020; 
                                        color: #CCCCCC; 
                                        border: 1px solid #555555;
                                        border-radius: 5px;
                                        padding: 6px 6px;
                                    }
                                    """
                                )

        reset_caption = QLabel("Reset")
        reset_caption.setAlignment(Qt.AlignVCenter)
        reset_caption.setFixedWidth(53)
        reset_caption.setStyleSheet(
                                    """
                                    QLabel
                                    {
                                        color: #A0A0A0; 
                                        font-size: 14px; 
                                        font-weight: 500;
                                        padding: 8px 8px;
                                    }
                                    """
                                )

        reset_icon = QPixmap("files/reset.png")

        reset_button = QPushButton()
        reset_button.setIcon(reset_icon)
        reset_button.setFixedSize(30, 30)
        reset_button.clicked.connect(self.reset_settings)
        reset_button.setStyleSheet(
                                    """
                                    QPushButton {
                                        font-size: 15px;
                                        font-weight: 800;
                                        padding: 8px 8px;
                                        border-radius: 5px;

                                        background-color: #151515;
                                        border: 1px solid #555555;
                                        color: #CCCCCC;
                                    }
                                    
                                    QPushButton:hover {
                                        background-color: #80AA80;
                                        border: 0px solid #555555;
                                        color: #101010;
                                    }
                                    
                                    QPushButton:pressed {
                                        background-color: #444444;
                                        border: 2px solid #777777;
                                        color: #CCCCCC;
                                    }
                                    """
                                )
        
        reset_layout = QHBoxLayout()
        reset_layout.addWidget(reset_caption)
        reset_layout.setAlignment(reset_caption, Qt.AlignRight)
        reset_layout.addWidget(reset_button)
        reset_layout.setAlignment(reset_button, Qt.AlignLeft)

        saves_layout = QHBoxLayout()
        saves_layout.addSpacing(5)
        saves_layout.addWidget(saves_caption)
        saves_layout.addWidget(self.saves_textbox)
        saves_layout.addWidget(saves_button)
        saves_layout.addSpacing(5)

        host_layout = QHBoxLayout()
        host_layout.addSpacing(5)
        host_layout.addWidget(host_caption)
        host_layout.addSpacing(5)
        host_layout.addWidget(self.host_textbox)
        host_layout.addSpacing(5)

        port_layout = QHBoxLayout()
        port_layout.addSpacing(5)
        port_layout.addWidget(port_caption)
        port_layout.addSpacing(5)
        port_layout.addWidget(self.port_textbox)
        port_layout.addSpacing(5)

        central_layout = QVBoxLayout()
        central_layout.addLayout(saves_layout)
        central_layout.addLayout(host_layout)
        central_layout.addLayout(port_layout)
        central_layout.addLayout(reset_layout)

        button_layout = QHBoxLayout()
        button_layout.addWidget(cancel_button)
        button_layout.setAlignment(cancel_button, Qt.AlignRight)
        button_layout.addSpacing(20)
        button_layout.addWidget(apply_button)
        button_layout.setAlignment(apply_button, Qt.AlignLeft)

        settings_layout = QVBoxLayout()
        settings_layout.setAlignment(Qt.AlignCenter)
        settings_layout.addWidget(header)
        settings_layout.setAlignment(header, Qt.AlignTop)
        settings_layout.addSpacing(10)
        settings_layout.addLayout(central_layout)
        settings_layout.addSpacing(10)
        settings_layout.addLayout(button_layout)
        settings_layout.setAlignment(button_layout, Qt.AlignBottom)
        settings_layout.addSpacing(10)

        settings_widget = QWidget()
        settings_widget.setLayout(settings_layout)

        return settings_widget

    def sending_ui(self):
        self.sending_header = QLabel("Trying to Connecting")
        self.sending_header.setAlignment(Qt.AlignCenter)
        self.sending_header.setStyleSheet(
                                    """
                                    QLabel
                                    {
                                        color: #CCCCCC; 
                                        font-size: 20px; 
                                        font-weight: 600;
                                        padding: 8px 8px;
                                    }
                                    """
                                )

        cancel_button = QPushButton("CANCEL")
        cancel_button.setFixedSize(130, 40)
        cancel_button.clicked.connect(self.close_sender_thread)
        cancel_button.setStyleSheet(
                                    """
                                    QPushButton {
                                        font-size: 15px;
                                        font-weight: 800;
                                        padding: 8px 8px;
                                        border-radius: 5px;

                                        background-color: #151515;
                                        border: 1px solid #555555;
                                        color: #CCCCCC;
                                    }
                                    
                                    QPushButton:hover {
                                        background-color: #AA8080;
                                        border: 0px solid #555555;
                                        color: #101010;
                                    }
                                    
                                    QPushButton:pressed {
                                        background-color: #444444;
                                        border: 2px solid #777777;
                                        color: #CCCCCC;
                                    }
                                    """
                                )

        self.senter_loading_icon = RotatingImage("files/loading.png", 64, 64, -1, 2)
        self.senter_loading_icon.setFixedSize(96, 96)
        self.senter_loading_icon.setStyleSheet(
            """
                QGraphicsView
                {
                    border: 0px;
                }
            """
        )

        self.sender_progressbar = Progressbar_Widget()
        self.sender_progressbar.set_red_theme()
        self.sender_progressbar.setFixedWidth(500)

        sending_layout = QVBoxLayout()
        sending_layout.addWidget(self.sending_header)
        sending_layout.setAlignment(self.sending_header, Qt.AlignTop | Qt.AlignHCenter)
        sending_layout.addSpacing(10)
        sending_layout.addWidget(self.senter_loading_icon)
        sending_layout.setAlignment(self.senter_loading_icon, Qt.AlignCenter)
        sending_layout.addWidget(self.sender_progressbar)
        sending_layout.setAlignment(self.sender_progressbar, Qt.AlignCenter)
        sending_layout.addSpacing(10)
        sending_layout.addWidget(cancel_button)
        sending_layout.setAlignment(cancel_button, Qt.AlignBottom | Qt.AlignHCenter)
        sending_layout.addSpacing(10)

        sending_widget = QWidget()
        sending_widget.setLayout(sending_layout)

        return sending_widget

    def receiver_ui(self):
        self.receiver_header = QLabel("Trying to Connecting")
        self.receiver_header.setAlignment(Qt.AlignCenter)
        self.receiver_header.setStyleSheet(
                                    """
                                    QLabel
                                    {
                                        color: #CCCCCC; 
                                        font-size: 20px; 
                                        font-weight: 600;
                                        padding: 8px 8px;
                                    }
                                    """
                                )

        cancel_button = QPushButton("CANCEL")
        cancel_button.setFixedSize(130, 40)
        cancel_button.clicked.connect(self.main_page)
        cancel_button.setStyleSheet(
                                    """
                                    QPushButton {
                                        font-size: 15px;
                                        font-weight: 800;
                                        padding: 8px 8px;
                                        border-radius: 5px;

                                        background-color: #151515;
                                        border: 1px solid #555555;
                                        color: #CCCCCC;
                                    }
                                    
                                    QPushButton:hover {
                                        background-color: #AA8080;
                                        border: 0px solid #555555;
                                        color: #101010;
                                    }
                                    
                                    QPushButton:pressed {
                                        background-color: #444444;
                                        border: 2px solid #777777;
                                        color: #CCCCCC;
                                    }
                                    """
                                )

        self.receiver_loading_icon = RotatingImage("files/loading.png", 64, 64, -1, 2)
        self.receiver_loading_icon.setFixedSize(96, 96)
        self.receiver_loading_icon.setStyleSheet(
            """
                QGraphicsView
                {
                    border: 0px;
                }
            """
        )

        self.receiver_progressbar = Progressbar_Widget()
        self.receiver_progressbar.set_green_theme()
        self.receiver_progressbar.setFixedWidth(500)

        receiver_layout = QVBoxLayout()
        receiver_layout.addWidget(self.receiver_header)
        receiver_layout.setAlignment(self.receiver_header, Qt.AlignTop | Qt.AlignHCenter)
        receiver_layout.addSpacing(10)
        receiver_layout.addWidget(self.receiver_loading_icon)
        receiver_layout.setAlignment(self.receiver_loading_icon, Qt.AlignCenter)
        receiver_layout.addWidget(self.receiver_progressbar)
        receiver_layout.setAlignment(self.receiver_progressbar, Qt.AlignCenter)
        receiver_layout.addSpacing(10)
        receiver_layout.addWidget(cancel_button)
        receiver_layout.setAlignment(cancel_button, Qt.AlignBottom | Qt.AlignHCenter)
        receiver_layout.addSpacing(10)

        receiver_widget = QWidget()
        receiver_widget.setLayout(receiver_layout)

        return receiver_widget

    def sender_ui(self):
        header = QLabel("Select file")
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet(
                                    """
                                    QLabel
                                    {
                                        color: #CCCCCC; 
                                        font-size: 20px; 
                                        font-weight: 600;
                                        padding: 8px 8px;
                                    }
                                    """
                                )

        file_button = QPushButton("...")
        file_button.setFixedSize(60, 50)
        file_button.clicked.connect(self.open_file_dialog)
        file_button.setStyleSheet(
                                    """
                                    QPushButton {
                                        font-size: 15px;
                                        font-weight: 800;
                                        padding: 8px 8px;
                                        border-radius: 5px;

                                        background-color: #151515;
                                        border: 1px solid #555555;
                                        color: #CCCCCC;
                                    }
                                    
                                    QPushButton:hover {
                                        background-color: #AA8080;
                                        border: 0px solid #555555;
                                        color: #101010;
                                    }
                                    
                                    QPushButton:pressed {
                                        background-color: #444444;
                                        border: 2px solid #777777;
                                        color: #CCCCCC;
                                    }
                                    """
                                )

        back_button = QPushButton("BACK")
        back_button.setFixedSize(130, 40)
        back_button.clicked.connect(self.main_page)
        back_button.setStyleSheet(
                                    """
                                    QPushButton {
                                        font-size: 15px;
                                        font-weight: 800;
                                        padding: 8px 8px;
                                        border-radius: 5px;

                                        background-color: #151515;
                                        border: 1px solid #555555;
                                        color: #CCCCCC;
                                    }
                                    
                                    QPushButton:hover {
                                        background-color: #AA8080;
                                        border: 0px solid #555555;
                                        color: #101010;
                                    }
                                    
                                    QPushButton:pressed {
                                        background-color: #444444;
                                        border: 2px solid #777777;
                                        color: #CCCCCC;
                                    }
                                    """
                                )
        
        send_button = QPushButton("SEND")
        send_button.setFixedSize(130, 40)
        send_button.clicked.connect(self.send)
        send_button.setStyleSheet(
                                    """
                                    QPushButton {
                                        font-size: 15px;
                                        font-weight: 800;
                                        padding: 8px 8px;
                                        border-radius: 5px;

                                        background-color: #151515;
                                        border: 1px solid #555555;
                                        color: #CCCCCC;
                                    }
                                    
                                    QPushButton:hover {
                                        background-color: #AA8080;
                                        border: 0px solid #555555;
                                        color: #101010;
                                    }
                                    
                                    QPushButton:pressed {
                                        background-color: #444444;
                                        border: 2px solid #777777;
                                        color: #CCCCCC;
                                    }
                                    """
                                )

        self.file_path_label = QLabel("No file selected")
        self.file_path_label.setAlignment(Qt.AlignCenter)
        self.file_path_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.file_path_label.setWordWrap(True)
        self.file_path_label.setStyleSheet(
                                    """
                                    QLabel
                                    {
                                        color: #AAAAAA; 
                                        font-size: 15px; 
                                        font-weight: 500;
                                        padding: 8px 8px;
                                    }
                                    """
                                )
        
        self.file_size_label = QLabel("N/A")
        self.file_size_label.setAlignment(Qt.AlignCenter)
        self.file_size_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.file_size_label.setFixedWidth(96)
        self.file_size_label.setWordWrap(True)
        self.file_size_label.setStyleSheet(
                                    """
                                    QLabel
                                    {
                                        color: #AAAAAA; 
                                        font-size: 15px; 
                                        font-weight: 500;
                                        padding: 8px 8px;
                                    }
                                    """
                                )
        
        self.file_icon_label = QLabel("No File")
        self.file_icon_label.setFixedSize(128, 128)
        self.file_icon_label.setAlignment(Qt.AlignCenter)
        self.file_icon_label.setStyleSheet(
                                    """
                                    QLabel
                                    {
                                        color: #808080; 
                                        background-color: #202020;
                                        border-radius: 8px;
                                        font-size: 14px; 
                                        font-weight: 400;
                                    }
                                    """
                                )

        file_info_layout = QHBoxLayout()
        file_info_layout.setAlignment(Qt.AlignCenter)
        file_info_layout.addSpacing(5)
        file_info_layout.addWidget(self.file_icon_label)
        file_info_layout.addSpacing(5)
        file_info_layout.addWidget(self.file_path_label)
        file_info_layout.addSpacing(5)
        file_info_layout.addWidget(self.file_size_label)
        file_info_layout.addSpacing(5)
        file_info_layout.addWidget(file_button)
        file_info_layout.addSpacing(5)

        file_info_widget = QWidget()
        file_info_widget.setLayout(file_info_layout)
        file_info_widget.setStyleSheet(
                                    """
                                    QWidget
                                    {
                                        background-color: #151515;
                                        border-radius: 8px;
                                    }
                                    """
                                )

        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignCenter)
        button_layout.addWidget(back_button)
        button_layout.addSpacing(20)
        button_layout.addWidget(send_button)

        send_layout = QVBoxLayout()
        send_layout.setAlignment(Qt.AlignCenter)
        send_layout.addWidget(header)
        send_layout.addSpacing(10)
        send_layout.addWidget(file_info_widget)
        send_layout.addSpacing(20)
        send_layout.addLayout(button_layout)
        send_layout.addSpacing(10)

        send_widget = QWidget()
        send_widget.setLayout(send_layout)

        return send_widget

    def saves_folder_dialog(self):
        folder_dialog = QFileDialog()
        folder_path = folder_dialog.getExistingDirectory(None, "Save Location", "/path/to/default/folder")

        if folder_path:
            self.saves_textbox.setPlainText(folder_path)

    def open_file_dialog(self):
        file_dialog = QFileDialog()
        self.sending_file_path, _ = file_dialog.getOpenFileName(
            self, "Open File", "", "All Files (*)"
        )
        if self.sending_file_path:
            self.file_path_label.setText(f"File Path: {self.sending_file_path}")
            file_size = os.path.getsize(self.sending_file_path)
            formatted_size = self.format_file_size(file_size)
            self.file_size_label.setText(f"{formatted_size}")
            self.set_file_icon(self.sending_file_path)

            self.file_path_label.adjustSize()
            self.file_size_label.adjustSize()

    @staticmethod
    def format_file_size(size):
        units = ['bytes', 'KB', 'MB', 'GB', 'TB']
        index = 0
        while size >= 1024 and index < len(units) - 1:
            size /= 1024
            index += 1
        return f"{size:.2f} {units[index]}"

    def set_file_icon(self, file_path):
        icon = QIcon.fromTheme("text-x-generic")  # Default icon if specific icon is not found
        file_info = QFileInfo(file_path)
        if file_info.exists() and file_info.isFile():
            icon_provider = QFileIconProvider()
            icon = icon_provider.icon(file_info)
            self.file_icon_label.setPixmap(icon.pixmap(128, 128))
            self.set_file_preview(file_path)

    def set_file_preview(self, file_path):
        image_extensions = ['png', 'jpg', 'jpeg', 'gif', 'ico', 'webp']
        video_extensions = ['mp4', 'avi', 'mkv']

        file_info = QFileInfo(file_path)
        file_extension = file_info.suffix().lower()

        if file_extension in image_extensions:
            self.show_image_preview(file_path)
        elif file_extension in video_extensions:
            self.show_video_preview(file_path)
        else:
            self.show_default_preview(file_path)

    def show_image_preview(self, file_path):
        image = QImage(file_path)

        width = image.width()
        height = image.height()
        size = min(width, height)

        start_x = (width - size) // 2
        start_y = (height - size) // 2

        cropped_image = QImage(size, size, QImage.Format_RGB32)
        painter = QPainter(cropped_image)
        painter.drawImage(0, 0, image, start_x, start_y, size, size)
        painter.end()

        pixmap = QPixmap.fromImage(cropped_image)
        pixmap = pixmap.scaled(128, 128, Qt.AspectRatioMode.KeepAspectRatio, Qt.SmoothTransformation)

        self.file_icon_label.setPixmap(pixmap)

    def show_video_preview(self, file_path):
        cap = cv2.VideoCapture(file_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        center_frame = total_frames // 4
        cap.set(cv2.CAP_PROP_POS_FRAMES, center_frame)
        _, frame = cap.read()
        cap.release()
        cv2.destroyAllWindows()

        height, width = frame.shape[:2]
        size = min(height, width)
        start_x = (width - size) // 2
        start_y = (height - size) // 2
        frame = frame[start_y:start_y+size, start_x:start_x+size]

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        height, width, channel = rgb_frame.shape
        bytes_per_line = channel * width
        image = QImage(rgb_frame.data, width, height, bytes_per_line, QImage.Format_RGB888)

        pixmap = QPixmap.fromImage(image)
        pixmap = pixmap.scaled(128, 128, Qt.AspectRatioMode.KeepAspectRatio, Qt.SmoothTransformation)
        self.file_icon_label.setPixmap(pixmap)

    def show_default_preview(self, file_path):
        icon = QIcon.fromTheme("text-x-generic")
        file_info = QFileInfo(file_path)
        if file_info.exists() and file_info.isFile():
            icon_provider = QFileIconProvider()
            icon = icon_provider.icon(file_info)
        self.file_icon_label.setPixmap(icon.pixmap(48, 48))

    def sender_connecting_state(self):
        self.senter_loading_icon.start_animation()
        self.senter_loading_icon.show()
        self.sender_progressbar.hide()
        self.sending_header.setText("Trying to Connecting")

    def sender_sending_state(self):
        self.senter_loading_icon.stop_animation()
        self.senter_loading_icon.hide()
        self.sender_progressbar.show()
        self.sending_header.setText("Sending File")

    def sender_finished_state(self):
        self.senter_loading_icon.stop_animation()
        self.senter_loading_icon.hide()
        self.sender_progressbar.hide()
        self.sending_header.setText("Successful")

    def close_sender_thread(self):
        self.sender_thread.stop()
        self.sender_page()

    def receiver_connecting_state(self):
        self.receiver_loading_icon.start_animation()
        self.receiver_loading_icon.show()
        self.receiver_progressbar.hide()
        self.receiver_header.setText("Trying to Connecting")

    def receiver_receiving_state(self):
        self.receiver_loading_icon.stop_animation()
        self.receiver_loading_icon.hide()
        self.receiver_progressbar.show()
        self.receiver_header.setText("Receiving File")

    def receiver_finished_state(self):
        self.receiver_loading_icon.stop_animation()
        self.receiver_loading_icon.hide()
        self.receiver_progressbar.hide()
        self.receiver_header.setText("Successful")

    # Sender
    def send(self):
        if os.path.isfile(self.sending_file_path):
            self.sending_page()

            self.sender_thread = SenderThread(self.host, self.port, self.sending_file_path)
            self.sender_thread.connectionEstablished.connect(self.sender_sending_state)
            # self.sender_thread.progressChanged.connect()
            self.sender_thread.fileRecieved.connect(self.sender_finished_state)
            self.sender_thread.start()

    # Reciever
    def receive(self):
        if os.path.isdir(self.save_path):
            self.receiver_page()

            self.receiver_thread = ReceiverThread(self.host, self.port, self.save_path)
            self.receiver_thread.connectionEstablished.connect(self.receiver_receiving_state)
            self.receiver_thread.progressChanged.connect(self.receiver_progressbar.set_current_data)
            self.receiver_thread.fileRecieved.connect(self.receiver_finished_state)
            self.receiver_thread.fileSize.connect(self.receiver_progressbar.set_maximum_data)
            self.receiver_thread.start()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow(app)
    window.show()
    app.exec()