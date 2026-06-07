from caption_engine import transcribe_video
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/")
def read_root():
    return {"message": "Server is running! Access /transcribe for POST."}
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/transcribe")
@app.post("/transcribe/")
async def transcribe(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Transcription call
    captions = transcribe_video(file_path)
    
    # MEMORY FIX: File delete karo takki server crash na ho
    if os.path.exists(file_path):
        os.remove(file_path)

    return {"success": True, "captions": captions}
