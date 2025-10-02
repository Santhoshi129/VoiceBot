import gradio as gr
import torch
from transformers import pipeline

# === Speech-to-Text ===
asr = pipeline("automatic-speech-recognition", model="openai/whisper-small")

# === Text-to-Speech ===
tts = pipeline("text-to-speech", model="espnet/kan-bayashi_ljspeech_vits")

# === Polished Interview Answers (friendly spoken style) ===
answers = {
    "life story": "That’s a great question! I grew up in India with a natural curiosity for technology and creativity. Over the years, I explored different projects that pushed me to learn continuously. Today, I’m passionate about building AI tools that make people’s lives easier and more meaningful.",
    "superpower": "If I had to pick one, I’d say my superpower is adaptability. I can quickly adjust to new challenges, learn fast, and stay calm under pressure — it’s what keeps me moving forward.",
    "top 3 areas": "I’d love to keep growing in three areas: expanding my knowledge in advanced AI and emerging technologies, strengthening my problem-solving skills with real-world applications, and refining my ability to collaborate across diverse teams to build impactful solutions.",
    "misconception": "Some coworkers think I’m a little quiet. But in reality, I’m just reflective — I prefer to listen first, think deeply, and then share thoughtful inputs.",
    "push limits": "I push my limits by setting ambitious goals, embracing challenges outside my comfort zone, and taking on projects that stretch both my technical skills and my mindset."
}

# === Voicebot Logic ===
def voicebot(audio):
    # Convert speech to text
    text = asr(audio)["text"].lower()

    # Match response
    response = "Thanks for asking! I’m passionate about AI and building tools that make life better."
    for key in answers:
        if key in text:
            response = answers[key]
            break

    # Convert to speech
    speech = tts(response, forward_params={"speaker": "default"})
    return response, (speech["audio"], speech["sampling_rate"])

# === UI with Avatar GIF + Styling ===
with gr.Blocks(css=".gradio-container {background: linear-gradient(to right, #fefefe, #f2f6f9);} ") as demo:
    with gr.Row():
        gr.HTML("""
        <div style="text-align:center; font-family:Arial;">
            <img src="subhasya.gif" width="220" style="border-radius:50%; box-shadow:0px 6px 15px rgba(0,0,0,0.25); margin-bottom:10px;">
            <h1 style="color:#2c3e50;">👋 Hello, Welcome!</h1>
            <h2 style="color:#34495e;">I am <b>Subhasya</b></h2>
            <p style="font-size:17px; color:#555; line-height:1.5;">
                I’m here to chat with you in a natural voice.<br>
                🎙️ Click the Speak button below and ask me a question.<br>
                I’m excited to share my story with you!
            </p>
        </div>
        """)

    with gr.Row():
        audio_in = gr.Audio(sources=["microphone"], type="filepath", label="🎙️ Speak Here")

    with gr.Row():
        output_text = gr.Textbox(label="💬 Bot Reply", lines=3)
        output_audio = gr.Audio(label="🔊 Bot Voice", type="numpy")

    audio_in.change(fn=voicebot, inputs=audio_in, outputs=[output_text, output_audio])

demo.launch()
