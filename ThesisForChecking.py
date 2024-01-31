import tkinter as tk
from tkinter import Label, StringVar, font, Button
import vosk
import pyaudio
import time
import threading
import numpy as np
import pyaudio
from keras_yamnet import params
from keras_yamnet.yamnet import YAMNet, class_names
from keras_yamnet.preprocessing import preprocess_input
#import RPi.GPIO as GPIO

# Set the logging level to suppress Vosk logs
vosk.SetLogLevel(-1)

# Initialize GPIO
#GPIO.setmode(GPIO.BOARD)
#GPIO.setup(31, GPIO.OUT)

# Function to control vibration
def vibrate(duration):
    #GPIO.output(31, True)  # Turn on
    time.sleep(duration)   # Vibrate for specified duration
    #GPIO.output(31, False)  # Turn off
    
# English model
model_en = vosk.Model(r"C:\Users\hp\Downloads\Thesis Prototype\vosk-sr\vosk-model-small-en-us-0.15")
recognizer_en = vosk.KaldiRecognizer(model_en, 16000)

# Filipino model
model_ph = vosk.Model(r"C:\Users\hp\Downloads\Thesis Prototype\vosk-sr\vosk-model-tl-ph-generic-0.6")
recognizer_ph = vosk.KaldiRecognizer(model_ph, 16000)

#################### MODEL #####################
model = YAMNet(weights='keras_yamnet/yamnet.h5')
yamnet_classes = class_names('keras_yamnet/yamnet_class_map.csv')
plt_classes = [389, 11, 390, 349]  # Alarm Clock, Screaming, Siren, Doorbell

mic = pyaudio.PyAudio()
stream = mic.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192)
stream.start_stream()

WIN_SIZE_SEC = 0.975
RATE = params.SAMPLE_RATE
CHUNK = int(WIN_SIZE_SEC * RATE)


# Define the target words
target_words = ["fire", "alarm", "police", "help", "sunog", "watch out", "emergency", "intruder", "trouble", "tulong", "evacuate", "hazard", "slippery", "danger", "warning"]

# GUI
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Speech Recognition Alert System")

        # Set custom fonts
        self.label_font = font.Font(family="Helvetica", size=20, weight="bold")
        self.active_font = font.Font(family="Helvetica", size=28, weight="bold")

        # Set initial label text
        self.label_text = StringVar()
        self.label_text.set("ACTIVE")

        # Create and pack labels
        self.label = Label(root, textvariable=self.label_text, font=self.active_font, fg="black", bg="white")
        self.label.pack(pady=10)

        # Add Mode Selection Buttons
        self.speech_to_text_button = Button(root, text="Speech to Text", command=self.speech_to_text_mode, font=("Helvetica", 16))
        self.speech_to_text_button.pack(side=tk.LEFT, padx=10, pady=10)

        self.sound_recognition_button = Button(root, text="Sound Recognition", command=self.sound_recognition_mode, font=("Helvetica", 16))
        self.sound_recognition_button.pack(side=tk.RIGHT, padx=10, pady=10)

        # Add Exit button
        exit_button = Button(root, text="Exit", command=root.destroy, font=("Helvetica", 16))
        exit_button.pack(side=tk.BOTTOM, pady=10)

        self.mode = "speech_to_text"  # Default mode
        self.speech_to_text_button.config(bg="green")  # Set initial color
        self.sound_recognition_button.config(bg="red")

        self.root.after(100, self.listen_for_input)

    def flash_word(self, word):
        self.label_text.set(word)
        self.label.config(fg="white" if word in target_words else "yellow", bg="red")
        self.root.update()
        vibrate(3)
        
        self.label_text.set("ACTIVE")
        self.label.config(fg="black", bg="white")
        self.root.update()

    def listen_for_input(self):
        data = stream.read(8192)  # Increase buffer size
        if self.mode == "speech_to_text":
            self.listen_for_speech()
        elif self.mode == "sound_recognition":
            # Add code for sound recognition here
            self.listen_for_sound()
            pass

        self.root.after(100, self.listen_for_input)

    def speech_to_text_mode(self):
        self.mode = "speech_to_text"
        self.speech_to_text_button.config(bg="green")
        self.sound_recognition_button.config(bg="red")

    def sound_recognition_mode(self):
        self.mode = "sound_recognition"
        self.speech_to_text_button.config(bg="red")
        self.sound_recognition_button.config(bg="green")

    def listen_for_speech(self):
        mic = pyaudio.PyAudio()
        #stream = mic.open(format=pyaudio.paFloat32,channels=1,rate=RATE,input=True,frames_per_buffer=int(WIN_SIZE_SEC * RATE))
        stream = mic.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192)
        stream.start_stream()

        while True:
            data = stream.read(8192)

            if recognizer_en.AcceptWaveform(data) or recognizer_ph.AcceptWaveform(data):
                text_en = recognizer_en.Result()
                text_ph = recognizer_ph.Result()
                print(f"English: '{text_en[14:-3]}'")
                print(f"Filipino: '{text_ph[14:-3]}'")
                detected_words_en = [word for word in target_words if word in text_en]
                detected_words_ph = [word for word in target_words if word in text_ph]
                if detected_words_en:
                    self.flash_word(detected_words_en[0])
                elif detected_words_ph:
                    self.flash_word(detected_words_ph[0])
            break
        stream.stop_stream()
        stream.close()
        mic.terminate()
                               
    def listen_for_sound(self):
        mic = pyaudio.PyAudio()
        #stream = mic.open(format=pyaudio.paFloat32,channels=1,rate=RATE,input=True,frames_per_buffer=int(WIN_SIZE_SEC * RATE))
        stream = mic.open(format=pyaudio.paFloat32,channels=1,rate=RATE,input=True,frames_per_buffer=8192)
        detection_threshold = 0.7
        data = preprocess_input(np.fromstring(stream.read(CHUNK), dtype=np.float32), RATE)
        prediction = model.predict(np.expand_dims(data, 0))[0]

            # Check for specific classes and print an alert
        for idx, class_idx in enumerate(plt_classes):
            if prediction[class_idx] > detection_threshold:
                class_name = yamnet_classes[class_idx]
                probability = prediction[class_idx]
                self.flash_word(class_name)
        
        stream.stop_stream()
        stream.close()
        mic.terminate()

# Initialize and run the GUI
root = tk.Tk()
root.geometry("640x480")  # Set the size to fit the 3.5-inch LCD Raspberry Pi screen
root.configure(bg="white")

app = App(root)
root.mainloop()

# Cleanup GPIO
# GPIO.cleanup()
