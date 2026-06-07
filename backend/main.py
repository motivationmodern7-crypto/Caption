import os
import shutil
import moviepy.editor as mp
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq

app = FastAPI()

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Groq client
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    video_path = "temp_video.mp4"
    audio_path = "temp_audio.mp3"
    
    try:
        # Save uploaded video
        with open(video_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Convert to audio
        clip = mp.VideoFileClip(video_path)
        clip.audio.write_audiofile(audio_path, bitrate="16k", logger=None)
        clip.close()
        
        # Transcribe with Groq
        with open(audio_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                file=(audio_path, audio_file.read()),
                model="distil-whisper-large-v3",
                response_format="verbose_json"
            )
            
        # Extract words safely (handling both 'words' and 'segments' structures)
        words_list = []
        if hasattr(transcript, 'words') and transcript.words:
            words_list = [{"word": w.word.strip(), "start": w.start, "end": w.end} for w in transcript.words]
        elif hasattr(transcript, 'segments') and transcript.segments:
            for segment in transcript.segments:
                # Handle cases where segments might be objects or dicts
                seg_words = segment.get('words', []) if isinstance(segment, dict) else getattr(segment, 'words', [])
                for word_info in seg_words:
                    words_list.append({
                        "word": word_info.get('word', '').strip() if isinstance(word_info, dict) else word_info.word.strip(),
                        "start": word_info.get('start') if isinstance(word_info, dict) else word_info.start,
                        "end": word_info.get('end') if isinstance(word_info, dict) else word_info.end
                    })

        # Format output for frontend
        formatted_captions = [{
            "text": transcript.text,
            "words": words_list
        }]
            
        # Cleanup
        if os.path.exists(video_path): os.remove(video_path)
        if os.path.exists(audio_path): os.remove(audio_path)
        
        return {"success": True, "captions": formatted_captions}
        
    except Exception as e:
        # Cleanup on failure
        if os.path.exists(video_path): os.remove(video_path)
        if os.path.exists(audio_path): os.remove(audio_path)
        return {"success": False, "error": str(e)}

@app.get("/")
def read_root():
    return {"status": "Backend is running smooth!"}

@app.get("/test")
async def test_backend():
    return {"status": "Backend is working perfectly!"}
