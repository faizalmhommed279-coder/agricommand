from typing import Optional, Dict, Any
from backend.app.schemas.common import StateStatus
from backend.app.core.config import settings
import urllib.request
import json
import logging

logger = logging.getLogger(__name__)

class SoilGridsProvider:
    """
    ISRIC SoilGrids 2.0 Integration
    Provides global regional soil property priors (sand, silt, clay, organic carbon, pH, CEC)
    at 250m spatial resolution.
    STRICT RULE: Regional SoilGrids priors are strictly marked with provenance 'REGIONAL_PRIOR'
    and are never misrepresented as local laboratory field measurements.
    """
    def __init__(self, api_base: Optional[str] = None):
        self.api_base = api_base or settings.ISRIC_SOILGRIDS_API_BASE
        self.provider_name = "ISRIC_SOILGRIDS"

    def is_configured(self) -> bool:
        return bool(self.api_base and len(self.api_base.strip()) > 0)

    def fetch_regional_priors(
        self,
        latitude: float,
        longitude: float
    ) -> Dict[str, Any]:
        """
        Queries ISRIC SoilGrids REST API for standard physical and chemical layers.
        """
        if not self.is_configured():
            return {
                "status": StateStatus.NOT_CONFIGURED.value,
                "message": "SoilGrids REST endpoint not configured.",
                "data": None
            }

        query_url = (
            f"{self.api_base}?lat={latitude}&lon={longitude}"
            f"&property=clay&property=sand&property=silt&property=phh2o&property=soc"
            f"&depth=0-5cm&depth=5-15cm&depth=15-30cm&value=mean"
        )

        try:
            req = urllib.request.Request(
                query_url,
                headers={"User-Agent": "AgriCommand-Platform/1.0", "Accept": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    return {
                        "status": StateStatus.AVAILABLE.value,
                        "data": data,
                        "provenance": {
                            "source": "ISRIC_SOILGRIDS_REGIONAL_PRIOR",
                            "resolution": "250m",
                            "coordinate": [latitude, longitude],
                            "disclaimer": "Regional statistical prior. Not a substitute for certified laboratory soil core analysis."
                        },
                        "message": "Regional SoilGrids priors retrieved successfully."
                    }
                else:
                    return {
                        "status": StateStatus.FAILED.value,
                        "message": f"ISRIC SoilGrids returned HTTP {response.status}",
                        "data": None
                    }
        except Exception as e:
            logger.warning(f"ISRIC SoilGrids fetch failed: {str(e)}")
            return {
                "status": StateStatus.FAILED.value,
                "message": f"Unable to reach ISRIC SoilGrids service: {str(e)}",
                "data": None
            }
