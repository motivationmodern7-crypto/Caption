import os
import shutil
import subprocess
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

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def compress_video(input_path, output_path):
    # FFmpeg command: resolution ko 480p kar raha hai aur size compress kar raha hai
    cmd = [
        "ffmpeg", "-i", input_path, 
        "-vf", "scale=480:-1", 
        "-c:v", "libx264", "-crf", "30", 
        "-c:a", "aac", "-b:a", "64k", 
        "-y", output_path
    ]
    subprocess.run(cmd, check=True)

@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    raw_path = "raw_video.mp4"
    compressed_path = "compressed.mp4"
    audio_path = "temp_audio.mp3"
    
    try:
        with open(raw_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 1. Video Compress karo
        compress_video(raw_path, compressed_path)
        
        # 2. Audio extract karo
        cmd_audio = ["ffmpeg", "-i", compressed_path, "-vn", "-acodec", "libmp3lame", "-q:a", "2", "-y", audio_path]
        subprocess.run(cmd_audio, check=True)
        
        # 3. Transcribe
        with open(audio_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                file=(audio_path, audio_file.read()),
                model="whisper-large-v3",
                language="ur",
                response_format="verbose_json"
            )
            
        # Extraction
        words_data = []
        for segment in transcript.segments:
            for word_info in segment.get('words', []):
                words_data.append({
                    "word": word_info.get('word', '').strip(),
                    "start": word_info.get('start'),
                    "end": word_info.get('end')
                })
        
        # Cleanup
        for path in [raw_path, compressed_path, audio_path]:
            if os.path.exists(path): os.remove(path)
        
        return {"success": True, "captions": [{"words": words_data}]}
        
    except Exception as e:
        return {"success": False, "error": str(e)}
