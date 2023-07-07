import sys
from PySide6.QtCore import QTimer, QThread, Signal
from PySide6.QtWidgets import QApplication, QMainWindow, QProgressBar

class WorkerThread(QThread):
    progress_updated = Signal(int)
    progress = 0

    def run(self):
        self.timer = QTimer()
        self.timer.moveToThread(self)
        self.timer.setInterval(100)  # Update every second
        self.timer.timeout.connect(self.update_progress)
        self.timer.start()

    def update_progress(self):
        self.progress += 1
        if self.progress > 100:
            self.progress = 0
        self.progress_updated.emit(self.progress)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setFixedSize(400, 200)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setGeometry(50, 50, 200, 25)

        self.worker_thread = WorkerThread()
        self.worker_thread.progress_updated.connect(self.update_progress)

    def update_progress(self, progress):
        self.progress_bar.setValue(progress)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    window.worker_thread.start()
    app.exec()