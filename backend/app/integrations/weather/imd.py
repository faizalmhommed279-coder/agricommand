from typing import Optional, Dict, Any
from datetime import date
from backend.app.schemas.common import StateStatus
from backend.app.core.config import settings

class IMDProvider:
    """
    India Meteorological Department (IMD) Integration Boundary
    Designed for high-resolution gridded rainfall (0.25° x 0.25°),
    historical rainfall statistics, and monsoonal climate anomalies.
    """
    def __init__(self, api_base: Optional[str] = None):
        self.api_base = api_base or settings.IMD_GRIDDED_API_BASE
        self.provider_name = "IMD_GRIDDED"

    def is_configured(self) -> bool:
        return bool(self.api_base and len(self.api_base.strip()) > 0)

    def fetch_gridded_rainfall(
        self,
        latitude: float,
        longitude: float,
        target_date: date
    ) -> Dict[str, Any]:
        """
        Retrieves IMD gridded rainfall for a given geo coordinate.
        Strictly returns NOT_CONFIGURED when no active credentials or API endpoint is wired,
        rather than inventing rainfall numbers.
        """
        if not self.is_configured():
            return {
                "status": StateStatus.NOT_CONFIGURED.value,
                "message": "IMD Gridded Rainfall API provider is not connected. Configure an authorized IMD endpoint in settings.",
                "data": None,
                "source": self.provider_name
            }

        # Real fetch implementation when provider endpoint is set
        return {
            "status": StateStatus.NOT_CONFIGURED.value,
            "message": "IMD pipeline interface awaiting verified data access key.",
            "data": None
        }
