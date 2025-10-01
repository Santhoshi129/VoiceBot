import streamlit as st
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase, WebRtcMode
import av
import speech_recognition as sr
from gtts import gTTS
import tempfile
import os
from openai import OpenAI

# --- PAGE CONFIG ---
st.set_page_config(page_title="Voice Assistant", page_icon="🎙", layout="centered")

# --- HEADER / AVATAR ---
st.image("animated_avatar.jpg", width=250)
st.markdown(
    """
    <h1 style='text-align: left;'>Hello, welcome!</h1>
    <p style='font-size:18px;'>Hey! This is Subhasya's personal assistant. 
    Click the <b>Speak</b> button below and ask anything about her life, strengths, or growth journey —
    I’ll respond as Subhasya in voice and text.</p>
    """,
    unsafe_allow_html=True,
)

# --- STATE ---
if "transcript" not in st.session_state:
    st.session_state["transcript"] = ""

# --- OPENAI CLIENT ---
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def get_ai_reply(user_text: str) -> str:
    """Generate assistant reply as if Subhasya is answering in first person."""
    prompt = f"""
    You are Subhasya's personal assistant. 
    Always answer in first person as if you are Subhasya herself. 
    Be warm, reflective, and authentic. 

    User asked: {user_text}
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": "You are Subhasya."},
                  {"role": "user", "content": prompt}],
        max_tokens=150,
    )
    return response.choices[0].message.content.strip()


# --- AUDIO PROCESSOR ---
class AudioProcessor(AudioProcessorBase):
    def __init__(self):
        self.recognizer = sr.Recognizer()

    def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
        audio = frame.to_ndarray().flatten().astype("int16").tobytes()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
            tmpfile.write(audio)
            tmp_filename = tmpfile.name

        try:
            with sr.AudioFile(tmp_filename) as source:
                audio_data = self.recognizer.record(source)
                user_text = self.recognizer.recognize_google(audio_data)

                # --- AI Reply ---
                reply = get_ai_reply(user_text)

                # --- Store transcript ---
                st.session_state["transcript"] += f"\nUser: {user_text}"
                st.session_state["transcript"] += f"\nSubhasya: {reply}"

                # --- Voice Reply ---
                tts = gTTS(reply)
                tts_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
                tts.save(tts_file.name)
                st.audio(tts_file.name, format="audio/mp3")

        except Exception as e:
            st.warning(f"Speech recognition failed: {e}")

        finally:
            if os.path.exists(tmp_filename):
                os.remove(tmp_filename)

        return frame


# --- SPEAK BUTTON / WEBRTC ---
st.markdown(
    """
    <style>
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        padding: 12px 24px;
        border-radius: 12px;
        font-size: 18px;
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

webrtc_streamer(
    key="speech-to-speech",
    mode=WebRtcMode.SENDONLY,
    audio_processor_factory=AudioProcessor,
    media_stream_constraints={"audio": True, "video": False},
)

# --- SHOW TRANSCRIPT ---
st.subheader("Transcript")
st.write(st.session_state["transcript"])
