from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db import get_db, User
from app.services.auth import get_current_admin
from app.core.publish import PublishService

router = APIRouter(prefix="/api/admin", tags=["publish"])

@router.post("/publish")
async def trigger_publish(
    format: str = Query("markdown", description="输出格式: markdown 或 html"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    if format not in ["markdown", "html"]:
        return {"error": "Format must be 'markdown' or 'html'"}

    service = PublishService(db=db, operator_id=current_user.id)
    result = service.publish(format=format)
    return result