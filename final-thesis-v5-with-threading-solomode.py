import tkinter as tk
from tkinter import Label, StringVar, font, Button
import pyaudio
import time
import threading
import numpy as np
import pyaudio
from keras_yamnet import params
from keras_yamnet.yamnet import YAMNet, class_names
from keras_yamnet.preprocessing import preprocess_input
#import RPi.GPIO as GPIO
import speech_recognition as sr
from datetime import date
from time import sleep
import sounddevice


# Initialize GPIO
#GPIO.setmode(GPIO.BOARD)
#GPIO.setup(31, GPIO.OUT)

# Function to control vibration
def vibrate(duration):
    #GPIO.output(31, True)  # Turn on
    time.sleep(duration)   # Vibrate for specified duration
    #GPIO.output(31, False)  # Turn off


# Sound Recognition Model Initialization
model = YAMNet(weights='keras_yamnet/yamnet.h5')
yamnet_classes = class_names('keras_yamnet/yamnet_class_map.csv')
plt_classes = [389, 11, 390, 349]  # Alarm Clock, Screaming, Siren, Doorbell

# Microphone Settings for Speech Recognition
mic = pyaudio.PyAudio()
stream = mic.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192)
stream.start_stream()

WIN_SIZE_SEC = 0.975
RATE = params.SAMPLE_RATE
CHUNK = int(WIN_SIZE_SEC * RATE)

# Define the target words and their sound-alike equivalents
target_words = [
    "fire",#90% Accuracy
    "sunog", #70%
    "pulis", #70%
    "warning", #60%
    "magnanakaw", #60%
    "stop", #80%
    "tulong", #80%
    "run", #90%
    "takbo", "tumakbo",
    "police", # 100%
    "intruder", # 80%
    "emergency", #70%
    "trouble",
    "evacuate",
    "danger", #80%
    "iwas", #70%
    "ingat", #90%
    "call", #80%
    "alert", #70%
    #20 words ^^
    "alarm", #80%
    "lindol", #new
    "saklolo", #new
    "excuse", #new
    "atras", #new
    "abante", #new
    "alis", #new
    "tigil","tumigil",
    "bilis", #new
    "layo","lumayo",
    "slippery",
    # Add more target words and their sound-alike equivalents
]

# GUI
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Speech Recognition Alert System")

        # Set custom fonts
        self.label_font = font.Font(family="Helvetica", size=60, weight="bold")
        self.active_font = font.Font(family="Helvetica", size=60, weight="bold")

        # Set initial label text
        self.label_text = StringVar()
        self.label_text.set("ACTIVE")

        # Create and pack labels
        self.label = Label(root, textvariable=self.label_text, font=self.active_font, fg="black", bg="white",
                          width=20, height=3)  # Adjust width and height for smaller GUI
        self.label.pack(padx=20, pady=20)

        # Add Mode Selection Buttons
        self.speech_to_text_button = Button(root, text="Speech to Text", command=self.speech_to_text_mode,
                                             font=("Helvetica", 23))
        self.speech_to_text_button.pack(side=tk.LEFT, padx=10, pady=10)

        self.sound_recognition_button = Button(root, text="Sound Recognition", command=self.sound_recognition_mode,
                                              font=("Helvetica", 23))
        self.sound_recognition_button.pack(side=tk.LEFT, padx=10, pady=30)

        # Add Exit button
        exit_button = Button(root, text="Exit", command=root.destroy, font=("Helvetica", 23))
        exit_button.pack(side=tk.LEFT, pady=10)

        self.mode = "speech_to_text"  # Default mode
        self.speech_to_text_button.config(bg="green")  # Set initial color
        self.sound_recognition_button.config(bg="red")

        self.root.after(100, self.listen_for_input)
        
         # Create a threading.Event to signal the threads to stop
        self.stop_event = threading.Event()

        # Create threads for speech recognition and sound recognition
        self.speech_thread = threading.Thread(target=self.listen_for_speech_thread)
        self.sound_thread = threading.Thread(target=self.listen_for_sound_thread)

        # Start the threads
        self.speech_thread.start()
        self.sound_thread.start()

    def flash_word(self, detected_words):
        if detected_words:
            word = detected_words[0]
            self.label_text.set(word)
            self.label.config(fg="white" if word in target_words else "yellow", bg="red")
            self.root.update()
            #vibrate(3)
            # Use after method to schedule the update after a delay
            self.root.after(3000, self.reset_label)

    def reset_label(self):
        self.label_text.set("ACTIVE")
        self.label.config(fg="black", bg="white")
        self.root.update()

    def listen_for_input(self):
        data = stream.read(8192)  # Increase buffer size
        self.listen_for_speech()
        self.listen_for_sound()
            

        self.root.after(100, self.listen_for_input)

    def speech_to_text_mode(self):
        self.mode = "speech_to_text"
        self.speech_to_text_button.config(bg="green")
        self.sound_recognition_button.config(bg="red")

    def sound_recognition_mode(self):
        self.mode = "sound_recognition"
        self.speech_to_text_button.config(bg="red")
        self.sound_recognition_button.config(bg="green")


    def listen_for_speech_thread(self):
        r = sr.Recognizer()
        mic = sr.Microphone()

        while not self.stop_event.is_set():
            with mic as source:
                audio = r.listen(source)
            try:
                words = r.recognize_google(audio)
                print(words)
                detected_words = [word for word in target_words if word in words]
                if detected_words:
                    self.flash_word(detected_words)
            except sr.UnknownValueError:
                words = "not recognised"

    def listen_for_sound_thread(self):
        mic = pyaudio.PyAudio()
        stream = mic.open(format=pyaudio.paFloat32, channels=1, rate=RATE, input=True, frames_per_buffer=8192)

        detection_threshold = 0.7

        while not self.stop_event.is_set():
            data = preprocess_input(np.fromstring(stream.read(CHUNK), dtype=np.float32), RATE)
            prediction = model.predict(np.expand_dims(data, 0))[0]

            detected_classes = []

            for idx, class_idx in enumerate(plt_classes):
                if prediction[class_idx] > detection_threshold:
                    class_name = yamnet_classes[class_idx]
                    probability = prediction[class_idx]
                    detected_classes.append(class_name)

            self.flash_word(detected_classes)

        stream.stop_stream()
        stream.close()
        mic.terminate()


# Initialize and run the GUI
root = tk.Tk()
root.geometry("640x480")  # Set the size to fit the 3.5-inch LCD Raspberry Pi screen
root.configure(bg="white")

app = App(root)

# Cleanup GPIO
# GPIO.cleanup()
def on_closing():
    app.stop_event.set()  # Set the stop event to stop the threads
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)

root.mainloop()
