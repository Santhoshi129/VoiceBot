import streamlit as st
import speech_recognition as sr
import pyttsx3

st.set_page_config(page_title="VoiceBot", page_icon="🗣️", layout="centered")

st.image("assets/avatar.png", width=250)   # Your assistant image
st.title("Hello, welcome!")
st.write("Hey! This is Subhasya's personal assistant. Click 'Speak' below, ask anything — I’ll respond in voice.")

# Initialize speech recognizer and TTS
recognizer = sr.Recognizer()
tts = pyttsx3.init()

# Speak button
if st.button("🎙️ Speak"):
    try:
        with sr.Microphone() as source:
            st.write("Listening...")
            audio = recognizer.listen(source, phrase_time_limit=8)  # listen for 8s
            st.write("Processing...")

            # Convert speech → text
            text = recognizer.recognize_google(audio)
            st.success(f"You said: {text}")

            # Generate a response (simple echo, you can replace with LLM)
            response = f"Nice to meet you! You said: {text}"
            st.write("Assistant:", response)

            # Text-to-speech playback
            tts.say(response)
            tts.runAndWait()

    except sr.UnknownValueError:
        st.error("Sorry, I couldn’t understand your speech. Try again.")
    except sr.RequestError as e:
        st.error(f"Speech Recognition API error: {e}")
