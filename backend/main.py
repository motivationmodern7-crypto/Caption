import os
import shutil
import moviepy.editor as mp
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI  # Naya import

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Naya OpenAI client initialization
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    # Unique filenames taaki user data mix na ho
    video_path = f"temp_{file.filename}"
    audio_path = f"audio_{file.filename}.mp3"
    
    try:
        # 1. File save karo
        with open(video_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 2. Audio nikalo (bitrate 32k se file size bahut chota ho jayega)
        clip = mp.VideoFileClip(video_path)
        if clip.audio:
            clip.audio.write_audiofile(audio_path, bitrate="32k", logger=None)
        else:
            raise Exception("Video file mein audio track nahi mila!")
        clip.close()
        
        # 3. OpenAI Whisper ko naye format mein bhejo
        with open(audio_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1", 
                file=audio_file
            )
        
        # 4. Cleanup (Files delete karo)
        if os.path.exists(video_path): os.remove(video_path)
        if os.path.exists(audio_path): os.remove(audio_path)
        
        return {"success": True, "captions": transcript.text}
        
    except Exception as e:
        # Error aane par bhi file saaf karni zaroori hai
        if os.path.exists(video_path): os.remove(video_path)
        if os.path.exists(audio_path): os.remove(audio_path)
        return {"success": False, "error": str(e)}

@app.get("/")
def health_check():
    return {"status": "Backend is live!"}
