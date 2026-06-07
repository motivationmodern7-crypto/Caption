import os
import shutil
import moviepy.editor as mp
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import openai

app = FastAPI()

# 1. CORS Middleware (Frontend-Backend connection ke liye)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# OpenAI API Key (Apna key yahan daal do ya Environment Variable use karo)
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    video_path = f"temp_{file.filename}"
    audio_path = "temp_audio.mp3"
    
    try:
        # 1. File save karo
        with open(video_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 2. Audio nikalo (MoviePy) - Ye 33MB ki video ko chota MP3 bana dega
        clip = mp.VideoFileClip(video_path)
        clip.audio.write_audiofile(audio_path)
        clip.close()
        
        # 3. OpenAI Whisper ko chhota Audio bhejo
        audio_file = open(audio_path, "rb")
        transcript = openai.Audio.transcribe("whisper-1", audio_file)
        audio_file.close()
        
        # Files delete karo
        if os.path.exists(video_path): os.remove(video_path)
        if os.path.exists(audio_path): os.remove(audio_path)
        
        return {"success": True, "captions": transcript['text']}
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/")
def read_root():
    return {"status": "Backend running"}
