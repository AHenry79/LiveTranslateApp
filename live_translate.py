import os
import deepl
from dotenv import load_dotenv
import azure.cognitiveservices.speech as speechsdk

load_dotenv()

device = os.getenv("device")
deepl_api_key = os.getenv("deepl_api_key")
translator = deepl.Translator(deepl_api_key)

def audio_to_text(api_key, region):
    speech_config = speechsdk.SpeechConfig(subscription=api_key, region=region)
    speech_config.speech_recognition_language = "en-US"
    audio_config = speechsdk.audio.AudioConfig(device_name=device)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

    # Set timeout durations

    speech_recognizer.properties.set_property(speechsdk.PropertyId.SpeechServiceConnection_InitialSilenceTimeoutMs, "60000") # 60 seconds
    speech_recognizer.properties.set_property(speechsdk.PropertyId.SpeechServiceConnection_EndSilenceTimeoutMs, "20000") # 20 seconds

    print("Speak into microphone. Say 'stop session' to end.")

    while True:
        speech_recognition_result = speech_recognizer.recognize_once_async().get()

        if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:
            text = speech_recognition_result.text
            print("Recognized: {}".format(speech_recognition_result.text))

            translation = translator.translate_text(text, target_lang="JA")
            if translation:
                print("Translation (JA): {}".format(translation))
            if "stop session" in speech_recognition_result.text.lower():
                print("Session ended by user.")
                break
        elif speech_recognition_result.reason == speechsdk.ResultReason.NoMatch:
            print("No speech could be recognized: {}".format(speech_recognition_result.no_match_details))
        elif speech_recognition_result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = speech_recognition_result.cancellation_details
            print("Speech recognition cancelled: {}".format(cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                print("Error details: {}".format(cancellation_details.error_details))
                print("Did you set the speech resource key and region values?")

api_key = os.getenv("azure_api_key")
region = os.getenv("azure_region")

audio_to_text(api_key, region)