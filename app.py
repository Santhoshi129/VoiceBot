import streamlit as st
import openai
import tempfile
import sounddevice as sd
from scipy.io.wavfile import write
import pyttsx3
import os

# -----------------------
# Page configuration
# -----------------------
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

# -----------------------
# Load secrets
# -----------------------
openai.api_key = st.secrets["OPENAI_API_KEY"]
MODEL_NAME = st.secrets.get("OPENAI_MODEL", "gpt-4o-mini")
RECORD_DURATION = int(st.secrets.get("RECORD_DURATION", 5))
VOICE_RATE = int(st.secrets.get("VOICE_RATE", 160))
VOICE_VOLUME = float(st.secrets.get("VOICE_VOLUME", 1.0))

# -----------------------
# Introduction
# -----------------------
st.title("Hi, I’m Subhasya 👋")
st.write("I’m an AI & Data Science expert. Ask me anything about my career, skills, projects, or AI expertise.")

# -----------------------
# Preloaded Questions & Answers
# -----------------------
preloaded_answers = {
    "life story": (
        "I’m Subhasya Santhoshi, an AI and Data Science expert from India. "
        "I’ve designed and deployed conversational AI, chatbots, and voicebots using Dialogflow and cloud platforms. "
        "I enjoy solving real-world problems using AI and collaborating with teams to deliver impactful solutions."
    ),
    "superpower": (
        "My superpower is designing intelligent AI systems that transform business processes and provide actionable insights."
    ),
    "growth areas": (
        "I want to advance in Generative AI, cloud AI deployment, and building scalable conversational systems."
    ),
    "misconceptions": (
        "Some people may think I’m quiet, but I’m actually very engaged and collaborative in projects."
    ),
    "push boundaries": (
        "I challenge myself with new technologies and complex projects to grow both technically and professionally."
    )
}

example_questions = [
    "What should we know about your life story in a few sentences?",
    "What’s your #1 superpower?",
    "What are the top 3 areas you’d like to grow in?",
    "What misconception do your coworkers have about you?",
    "How do you push your boundaries and limits?"
]

# -----------------------
# Functions
# -----------------------
def speak_text(text):
    """Convert text to speech using pyttsx3"""
    engine = pyttsx3.init()
    engine.setProperty('rate', VOICE_RATE)
    engine.setProperty('volume', VOICE_VOLUME)
    engine.say(text)
    engine.runAndWait()

def record_audio(duration=RECORD_DURATION, fs=44100):
    """Record audio from microphone"""
    st.info(f"Recording for {duration} seconds... Speak now!")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()
    file_path = tempfile.mktemp(suffix=".wav")
    write(file_path, fs, recording)
    return file_path

def get_bot_response(user_input):
    """Return bot response based on preloaded answers or GPT"""
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
        # GPT response for any other input
        response = openai.ChatCompletion.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are Subhasya Santhoshi's personal AI voice bot. Answer in friendly, professional, and approachable tone."},
                {"role": "user", "content": user_input}
            ]
        )
        return response.choices[0].message['content']

# -----------------------
# Main App
# -----------------------
if st.button("🎤 Record", key="record", help="Click to record your question"):
    audio_file = record_audio(duration=RECORD_DURATION)
    
    # Transcribe using OpenAI Whisper
    with open(audio_file, "rb") as f:
        transcript = openai.Audio.transcriptions.create(file=f, model="whisper-1")
    user_input = transcript['text']
    
    st.markdown(f"**You:** {user_input}")
    
    bot_answer = get_bot_response(user_input)
    st.markdown(f"**Subhasya Bot:** {bot_answer}")
    
    speak_text(bot_answer)

# -----------------------
# Show example questions
# -----------------------
st.subheader("Example questions you can ask:")
for q in example_questions:
    st.write(f"- {q}")

