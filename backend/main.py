import os
import shutil
import httpx
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

# Groq Client Initialization
# DHAYAN DO: Railway ke Variable mein jo naam rakha hai (GROQ_API_KEY ya GROK_API_KEY), wahi yahan use karna
client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
    http_client=httpx.Client(proxies=None)
)

def convert_to_roman(text):
    """Llama 3.1 ka use karke text ko Roman Urdu mein convert karega"""
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are an expert in converting Urdu text to Roman Urdu (Urdu written in English script)."},
                {"role": "user", "content": f"Convert the following text to Roman Urdu: {text}"}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("Romanization Error:", e)
        return text

@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    video_path = f"temp_{file.filename}"
    audio_path = f"audio_{file.filename}.mp3"
    
    try:
        # 1. File save karo
        with open(video_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 2. Audio extract karo
        clip = mp.VideoFileClip(video_path)
        if clip.audio:
            clip.audio.write_audiofile(audio_path, bitrate="32k", logger=None)
        clip.close()
        
        # 3. Groq se Transcription (Whisper)
        with open(audio_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                file=(audio_path, audio_file.read()),
                model="whisper-large-v3",
                response_format="text"
            )
        
        # 4. Roman Urdu mein conversion
        roman_captions = convert_to_roman(transcript)
        
        # 5. Cleanup
        if os.path.exists(video_path): os.remove(video_path)
        if os.path.exists(audio_path): os.remove(audio_path)
        
        return {"success": True, "captions": roman_captions}
        
    except Exception as e:
        if os.path.exists(video_path): os.remove(video_path)
        if os.path.exists(audio_path): os.remove(audio_path)
        return {"success": False, "error": str(e)}

@app.get("/")
def health_check():
    return {"status": "Backend is live and ready for Roman Urdu!"}
