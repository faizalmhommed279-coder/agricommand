from sqlalchemy.orm import Session
from backend.app.models.entities import AuditEventModel
from typing import Optional, Dict, Any

def log_audit_event(
    db: Session,
    action: str,
    entity_type: str,
    entity_id: str,
    source: str,
    user_id: Optional[str] = None,
    previous_state: Optional[Dict[str, Any]] = None,
    new_state: Optional[Dict[str, Any]] = None,
    model_version: Optional[str] = None
) -> AuditEventModel:
    event = AuditEventModel(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        previous_state=previous_state,
        new_state=new_state,
        source=source,
        model_version=model_version
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event
