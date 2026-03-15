import uuid
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from softlab.api.deps import get_db
from softlab.models.project import Project

router = APIRouter()


class ProjectCreate(BaseModel):
    name: str
    owner_id: str = "anonymous"


class ProjectResponse(BaseModel):
    id: str
    name: str
    owner_id: str

    model_config = {"from_attributes": True}


@router.post("", response_model=ProjectResponse, status_code=201)
async def create_project(payload: ProjectCreate, db: AsyncSession = Depends(get_db)):
    project = Project(
        id=str(uuid.uuid4()),
        name=payload.name,
        owner_id=payload.owner_id,
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return project
