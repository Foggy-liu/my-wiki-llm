from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from .database import Base

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"

class OperationType(str, enum.Enum):
    INGEST = "ingest"
    QUERY = "query"
    LINT = "lint"
    PUBLISH = "publish"

class OperationStatus(str, enum.Enum):
    SUCCESS = "success"
    FAILED = "failed"
    IN_PROGRESS = "in_progress"

class PageStatus(str, enum.Enum):
    ACTIVE = "active"
    STALE = "stale"
    ARCHIVED = "archived"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default=UserRole.USER.value)
    created_at = Column(DateTime, default=datetime.utcnow)

class WikiPage(Base):
    __tablename__ = "wiki_pages"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    category = Column(String(50), nullable=False)
    file_path = Column(String(500), nullable=False)
    confidence = Column(Float, default=0.5)
    status = Column(String(20), default=PageStatus.ACTIVE.value)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class OperationLog(Base):
    __tablename__ = "operation_logs"

    id = Column(Integer, primary_key=True, index=True)
    operation = Column(String(20), nullable=False)
    status = Column(String(20), nullable=False)
    details = Column(Text)
    operator_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
