import math
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from dataclasses import dataclass
from backend.app.schemas.common import StateStatus

@dataclass
class FAO56WeatherInput:
    temp_min_c: float
    temp_max_c: float
    temp_mean_c: float
    relative_humidity_percent: float
    solar_radiation_mj_m2: float # Rs
    wind_speed_2m_ms: float
    elevation_m: float
    latitude_deg: float
    day_of_year: int

@dataclass
class FAO56CropInput:
    crop_name: str
    growth_stage: str # "INITIAL", "DEV", "MID", "LATE"
    kc_init: float
    kc_mid: float
    kc_end: float
    rooting_depth_m: float
    depletion_fraction_p: float

@dataclass
class FAO56SoilInput:
    field_capacity_volumetric: float # e.g. 0.30 m3/m3
    wilting_point_volumetric: float   # e.g. 0.15 m3/m3
    current_soil_moisture_volumetric: Optional[float] = None

class FAO56WaterDemandEngine:
    """
    FAO Irrigation and Drainage Paper No. 56 Penman-Monteith Calculation Engine
    Deterministic physical formulas for Reference Evapotranspiration (ET0) and Crop ET (ETc).
    Zero fake inputs accepted.
    """

    @staticmethod
    def calculate_et0_penman_monteith(weather: FAO56WeatherInput) -> float:
        """
        Calculates reference evapotranspiration ETo (mm/day) using standard FAO-56 Penman-Monteith.
        """
        t = weather.temp_mean_c
        t_max = weather.temp_max_c
        t_min = weather.temp_min_c
        rh = weather.relative_humidity_percent
        u2 = max(0.5, weather.wind_speed_2m_ms)
        z = weather.elevation_m
        j = weather.day_of_year
        lat_rad = (math.pi / 180.0) * weather.latitude_deg

        # Atmospheric pressure P (kPa)
        p = 101.3 * math.pow((293.0 - 0.0065 * z) / 293.0, 5.26)
        # Psychrometric constant gamma (kPa/°C)
        gamma = 0.000665 * p

        # Slope of saturation vapor pressure curve Delta (kPa/°C)
        delta = 4098.0 * (0.6108 * math.exp((17.27 * t) / (t + 237.3))) / math.pow(t + 237.3, 2)

        # Saturation vapor pressure e_s (kPa)
        e_tmax = 0.6108 * math.exp((17.27 * t_max) / (t_max + 237.3))
        e_tmin = 0.6108 * math.exp((17.27 * t_min) / (t_min + 237.3))
        es = (e_tmax + e_tmin) / 2.0

        # Actual vapor pressure e_a (kPa)
        ea = es * (rh / 100.0)

        # Solar geometry
        dr = 1.0 + 0.033 * math.cos((2.0 * math.pi / 365.0) * j)
        delta_sun = 0.409 * math.sin(((2.0 * math.pi / 365.0) * j) - 1.39)
        ws = math.acos(-math.tan(lat_rad) * math.tan(delta_sun))
        ra = (24.0 * 60.0 / math.pi) * 0.0820 * dr * (
            ws * math.sin(lat_rad) * math.sin(delta_sun) +
            math.cos(lat_rad) * math.cos(delta_sun) * math.sin(ws)
        )
        rso = (0.75 + 2e-5 * z) * ra
        rs = min(weather.solar_radiation_mj_m2, rso)

        # Net shortwave radiation Rns
        rns = (1.0 - 0.23) * rs

        # Net longwave radiation Rnl
        sigma = 4.903e-9 # MJ K^-4 m^-2 day^-1
        t_max_k4 = math.pow(t_max + 273.16, 4)
        t_min_k4 = math.pow(t_min + 273.16, 4)
        rnl = sigma * ((t_max_k4 + t_min_k4) / 2.0) * (0.34 - 0.14 * math.sqrt(ea)) * (1.35 * (rs / max(0.1, rso)) - 0.35)

        # Net radiation Rn
        rn = rns - rnl
        # Soil heat flux G (assumed ~0 for daily timestep)
        g = 0.0

        # Penman-Monteith equation
        numerator = 0.408 * delta * (rn - g) + gamma * (900.0 / (t + 273.0)) * u2 * (es - ea)
        denominator = delta + gamma * (1.0 + 0.34 * u2)

        et0 = numerator / denominator
        return max(0.0, round(et0, 2))

    @staticmethod
    def compute_water_balance(
        weather: Optional[FAO56WeatherInput],
        crop: Optional[FAO56CropInput],
        soil: Optional[FAO56SoilInput]
    ) -> Dict[str, Any]:
        """
        Validates completeness of input observations before running water demand calculations.
        If required inputs are missing, returns INSUFFICIENT_DATA as required.
        """
        missing_inputs = []
        if weather is None:
            missing_inputs.append("Meteorological observations (Temperature, Humidity, Solar Radiation, Wind Speed)")
        if crop is None:
            missing_inputs.append("Active crop growth stage and FAO Kc coefficients")
        if soil is None:
            missing_inputs.append("Soil profile parameters (Field capacity, Wilting point)")

        if missing_inputs:
            return {
                "status": StateStatus.INSUFFICIENT_DATA.value,
                "message": f"Insufficient validated data for water-demand calculation. Missing: {', '.join(missing_inputs)}",
                "data": None
            }

        et0 = FAO56WaterDemandEngine.calculate_et0_penman_monteith(weather)
        
        # Select Kc based on stage
        stage_kc = crop.kc_mid
        if crop.growth_stage.upper() == "INITIAL":
            stage_kc = crop.kc_init
        elif crop.growth_stage.upper() == "LATE":
            stage_kc = crop.kc_end

        etc = round(et0 * stage_kc, 2)

        # Total Available Water (TAW) in root zone (mm)
        taw_mm = 1000.0 * (soil.field_capacity_volumetric - soil.wilting_point_volumetric) * crop.rooting_depth_m
        raw_mm = taw_mm * crop.depletion_fraction_p # Readily Available Water

        # If current soil moisture is provided from validated telemetry:
        ks = 1.0
        depletion_mm = 0.0
        if soil.current_soil_moisture_volumetric is not None:
            theta = soil.current_soil_moisture_volumetric
            # Root zone depletion Dr
            theta_deficit = max(0.0, soil.field_capacity_volumetric - theta)
            depletion_mm = round(1000.0 * theta_deficit * crop.rooting_depth_m, 1)
            if depletion_mm > raw_mm and taw_mm > raw_mm:
                ks = max(0.0, (taw_mm - depletion_mm) / (taw_mm - raw_mm))
            else:
                ks = 1.0

        net_irrigation_requirement_mm = max(0.0, round(depletion_mm, 1))

        return {
            "status": StateStatus.AVAILABLE.value,
            "data": {
                "crop": crop.crop_name,
                "growth_stage": crop.growth_stage,
                "kc": stage_kc,
                "et0_mm_day": et0,
                "etc_mm_day": etc,
                "stress_coefficient_ks": round(ks, 2),
                "taw_mm": round(taw_mm, 1),
                "raw_mm": round(raw_mm, 1),
                "current_depletion_mm": depletion_mm,
                "net_irrigation_requirement_mm": net_irrigation_requirement_mm
            },
            "provenance": {
                "calculation_engine": "FAO-56 Penman-Monteith",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "assumptions": "Daily time step, neutral stability, standardized 0.12m hypothetical grass reference"
            },
            "message": "FAO-56 water-demand calculations computed from validated field and weather observations."
        }
