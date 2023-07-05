import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QProgressBar, QPushButton, QHBoxLayout, QLabel
from PySide6.QtCore import Qt, QTimer

class Progressbar_Widget(QWidget):

    def __init__(self):
        super().__init__()
        self.setFixedSize(400, 200)
        self.setStyleSheet(
            """
                QWidget
                {
                    background-color: #282828;
                }
            """
        )

        self.current_data = QLabel("0B")
        self.maximum_data = QLabel("0B")
        self.percentage = QLabel("0%")
        self.progressbar = QProgressBar()

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
        slash.setStyleSheet(
            """
                Qlabel
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
        data_layout.addWidget(self.maximum_data)
        data_layout.setAlignment(self.maximum_data, Qt.AlignLeft | Qt.AlignVCenter)

        text_layout = QHBoxLayout()
        text_layout.addSpacing(5)
        text_layout.addWidget(self.percentage)
        text_layout.setAlignment(self.percentage, Qt.AlignBottom | Qt.AlignLeft)
        text_layout.addLayout(data_layout)
        text_layout.setAlignment(data_layout, Qt.AlignBottom | Qt.AlignRight)
        text_layout.addSpacing(5)

        start_button = QPushButton("START")
        start_button.setFixedSize(200, 80)
        start_button.clicked.connect(self.start_animation)
        start_button.setStyleSheet(
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
        
        progressbar_layout = QVBoxLayout()
        progressbar_layout.setAlignment(Qt.AlignCenter)
        progressbar_layout.addLayout(text_layout)
        progressbar_layout.addWidget(self.progressbar)
        progressbar_layout.addWidget(start_button)

        self.setLayout(progressbar_layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)

        self.animation_duration = 3000  # Animation duration in milliseconds
        self.animation_steps = 100  # Number of steps for the animation
        self.current_value = 0

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


    def start_animation(self):
        self.current_value = 0
        self.progressbar.setValue(0)
        self.timer.start(self.animation_duration // self.animation_steps)

    def update_progress(self):
        self.current_value += 1
        if self.current_value <= self.animation_steps:
            value = int(self.current_value * 100 / self.animation_steps)
            self.progressbar.setValue(value)
            self.percentage.setText(str(value) + "%")
        else:
            self.timer.stop()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = Progressbar_Widget()
    window.set_green_theme()
    window.show()

    app.exec()