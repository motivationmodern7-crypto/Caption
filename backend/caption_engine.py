import os
import httpx
from groq import Groq

# Client initialization (Q ke saath fix kiya)
client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"), 
    http_client=httpx.Client(proxies=None)
)

def transcribe_video(video_path):
    try:
        with open(video_path, "rb") as file:
            transcription = client.audio.transcriptions.create(
                file=(video_path, file.read()),
                model="whisper-large-v3",
                response_format="verbose_json",
            )
        
        # segments handle karne ke liye check
        return [{"text": segment.text.strip(), "start": segment.start, "end": segment.end} 
                for segment in transcription.segments]
                
    except Exception as e:
        print(f"Transcription Error: {e}")
        return []
