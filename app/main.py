from fastapi import Depends, FastAPI, File, UploadFile, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from fastapi.responses import FileResponse
import stripe
import secrets
from app.database import SessionLocal, User

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
@app.head("/")
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

# ==========================================
# Stripe Webhook (決済完了通知の受け取り)
# ==========================================

# ※後でStripeダッシュボードから取得した本物のキーに差し替える
import os
stripe.api_key = os.getenv("STRIPE_API_KEY", "")
endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET", "")
@app.post("/webhook")
async def stripe_webhook(request: Request):
    # Stripeから送られてくる生のデータ（ペイロード）を取得
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    # 本来はセキュリティのためにStripeからのリクエストか検証する
    # 今回はテスト用に簡易的にJSONとして読み込む
    import json
    try:
        event = json.loads(payload)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    # 「決済が完了した」というイベントかチェック
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        # 決済したユーザーのメールアドレスを取得
        customer_email = session.get("customer_details", {}).get("email")
        
        if customer_email:
            # 新しいAPIキーを発行 (meeting_から始まるランダムな文字列)
            new_api_key = f"meeting_{secrets.token_urlsafe(32)}"
            
            # データベースに保存
            db = SessionLocal()
            
            # すでに登録済みのメールアドレスか確認
            existing_user = db.query(User).filter(User.email == customer_email).first()
            
            if existing_user:
                # すでにいる場合はキーを更新
                existing_user.api_key = new_api_key
            else:
                # 新規ユーザーとして登録
                user = User(email=customer_email, api_key=new_api_key)
                db.add(user)
            
            db.commit()
            db.close()
            
            print(f"✅ 決済完了: {customer_email} に新しいAPIキーを発行しました")
            
            # 本来はここでメール送信（Resendなど）を行う
            # send_email(customer_email, new_api_key)

    return {"status": "success"}