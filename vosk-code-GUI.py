import tkinter as tk
from tkinter import Label, StringVar, font, Button
import vosk
import pyaudio
import time
import threading

# Set the logging level to suppress Vosk logs
vosk.SetLogLevel(-1)

# Initialize GPIO
# GPIO.setmode(GPIO.BOARD)
# GPIO.setup(11, GPIO.OUT)

# Function to control vibration
# def vibrate(duration):
#     GPIO.output(11, True)  # Turn on
#     time.sleep(duration)   # Vibrate for specified duration
#     GPIO.output(11, False)  # Turn off

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

        # Add Exit button
        exit_button = Button(root, text="Exit", command=root.destroy, font=("Helvetica", 16))
        exit_button.pack(side=tk.BOTTOM, pady=10)

        self.root.after(100, self.listen_for_speech)

    def flash_word(self, word):
        self.label_text.set(word)
        self.label.config(fg="white" if word in target_words else "yellow", bg="red")
        self.root.update()

        # vibrate_thread = threading.Thread(target=vibrate, args=(3,))
        # vibrate_thread.start()

        time.sleep(3)  # Wait for vibration to finish

        self.label_text.set("ACTIVE")
        self.label.config(fg="black", bg="white")
        self.root.update()

    def listen_for_speech(self):
        data = stream.read(8192)  # Increase buffer size

        if recognizer_en.AcceptWaveform(data):
            text_en = recognizer_en.Result()
            detected_words_en = [word for word in target_words if word in text_en]
            if detected_words_en:
                self.flash_word(detected_words_en[0])
        else:
            if recognizer_ph.AcceptWaveform(data):
                text_ph = recognizer_ph.Result()
                detected_words_ph = [word for word in target_words if word in text_ph]
                if detected_words_ph:
                    self.flash_word(detected_words_ph[0])

        self.root.after(100, self.listen_for_speech)

# Initialize and run the GUI
root = tk.Tk()
root.geometry("480x320")  # Set the size to fit the 3.5-inch LCD Raspberry Pi screen
root.configure(bg="white")

app = App(root)
root.mainloop()

# Cleanup GPIO
# GPIO.cleanup()
