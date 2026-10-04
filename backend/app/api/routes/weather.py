from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from backend.app.core.database import get_db
from backend.app.models.entities import WeatherObservationModel, FarmModel
from backend.app.schemas.common import StandardResponse, StateStatus
from backend.app.schemas.domain import WeatherObservationOut
from backend.app.integrations.weather.nasa_power import NasaPowerProvider
from backend.app.integrations.weather.imd import IMDProvider

router = APIRouter()

nasa_provider = NasaPowerProvider()
imd_provider = IMDProvider()

@router.get("", response_model=StandardResponse[List[WeatherObservationOut]])
def get_weather_observations(
    farm_id: Optional[str] = None,
    limit: int = 30,
    db: Session = Depends(get_db)
):
    query = db.query(WeatherObservationModel)
    if farm_id:
        query = query.filter(WeatherObservationModel.farm_id == farm_id)
    observations = query.order_by(WeatherObservationModel.observed_at.desc()).limit(limit).all()
    
    if not observations:
        return StandardResponse(
            status=StateStatus.NOT_CONFIGURED,
            data=[],
            message="Weather data source not connected. Configure an approved weather data provider (NASA POWER or IMD) to retrieve observations."
        )
    return StandardResponse(
        status=StateStatus.AVAILABLE,
        data=observations,
        message=f"Retrieved {len(observations)} weather observation(s)."
    )

@router.get("/provider-status")
def get_provider_status():
    return {
        "status": StateStatus.AVAILABLE,
        "providers": {
            "NASA_POWER": {
                "configured": nasa_provider.is_configured(),
                "status": "READY" if nasa_provider.is_configured() else "NOT_CONFIGURED",
                "capabilities": ["Daily Agroclimatology", "Solar Radiation", "T2M_MIN/MAX", "Wind Speed"]
            },
            "IMD_GRIDDED": {
                "configured": imd_provider.is_configured(),
                "status": "NOT_CONFIGURED",
                "capabilities": ["0.25° Gridded Rainfall", "Monsoon Baselines"]
            }
        },
        "message": "Weather provider status queried."
    }

@router.post("/sync/nasa-power")
def sync_nasa_power(farm_id: str, start_date: date, end_date: date, db: Session = Depends(get_db)):
    farm = db.query(FarmModel).filter(FarmModel.id == farm_id).first()
    if not farm or farm.latitude is None or farm.longitude is None:
        return StandardResponse(
            status=StateStatus.INSUFFICIENT_DATA,
            data=None,
            message="Farm coordinates (latitude/longitude) are required to query NASA POWER."
        )

    res = nasa_provider.fetch_daily_agrometeorology(
        latitude=farm.latitude,
        longitude=farm.longitude,
        start_date=start_date,
        end_date=end_date
    )
    return res
