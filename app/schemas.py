from pydantic import BaseModel, Field

class TicketCreate(BaseModel):
    title: str = Field(..., max_length=200)
    message: str

class TicketOut(BaseModel):
    id: int
    title: str
    message: str
    category: str
    urgency: str
    summary: str
    draft_reply: str
    confidence: float
    escalated: bool

    class Config:
        from_attributes = True

class TriageResult(BaseModel):
    category: str
    urgency: str = Field(..., pattern="^(Low|Medium|High|Critical)$")
    summary: str
    draft_reply: str
    confidence: float = Field(..., ge=0, le=1)
