from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtGui import QPixmap
from PyQt6.QtMultimedia import QMediaPlayer
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtCore import QUrl

class MediaWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.setStyleSheet("background-color: #4a4f3b;")
        
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.image_label)
        
        self.video_widget = QVideoWidget()
        self.layout.addWidget(self.video_widget)
        
        # Initially hide video widget
        self.video_widget.hide()

    def display_image(self, file_path):
        """Display an image in the widget."""
        pixmap = QPixmap(file_path)
        self.image_label.setPixmap(pixmap.scaled(self.size(), aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio))
        self.image_label.show()
        self.video_widget.hide()

    def display_video(self, file_path):
        """Display a video in the widget."""
        self.image_label.hide()
        self.video_widget.show()
        
        player = QMediaPlayer()
        player.setVideoOutput(self.video_widget)
        player.setSource(QUrl.fromLocalFile(file_path))
        player.play()
