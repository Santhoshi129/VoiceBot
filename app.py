# Streamlit Voice Bot for Subhasya Santhoshi

import streamlit as st
from streamlit_chat import message
import openai
import tempfile
import sounddevice as sd
from scipy.io.wavfile import write
import pyttsx3
import os

# -------------------
# Page configuration
# -------------------
st.set_page_config(
    page_title="Subhasya's Voice Bot",
    page_icon="🤖",
    layout="wide"
)

st.markdown("""
<style>
body {
    background: linear-gradient(135deg, #ff9a9e 0%, #fad0c4 100%);
    font-family: 'Segoe UI', sans-serif;
}
.record-btn {
    font-size: 2rem;
    padding: 1rem 2rem;
    border-radius: 50%;
    background: radial-gradient(circle, #ff5f6d, #ffc371);
    color: white;
}
</style>
""", unsafe_allow_html=True)

# -------------------
# OpenAI API Key
# -------------------
openai.api_key = st.secrets["OPENAI_API_KEY"]

# -------------------
# Intro
# -------------------
st.title("Hi, I’m Subhasya 👋")
st.write("I’m an AI & Data Science expert. Let’s start the conversation! Ask me anything about my background, skills, or projects.")

# -------------------
# Preloaded Questions & Answers
# -------------------
preloaded_answers = {
    "life story": (
        "I’m Subhasya Santhoshi, an AI and Data Science expert from India. "
        "I’ve designed and deployed conversational AI, chatbots, and voicebots using Dialogflow and cloud-based platforms. "
        "I enjoy solving real-world problems using AI and collaborating with teams to deliver impactful solutions."
    ),
    "superpower": (
        "My superpower is designing and deploying intelligent AI systems that transform business processes. "
        "I can translate complex technical solutions into actionable insights that make a difference."
    ),
    "growth areas": (
        "I am focusing on advancing my skills in Generative AI, cloud-based AI deployment, and building scalable conversational systems. "
        "I also aim to enhance my project management and cross-functional collaboration abilities."
    ),
    "misconceptions": (
        "Some people may think I’m quiet at first, but I’m actually very engaged and collaborative when working on AI and data projects."
    ),
    "push boundaries": (
        "I constantly challenge myself with new projects, emerging AI technologies, and innovative workflows to push both my technical and professional limits."
    )
}

example_questions = [
    "What should we know about your life story in a few sentences?",
    "What’s your #1 superpower?",
    "What are the top 3 areas you’d like to grow in?",
    "What misconception do your coworkers have about you?",
    "How do you push your boundaries and limits?"
]

# -------------------
# Function to convert text to speech
# -------------------
def speak_text(text):
    engine = pyttsx3.init()
    engine.setProperty('rate', 160)
    engine.say(text)
    engine.runAndWait()

# -------------------
# Function to record audio
# -------------------
def record_audio(duration=5, fs=44100):
    st.info("Recording for 5 seconds... Speak now!")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()
    file_path = tempfile.mktemp(suffix=".wav")
    write(file_path, fs, recording)
    return file_path

# -------------------
# Function to handle user input and generate bot response
# -------------------
def get_bot_response(user_input):
    # Check for preloaded answers
    lower_input = user_input.lower()
    if "life story" in lower_input or "about you" in lower_input:
        return preloaded_answers["life story"]
    elif "superpower" in lower_input:
        return preloaded_answers["superpower"]
    elif "grow" in lower_input or "areas" in lower_input:
        return preloaded_answers["growth areas"]
    elif "misconception" in lower_input or "coworkers" in lower_input:
        return preloaded_answers["misconceptions"]
    elif "push" in lower_input or "boundaries" in lower_input:
        return preloaded_answers["push boundaries"]
    else:
        # Use GPT for any other question in your tone
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are Subhasya Santhoshi's personal voice bot. Answer in friendly, professional, and approachable tone, reflecting Subhasya's background in AI, data science, and conversational AI."},
                {"role": "user", "content": user_input}
            ]
        )
        return response.choices[0].message['content']

# -------------------
# Main interaction
# -------------------
if st.button("🎤 Record", key="record", help="Click to record your question"):
    audio_file = record_audio(duration=5)
    
    # Transcribe audio using OpenAI Whisper
    with open(audio_file, "rb") as f:
        transcript = openai.Audio.transcriptions.create(file=f, model="whisper-1")
    user_input = transcript['text']
    
    message(user_input, is_user=True)
    
    bot_answer = get_bot_response(user_input)
    message(bot_answer, is_user=False)
    
    speak_text(bot_answer)

# -------------------
# Show example questions
# -------------------
st.subheader("Example questions you can ask:")
for q in example_questions:
    st.write(f"- {q}")

