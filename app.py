import streamlit as st
import openai
from gtts import gTTS
import tempfile

# -----------------------
# Page config
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
</style>
""", unsafe_allow_html=True)

# -----------------------
# OpenAI key & model
# -----------------------
openai.api_key = st.secrets["OPENAI_API_KEY"]
MODEL_NAME = st.secrets.get("OPENAI_MODEL", "gpt-4o-mini")

# -----------------------
# Introduction
# -----------------------
st.title("Hi, I’m Subhasya 👋")
st.write("I’m an AI & Data Science expert. Ask me anything about my career, skills, or projects.")

# -----------------------
# Preloaded Q&A
# -----------------------
preloaded_answers = {
    "life story": "I’m Subhasya Santhoshi, an AI and Data Science expert from India. I’ve designed and deployed conversational AI, chatbots, and voicebots using Dialogflow and cloud platforms. I enjoy solving real-world problems using AI and collaborating with teams to deliver impactful solutions.",
    "superpower": "My superpower is designing intelligent AI systems that transform business processes and provide actionable insights.",
    "growth areas": "I want to advance in Generative AI, cloud AI deployment, and building scalable conversational systems.",
    "misconceptions": "Some people may think I’m quiet, but I’m actually very engaged and collaborative in projects.",
    "push boundaries": "I challenge myself with new technologies and complex projects to grow both technically and professionally."
}

example_questions = [
    "What should we know about your life story in a few sentences?",
    "What’s your #1 superpower?",
    "What are the top 3 areas you’d like to grow in?",
    "What misconception do your coworkers have about you?",
    "How do you push your boundaries and limits?"
]

# -----------------------
# Helper function for GPT response
# -----------------------
def get_bot_response(user_input):
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
        response = openai.ChatCompletion.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are Subhasya Santhoshi's personal AI bot. Answer in friendly, professional, and approachable tone."},
                {"role": "user", "content": user_input}
            ]
        )
        return response.choices[0].message['content']

# -----------------------
# User interaction
# -----------------------
st.subheader("Type your question:")
user_input = st.text_input("Your question here:")

if user_input:
    answer = get_bot_response(user_input)
    st.markdown(f"**Subhasya Bot:** {answer}")

    # Convert to speech using gTTS
    tts = gTTS(text=answer, lang='en')
    tts_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(tts_file.name)
    st.audio(tts_file.name)

# -----------------------
# Example questions
# -----------------------
st.subheader("Example questions you can ask:")
for q in example_questions:
    st.write(f"- {q}")

