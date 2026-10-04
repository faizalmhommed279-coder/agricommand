from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.app.core.database import get_db
from backend.app.models.entities import PredictionEntity, PredictionModelEntity
from backend.app.schemas.common import StandardResponse, StateStatus
from backend.app.schemas.domain import PredictionOut, PredictionRequest
from backend.app.analytics.predictions import prediction_service

router = APIRouter()

@router.get("", response_model=StandardResponse[List[PredictionOut]])
def list_predictions(field_id: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(PredictionEntity)
    if field_id:
        query = query.filter(PredictionEntity.field_id == field_id)
    preds = query.order_by(PredictionEntity.created_at.desc()).all()
    if not preds:
        return StandardResponse(
            status=StateStatus.NOT_CONFIGURED,
            data=[],
            message="Prediction model not connected. The prediction interface is ready for a future agricultural model."
        )
    return StandardResponse(
        status=StateStatus.AVAILABLE,
        data=preds,
        message=f"Retrieved {len(preds)} prediction record(s)."
    )

@router.get("/models")
def list_models(db: Session = Depends(get_db)):
    models = db.query(PredictionModelEntity).all()
    if not models:
        return {
            "status": StateStatus.NOT_CONFIGURED,
            "models": [],
            "supported_contracts": [
                "Yield-Prediction-XGBoost-Interface",
                "Water-Demand-Recurrent-Interface",
                "Crop-Stress-Sentinel-Interface"
            ],
            "message": "Prediction model not connected. Train and register an agricultural ML model to enable predictive inferences."
        }
    return {
        "status": StateStatus.AVAILABLE,
        "models": models,
        "message": f"Retrieved {len(models)} registered model definition(s)."
    }

@router.post("/yield-inference")
def run_yield_inference(payload: PredictionRequest):
    """
    Yield prediction interface contract.
    Strictly returns MODEL_NOT_CONFIGURED when no trained weights exist.
    """
    return prediction_service.predict_yield(payload.field_id)

@router.post("/climate-risk-inference")
def run_climate_risk_inference(payload: PredictionRequest):
    return prediction_service.predict_climate_risk(payload.field_id)
