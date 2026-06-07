import os
import shutil
import moviepy.editor as mp
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq

app = FastAPI()

# CORS for Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Groq Client
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    video_path = "temp_video.mp4"
    audio_path = "temp_audio.mp3"
    
    try:
        # Save file
        with open(video_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Audio extraction
        clip = mp.VideoFileClip(video_path)
        clip.audio.write_audiofile(audio_path, bitrate="16k", logger=None)
        clip.close()
        
        # Transcribe
        with open(audio_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                file=(audio_path, audio_file.read()),
                model="whisper-large-v3", # Final model set
                response_format="verbose_json"
            )
            
        # Extraction logic
        words_list = []
        if hasattr(transcript, 'words') and transcript.words:
            words_list = [{"word": w.word.strip(), "start": w.start, "end": w.end} for w in transcript.words]
        elif hasattr(transcript, 'segments') and transcript.segments:
            for segment in transcript.segments:
                seg_words = segment.get('words', []) if isinstance(segment, dict) else getattr(segment, 'words', [])
                for word_info in seg_words:
                    words_list.append({
                        "word": word_info.get('word', '').strip() if isinstance(word_info, dict) else word_info.word.strip(),
                        "start": word_info.get('start') if isinstance(word_info, dict) else word_info.start,
                        "end": word_info.get('end') if isinstance(word_info, dict) else word_info.end
                    })

        # Return format
        formatted_captions = [{"text": transcript.text, "words": words_list}]
            
        # Cleanup
        if os.path.exists(video_path): os.remove(video_path)
        if os.path.exists(audio_path): os.remove(audio_path)
        
        return {"success": True, "captions": formatted_captions}
        
    except Exception as e:
        if os.path.exists(video_path): os.remove(video_path)
        if os.path.exists(audio_path): os.remove(audio_path)
        return {"success": False, "error": str(e)}

@app.get("/")
def read_root():
    return {"status": "Backend is running smooth!"}

@app.get("/test")
async def test_backend():
    return {"status": "Backend is working perfectly!"}
