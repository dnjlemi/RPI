import speech_recognition as sr

# Initialize the recognizer
r = sr.Recognizer()

# Define a function to recognize speech
def recognize_speech():
    with sr.Microphone() as source:
        print("Listening...")
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)

    try:
        print("Recognizing...")
        text = r.recognize_whisper(audio)
        print(f"You said: {text}")
    except sr.UnknownValueError:
        print("Could not understand audio")
    except sr.RequestError as e:
        print(f"Error: {e}")

# Continuously listen for speech
while True:
    recognize_speech()
