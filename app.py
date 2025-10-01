import streamlit as st
import openai
import base64
import tempfile

# -----------------------------
# Page config
# -----------------------------
st.set_page_config(
    page_title="Subhasya's Voice Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
body {
    background: linear-gradient(135deg, #ff9a9e 0%, #fad0c4 100%);
    font-family: 'Segoe UI', sans-serif;
}
button {
    background-color: #4CAF50;
    color: white;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Load API key
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
# Helper functions
# -----------------------------
def get_bot_response(user_input):
    lower_input = user_input.lower()
    for key in predefined_answers:
        if key in lower_input:
            return predefined_answers[key]
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
        voice="alloy",
        input=text
    )
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    temp_file.write(audio_response.read())
    temp_file.flush()
    return temp_file.name

# -----------------------------
# Avatar & Greeting
# -----------------------------
st.image("animated_avatar.gif", width=300)  # Replace with your GIF
st.title("Hello, welcome!")
st.write("Hey! This is Subhasya's personal assistant. Click the 'Speak' button below and ask anything about her — I’ll respond in voice.")

# -----------------------------
# HTML + JS microphone recorder
# -----------------------------
st.markdown("""
<button onclick="startRecording()">🎤 Speak</button>
<script>
let mediaRecorder;
let audioChunks = [];

function startRecording() {
    navigator.mediaDevices.getUserMedia({ audio: true })
    .then(stream => {
        mediaRecorder = new MediaRecorder(stream);
        mediaRecorder.start();
        audioChunks = [];
        mediaRecorder.ondataavailable = e => { audioChunks.push(e.data); };
        mediaRecorder.onstop = e => {
            let blob = new Blob(audioChunks, { type: 'audio/wav' });
            let reader = new FileReader();
            reader.readAsDataURL(blob);
            reader.onloadend = function() {
                let base64data = reader.result;
                const input = document.createElement('input');
                input.type = 'hidden';
                input.id = 'audio_data';
                input.value = base64data;
                document.body.appendChild(input);
                const event = new Event('audioCaptured');
                document.dispatchEvent(event);
            }
        };
        setTimeout(() => mediaRecorder.stop(), 5000);  // 5s max recording
    });
}
</script>
""", unsafe_allow_html=True)

# -----------------------------
# Listen for audio event
# -----------------------------
audio_data = st.experimental_get_query_params().get("audio_data")

if audio_data:
    audio_base64 = audio_data[0].split(",")[1]
    audio_bytes = base64.b64decode(audio_base64)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
        f.write(audio_bytes)
        f.flush()
        # Transcribe using Whisper
        audio_file = open(f.name, "rb")
        transcript = openai.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
        user_text = transcript.text
        st.write(f"You said: {user_text}")

        # Bot response
        bot_response = get_bot_response(user_text)
        audio_file = text_to_speech_oa(bot_response)
        st.audio(audio_file)
