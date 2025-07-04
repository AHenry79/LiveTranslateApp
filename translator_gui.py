import sys
import pyaudio
import os
from translator_config import azure_language_codes, deepl_source_codes, deepl_target_codes, button_style
from translator_controller import TranslatorController
from dotenv import load_dotenv
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QHBoxLayout, QVBoxLayout,
    QComboBox, QPushButton, QTextEdit, QSizePolicy
)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt

load_dotenv()

deepl_api_key = os.getenv("deepl_api_key")

def get_audio_devices():
    audio = pyaudio.PyAudio()
    devices = []
    for i in range(audio.get_device_count()):
        info = audio.get_device_info_by_index(i)
        if info["maxInputChannels"] > 0:
            devices.append(info["name"])
    audio.terminate()
    return devices


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.azure_language_codes = azure_language_codes
        self.deepl_source_codes = deepl_source_codes
        self.deepl_target_codes = deepl_target_codes
        self.button_style = button_style

        self.setWindowTitle("Live Translator")
        self.resize(1200, 700)
        self.setWindowIcon(QIcon("Green_translation_icon.svg"))
        self.setWindowIcon(QIcon("./favicon_io/favicon.ico"))
        self.setStyleSheet("background-color: #222831; color: white;")

        # === Main Layout Setup ===
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # === Header ===
        header_widget = QWidget()
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(10, 10, 10, 10)
        header_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        header_widget.setLayout(header_layout)

        title_label = QLabel("🌐 Live Translator")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        header_layout.addWidget(title_label)

        main_layout.addWidget(header_widget)

        # === Audio Source Selection ===
        audio_bar = QWidget()
        audio_layout = QHBoxLayout()
        audio_layout.setContentsMargins(0, 10, 0, 10)
        audio_bar.setLayout(audio_layout)

        audio_label = QLabel("🎧 Audio Input:")
        audio_label.setStyleSheet("font-size: 16px;")

        self.audio_source = QComboBox()
        self.audio_source.setStyleSheet("padding: 6px; border-radius: 4px; background-color: #31363F; color: white;")
        self.audio_source.setCursor(Qt.CursorShape.PointingHandCursor)
        # Populate available devices
        self.audio_source.addItems(get_audio_devices())

        audio_layout.addWidget(audio_label)
        audio_layout.addWidget(self.audio_source)

        # === Language Selection Bar ===
        lang_bar = QWidget()
        lang_layout = QHBoxLayout()
        lang_layout.setSpacing(15)
        lang_layout.setContentsMargins(0, 10, 0, 10)
        lang_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        lang_bar.setLayout(lang_layout)

        self.source_lang = QComboBox()
        self.source_lang.setCursor(Qt.CursorShape.PointingHandCursor)
        self.target_lang = QComboBox()
        self.target_lang.setCursor(Qt.CursorShape.PointingHandCursor)
        self.swap_button = QPushButton("↔")
        self.swap_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.swap_button.setStyleSheet(self.button_style)

        # Add language options
        # language_names = list(self.azure_language_codes.keys())
        self.source_lang.addItems(list(self.deepl_source_codes.keys()))
        self.target_lang.addItems(list(self.deepl_target_codes.keys()))
        self.source_lang.setCurrentText("Japanese")  
        self.target_lang.setCurrentText("English")

        # Style dropdowns and button
        combo_style = "padding: 6px; border-radius: 4px; background-color: #31363F; color: white;"
        # button_style = "padding: 6px; border-radius: 6px; background-color: #76ABAE; color: #31363F; font-weight: bold;"
        self.source_lang.setStyleSheet(combo_style)
        self.target_lang.setStyleSheet(combo_style)
        self.swap_button.setStyleSheet(self.button_style)

        lang_layout.addWidget(self.source_lang)
        lang_layout.addWidget(self.swap_button)
        lang_layout.addWidget(self.target_lang)

        main_layout.addWidget(lang_bar)
        main_layout.addWidget(audio_bar)

        # Save session button
        self.save_button = QPushButton("💾 Save Session")
        self.save_button.setStyleSheet(self.button_style)
        self.save_button.setCursor(Qt.CursorShape.PointingHandCursor)

        lang_layout.addStretch()  # pushes button to the right
        lang_layout.addWidget(self.save_button)

        # Default label
        self.toggle_button = QPushButton("🎙 Start Recording")
        self.toggle_button.setStyleSheet(self.button_style)
        self.toggle_button.setCursor(Qt.CursorShape.PointingHandCursor)

        # Label added to button as layout
        self.button_layout = QVBoxLayout()
        self.toggle_button.setLayout(self.button_layout)

        main_layout.addWidget(self.toggle_button)

        # === Transcription Panel ===
        trans_label = QLabel("🎙️ Transcription")
        trans_label.setStyleSheet("font-size: 18px; margin-top: 10px;")
        main_layout.addWidget(trans_label)

        self.transcription_box = QTextEdit()
        self.transcription_box.setReadOnly(True)
        self.transcription_box.setStyleSheet(
            "background-color: #393E46; color: white; font-size: 14px; padding: 10px; border-radius: 6px;"
        )
        self.transcription_box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        main_layout.addWidget(self.transcription_box)

        # === Translation Panel ===
        trans_label = QLabel("🌐 Translation")
        trans_label.setStyleSheet("font-size: 18px; margin-top: 10px;")
        main_layout.addWidget(trans_label)

        self.translation_box = QTextEdit()
        self.translation_box.setReadOnly(True)
        self.translation_box.setStyleSheet(
            "background-color: #00ADB5; color: white; font-size: 14px; padding: 10px; border-radius: 6px;"
        )
        self.translation_box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        main_layout.addWidget(self.translation_box)

        self.controller = TranslatorController(
            ui=self,
            azure_codes=self.azure_language_codes,
            deepl_source=self.deepl_source_codes,
            deepl_target=self.deepl_target_codes,
            button_style=self.button_style,
            deepl_api_key=deepl_api_key
        )

        # Connect swap button action
        self.swap_button.clicked.connect(self.controller.swap_languages)
        self.save_button.clicked.connect(self.controller.save_session)
        self.toggle_button.clicked.connect(self.controller.toggle_transcription)
    
def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()