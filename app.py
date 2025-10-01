import streamlit as st
import openai
from streamlit_webrtc import webrtc_streamer
import tempfile

# -----------------------------
# Page config
# -----------------------------
st.set_page_config(
    page_title="Subhasya's Voice Assistant",
    page_icon="🤖",
    layout="wide"
)

st.markdown("""
<style>
body {
    background: linear-gradient(135deg, #ff9a9e 0%, #fad0c4 100%);
    font-family: 'Segoe UI', sans-serif;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Secrets: OpenAI API key
# -----------------------------
openai.api_key = st.secrets["OPENAI_API_KEY"]

# -----------------------------
# Predefined answers
# -----------------------------
predefined_answers = {
    "life story": "I'm Subhasya Santhoshi, an AI and Data Science expert from India. I design and deploy conversational AI, chatbots, and voicebots.",
    "superpower": "My superpower is designing intelligent AI systems that transform business processes and provide actionable insights.",
    "growth areas": "I want to advance in Generative AI, cloud AI deployment, and building scalable conversational systems.",
    "misconceptions": "Some people may think I'm quiet, but I’m very engaged and collaborative in projects.",
    "push boundaries": "I challenge myself with new technologies and complex projects to grow both technically and professionally."
}

# -----------------------------
# Functions
# -----------------------------
def get_bot_response(user_input):
    lower_input = user_input.lower()
    for key in predefined_answers:
        if key in lower_input:
            return predefined_answers[key]
    # GPT fallback
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are Subhasya Santhoshi's personal AI assistant. Speak in a friendly, professional, and lively tone."},
            {"role": "user", "content": user_input}
        ]
    )
    return response.choices[0].message['content']

def text_to_speech_oa(text):
    """Generate speech using OpenAI TTS"""
    audio_response = openai.audio.speech.create(
        model="gpt-4o-mini-tts",
        voice="alloy",  # default free voice
        input=text
    )
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    temp_file.write(audio_response.read())
    temp_file.flush()
    return temp_file.name

# -----------------------------
# UI: Avatar & Greeting
# -----------------------------
st.image("animated_avatar.gif", width=300)  # Replace with your GIF
st.title("Hello, welcome!")
st.write("Hey! This is Subhasya's personal assistant. Ask me anything about her – I’ll respond in voice.")

# -----------------------------
# Voice recording (Streamlit WebRTC)
# -----------------------------
webrtc_streamer(key="voice-assistant")

# -----------------------------
# Text input fallback
# -----------------------------
user_input = st.text_input("Type your question here (fallback):")

if user_input:
    bot_response = get_bot_response(user_input)
    audio_file = text_to_speech_oa(bot_response)
    st.audio(audio_file)
