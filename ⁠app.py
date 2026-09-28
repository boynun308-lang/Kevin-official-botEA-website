import os
import uuid
import shutil
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv

# Load services
from services.video_processing import extract_audio, merge_audio_video
from services.transcription import transcribe_audio
from services.translation import translate_text
from services.text_to_speech import generate_tts

load_dotenv()

app = FastAPI(title="AI Story Translator")

# Setup directories
os.makedirs("uploads", exist_ok=True)
os.makedirs("outputs", exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/upload")
async def upload_video(file: UploadFile = File(...)):
    if not file.filename.endswith(('.mp4', '.mov', '.avi', '.mkv', '.webm')):
        raise HTTPException(status_code=400, detail="Unsupported file format")
    
    file_id = str(uuid.uuid4())
    ext = os.path.splitext(file.filename)[1]
    video_path = f"uploads/{file_id}{ext}"
    
    with open(video_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    return {"file_id": file_id, "video_path": video_path, "filename": file.filename}

@app.post("/api/transcribe")
async def transcribe(video_path: str = Form(...)):
    if not os.path.exists(video_path):
        raise HTTPException(status_code=404, detail="Video not found")
        
    audio_path = video_path.rsplit('.', 1)[0] + ".mp3"
    
    # 1. Extract Audio
    try:
        extract_audio(video_path, audio_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"FFmpeg audio extraction failed: {str(e)}")
        
    # 2. Transcribe
    try:
        script = transcribe_audio(audio_path)
        return {"script": script, "audio_path": audio_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

@app.post("/api/translate")
async def translate(script: str = Form(...), source_lang: str = Form(...), target_lang: str = Form(...)):
    try:
        translated_script = translate_text(script, source_lang, target_lang)
        return {"translated_script": translated_script}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")

@app.post("/api/generate-voice")
async def generate_voice(translated_script: str = Form(...), target_lang: str = Form(...), voice_gender: str = Form(...)):
    file_id = str(uuid.uuid4())
    output_audio = f"outputs/{file_id}.mp3"
    
    try:
        await generate_tts(translated_script, target_lang, voice_gender, output_audio)
        return {"audio_path": output_audio, "audio_url": f"/outputs/{file_id}.mp3"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS failed: {str(e)}")

@app.post("/api/create-video")
async def create_video(video_path: str = Form(...), audio_path: str = Form(...)):
    if not os.path.exists(video_path) or not os.path.exists(audio_path):
        raise HTTPException(status_code=404, detail="Input files missing")
        
    file_id = str(uuid.uuid4())
    output_video = f"outputs/{file_id}.mp4"
    
    try:
        merge_audio_video(video_path, audio_path, output_video)
        return {"video_path": output_video, "video_url": f"/outputs/{file_id}.mp4"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Video creation failed: {str(e)}")

@app.get("/api/download/{filename}")
async def download_file(filename: str):
    file_path = f"outputs/{filename}"
    if os.path.exists(file_path):
        return FileResponse(path=file_path, filename=filename)
    raise HTTPException(status_code=404, detail="File not found")
