from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.app.core.database import get_db
from backend.app.models.entities import RecommendationModel, FieldModel, SensorObservationModel, WeatherObservationModel
from backend.app.schemas.common import StandardResponse, StateStatus
from backend.app.schemas.domain import RecommendationOut, RecommendationCreate
from backend.app.analytics.recommendations import RecommendationEngine

router = APIRouter()

@router.get("", response_model=StandardResponse[List[RecommendationOut]])
def list_recommendations(farm_id: Optional[str] = None, field_id: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(RecommendationModel)
    if farm_id:
        query = query.filter(RecommendationModel.farm_id == farm_id)
    if field_id:
        query = query.filter(RecommendationModel.field_id == field_id)
    recs = query.order_by(RecommendationModel.created_at.desc()).all()
    if not recs:
        return StandardResponse(
            status=StateStatus.NO_DATA,
            data=[],
            message="Insufficient validated evidence to generate a recommendation. Ingest validated sensor or weather observations to trigger agronomic advisories."
        )
    return StandardResponse(
        status=StateStatus.AVAILABLE,
        data=recs,
        message=f"Retrieved {len(recs)} explainable recommendation(s)."
    )

@router.post("/evaluate-field/{field_id}")
def evaluate_field(field_id: str, db: Session = Depends(get_db)):
    field = db.query(FieldModel).filter(FieldModel.id == field_id).first()
    if not field:
        return StandardResponse(
            status=StateStatus.NO_DATA,
            data=None,
            message="Field does not exist."
        )

    # Fetch latest validated soil moisture
    latest_soil_obs = db.query(SensorObservationModel)\
        .filter(SensorObservationModel.field_id == field.id, SensorObservationModel.validation_status == "VALIDATED")\
        .order_by(SensorObservationModel.observed_at.desc()).first()

    sm_pct = latest_soil_obs.calibrated_value if latest_soil_obs else None

    # Fetch latest weather
    latest_weather = db.query(WeatherObservationModel)\
        .filter(WeatherObservationModel.farm_id == field.farm_id)\
        .order_by(WeatherObservationModel.observed_at.desc()).first()

    temp_c = latest_weather.temp_max_c if latest_weather else None
    rain_mm = latest_weather.precipitation_mm if latest_weather else None

    result = RecommendationEngine.evaluate_field_observations(
        field_id=field.id,
        field_name=field.name,
        soil_moisture_pct=sm_pct,
        temp_c=temp_c,
        forecast_rain_mm=rain_mm
    )

    if result["status"] == StateStatus.AVAILABLE.value:
        # Commit recommendations to database
        for item in result["data"]:
            rec = RecommendationModel(
                farm_id=field.farm_id,
                field_id=field.id,
                title=item["title"],
                what_happened=item["what_happened"],
                why_it_matters=item["why_it_matters"],
                affected_field_summary=item["affected_field_summary"],
                suggested_action=item["suggested_action"],
                urgency=item["urgency"],
                evidence_provenance=item["evidence_provenance"]
            )
            db.add(rec)
        db.commit()

    return result
