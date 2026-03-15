import uuid
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from softlab.api.deps import get_db
from softlab.models.analysis import Analysis

router = APIRouter()


class AnalysisCreate(BaseModel):
    project_id: str
    source_url: str | None = None
    modules: list[str] = ["static"]
    config: dict = {}


class AnalysisResponse(BaseModel):
    id: str
    status: str
    project_id: str
    language: str
    score: float | None
    grade: str | None

    model_config = {"from_attributes": True}


@router.post("", response_model=AnalysisResponse, status_code=202)
async def create_analysis(payload: AnalysisCreate, db: AsyncSession = Depends(get_db)):
    analysis = Analysis(
        id=str(uuid.uuid4()),
        project_id=payload.project_id,
        status="queued",
        language="unknown",
        modules=payload.modules,
    )
    db.add(analysis)
    await db.commit()
    await db.refresh(analysis)
    return analysis


@router.get("/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis(analysis_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Analysis).where(Analysis.id == analysis_id))
    analysis = result.scalar_one_or_none()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return analysis
