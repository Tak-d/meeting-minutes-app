from fastapi import Header, HTTPException

from app.config import settings

VALID_KEYS: dict[str, dict] = {
    settings.admin_api_key: {"plan": "admin", "limit": 10**9, "used": 0},
}

PLAN_LIMITS = {
    "free": settings.free_limit,
    "basic": settings.basic_limit,
    "pro": settings.pro_limit,
    "business": settings.business_limit,
    "admin": 10**9,
}


async def verify_api_key(x_api_key: str = Header(..., alias="X-API-Key")) -> str:
    if x_api_key not in VALID_KEYS:
        raise HTTPException(status_code=401, detail="Invalid API key")
    info = VALID_KEYS[x_api_key]
    limit = PLAN_LIMITS.get(info["plan"], 0)
    if info["used"] >= limit:
        raise HTTPException(status_code=429, detail="Monthly limit exceeded")
    info["used"] += 1
    return x_api_key