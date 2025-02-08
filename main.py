import pvporcupine
import pyaudio
import struct
import pyttsx3
import time

# Initialize pyttsx3 for text-to-speech
engine = pyttsx3.init()
engine.setProperty('rate', 170)  # Adjust speaking speed
engine.setProperty('volume', 1.0)  # Set volume level to max

# Load Porcupine wake word models (Corrected)
porcupine = pvporcupine.create(
    access_key="xpiJY3udZ34lkRnMmGvSp0R8vwGWhy8acuYEjWw41s3WTt1UznZwuA==",  # Your actual Picovoice access key
    keyword_paths=[
        "C:/Users/LENOVO/Desktop/medi/hey-Med-I_en_windows_v3_0_0.ppn",  # "Hey Medi"
        "C:/Users/LENOVO/Desktop/medi/ok-goodbye_en_windows_v3_0_0.ppn"  # "Stop Med I" (or similar)
    ]
)

# Function to speak text
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Initialize microphone input
pa = pyaudio.PyAudio()
audio_stream = pa.open(
    rate=porcupine.sample_rate,
    channels=1,
    format=pyaudio.paInt16,
    input=True,
    frames_per_buffer=porcupine.frame_length
)

def listen_for_wake_word():
    print("Listening for 'Hey Medi'... 🎙️ (Auto-stops after 10 min or 'Stop Med I')")

    start_time = time.time()  # Start timer
    max_duration = 10 * 60  # 10 minutes in seconds

    while True:
        # Read audio data
        pcm = audio_stream.read(porcupine.frame_length, exception_on_overflow=False)
        pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)

        # Check if a wake word is detected
        result = porcupine.process(pcm)

        if result == 0:  # "Hey Medi" detected
            print("Wake Word Detected! 🔥")
            speak("Yes sir, have a good health. How can I assist you today?")

        elif result == 1:  # "Stop Med I" detected
            print("Stop Command Detected! ❌")
            speak("Goodbye, take care!")
            break  # Exit loop immediately

        # Auto-stop after 10 minutes
        if time.time() - start_time > max_duration:
            print("Auto Stopping after 10 minutes... ⏳")
            speak("Session timeout. See you next time!")
            break

    # Cleanup resources
    audio_stream.stop_stream()
    audio_stream.close()
    pa.terminate()

# Start listening for wake word
listen_for_wake_word()
