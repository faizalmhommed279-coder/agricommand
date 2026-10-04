from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from backend.app.schemas.common import StateStatus
from abc import ABC, abstractmethod

class BaseAgriculturalModel(ABC):
    """
    Abstract Base Class for Agricultural Prediction Models (XGBoost, Scikit-learn, PyTorch)
    """
    @abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def predict(self, feature_vector: Dict[str, Any]) -> Dict[str, Any]:
        pass

class PredictionService:
    """
    Agricultural Prediction Service Boundary
    Manages model registration, execution contracts, and strict state reporting.
    Does NOT fabricate fake predictions. If model weights are not loaded,
    strictly returns MODEL_NOT_CONFIGURED.
    """
    def __init__(self):
        self._registered_models: Dict[str, BaseAgriculturalModel] = {}

    def register_model(self, model_key: str, model_instance: BaseAgriculturalModel):
        self._registered_models[model_key] = model_instance

    def has_active_model(self, model_key: str) -> bool:
        return model_key in self._registered_models

    def predict_yield(self, field_id: str, context_features: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Yield prediction interface.
        Inputs: Crop, Variety, Field, Planting date, Weather baselines, Soil tests, NDVI.
        Returns MODEL_NOT_CONFIGURED if no trained model artifact is registered.
        """
        model_key = "YIELD_PREDICTION_V1"
        if not self.has_active_model(model_key):
            return {
                "status": StateStatus.NOT_CONFIGURED.value,
                "model_key": model_key,
                "data": None,
                "message": "Yield prediction model not configured. The prediction interface is ready for a future agricultural model (e.g. XGBoost / Crop Growth Simulation)."
            }

        model = self._registered_models[model_key]
        return model.predict(context_features or {})

    def predict_climate_risk(self, field_id: str, weather_trends: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Climate risk prediction interface (Heat stress, drought exposure, heavy rain).
        Returns MODEL_NOT_CONFIGURED until calibrated risk model is wired.
        """
        model_key = "CLIMATE_RISK_V1"
        if not self.has_active_model(model_key):
            return {
                "status": StateStatus.NOT_CONFIGURED.value,
                "model_key": model_key,
                "data": None,
                "message": "Climate-risk prediction model not configured. Connect historical hazard dataset to run risk inferences."
            }
        
        return self._registered_models[model_key].predict(weather_trends or {})

prediction_service = PredictionService()
