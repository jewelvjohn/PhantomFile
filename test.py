from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QStackedLayout

class MyWidget(QWidget):
    def __init__(self):
        super().__init__()

        # Create the main layout for the widget
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        # Create a QPushButton to switch between pages
        self.button = QPushButton("Switch Page")
        self.button.clicked.connect(self.switch_page)
        self.main_layout.addWidget(self.button)

        # Create the stacked layout
        self.stacked_layout = QStackedLayout()

        # Create and add Page 1 widget
        page1_widget = self.create_page_widget("Page 1", "This is Page 1")
        self.stacked_layout.addWidget(page1_widget)

        # Create and add Page 2 widget
        page2_widget = self.create_page_widget("Page 2", "This is Page 2")
        self.stacked_layout.addWidget(page2_widget)

        # Set the stacked layout as the main layout
        self.main_layout.addLayout(self.stacked_layout)

    def create_page_widget(self, title, message):
        # Create a QWidget for the page
        page_widget = QWidget()

        # Create a QVBoxLayout for the page widget
        page_layout = QVBoxLayout(page_widget)

        # Add a QLabel for the title
        title_label = QLabel(title)
        page_layout.addWidget(title_label)

        # Add a QLabel for the message
        message_label = QLabel(message)
        page_layout.addWidget(message_label)

        return page_widget

    def switch_page(self):
        # Toggle between page 1 and page 2
        current_index = self.stacked_layout.currentIndex()
        if current_index == 0:
            self.stacked_layout.setCurrentIndex(1)
        else:
            self.stacked_layout.setCurrentIndex(0)


# Create a QApplication instance
app = QApplication([])

# Create an instance of MyWidget
widget = MyWidget()
widget.show()

# Start the event loop
app.exec()