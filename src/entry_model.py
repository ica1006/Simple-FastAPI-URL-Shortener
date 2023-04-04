from pydantic import BaseModel

class Entry(BaseModel):
    _id: str
    query_id: str
    url: str