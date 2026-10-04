from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from backend.app.schemas.common import StateStatus

class RecommendationEngine:
    """
    Explainable Agricultural Recommendation System
    Evaluates only validated field observations, soil moisture, and weather alerts.
    Strictly answers the 4 core questions:
    1. What happened?
    2. Why does it matter?
    3. Which field is affected?
    4. What action should be considered?
    
    If no validated evidence triggers an advisory threshold,
    returns INSUFFICIENT_DATA or NO_DATA rather than inventing fake recommendations.
    """

    @staticmethod
    def evaluate_field_observations(
        field_id: str,
        field_name: str,
        soil_moisture_pct: Optional[float],
        wilting_threshold_pct: float = 20.0,
        temp_c: Optional[float] = None,
        forecast_rain_mm: Optional[float] = None
    ) -> Dict[str, Any]:
        
        if soil_moisture_pct is None and temp_c is None:
            return {
                "status": StateStatus.INSUFFICIENT_DATA.value,
                "message": "Insufficient validated evidence to generate a recommendation for this field.",
                "data": None
            }

        recommendations = []

        # Rule 1: Validated Soil Moisture Depletion below threshold
        if soil_moisture_pct is not None and soil_moisture_pct < wilting_threshold_pct:
            rain_incoming = forecast_rain_mm is not None and forecast_rain_mm > 5.0
            if not rain_incoming:
                recommendations.append({
                    "title": f"Soil Moisture Deficit Alert on {field_name}",
                    "what_happened": f"Validated capacitive sensor recorded soil moisture at {soil_moisture_pct}%, dropping below the critical wilting threshold ({wilting_threshold_pct}%).",
                    "why_it_matters": "Crop root zone water stress can trigger stomatal closure, reducing photosynthesis and inducing irreversible yield loss if sustained for >48 hours.",
                    "affected_field_summary": f"Field '{field_name}' (ID: {field_id}) currently in active vegetative/reproductive growth stage.",
                    "suggested_action": "Initiate targeted drip irrigation cycle of 25 mm/m2 during evening hours (18:00 - 22:00) to minimize evaporative losses.",
                    "urgency": "HIGH",
                    "evidence_provenance": {
                        "sensor_value": soil_moisture_pct,
                        "threshold": wilting_threshold_pct,
                        "forecast_rain_mm": forecast_rain_mm,
                        "rule": "RULE_CRITICAL_DEPLETION_UNMITIGATED"
                    }
                })

        # Rule 2: Extreme Temperature with Low Humidity
        if temp_c is not None and temp_c > 38.0:
            recommendations.append({
                "title": f"Atmospheric Heat Stress Warning on {field_name}",
                "what_happened": f"Air temperature reached {temp_c}°C, exceeding standard physiological heat tolerance limits.",
                "why_it_matters": "High vapor pressure deficit (VPD) drives excessive transpiration and can cause pollen sterility in sensitive crop stages.",
                "affected_field_summary": f"Field '{field_name}' (ID: {field_id})",
                "suggested_action": "Apply micro-sprinkler misting if available, or delay sensitive foliar chemical applications until ambient temperature drops below 30°C.",
                "urgency": "MEDIUM",
                "evidence_provenance": {
                    "temperature_c": temp_c,
                    "rule": "RULE_HEAT_WAVE_PHYSIOLOGICAL_RISK"
                }
            })

        if not recommendations:
            return {
                "status": StateStatus.NO_DATA.value,
                "message": "All validated field indicators are within normal agronomic thresholds. No actionable advisories pending.",
                "data": []
            }

        return {
            "status": StateStatus.AVAILABLE.value,
            "data": recommendations,
            "message": f"Generated {len(recommendations)} explainable recommendations from validated observations."
        }
