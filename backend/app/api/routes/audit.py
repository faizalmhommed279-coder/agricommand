from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.app.core.database import get_db
from backend.app.models.entities import AuditEventModel
from backend.app.schemas.common import StandardResponse, StateStatus
from backend.app.schemas.domain import AuditEventOut

router = APIRouter()

@router.get("", response_model=StandardResponse[List[AuditEventOut]])
def get_audit_trail(
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    query = db.query(AuditEventModel)
    if entity_type:
        query = query.filter(AuditEventModel.entity_type == entity_type)
    if entity_id:
        query = query.filter(AuditEventModel.entity_id == entity_id)

    events = query.order_by(AuditEventModel.created_at.desc()).limit(limit).all()
    if not events:
        return StandardResponse(
            status=StateStatus.NO_DATA,
            data=[],
            message="No audit events recorded yet. System mutations, farm registrations, and field configurations will appear here."
        )

    return StandardResponse(
        status=StateStatus.AVAILABLE,
        data=events,
        message=f"Retrieved {len(events)} immutable audit record(s)."
    )
