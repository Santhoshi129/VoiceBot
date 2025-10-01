# app.py
import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, ClientSettings
import queue
import threading
import numpy as np
import av
import openai
import requests

# -------------------------
# CONFIG
# -------------------------
st.set_page_config(page_title="🎤 Voice GPT Bot", layout="wide")
st.title("🎤 Interactive Voice Bot")

openai.api_key = st.secrets.get("OPENAI_API_KEY") or "YOUR_OPENAI_KEY"

# Queue for audio frames
audio_queue = queue.Queue()

# -------------------------
# WEBRTC CONFIG
# -------------------------
WEBRTC_CLIENT_SETTINGS = ClientSettings(
    media_stream_constraints={"audio": True, "video": False}
)

def audio_callback(frame: av.AudioFrame):
    pcm = frame.to_ndarray()
    audio_queue.put(pcm)
    return frame

webrtc_ctx = webrtc_streamer(
    key="voicebot",
    mode=WebRtcMode.SENDRECV,
    client_settings=WEBRTC_CLIENT_SETTINGS,
    audio_receiver_size=1024,
    video_frame_callback=None,
    audio_frame_callback=audio_callback,
    async_processing=True,
)

# -------------------------
# SESSION STATE
# -------------------------
if "conversation" not in st.session_state:
    st.session_state["conversation"] = []
if "thread_started" not in st.session_state:
    st.session_state["thread_started"] = False
if "recording" not in st.session_state:
    st.session_state["recording"] = False

# -------------------------
# TRANSCRIPTION FUNCTION
# -------------------------
def transcribe_audio(audio_data: np.ndarray) -> str:
    import io
    import soundfile as sf

    buffer = io.BytesIO()
    if audio_data.ndim > 1:
        audio_data = np.mean(audio_data, axis=1)
    sf.write(buffer, audio_data.astype(np.float32), 48000, format="WAV")
    buffer.seek(0)

    transcription = openai.Audio.transcriptions.create(
        file=buffer,
        model="whisper-1"
    )
    return transcription.text

# -------------------------
# GPT RESPONSE FUNCTION
# -------------------------
def chatgpt_response(text: str) -> str:
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role":"user","content":text}]
    )
    return response.choices[0].message.content

# -------------------------
# AUDIO PROCESSING THREAD
# -------------------------
def process_audio():
    while st.session_state["recording"]:
        if not audio_queue.empty():
            pcm_data = audio_queue.get()
            transcription = transcribe_audio(pcm_data)
            gpt_reply = chatgpt_response(transcription)
            st.session_state["conversation"].append(
                {"user": transcription, "bot": gpt_reply}
            )
            st.session_state["tts_message"] = gpt_reply

if webrtc_ctx.state.playing and not st.session_state["thread_started"]:
    st.session_state["thread_started"] = True

# -------------------------
# VOICE BUTTON
# -------------------------
def toggle_recording():
    st.session_state["recording"] = not st.session_state["recording"]
    if st.session_state["recording"]:
        threading.Thread(target=process_audio, daemon=True).start()

st.button(
    "🎤 Start / Stop Recording",
    on_click=toggle_recording,
    key="voice_btn"
)

# -------------------------
# STYLING: Avatar + Chat
# -------------------------
avatar_url = "https://raw.githubusercontent.com/Santhoshi129/VoiceBot/main/avatar_gif.jpg"

st.markdown("""
<style>
.chat-container {
    max-height: 400px;
    overflow-y: auto;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 10px;
    background-color: #f9f9f9;
}
.chat-box {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    padding: 12px;
    border-radius: 10px;
    margin-bottom: 10px;
    display: flex;
    align-items: flex-start;
}
.chat-avatar {
    width: 50px;
    height: 50px;
    border-radius: 50%;
    margin-right: 10px;
}
.chat-text {
    font-size: 16px;
    padding: 8px;
    border-radius: 8px;
}
.user-msg { background-color: #d1e7dd; flex-direction: row-reverse; }
.user-msg .chat-avatar { margin-left: 10px; margin-right:0; }
.bot-msg { background-color: #f8d7da; }
</style>
""", unsafe_allow_html=True)

# Display conversation
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
for chat in st.session_state["conversation"]:
    # User
    st.markdown(f"""
    <div class="chat-box user-msg">
        <img src="{avatar_url}" class="chat-avatar"/>
        <div class="chat-text">{chat['user']}</div>
    </div>
    """, unsafe_allow_html=True)
    # Bot
    st.markdown(f"""
    <div class="chat-box bot-msg">
        <img src="{avatar_url}" class="chat-avatar"/>
        <div class="chat-text">{chat['bot']}</div>
    </div>
    """, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# -------------------------
# BROWSER TTS
# -------------------------
if "tts_message" in st.session_state:
    tts_text = st.session_state.pop("tts_message")
    st.components.v1.html(f"""
        <script>
        var msg = new SpeechSynthesisUtterance("{tts_text}");
        window.speechSynthesis.speak(msg);
        </script>
    """, height=0)
