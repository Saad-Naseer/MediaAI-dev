import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton, QGridLayout, QLabel, QVBoxLayout, QMenu
)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import QFileDialog, QMessageBox

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set window properties
        self.setWindowTitle("Professional GUI")
        self.setGeometry(100, 100, 800, 600)

        # Set the background color
        self.setStyleSheet("background-color: #3c4331;")

        # Main widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Main layout
        self.main_layout = QGridLayout(self.central_widget)

        # Side navigation menu with QVBoxLayout
        self.side_menu_widget = QWidget()
        self.side_menu_layout = QVBoxLayout(self.side_menu_widget)
        self.side_menu_layout.setContentsMargins(0, 0, 0, 0)
        self.side_menu_layout.setSpacing(20)

        # Create buttons with icons and object names
        self.btn_media = QPushButton()
        self.btn_media.setObjectName('mediaButton')
        self.btn_media.setIcon(QIcon('C:\\Users\\49178\\Documents\\GitHub\\MediaAI-dev\\icon\\playlist.png'))  # Replace with your icon path
        self.btn_media.setIconSize(QSize(32, 32))
        self.btn_media.setFixedSize(40, 40)
        self.btn_media.setCheckable(True)  # Set as toggle button

        self.btn_video = QPushButton()
        self.btn_video.setObjectName('videoButton')
        self.btn_video.setIcon(QIcon('C:\\Users\\49178\\Documents\\GitHub\\MediaAI-dev\\icon\\video.png'))  # Replace with your icon path
        self.btn_video.setIconSize(QSize(32, 32))
        self.btn_video.setFixedSize(40, 40)
        self.btn_video.setCheckable(True)  # Set as toggle button

        self.btn_audio = QPushButton()
        self.btn_audio.setObjectName('audioButton')
        self.btn_audio.setIcon(QIcon('C:\\Users\\49178\\Documents\\GitHub\\MediaAI-dev\\icon\\audio.png'))  # Replace with your icon path
        self.btn_audio.setIconSize(QSize(32, 32))
        self.btn_audio.setFixedSize(40, 40)
        self.btn_audio.setCheckable(True)  # Set as toggle button

        # Add buttons to the side menu layout
        self.side_menu_layout.addWidget(self.btn_media)
        self.side_menu_layout.addWidget(self.btn_video)
        self.side_menu_layout.addWidget(self.btn_audio)
        self.side_menu_layout.addStretch(1)  # This will push the buttons to the top

        # Add side menu to the main layout
        self.main_layout.addWidget(self.side_menu_widget, 0, 0)

        # Content area that changes based on the button clicked
        self.content_area = QLabel("Content Area")
        self.content_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content_area.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.content_area.customContextMenuRequested.connect(self.show_context_menu)

        # Add content area to the main layout
        self.main_layout.addWidget(self.content_area, 0, 1)
        self.main_layout.setColumnStretch(1,10)
        # Set stylesheets from external file
        self.load_stylesheet("C:\\Users\\49178\\Documents\\GitHub\\MediaAI-dev\\tools\\video_editing\\styles.qss")

        # Track the current section
        self.current_section = None

        # Connect buttons
        self.btn_media.clicked.connect(self.show_media_page)
        self.btn_video.clicked.connect(self.show_video_page)
        self.btn_audio.clicked.connect(self.show_audio_page)

    def load_stylesheet(self, file_path):
        """Load and apply the stylesheet from a file."""
        with open(file_path, "r") as file:
            stylesheet = file.read()
            self.setStyleSheet(stylesheet)

    def show_media_page(self):
        """Display content for Media page."""
        self.current_section = 'media'
        self.content_area.setText("Media Page Content")

    def show_video_page(self):
        """Display content for Video page."""
        self.current_section = 'video'
        self.content_area.setText("Video Page Content")

    def show_audio_page(self):
        """Display content for Audio page."""
        self.current_section = 'audio'
        self.content_area.setText("Audio Page Content")

    def show_context_menu(self, position):
        """Display a context menu on right-click."""
        context_menu = QMenu(self)

        if self.current_section == 'media':
            import_action = context_menu.addAction("Import Media")
            import_action.triggered.connect(self.import_media)  # Connect to your import function

        context_menu.exec(self.content_area.mapToGlobal(position))

    def import_media(self):
        """Placeholder function for Import Media action."""
        """Open a file dialog to select media files."""
        # Open file dialog to select media files
        options = QFileDialog.Option.ReadOnly
        file_dialog = QFileDialog(self, "Select Media Files", "", "All Files (*);;Video Files (*.mp4 *.avi *.mov);;Audio Files (*.mp3 *.wav)")
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        file_dialog.setOptions(options)
        
        if file_dialog.exec() == QFileDialog.DialogCode.Accepted:
            selected_files = file_dialog.selectedFiles()
            
            # Display selected files
            if selected_files:
                files_list = '\n'.join(selected_files)
                QMessageBox.information(self, "Selected Files", f"Files selected:\n{files_list}")
            else:
                QMessageBox.warning(self, "No Files Selected", "No files were selected.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
