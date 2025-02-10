import pvporcupine
import sounddevice as sd
import struct
import json
import queue
import pyttsx3
import ollama
from vosk import Model, KaldiRecognizer
import numpy as np

# ============================ INITIALIZATION ============================

# Text-to-Speech (TTS) Engine
engine = pyttsx3.init()
engine.setProperty("rate", 180)  # Adjust speaking speed

# Wake Word Detection (Porcupine)
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

# Speech-to-Text (STT) Model (Vosk)
vosk_model_path = r"C:\Users\LENOVO\Desktop\medi\model"  # Change this if needed
vosk_model = Model(vosk_model_path)
recognizer = KaldiRecognizer(vosk_model, 16000)

# SoundDevice Setup for STT
audio_queue = queue.Queue()

def audio_callback(indata, frames, time, status):
    if status:
        print(status)
    audio_queue.put(indata.copy())

stream = sd.InputStream(samplerate=16000, channels=1, dtype='int16', callback=audio_callback)
stream.start()

# ============================ FUNCTIONALITY ============================

def speak(text):
    """ Convert text to speech """
    print(f"🎙️ Speaking: {text}")
    engine.say(text)
    engine.runAndWait()

def listen():
    """ Capture audio and convert it to text using Vosk """
    print("🎤 Listening for command...")
    
    while True:
        data = audio_queue.get()
        audio_data = np.frombuffer(data, dtype=np.int16).tobytes()
        
        if recognizer.AcceptWaveform(audio_data):
            result = json.loads(recognizer.Result())["text"]
            if result:
                print(f"📝 Recognized: {result}")
                return result  # Return recognized text

def generate_health_response(query):
    """ Stream AI response for real-time feedback using TinyLlama """
    print("🤖 Processing response...")

    try:
        response = ollama.chat(model="tinyllama", messages=[{"role": "user", "content": query}], stream=True)
        
        final_response = ""
        for chunk in response:
            if "message" in chunk and "content" in chunk["message"]:
                content = chunk["message"]["content"]
                print(content, end="", flush=True)  # Show live updates
                final_response += content

        return final_response

    except Exception as e:  # Make sure there's an except block
        print(f"❌ Error: {e}")
        return "I'm facing some issues fetching the response."




def listen_for_wake_word():
    """ Continuously listens for wake words to activate or deactivate assistant """
    print("🎙️ Listening for 'Hey Medi' to activate... (Say 'Ok Goodbye' to deactivate)")

    while True:
        try:
            pcm = np.zeros(porcupine.frame_length, dtype=np.int16)
            audio_data = audio_queue.get()
            pcm[:len(audio_data)] = np.frombuffer(audio_data, dtype=np.int16)
        except Exception as e:
            print(f"❌ Microphone read error: {e}")
            continue  

        result = porcupine.process(pcm)

        if result == 0:  # "Hey Medi" detected
            print("🔥 Wake Word Detected! Assistant Activated.")
            speak("Yes sir, have a good health. How can I help you?")
            run_voice_assistant()  # Start assistant after wake word
        elif result == 1:  # "Ok Goodbye" detected
            print("❌ Stop Command Detected! Shutting down.")
            speak("Ok goodbye. Have a great day.")
            cleanup()

def run_voice_assistant():
    """ Main loop for processing voice commands """
    while True:
        user_query = listen()  # Get user input via voice
        if user_query:
            response = generate_health_response(user_query)  # Get AI response
            speak(response)  # Speak response

def cleanup():
    """ Clean up and close resources """
    print("🔄 Cleaning up...")
    stream.stop()
    stream.close()
    porcupine.delete()
    exit(0)

# ============================ START ASSISTANT ============================
listen_for_wake_word()
