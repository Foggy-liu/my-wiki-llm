from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db import get_db, User
from app.services.auth import get_current_admin
from app.core.lint import LintService

router = APIRouter(prefix="/api/admin", tags=["lint"])

@router.post("/lint")
async def trigger_lint(
    auto_fix: bool = Query(True, description="是否自动修复问题"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    service = LintService(db=db, operator_id=current_user.id)
    result = service.run(auto_fix=auto_fix)
    return result

@router.get("/lint/report")
async def get_lint_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    from app.db import OperationLog
    from sqlalchemy import desc

    log = db.query(OperationLog).filter(
        OperationLog.operation == "lint"
    ).order_by(desc(OperationLog.created_at)).first()

    if not log:
        return {"message": "No lint reports yet"}

    import json
    return {
        "timestamp": log.created_at.isoformat() if log.created_at else None,
        "report": json.loads(log.details) if log.details else {}
    }