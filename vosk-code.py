import vosk
import pyaudio
import logging

# Set the logging level to suppress Vosk logs
vosk.SetLogLevel(-1)

# English model
model_en = vosk.Model(r"C:\Users\hp\Downloads\Thesis Prototype\vosk-sr\vosk-model-small-en-us-0.15")
recognizer_en = vosk.KaldiRecognizer(model_en, 16000)

# Filipino model
model_ph = vosk.Model(r"C:\Users\hp\Downloads\Thesis Prototype\vosk-sr\vosk-model-tl-ph-generic-0.6")
recognizer_ph = vosk.KaldiRecognizer(model_ph, 16000)

mic = pyaudio.PyAudio()
stream = mic.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192)
stream.start_stream()

# Define the target words
target_words = ["fire", "alarm", "police", "help", "sunog", "watch out", "emergency", "intruder", "trouble", "tulong", "evacuate", "hazard", "slippery", "danger", "warning"]

# Sets to keep track of detected words by each recognizer
detected_words_set_en = set()
detected_words_set_ph = set()

while True:
    data = stream.read(4096)

    if recognizer_en.AcceptWaveform(data):
        text_en = recognizer_en.Result()
        detected_words_en = [word for word in target_words if word in text_en]
        if detected_words_en:
            #print(f"English: Detected words - {', '.join(detected_words_en)}")
            print(', '.join(detected_words_en))
            detected_words_set_en.update(detected_words_en)
    else:
        if recognizer_ph.AcceptWaveform(data):
            text_ph = recognizer_ph.Result()
            detected_words_ph = [word for word in target_words if word in text_ph and word not in detected_words_set_en]
            if detected_words_ph:
                #print(f"Filipino: Detected words - {', '.join(detected_words_ph)}")
                print(', '.join(detected_words_ph))
                detected_words_set_ph.update(detected_words_ph)
