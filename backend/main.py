import os
import shutil
import moviepy.editor as mp
import time
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

@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    video_path = "temp_video.mp4"
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
                language="ur", # Yahan "ur" (Urdu/Hindi mix) set karo
                response_format="verbose_json"
            )
            
        # Structure create karna jo tumhare React 'captions.map' ke liye sahi hai
        words_data = []
        for segment in transcript.segments:
            for word_info in segment.get('words', []):
                words_data.append({
                    "word": word_info.get('word', '').strip(),
                    "start": word_info.get('start'),
                    "end": word_info.get('end')
                })
        
        # Cleanup
        if os.path.exists(video_path): os.remove(video_path)
        if os.path.exists(audio_path): os.remove(audio_path)
        
        # Array return kar rahe hain jisme words ka list hai
        return {"success": True, "captions": [{"words": words_data}]}
        
    except Exception as e:
        return {"success": False, "error": str(e)}
