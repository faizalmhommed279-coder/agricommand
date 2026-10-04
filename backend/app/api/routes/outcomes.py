from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone
from backend.app.core.database import get_db
from backend.app.models.entities import OutcomeModel, ActionModel, DataCategory
from backend.app.schemas.common import StandardResponse, StateStatus

router = APIRouter()

@router.get("")
def list_outcomes(field_id: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(OutcomeModel)
    if field_id:
        query = query.filter(OutcomeModel.field_id == field_id)
    outcomes = query.order_by(OutcomeModel.observed_at.desc()).all()
    if not outcomes:
        return StandardResponse(
            status=StateStatus.NO_DATA,
            data=[],
            message="No observed outcomes recorded yet. Record actual harvest yields and post-irrigation outcomes to complete the closed-loop decision cycle."
        )
    return StandardResponse(
        status=StateStatus.AVAILABLE,
        data=outcomes,
        message=f"Retrieved {len(outcomes)} observed outcome(s)."
    )

@router.post("")
def record_outcome(
    field_id: str,
    metric_name: str,
    actual_value: float,
    predicted_value: Optional[float] = None,
    action_id: Optional[str] = None,
    provenance_note: Optional[str] = None,
    db: Session = Depends(get_db)
):
    variance = None
    if predicted_value is not None and predicted_value > 0:
        variance = round(((actual_value - predicted_value) / predicted_value) * 100.0, 2)

    outcome = OutcomeModel(
        action_id=action_id,
        field_id=field_id,
        metric_name=metric_name,
        predicted_metric_value=predicted_value,
        actual_metric_value=actual_value,
        variance_percentage=variance,
        data_category=DataCategory.OBSERVED_OUTCOME.value,
        provenance=provenance_note or "Logged via AgriCommand Outcome Observer"
    )
    db.add(outcome)
    db.commit()
    db.refresh(outcome)

    return StandardResponse(
        status=StateStatus.AVAILABLE,
        data=outcome,
        message="Observed outcome recorded for model evaluation."
    )
