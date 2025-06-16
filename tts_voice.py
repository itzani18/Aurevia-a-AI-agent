import os
import threading
import pygame
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings

api_key = "sk_94a0e7232ed870647d635d1c0853de1bc5cc62e7cd835bcf"
client = ElevenLabs(api_key=api_key)
voice_id = "cA7uzZlCjwGEkoIQu7gK"
import pyttsx3
def speak_plan(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

"""def speak_plan(text, voice_id=voice_id, filename="aurevia_plan.mp3"):
    try:
        audio = client.text_to_speech.convert(
            voice_id=voice_id,
            text=text,
            model_id="eleven_multilingual_v2",
            voice_settings=VoiceSettings(stability=0.4, similarity_boost=0.7)
        )
        with open(filename, "wb") as f:
            for chunk in audio:
                f.write(chunk)
        def play_audio():
            pygame.mixer.init()
            pygame.mixer.music.load(filename)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pass
        thread = threading.Thread(target=play_audio)
        thread.start()
        return filename
    except Exception as e:
        print("Voice error:", e)
        # Streamlit mein show karo:
        import streamlit as st
        st.warning("Voice feature is not working (API/Internet Error). Try again later.")
        return None"""

def stop_audio():
    try:
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()
        else:
            print("Pygame mixer not initialized, nothing to stop.")
    except Exception as e:
        print("Error stopping audio:", e)

# For local test
if __name__ == "__main__":
    test_text = "This is a test using the ElevenLabs Python SDK version 2.x."
    print("Generating and playing voice...")
    speak_plan(test_text)