from PyQt6.QtCore import pyqtSignal, QObject
import azure.cognitiveservices.speech as speechsdk
import deepl
import os

deepl_api_key = os.getenv("deepl_api_key")

class RecognitionWorker(QObject):
    transcript_received = pyqtSignal(str)
    translation_received = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, api_key, region, azure_lang, deepl_source, deepl_target, deepl_api_key):
        super().__init__()
        self.api_key = api_key
        self.region = region
        self.azure_lang = azure_lang
        self.deepl_source = deepl_source
        self.deepl_target = deepl_target
        self._stop_requested = False
        self.translator = deepl.Translator(deepl_api_key)
        self.recognizer = None

    def stop(self):
        self._stop_requested = True
        if self.recognizer:
            self.recognizer.stop_continuous_recognition_async()

    def run(self):
        speech_config = speechsdk.SpeechConfig(subscription=self.api_key, region=self.region)
        speech_config.speech_recognition_language = self.azure_lang
        audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)

        self.recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

        def recognized_handler(evt):
            if self._stop_requested:
                return

            text = evt.result.text
            if text:
                self.transcript_received.emit(text)
                try:
                    result = self.translator.translate_text(
                        text,
                        source_lang=self.deepl_source,
                        target_lang=self.deepl_target
                    )
                    self.translation_received.emit(str(result))
                except Exception as e:
                    self.translation_received.emit(f"[Translation error]: {e}")
        def canceled_handler(evt):
            self.finished.emit()
        def session_stopped_handler(evt):
            self.finished.emit()  

        self.recognizer.recognized.connect(recognized_handler)
        self.recognizer.canceled.connect(canceled_handler)
        self.recognizer.session_stopped.connect(session_stopped_handler)
        self.recognizer.start_continuous_recognition_async()