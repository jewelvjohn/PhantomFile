import sys
from PySide6.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
from PySide6.QtGui import QPixmap, QTransform
from PySide6.QtCore import QTimer

class AnimatedImage(QGraphicsView):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Animated Image")
        self.setGeometry(100, 100, 400, 300)

        self.scene = QGraphicsScene()
        self.setScene(self.scene)

        self.pixmap_item = QGraphicsPixmapItem()
        self.scene.addItem(self.pixmap_item)

        pixmap = QPixmap("image.png")
        self.pixmap_item.setPixmap(pixmap)
        self.pixmap_item.setTransformOriginPoint(pixmap.width() / 2, pixmap.height() / 2)

        self.start_animation()

    def start_animation(self):
        self.rotation_angle = 0
        self.rotation_timer = QTimer()
        self.rotation_timer.timeout.connect(self.update_rotation)
        self.rotation_timer.start(20)  # Adjust the interval (in milliseconds) to control the rotation speed

    def update_rotation(self):
        self.rotation_angle += 1
        transform = QTransform().rotate(self.rotation_angle)
        self.pixmap_item.setTransform(transform)

app = QApplication([])
window = AnimatedImage()
window.show()
sys.exit(app.exec())
