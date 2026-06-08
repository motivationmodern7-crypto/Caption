import os
import shutil
import subprocess
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq

app = FastAPI()

# CORS: Allow frontend to communicate with backend
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Key check
api_key = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=api_key)

@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    raw_path = "raw_video.mp4"
    audio_path = "temp_audio.mp3"
    
    try:
        # Save file
        with open(raw_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Audio Extraction using ffmpeg
        subprocess.run(["ffmpeg", "-i", raw_path, "-vn", "-acodec", "libmp3lame", "-y", audio_path], check=True)
        
        # Transcribe
        with open(audio_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                file=(audio_path, audio_file.read()),
                model="whisper-large-v3",
                language="ur",
                response_format="verbose_json"
            )
            
        words_data = []
        for segment in transcript.segments:
            for w in segment.get('words', []):
                words_data.append({
                    "word": w.get('word', '').strip(),
                    "start": w.get('start'),
                    "end": w.get('end')
                })
        
        # Cleanup
        if os.path.exists(raw_path): os.remove(raw_path)
        if os.path.exists(audio_path): os.remove(audio_path)
        
        return {"success": True, "captions": [{"words": words_data}]}
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/")
def read_root():
    return {"status": "Active"}
