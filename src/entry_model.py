from pydantic import BaseModel
from typing import Optional

class Entry(BaseModel):
    _id: Optional[str]
    domain: str
    query_id: str
    url: str