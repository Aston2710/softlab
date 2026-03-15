from sqlalchemy import String, Integer, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from softlab.models.project import Base


class Issue(Base):
    __tablename__ = "issues"

    id:          Mapped[str] = mapped_column(String, primary_key=True)
    analysis_id: Mapped[str] = mapped_column(String, ForeignKey("analyses.id"), nullable=False)
    module_id:   Mapped[str] = mapped_column(String, nullable=False)
    rule_id:     Mapped[str] = mapped_column(String, nullable=False)
    severity:    Mapped[str] = mapped_column(String, nullable=False)
    title:       Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    suggestion:  Mapped[str] = mapped_column(String, nullable=False)
    file_path:   Mapped[str] = mapped_column(String, nullable=False)
    line_start:  Mapped[int] = mapped_column(Integer, nullable=False)
    line_end:    Mapped[int | None] = mapped_column(Integer, nullable=True)
    extra_data:  Mapped[dict] = mapped_column(JSON, default=dict)
