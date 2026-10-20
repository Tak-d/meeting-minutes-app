from fastapi import Header, HTTPException

from app.config import settings
from app.database import SessionLocal, User

PLAN_LIMITS = {
    "free": settings.free_limit,
    "basic": settings.basic_limit,
    "pro": settings.pro_limit,
    "business": settings.business_limit,
    "admin": 10**9,
}


async def verify_api_key(x_api_key: str = Header(..., alias="X-API-Key")) -> str:
    # 1. 管理者キー（テスト用）のチェック
    if x_api_key == settings.admin_api_key:
        return x_api_key
        
    # 2. DBに登録されている正規ユーザーのキーかチェック
    db = SessionLocal()
    user = db.query(User).filter(User.api_key == x_api_key).first()
    db.close()
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key")
        
    return x_api_key