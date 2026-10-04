from enum import Enum
from typing import Generic, TypeVar, Optional, Any, List, Dict
from pydantic import BaseModel, Field
from datetime import datetime

class StateStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    NOT_CONFIGURED = "NOT_CONFIGURED"
    NO_DATA = "NO_DATA"
    PROCESSING = "PROCESSING"
    STALE = "STALE"
    INVALID = "INVALID"
    FAILED = "FAILED"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"

T = TypeVar("T")

class StandardResponse(BaseModel, Generic[T]):
    status: StateStatus
    data: Optional[T] = None
    message: str
    provenance: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class PaginatedResponse(BaseModel, Generic[T]):
    status: StateStatus
    items: List[T] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    page_size: int = 50
    message: str
