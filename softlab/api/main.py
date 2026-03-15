from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from softlab.api.routers import analyses, projects


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="SoftLab API",
    description="Software Quality Laboratory",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyses.router, prefix="/api/v1/analyses", tags=["analyses"])
app.include_router(projects.router, prefix="/api/v1/projects", tags=["projects"])


@app.get("/health")
async def health():
    return {"status": "ok", "service": "softlab-api"}
