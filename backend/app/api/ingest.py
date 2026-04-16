from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pathlib import Path

from app.db import get_db, User
from app.services.auth import get_current_admin
from app.core.ingest import IngestService
from app.config import settings

router = APIRouter(prefix="/api/admin", tags=["ingest"])

@router.post("/ingest/upload")
async def upload_file(
    file: UploadFile = File(...),
    category: str = "articles",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    valid_categories = ["papers", "articles", "transcripts", "docs", "assets"]
    if category not in valid_categories:
        raise HTTPException(status_code=400, detail=f"Invalid category. Must be one of {valid_categories}")

    upload_dir = settings.RAW_DIR / category
    upload_dir.mkdir(parents=True, exist_ok=True)

    file_path = upload_dir / file.filename
    content = await file.read()
    file_path.write_bytes(content)

    return {"message": "File uploaded", "path": str(file_path)}

@router.post("/ingest")
async def trigger_ingest(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    service = IngestService(db=db, operator_id=current_user.id)
    results = await service.run()
    return {"results": results}

@router.get("/ingest/status")
async def get_ingest_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    service = IngestService(db=db)
    pending = service.get_pending_files()
    return {
        "pending_count": len(pending),
        "pending_files": [str(p) for p in pending]
    }