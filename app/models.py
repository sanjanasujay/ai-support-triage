from sqlalchemy import String, Text, Float, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from .db import Base

class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200))
    message: Mapped[str] = mapped_column(Text)

    category: Mapped[str] = mapped_column(String(50), default="Unknown")
    urgency: Mapped[str] = mapped_column(String(20), default="Low")
    summary: Mapped[str] = mapped_column(Text, default="")
    draft_reply: Mapped[str] = mapped_column(Text, default="")

    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    escalated: Mapped[bool] = mapped_column(Boolean, default=False)
