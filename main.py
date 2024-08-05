import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QTextEdit, QFileDialog, QLabel, QWidget, QGridLayout
from PyQt6.QtWidgets import QComboBox, QSpacerItem, QSizePolicy
#from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from tools.audio_to_text.audio_to_text import SpeechRecognizer
from threading import Thread

class MediaAiApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("MediaAI")
        #self.setWindowIcon(QIcon("../../icon/icon.png"))
        self.setGeometry(100, 100, 600, 400)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.layout = QGridLayout()
        self.central_widget.setLayout(self.layout)
        
        self.result_layout = QGridLayout()
        self.layout.addLayout(self.result_layout, 0 , 0)
        
        self.result_label = QLabel("Result:")
        self.result_layout.addWidget(self.result_label, 0, 0)

        self.text_edit = QTextEdit(self)
        self.result_layout.addWidget(self.text_edit, 1, 0)
        self.text_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.status_label = QLabel('', self)
        self.result_layout.addWidget(self.status_label, 2, 0)
        
        self.btns_layout = QGridLayout()
        self.layout.addLayout(self.btns_layout, 0, 1)

        self.record_button = QPushButton('Record from Mic', self)
        self.record_button.clicked.connect(self.mic_to_text)
        self.btns_layout.addWidget(self.record_button, 1, 0)
        
        self.upload_button = QPushButton('Upload Audio File', self)
        self.upload_button.clicked.connect(self.upload_file)
        self.btns_layout.addWidget(self.upload_button, 2, 0)
        
        self.create_language_combobox()
        self.create_out_file_combobox()
        
        self.generate_file_button = QPushButton('Generate File', self)
        self.generate_file_button.clicked.connect(self.generate_file)
        self.btns_layout.addWidget(self.generate_file_button, 4, 0)
        # Create a spacer item to push the layout content up
        self.spacer = QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.btns_layout.addItem(self.spacer, 5, 0)  # Place the spacer at the top
        self.layout.setColumnStretch(3,0)
        self.show()
    
    def create_language_combobox(self):
        self.language_combobox_layout = QGridLayout()
        self.btns_layout.addLayout(self.language_combobox_layout,0 , 0)

        self.language_combobox = QComboBox()
        self.language_combobox_label = QLabel("Select Language:")
        self.language_combobox.addItems([
            "English (US) - en",
            "Spanish - es", "French - fr",
            "German - de"
        ])
        self.language_combobox.currentIndexChanged.connect(self.change_language)
        self.language_combobox_layout.addWidget(self.language_combobox_label, 0, 0)
        self.language_combobox_layout.addWidget(self.language_combobox, 1, 0)
        self.change_language()
        
    
    def change_language(self):
        lang_code = self.language_combobox.currentText().split(" - ")[1]
        self.language = lang_code

    def create_out_file_combobox(self):
        self.out_file_combobox_layout = QGridLayout()
        self.btns_layout.addLayout(self.out_file_combobox_layout, 3, 0)
        self.out_file_combobox = QComboBox()
        self.out_file_combobox_label = QLabel("Select Output File Type:")
        self.out_file_combobox.addItems([".txt", ".srt", ".vvt"])
        self.out_file_combobox.currentIndexChanged.connect(self.change_out_file_type)
        self.out_file_combobox_layout.addWidget(self.out_file_combobox_label, 0, 0)
        self.out_file_combobox_layout.addWidget(self.out_file_combobox, 1, 0)
        self.change_out_file_type()
    
    def change_out_file_type(self):
        self.file_path = "output/out"+self.out_file_combobox.currentText()
        #print(self.file_path)

    def mic_to_text(self):
        self.speech_recognizer = SpeechRecognizer(tool="mic", language=self.language)
        self.speech_recognizer.status_update.connect(self.status_update)
        self.speech_recognizer.text_update.connect(self.text_update)
        self.speech_recognizer.start()

    def upload_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Audio File", "", "Audio Files (*.wav *.flac *.mp3)")
        if file_path:
            self.speech_recognizer= SpeechRecognizer(tool="file", language=self.language, file_path=file_path)
            self.speech_recognizer.status_update.connect(self.status_update)
            self.speech_recognizer.text_update.connect(self.text_update)
            self.speech_recognizer.start()

    def generate_file(self):
         with open(self.file_path, "w") as file:
            file.write(self.text_edit.toPlainText())

    def status_update(self, status):
        self.status_label.setText(status)

    def text_update(self, text):
        self.text_edit.setText(text)

def main():
    app = QApplication(sys.argv)
    ex = MediaAiApp()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
