# app.py
import os
import tempfile
import streamlit as st
from gtts import gTTS
from streamlit_mic_recorder import mic_recorder
import openai

# --- Config ---
st.set_page_config(page_title="Subhasya's Voice Assistant", page_icon="🎤", layout="centered")

AVATAR = "avatar_gif.jpg" 
INTRO = (
    "Hello! I am Subhasya’s personal assistant. "
    "You can ask me about her life story, superpower, growth areas, misconceptions, or how she pushes boundaries. "
    "Just click the mic below and start speaking!"
)

# --- Predefined lively answers ---
RESPONSES = {
    "life": "Subhasya’s journey is full of curiosity, learning, and determination. She embraces change and keeps kindness at her core.",
    "superpower": "Her biggest superpower is empathy — she connects with people and makes them feel truly understood.",
    "growth": "She wants to grow in leadership, creative problem solving, and emotional intelligence.",
    "misconception": "People think she’s reserved, but once you know her, she’s warm, lively, and expressive!",
    "boundary": "She pushes boundaries by taking on challenges that scare her a little, and growing stronger each time.",
    "default": "That’s a wonderful question! Subhasya is always learning and evolving."
}

# --- Helper functions ---
def tts_bytes(text: str) -> bytes:
    """Generate Indian English female voice with gTTS."""
    tts = gTTS(text, lang="en", tld="co.in")
    tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
    tts.save(tmp.name)
    with open(tmp.name, "rb") as f:
        data = f.read()
    os.unlink(tmp.name)
    return data

def transcribe_audio(wav_bytes: bytes) -> str:
    """Send audio to OpenAI Whisper and return text transcription."""
    openai.api_key = os.environ.get("OPENAI_API_KEY")
    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    tmp.write(wav_bytes)
    tmp.flush()
    tmp.seek(0)
    with open(tmp.name, "rb") as f:
        transcript = openai.Audio.transcribe("whisper-1", f)
    os.unlink(tmp.name)
    return transcript["text"]

def match_response(user_text: str) -> str:
    """Find best matching response for user input."""
    text = user_text.lower()
    for key in RESPONSES.keys():
        if key in text:
            return RESPONSES[key]
    return RESPONSES["default"]

# --- UI Layout ---
col1, col2 = st.columns([1, 2])

with col1:
    if os.path.exists(AVATAR):
        st.image(AVATAR, width=220)
    else:
        st.image("https://via.placeholder.com/220.png?text=Subhasya", width=220)

with col2:
    st.title("🌸 Welcome!")
    st.write("This is **Subhasya’s lively personal assistant**. Ask me anything about her!")
    st.info(INTRO)

st.write("---")
st.subheader("🎤 Start a Conversation")

# --- Mic recorder ---
audio = mic_recorder(
    start_prompt="🎙️ Start Recording",
    stop_prompt="⏹️ Stop",
    just_once=True,
    as_wav=True
)

if audio:
    st.audio(audio["bytes"], format="audio/wav")
    st.markdown("**You spoke! Processing...**")

    try:
        # 1. Transcribe
        user_text = transcribe_audio(audio["bytes"])
        st.markdown(f"**You (transcribed):** {user_text}")

        # 2. Find best response
        reply = match_response(user_text)
        st.markdown(f"**Assistant:** {reply}")

        # 3. Voice output
        audio_bytes = tts_bytes(reply)
        st.audio(audio_bytes, format="audio/mp3")

    except Exception as e:
        st.error(f"Error: {e}")

