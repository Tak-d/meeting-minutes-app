from fastapi import Depends, FastAPI, File, UploadFile, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from fastapi.responses import FileResponse

from app.auth import verify_api_key
from app.config import settings
from app.models import MinutesResponse
from app.transcriber import transcribe_audio
from app.summarizer import generate_minutes

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title=settings.app_name, version="0.1.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静的ファイルの配信
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def root():
    return FileResponse("static/index.html")

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/api/v1/minutes", response_model=MinutesResponse)
@limiter.limit("10/minute")
async def create_minutes(
    request: Request,
    file: UploadFile = File(...),
    _: str = Depends(verify_api_key),
):
    audio_bytes = await file.read()
    
    # 1. 文字起こし
    transcript = transcribe_audio(audio_bytes)
    
    # 2. 議事録生成
    minutes = generate_minutes(transcript)
    
    return MinutesResponse(transcript=transcript, minutes=minutes)