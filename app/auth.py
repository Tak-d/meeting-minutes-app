from fastapi import Header, HTTPException

from app.config import settings
from app.database import SessionLocal, User

# 管理者は無制限、一般ユーザーは30回まで
PLAN_LIMITS = {
    "admin": 10**9, 
    "pro": 30,      
}

async def verify_api_key(x_api_key: str = Header(..., alias="X-API-Key")) -> str:
    # 1. 管理者キーのチェック
    if x_api_key == settings.admin_api_key:
        return x_api_key
        
    # 2. DBに登録されているキーかチェック
    db = SessionLocal()
    user = db.query(User).filter(User.api_key == x_api_key).first()
    
    if not user:
        db.close()
        raise HTTPException(status_code=401, detail="Invalid API key")
        
    # 3. 利用回数のチェック
    if user.used_count >= PLAN_LIMITS["pro"]:
        db.close()
        raise HTTPException(status_code=429, detail="月間の利用上限（30回）に達しました。プランをアップグレードしてください。")
        
    # 4. 利用回数をカウントアップ
    user.used_count += 1
    db.commit()
    db.close()
    
    return x_api_key