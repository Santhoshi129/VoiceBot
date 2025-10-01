# app.py
import os
import tempfile
import streamlit as st
from gtts import gTTS
from streamlit_mic_recorder import mic_recorder
import openai

# --- Config ---
st.set_page_config(page_title="Subhasya's Voice Assistant", page_icon="🌸", layout="centered")

AVATAR = "animated_gif.jpg"
INTRO = (
    "Hello! I am Subhasya’s personal assistant 🌸. "
    "You can ask me about her life story, superpower, growth areas, misconceptions, "
    "or how she pushes boundaries. Just click the mic below and start speaking!"
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

# --- Helpers ---
def tts_bytes(text: str) -> bytes:
    tts = gTTS(text, lang="en", tld="co.in")
    tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
    tts.save(tmp.name)
    with open(tmp.name, "rb") as f:
        data = f.read()
    os.unlink(tmp.name)
    return data

def transcribe_audio(wav_bytes: bytes) -> str:
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
    text = user_text.lower()
    for key in RESPONSES.keys():
        if key in text:
            return RESPONSES[key]
    return RESPONSES["default"]

# --- Custom CSS for chat bubbles ---
st.markdown("""
<style>
.chat-bubble-user {
    background-color: #DCF8C6;
    padding: 10px 15px;
    border-radius: 20px;
    max-width: 75%;
    margin: 5px 0;
    text-align: right;
    margin-left: auto;
    box-shadow: 0px 1px 3px rgba(0,0,0,0.1);
}
.chat-bubble-assistant {
    background-color: #F1F0F0;
    padding: 10px 15px;
    border-radius: 20px;
    max-width: 75%;
    margin: 5px 0;
    text-align: left;
    margin-right: auto;
    box-shadow: 0px 1px 3px rgba(0,0,0,0.1);
}
</style>
""", unsafe_allow_html=True)

# --- UI ---
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

# --- Mic Recorder (without as_wav) ---
audio = mic_recorder(
    start_prompt="🎙️ Start Recording",
    stop_prompt="⏹️ Stop",
    key="recorder"
)

if audio:
    wav_data = audio.get("bytes")  # older versions return "bytes"

    if wav_data:
        st.audio(wav_data, format="audio/wav")

        try:
            # 1. Transcribe with Whisper
            user_text = transcribe_audio(wav_data)
            st.markdown(f'<div class="chat-bubble-user">You: {user_text}</div>', unsafe_allow_html=True)

            # 2. Find best response
            reply = match_response(user_text)
            st.markdown(f'<div class="chat-bubble-assistant">Assistant: {reply}</div>', unsafe_allow_html=True)

            # 3. Voice reply
            audio_bytes = tts_bytes(reply)
            st.audio(audio_bytes, format="audio/mp3")

        except Exception as e:
            st.error(f"Error during processing: {e}")
    else:
        st.warning("No audio captured. Please try again.")
