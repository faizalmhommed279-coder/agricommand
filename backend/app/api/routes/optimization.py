from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.app.core.database import get_db
from backend.app.models.entities import OptimizationRunModel, FarmModel, FieldModel, WaterResourceModel
from backend.app.schemas.common import StandardResponse, StateStatus
from backend.app.schemas.domain import OptimizationRunRequest, OptimizationRunOut
from backend.app.analytics.optimization import FarmOptimizationEngine, FieldWaterDemandConstraint

router = APIRouter()

@router.get("/runs", response_model=StandardResponse[List[OptimizationRunOut]])
def list_optimization_runs(farm_id: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(OptimizationRunModel)
    if farm_id:
        query = query.filter(OptimizationRunModel.farm_id == farm_id)
    runs = query.order_by(OptimizationRunModel.created_at.desc()).all()
    if not runs:
        return StandardResponse(
            status=StateStatus.NO_DATA,
            data=[],
            message="Optimization data unavailable. Provide validated resource and field constraints to run optimization."
        )
    return StandardResponse(
        status=StateStatus.AVAILABLE,
        data=runs,
        message=f"Retrieved {len(runs)} optimization run(s)."
    )

@router.post("/solve-water-allocation")
def solve_water_allocation(payload: OptimizationRunRequest, db: Session = Depends(get_db)):
    farm = db.query(FarmModel).filter(FarmModel.id == payload.farm_id).first()
    if not farm:
        return StandardResponse(
            status=StateStatus.NO_DATA,
            data=None,
            message="Specified farm does not exist."
        )

    fields = db.query(FieldModel).filter(FieldModel.farm_id == payload.farm_id).all()
    if not fields:
        return StandardResponse(
            status=StateStatus.INSUFFICIENT_DATA,
            data=None,
            message="Optimization cannot run because no fields are configured for this farm."
        )

    field_constraints = []
    priorities = payload.field_priorities or {}
    for f in fields:
        # Default demand derived from area (e.g. 20,000 L / ha)
        area = f.area_hectares or 1.0
        req_liters = area * 20000.0
        prio = priorities.get(f.id, 5)
        field_constraints.append(FieldWaterDemandConstraint(
            field_id=f.id,
            field_name=f.name,
            required_liters=req_liters,
            priority_weight=prio,
            max_flow_rate_lph=5000.0
        ))

    result = FarmOptimizationEngine.solve_water_allocation(
        available_supply_liters=payload.available_water_liters,
        field_demands=field_constraints
    )

    # If successful, persist optimization run record
    if result["status"] == StateStatus.AVAILABLE.value:
        opt_run = OptimizationRunModel(
            farm_id=payload.farm_id,
            domain="WATER_ALLOCATION",
            solver="AgriCommand-Simplex-Linear-Formulation",
            objective_value=result["data"]["total_allocated_liters"],
            status=result["data"]["solver_status"],
            parameters_json={"available_supply_liters": payload.available_water_liters},
            schedule_result_json=result["data"]["allocation_schedule"],
            provenance="Computed via FarmOptimizationEngine"
        )
        db.add(opt_run)
        db.commit()
        db.refresh(opt_run)

    return result
