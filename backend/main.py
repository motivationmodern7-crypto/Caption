import os
import shutil
import subprocess
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq

app = FastAPI()

# CORS Fix: Clearly defined origins
origins = [
    "https://frontend8585.up.railway.app",
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def compress_and_extract(input_path, output_audio):
    # Video compress aur audio extract ek saath
    cmd = [
        "ffmpeg", "-i", input_path, 
        "-vn", "-acodec", "libmp3lame", 
        "-q:a", "2", "-y", output_audio
    ]
    subprocess.run(cmd, check=True)

@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    raw_path = "raw_video.mp4"
    audio_path = "temp_audio.mp3"
    
    try:
        with open(raw_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Audio extraction
        compress_and_extract(raw_path, audio_path)
        
        # Transcription
        with open(audio_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                file=(audio_path, audio_file.read()),
                model="whisper-large-v3",
                language="ur",
                response_format="verbose_json"
            )
            
        # Extracting words with timestamps
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
def health_check():
    return {"status": "Backend running correctly"}
