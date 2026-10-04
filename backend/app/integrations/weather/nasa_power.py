from typing import Optional, Dict, Any
from datetime import date
from backend.app.schemas.common import StateStatus
from backend.app.core.config import settings
import urllib.request
import json
import logging

logger = logging.getLogger(__name__)

class NasaPowerProvider:
    """
    NASA POWER (Prediction of Worldwide Energy Resources) API Integration
    Provides meteorological data, solar radiation, and historical agroclimatology.
    """
    def __init__(self, api_base: Optional[str] = None):
        self.api_base = api_base or settings.NASA_POWER_API_BASE
        self.provider_name = "NASA_POWER"

    def is_configured(self) -> bool:
        return bool(self.api_base)

    def fetch_daily_agrometeorology(
        self,
        latitude: float,
        longitude: float,
        start_date: date,
        end_date: date
    ) -> Dict[str, Any]:
        """
        Fetches T2M_MIN, T2M_MAX, T2M, RH2M, PRECTOTCORR, ALLSKY_SFC_SW_DWN, WS2M
        from NASA POWER.
        Does NOT fabricate any numbers. If request fails or service is unreachable,
        returns explicit error status.
        """
        if not self.is_configured():
            return {
                "status": StateStatus.NOT_CONFIGURED.value,
                "message": "NASA POWER API base URL is not configured.",
                "data": None
            }

        start_str = start_date.strftime("%Y%m%d")
        end_str = end_date.strftime("%Y%m%d")
        parameters = "T2M,T2M_MIN,T2M_MAX,RH2M,PRECTOTCORR,ALLSKY_SFC_SW_DWN,WS2M"
        
        query_url = (
            f"{self.api_base}?parameters={parameters}&community=AG"
            f"&longitude={longitude}&latitude={latitude}"
            f"&start={start_str}&end={end_str}&format=JSON"
        )
        
        try:
            req = urllib.request.Request(
                query_url,
                headers={"User-Agent": "AgriCommand-Platform/1.0"}
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    payload = json.loads(response.read().decode('utf-8'))
                    return {
                        "status": StateStatus.AVAILABLE.value,
                        "data": payload,
                        "source": self.provider_name,
                        "provenance": {
                            "query_url": query_url,
                            "coordinates": [latitude, longitude],
                            "date_range": [start_str, end_str]
                        },
                        "message": "NASA POWER meteorological observations retrieved successfully."
                    }
                else:
                    return {
                        "status": StateStatus.FAILED.value,
                        "message": f"NASA POWER API returned HTTP {response.status}",
                        "data": None
                    }
        except Exception as e:
            logger.warning(f"NASA POWER network fetch failed: {str(e)}")
            return {
                "status": StateStatus.FAILED.value,
                "message": f"Unable to reach NASA POWER service: {str(e)}",
                "data": None
            }
