# app.py
import os
import tempfile
import streamlit as st
from gtts import gTTS
import soundfile as sf
import numpy as np
from streamlit_mic_recorder import mic_recorder

st.set_page_config(page_title="Subhasya's Voice Assistant", page_icon="🎤", layout="centered")

AVATAR = "avatar_gif.jpg"  # place Subhasya’s image here
INTRO = (
    "Hello! I am Subhasya’s personal assistant. "
    "I can tell you about her life, superpowers, growth areas, and more. "
    "Just tap the mic below and ask me anything!"
)

# 🎤 Subhasya’s Persona – Predefined lively answers
RESPONSES = {
    "life story": "Subhasya’s journey is full of curiosity, learning, and determination. She has always been eager to explore, adapt, and grow while keeping her kindness intact.",
    "superpower": "Her number one superpower is empathy. She can truly understand people’s feelings and create a safe space for them.",
    "growth areas": "The top three areas Subhasya would love to grow in are leadership, creative problem solving, and emotional intelligence.",
    "misconception": "A common misconception is that she’s quiet and reserved — but in reality, once you know her, she’s lively, warm, and expressive.",
    "boundaries": "Subhasya pushes her boundaries by stepping outside her comfort zone, learning new skills, and challenging herself with opportunities that scare her a little.",
    "default": "That’s an interesting question! Subhasya would love me to keep learning to answer you better."
}

# --- Helpers ---
def tts_bytes(text: str) -> bytes:
    """Generate lively Indian English female TTS using gTTS."""
    tts = gTTS(text, lang="en", tld="co.in")  # co.in = Indian accent
    tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
    tts.save(tmp.name)
    with open(tmp.name, "rb") as f:
        data = f.read()
    os.unlink(tmp.name)
    return data

def match_response(user_text: str) -> str:
    """Pick a predefined response based on keywords."""
    text = user_text.lower()
    if "life" in text or "story" in text:
        return RESPONSES["life story"]
    elif "superpower" in text:
        return RESPONSES["superpower"]
    elif "grow" in text or "growth" in text:
        return RESPONSES["growth areas"]
    elif "misconception" in text or "coworker" in text:
        return RESPONSES["misconception"]
    elif "boundary" in text or "limit" in text:
        return RESPONSES["boundaries"]
    else:
        return RESPONSES["default"]

# --- UI ---
if os.path.exists(AVATAR):
    st.image(AVATAR, width=250)
else:
    st.image("https://via.placeholder.com/250x250.png?text=Subhasya", width=250)

st.title("Hello, Welcome!")
st.write("This is **Subhasya’s lively personal assistant**. Feel free to ask me about her!")

st.info(INTRO)

st.write("---")
st.subheader("🎤 Start a Conversation")

# Mic recording
audio = mic_recorder(start_prompt="Click to Record", stop_prompt="Stop Recording", just_once=True)

if audio:
    wav_path = tempfile.NamedTemporaryFile(suffix=".wav", delete=False).name
    sf.write(wav_path, np.array(audio["bytes"]), 44100)

    st.success("Processing your question...")

    # For demo: we don’t send to OpenAI, we just match keywords
    user_text = "[voice detected]"  # we skip transcription for simplicity
    st.markdown("**You:** (voice input)")

    reply = match_response(user_text)

    st.markdown(f"**Assistant:** {reply}")

    audio_bytes = tts_bytes(reply)
    st.audio(audio_bytes, format="audio/mp3")

