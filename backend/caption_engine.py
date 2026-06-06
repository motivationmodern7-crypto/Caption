import os
import httpx  # <--- Ye import zaroori hai!
from groq import Groq

# Client initialization
client = Groq(
    api_key=os.environ.get("GROK_API_KEY"),
    http_client=httpx.Client(proxies=None)
)

def transcribe_video(video_path):
    # Video file ko transcribe karne ke liye Groq API ka use
    with open(video_path, "rb") as file:
        transcription = client.audio.transcriptions.create(
            file=(video_path, file.read()),
            model="whisper-large-v3",
            response_format="verbose_json",
        )
    
    # Simple output format for your frontend
    # transcription.segments (Groq API ka return structure)
    return [{"text": segment.text, "start": segment.start, "end": segment.end} 
            for segment in transcription.segments]
