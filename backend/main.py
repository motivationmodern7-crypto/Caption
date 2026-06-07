import os
import shutil
import subprocess
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    raw_path = "raw.mp4"
    audio_path = "audio.mp3"
    
    with open(raw_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Simple extraction using ffmpeg
    subprocess.run(["ffmpeg", "-i", raw_path, "-vn", "-acodec", "libmp3lame", "-y", audio_path], check=True)
    
    with open(audio_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            file=(audio_path, audio_file.read()),
            model="distil-whisper-large-v3",
            response_format="verbose_json"
        )
    
    # YAHAN SE FIX HAI: Hum segments se words nikal rahe hain
    words_data = []
    for segment in transcript.segments:
        # Segment ke andar 'words' list hoti hai
        for w in segment.get('words', []):
            words_data.append({
                "word": w.get('word', '').strip(),
                "start": w.get('start'),
                "end": w.get('end')
            })
            
    # Cleanup
    if os.path.exists(raw_path): os.remove(raw_path)
    if os.path.exists(audio_path): os.remove(audio_path)
    
    # Frontend ko object ka array bhej rahe hain
    return {"success": True, "captions": [{"words": words_data}]}
