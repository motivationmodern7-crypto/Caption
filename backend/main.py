import os
import shutil
import moviepy.editor as mp
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq

app = FastAPI()

# CORS middleware zaroori hai frontend se connect karne ke liye
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Groq Client Initialization
client = Groq(
    api_key=os.environ.get("GROQ_API_KEY")
)

@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    # Temporary files ke naam
    video_path = f"temp_{file.filename}"
    audio_path = "temp_audio.mp3"
    
    try:
        # 1. Video save karo
        with open(video_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 2. Audio nikalo (16k bitrate for speed)
        clip = mp.VideoFileClip(video_path)
        clip.audio.write_audiofile(audio_path, bitrate="16k", logger=None)
        clip.close()
        
        # 3. Groq Whisper API (Transcription)
        with open(audio_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                file=(audio_path, audio_file.read()),
                model="whisper-large-v3",
                response_format="text"
            )
            
        # 4. Clean up files
        if os.path.exists(video_path): os.remove(video_path)
        if os.path.exists(audio_path): os.remove(audio_path)
        
        return {"success": True, "captions": transcript}
        
    except Exception as e:
        return {"success": False, "error": str(e)}

# Root endpoint (Backend Check)
@app.get("/")
def read_root():
    return {"status": "Backend is running smooth!"}

# Test endpoint (Live Check)
@app.get("/test")
async def test_backend():
    return {"status": "Backend is working perfectly!"}
