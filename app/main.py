from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .db import Base, engine, get_db
from .models import Ticket
from .schemas import TicketCreate, TicketOut
from .llm import triage_ticket
from .config import settings

app = FastAPI(title="AI Support Triage Backend", version="0.1.0")

@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.post("/tickets", response_model=TicketOut)
async def create_ticket(payload: TicketCreate, db: AsyncSession = Depends(get_db)):
    try:
        result = triage_ticket(payload.title, payload.message)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"LLM triage failed: {str(e)}")

    escalated = float(result.confidence) < float(settings.confidence_threshold)

    ticket = Ticket(
        title=payload.title,
        message=payload.message,
        category=result.category,
        urgency=result.urgency,
        summary=result.summary,
        draft_reply=result.draft_reply,
        confidence=float(result.confidence),
        escalated=escalated,
    )
    db.add(ticket)
    await db.commit()
    await db.refresh(ticket)
    return ticket

@app.get("/tickets/{ticket_id}", response_model=TicketOut)
async def get_ticket(ticket_id: int, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Ticket).where(Ticket.id == ticket_id))
    ticket = res.scalar_one_or_none()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/metrics/basic")
async def basic_metrics(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Ticket))
    tickets = res.scalars().all()
    total = len(tickets)
    escalated = sum(1 for t in tickets if t.escalated)
    high_or_critical = sum(1 for t in tickets if t.urgency in ("High", "Critical"))
    avg_conf = (sum(t.confidence for t in tickets) / total) if total else 0.0
    return {
        "tickets_total": total,
        "tickets_escalated": escalated,
        "tickets_high_or_critical": high_or_critical,
        "avg_confidence": round(avg_conf, 4),
        "confidence_threshold": settings.confidence_threshold,
    }
