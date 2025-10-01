import streamlit as st
import openai
from io import BytesIO
import soundfile as sf
import tempfile
import os
import pyttsx3
import speech_recognition as sr

# Set your OpenAI API key
openai.api_key = st.secrets["OPENAI_API_KEY"]

st.title("🎤 VoiceBot Demo")
st.write("Ask me anything — I'll listen, reply, and speak back!")

# Initialize conversation history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Audio recording
st.subheader("Speak to the bot")
audio_bytes = st.audio_input("Click and record your question:")

user_input = ""
if audio_bytes is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
        tmp_file.write(audio_bytes.read())
        tmp_file_path = tmp_file.name

    # Recognize speech
    r = sr.Recognizer()
    with sr.AudioFile(tmp_file_path) as source:
        audio = r.record(source)
        try:
            user_input = r.recognize_google(audio)
            st.write(f"**You said:** {user_input}")
        except sr.UnknownValueError:
            st.write("Sorry, could not understand the audio.")
        except sr.RequestError:
            st.write("Speech Recognition service failed.")

# Text input fallback
typed_input = st.text_input("Or type your question here:")
if typed_input:
    user_input = typed_input

# Send to OpenAI GPT
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=st.session_state.messages
    )
    bot_reply = response['choices'][0]['message']['content']
    
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
    
    st.write(f"**Bot:** {bot_reply}")

    # Convert bot reply to speech
    tts_engine = pyttsx3.init()
    tts_engine.save_to_file(bot_reply, "response.mp3")
    tts_engine.runAndWait()
    
    audio_file = open("response.mp3", "rb")
    st.audio(audio_file.read(), format="audio/mp3")

