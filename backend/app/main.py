from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.db import Base, engine
from app.api.auth import router as auth_router
from app.api.ingest import router as ingest_router
from app.api.query import router as query_router
from app.api.lint import router as lint_router
from app.api.publish import router as publish_router

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    # Create database tables
    Base.metadata.create_all(bind=engine)

app.include_router(auth_router)
app.include_router(ingest_router)
app.include_router(query_router)
app.include_router(lint_router)
app.include_router(publish_router)

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(status_code=400, content={"detail": str(exc)})

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"detail": f"内部错误: {str(exc)}"})

@app.get("/")
async def root():
    return {"message": "Artifact Wiki API", "version": "0.1.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
