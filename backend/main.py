import os
import shutil
import moviepy.editor as mp
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# FIXED: Proxies hata diya, simple client initialization
client = Groq(
    api_key=os.environ.get("GROQ_API_KEY")
)

@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    video_path = f"temp_{file.filename}"
    audio_path = "temp_audio.mp3"
    
    try:
        with open(video_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        clip = mp.VideoFileClip(video_path)
        clip.audio.write_audiofile(audio_path, bitrate="16k", logger=None)
        clip.close()
        
        with open(audio_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                file=(audio_path, audio_file.read()),
                model="whisper-large-v3",
                response_format="text"
            )
            
        if os.path.exists(video_path): os.remove(video_path)
        if os.path.exists(audio_path): os.remove(audio_path)
        
        return {"success": True, "captions": transcript}
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/test")
async def test_backend():
    return {"status": "Backend is working perfectly!"}
def read_root():
    return {"status": "Backend is running smooth!"}
