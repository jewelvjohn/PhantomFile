import os
import sys
import cv2
import tqdm
import time
import socket
import posixpath

from PySide6.QtWidgets import (QApplication, QWidget, 
                               QLabel, QPushButton, 
                               QVBoxLayout, QHBoxLayout, 
                               QTextEdit, QStackedLayout,
                               QFileDialog, QFileDialog, 
                               QFileIconProvider, QSizePolicy)
from PySide6.QtGui import QIcon, QPixmap, QPainter, QImage
from PySide6.QtCore import Qt, QFileInfo

class MainWindow(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.setWindowTitle("Phantom File")
        self.setStyleSheet("QWidget {background: rgb(40, 40, 40);}")
        self.setMinimumSize(650, 400)
        self.resize(650, 400)

        self.initialize_ui()
        self.initialize_settings()

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

        self.ip_addr = "127.0.0.1"
        self.port = 9999
        self.save_path = saves

        data = f"{self.ip_addr},{self.port},{self.save_path}"

        with open(self.settings_path, "w") as file:
            file.write(data)
        self.refresh_settings()

    def update_settings(self):
        ip_addr = self.ip_addr_textbox.toPlainText()
        port = int(self.port_textbox.toPlainText())
        save_path = self.saves_textbox.toPlainText()

        data = f"{ip_addr},{port},{save_path}"

        with open(self.settings_path, "w") as file:
            file.write(data)
        self.refresh_settings()
        self.intro_page()

    def refresh_settings(self):
        with open(self.settings_path, 'r') as file:
            data = file.read()
            addr, port, saves = data.split(",")
            os.makedirs(saves, exist_ok=True)

            self.ip_addr = addr
            self.port = int(port)
            self.save_path = saves

            self.ip_addr_textbox.setPlainText(self.ip_addr)
            self.port_textbox.setPlainText(str(self.port))
            self.saves_textbox.setPlainText(self.save_path)

    def initialize_ui(self):
        self.stacked_layout = QStackedLayout()

        intro_widget = self.intro_ui()
        self.stacked_layout.addWidget(intro_widget)

        settings_widget = self.settings_ui()
        self.stacked_layout.addWidget(settings_widget)

        send_widget = self.send_ui()
        self.stacked_layout.addWidget(send_widget)

        # recieve_widget = self.send_ui()
        # self.stacked_layout.addWidget(recieve_widget)

        self.main_layout = QVBoxLayout()
        self.main_layout.addLayout(self.stacked_layout)

        self.setLayout(self.main_layout)

    def intro_page(self):
        self.stacked_layout.setCurrentIndex(0)

    def settings_page(self):
        self.refresh_settings()
        self.stacked_layout.setCurrentIndex(1)

    def send_page(self):
        self.stacked_layout.setCurrentIndex(2)

    def intro_ui(self):
        main_header = QLabel("Phantom File")
        main_header.setStyleSheet(
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
        main_header.setAlignment(Qt.AlignCenter)

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
        sender_button.clicked.connect(self.send_page)
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
        
        reciever_button = QPushButton("RECIEVER")
        reciever_button.setFixedSize(200, 80)
        # recieve_button.clicked.connect(self.recieve_ui)
        reciever_button.setStyleSheet(
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

        recieve_button_layout = QVBoxLayout()
        recieve_button_layout.setAlignment(Qt.AlignCenter)
        recieve_button_layout.addWidget(reciever_button)
        recieve_button_layout.addWidget(server_header)

        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignCenter)
        button_layout.addLayout(send_button_layout)
        button_layout.addSpacing(20)
        button_layout.addLayout(recieve_button_layout)

        header_layout = QHBoxLayout()
        header_layout.addWidget(settings_button)
        header_layout.addWidget(main_header)
        header_layout.addWidget(dummy_header)
        header_layout.setAlignment(settings_button, Qt.AlignLeft)
        header_layout.setAlignment(main_header, Qt.AlignCenter)
        header_layout.setAlignment(dummy_header, Qt.AlignRight)

        intro_layout = QVBoxLayout()
        intro_layout.addLayout(header_layout)
        intro_layout.setAlignment(header_layout, Qt.AlignTop)
        intro_layout.addSpacing(20)
        intro_layout.addLayout(button_layout)
        intro_layout.setAlignment(button_layout, Qt.AlignCenter)
        intro_layout.addSpacing(20)
        intro_layout.addWidget(note)
        intro_layout.setAlignment(note, Qt.AlignBottom)

        intro_widget = QWidget()
        intro_widget.setLayout(intro_layout)

        return intro_widget

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
        cancel_button.clicked.connect(self.intro_page)
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

        ip_addr_caption = QLabel("Socket Address")
        ip_addr_caption.setAlignment(Qt.AlignVCenter)
        ip_addr_caption.setFixedWidth(120)
        ip_addr_caption.setStyleSheet(
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

        self.ip_addr_textbox = QTextEdit()
        self.ip_addr_textbox.setAlignment(Qt.AlignCenter)
        self.ip_addr_textbox.setFixedHeight(45)
        self.ip_addr_textbox.setStyleSheet(
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

        ip_addr_layout = QHBoxLayout()
        ip_addr_layout.addSpacing(5)
        ip_addr_layout.addWidget(ip_addr_caption)
        ip_addr_layout.addSpacing(5)
        ip_addr_layout.addWidget(self.ip_addr_textbox)
        ip_addr_layout.addSpacing(5)

        port_layout = QHBoxLayout()
        port_layout.addSpacing(5)
        port_layout.addWidget(port_caption)
        port_layout.addSpacing(5)
        port_layout.addWidget(self.port_textbox)
        port_layout.addSpacing(5)

        central_layout = QVBoxLayout()
        central_layout.addLayout(saves_layout)
        central_layout.addLayout(ip_addr_layout)
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

        settings_widget = QWidget()
        settings_widget.setLayout(settings_layout)

        return settings_widget

    def send_ui(self):
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
        back_button.clicked.connect(self.intro_page)
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
        # send_button.clicked.connect(self.disconnect)
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
        file_path, _ = file_dialog.getOpenFileName(
            self, "Open File", "", "All Files (*)"
        )
        if file_path:
            self.file_path_label.setText(f"File Path: {file_path}")
            file_size = os.path.getsize(file_path)
            formatted_size = self.format_file_size(file_size)
            self.file_size_label.setText(f"{formatted_size}")
            self.set_file_icon(file_path)

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
    def recieve(self, host: str, port: int, file_dir: str):
        os.makedirs(file_dir, exist_ok=True)

        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((host, port))
        server.listen()

        print("Server listening on {}:{}".format(host, port))
        client, client_addr = server.accept()

        print("Client connected: ", client_addr)

        file_name = client.recv(1024).decode()
        file_size = client.recv(1024).decode()
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