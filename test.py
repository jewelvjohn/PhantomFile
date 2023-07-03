import os
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel, QFileIconProvider
from PySide6.QtGui import QIcon, QPixmap, QImageReader, QImage
from PySide6.QtCore import QFileInfo, Qt

class FileDetailsWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("File Details")
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.file_path_label = QLabel("No file selected")
        self.layout.addWidget(self.file_path_label)

        self.file_icon_label = QLabel()
        self.file_icon_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.file_icon_label)

        self.file_size_label = QLabel("File Size: N/A")
        self.layout.addWidget(self.file_size_label)

        self.open_file_button = QPushButton("Open File")
        self.open_file_button.clicked.connect(self.open_file_dialog)
        self.layout.addWidget(self.open_file_button)

    def open_file_dialog(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self, "Open File", "", "All Files (*)"
        )
        if file_path:
            self.file_path_label.setText(f"File Path: {file_path}")
            file_size = os.path.getsize(file_path)
            formatted_size = self.format_file_size(file_size)
            self.file_size_label.setText(f"File Size: {formatted_size}")
            self.set_file_icon(file_path)

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
            self.file_icon_label.setPixmap(icon.pixmap(48, 48))
            self.set_file_preview(file_path)

    def set_file_preview(self, file_path):
        image_extensions = ['png', 'jpg', 'jpeg', 'gif']
        video_extensions = ['mp4', 'avi', 'mkv']

        file_info = QFileInfo(file_path)
        file_extension = file_info.suffix().lower()

        if file_extension in image_extensions:
            self.show_image_preview(file_path)
        elif file_extension in video_extensions:
            self.show_video_preview(file_path)
        else:
            self.show_default_preview()

    def show_image_preview(self, file_path):
        image = QImage(file_path)
        self.file_icon_label.setPixmap(QPixmap.fromImage(image).scaled(48, 48, Qt.AspectRatioMode.KeepAspectRatio))

    def show_video_preview(self, file_path):
        image_reader = QImageReader(file_path)
        image_reader.setScaledSize(self.file_icon_label.size())
        image = image_reader.read()
        self.file_icon_label.setPixmap(QPixmap.fromImage(image))

    def show_default_preview(self):
        # Use a default preview image for unsupported file types
        default_image = QImage('default_preview_image.png')
        self.file_icon_label.setPixmap(QPixmap.fromImage(default_image))


# Create a QApplication instance
app = QApplication([])

# Create an instance of FileDetailsWindow
window = FileDetailsWindow()
window.show()

# Start the event loop
app.exec()