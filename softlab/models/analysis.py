from datetime import datetime
from sqlalchemy import String, DateTime, Float, Integer, JSON, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column
from softlab.models.project import Base


class Analysis(Base):
    __tablename__ = "analyses"

    id:          Mapped[str]            = mapped_column(String, primary_key=True)
    project_id:  Mapped[str]            = mapped_column(String, ForeignKey("projects.id"), nullable=False)
    status:      Mapped[str]            = mapped_column(String, default="queued")   # queued|running|completed|failed
    language:    Mapped[str]            = mapped_column(String, nullable=False)
    modules:     Mapped[list]           = mapped_column(JSON, default=list)
    score:       Mapped[float | None]   = mapped_column(Float, nullable=True)
    grade:       Mapped[str | None]     = mapped_column(String(2), nullable=True)
    report:      Mapped[dict | None]    = mapped_column(JSON, nullable=True)
    created_at:  Mapped[datetime]       = mapped_column(DateTime, server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
