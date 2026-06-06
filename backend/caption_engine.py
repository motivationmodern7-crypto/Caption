import os
from groq import Groq

client = Groq(api_key=os.environ.get("GROK_API_KEY"))

def transcribe_video(video_path):
    # Video file ko transcribe karne ke liye Groq API ka use
    with open(video_path, "rb") as file:
        transcription = client.audio.transcriptions.create(
            file=(video_path, file.read()),
            model="whisper-large-v3",
            response_format="verbose_json",
        )
    
    # Simple output format for your frontend
    return [{"text": segment["text"], "start": segment["start"], "end": segment["end"]} 
            for segment in transcription.segments]
