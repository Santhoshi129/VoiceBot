import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode
import openai
import os
from gtts import gTTS
import tempfile

# 🔑 API Key is stored securely in Streamlit Secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

st.set_page_config(page_title="VoiceBot Demo", page_icon="🎤", layout="centered")
st.title("🎤 VoiceBot Demo")
st.markdown("Ask me anything — I'll listen, reply, and speak back!")

# Session state for chat history
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Input box for typed question (alternative to voice)
user_input = st.text_input("Or type your question here:")

if user_input:
    st.session_state["messages"].append({"role": "user", "content": user_input})

    # Send to GPT
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": "You are a warm, friendly voice assistant. Keep answers short, clear, and natural."}] +
                 st.session_state["messages"]
    )
    reply = response["choices"][0]["message"]["content"]
    st.session_state["messages"].append({"role": "assistant", "content": reply})

    # Display response
    st.success(reply)

    # Convert to speech
    tts = gTTS(reply)
    tmpfile = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(tmpfile.name)
    st.audio(tmpfile.name)

# Show chat history
st.write("### Conversation")
for msg in st.session_state["messages"]:
    role = "🧑 You" if msg["role"] == "user" else "🤖 VoiceBot"
    st.write(f"**{role}:** {msg['content']}")
