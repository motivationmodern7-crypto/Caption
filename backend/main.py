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

UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Backend is running!"}

@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        captions = transcribe_video(file_path)
        return {"success": True, "captions": captions}
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
