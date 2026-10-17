from pydantic import BaseModel

class MinutesResponse(BaseModel):
    transcript: str
    minutes: str