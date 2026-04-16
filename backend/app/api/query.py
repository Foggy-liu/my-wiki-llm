from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List

from app.db import get_db, User
from app.services.auth import get_current_user
from app.core.query import QueryService

router = APIRouter(prefix="/api/user", tags=["query"])

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    question: str
    answer: str
    sources: List[str]
    pages_used: List[str]
    confidence: float

@router.post("/query", response_model=QueryResponse)
async def query_knowledge(
    request: QueryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = QueryService(db=db, user_id=current_user.id)
    result = await service.query(request.question)
    return result

@router.get("/query/history")
async def get_query_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = QueryService(db=db, user_id=current_user.id)
    return {"history": service.get_query_history()}