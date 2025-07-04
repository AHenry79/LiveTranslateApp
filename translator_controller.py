# translator_controller.py
from PyQt6.QtCore import QThread
from live_translate import RecognitionWorker
import os

class TranslatorController:
    def __init__(self, ui, azure_codes, deepl_source, deepl_target, button_style, deepl_api_key):
        self.ui = ui
        self.azure_language_codes = azure_codes
        self.deepl_source_codes = deepl_source
        self.deepl_target_codes = deepl_target
        self.button_style = button_style
        self.deepl_api_key = deepl_api_key
        self.is_recording = False
    def start_transcription(self):
        # Access widgets via self.ui.<widget>
        self.ui.toggle_button.setStyleSheet(self.button_style)
        self.ui.toggle_button.setEnabled(True)

        # Grab language choices from dropdowns
        source_lang = self.ui.source_lang.currentText()
        target_lang = self.ui.target_lang.currentText()
        azure_lang = self.azure_language_codes.get(source_lang, "en-US")
        deepl_source = self.deepl_source_codes.get(source_lang, "EN")
        deepl_target = self.deepl_target_codes.get(target_lang, "JA")

        # Load environment keys
        api_key = os.getenv("azure_api_key")
        region = os.getenv("azure_region")

        self.ui.transcription_box.append("🎙 Session started.")

        # Thread setup
        self.thread = QThread()
        self.worker = RecognitionWorker(
            api_key, region, azure_lang,
            deepl_source, deepl_target, self.deepl_api_key
        )

        self.worker.moveToThread(self.thread)

        self.worker.transcript_received.connect(lambda text: self.ui.transcription_box.append(text))
        self.worker.translation_received.connect(lambda text: self.ui.translation_box.append(text))
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.finished.connect(self.on_worker_finished)

        self.thread.started.connect(self.worker.run)
        self.thread.start()

        self.ui.toggle_button.setText("🛑 Stop Session")
    def toggle_transcription(self):
        if not self.is_recording:
            self.ui.toggle_button.setEnabled(False)
            self.ui.toggle_button.setText("🔄 Starting recording...")
            self.start_transcription()
            self.is_recording = True
        else:
            self.ui.toggle_button.setEnabled(False)
            self.ui.toggle_button.setText("🔄 Stopping session...")
            self.stop_transcription()
            self.is_recording = False

    def stop_transcription(self):
        if hasattr(self, "worker"):
            self.worker.stop()
            self.ui.transcription_box.append("🔇 Session stopped.")
        self.ui.toggle_button.setText("🎙 Start Recording")
        self.ui.toggle_button.setEnabled(True)

    def on_worker_finished(self):
        self.ui.toggle_button.setText("🎙 Start Recording")
        self.ui.toggle_button.setEnabled(True)
        self.ui.is_recording = False

    def save_session(self):
        transcript = self.ui.transcription_box.toPlainText()
        translation = self.ui.translation_box.toPlainText()
        combined_text = (
            "📝 TRANSCRIPTION\n--------------------\n"
            f"{transcript}\n\n🌍 TRANSLATION\n--------------------\n{translation}"
        )
        try:
            with open("live_translation_output.txt", "w", encoding="utf-8") as f:
                f.write(combined_text)
            self.ui.transcription_box.append("✅ Session saved as 'live_translation_output.txt'.")
        except Exception as e:
            self.ui.transcription_box.append(f"❌ Error saving file: {e}")
    def swap_languages(self):
        source = self.ui.source_lang.currentText()
        target = self.ui.target_lang.currentText()
        self.ui.source_lang.setCurrentText(target)
        self.ui.target_lang.setCurrentText(source)

    def center(self):
        screen_geo = self.ui.screen().availableGeometry()
        frame_geo = self.ui.frameGeometry()
        frame_geo.moveCenter(screen_geo.center())
        self.ui.move(frame_geo.topLeft())  