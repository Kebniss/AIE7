from pydantic import BaseModel

class InvokeRequest(BaseModel):
    input: str

