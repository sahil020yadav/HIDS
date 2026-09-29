from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class SecurityLogOut(BaseModel):
    id: int
    user_id: Optional[int]
    event_type: str
    message: str
    severity: str
    created_at: datetime

    class Config:
        from_attributes = True