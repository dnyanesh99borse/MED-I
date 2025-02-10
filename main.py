import pvporcupine
import pyaudio
import struct
import time
import pyttsx3

# Initialize Text-to-Speech (TTS) engine
engine = pyttsx3.init()
engine.setProperty("rate", 180)  # Adjust speaking speed

# Initialize Porcupine Wake Word Detection
try:
    porcupine = pvporcupine.create(
        access_key="xpiJY3udZ34lkRnMmGvSp0R8vwGWhy8acuYEjWw41s3WTt1UznZwuA==",
        keyword_paths=[
            r"C:\Users\LENOVO\Desktop\medi\hey-Med-I_en_windows_v3_0_0.ppn",
            r"C:\Users\LENOVO\Desktop\medi\ok-goodbye_en_windows_v3_0_0.ppn"
        ]
    )
except Exception as e:
    print(f"❌ Error initializing Porcupine: {e}")
    exit(1)

# Initialize PyAudio
try:
    pa = pyaudio.PyAudio()
    audio_stream = pa.open(
        rate=porcupine.sample_rate,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=porcupine.frame_length
    )
except Exception as e:
    print(f"❌ Error accessing microphone: {e}")
    exit(1)

# Function to convert text to speech
def speak(text):
    print(f"🎙️ {text}")
    engine.say(text)
    engine.runAndWait()

# Wake Word Listener
def listen_for_wake_word():
    print("🎙️ Listening for 'Hey Medi' to activate... (Say 'Ok Goodbye' to deactivate)")
    while True:
        try:
            pcm = audio_stream.read(porcupine.frame_length, exception_on_overflow=False)
            pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)
        except Exception as e:
            print(f"❌ Microphone read error: {e}")
            continue  

        result = porcupine.process(pcm)

        if result == 0:  # "Hey Medi" detected
            print("🔥 Wake Word Detected! Assistant Activated.")
            speak("Yes sir, have a good health. How can I help you?")
        elif result == 1:  # "Ok Goodbye" detected
            print("❌ Stop Command Detected! Shutting down.")
            speak("Ok goodbye. Have a great day.")
            cleanup()

# Cleanup Function
def cleanup():
    print("🔄 Cleaning up...")
    audio_stream.stop_stream()
    audio_stream.close()
    pa.terminate()
    porcupine.delete()
    exit(0)

# Start Listening for Wake Word
listen_for_wake_word()
