from fastapi import APIRouter
from ...schemas.simulation import SimulationRequest, SimulationResult
from ...services.simulation_engine import run_simulation
router=APIRouter(prefix="/api/simulation",tags=["Simulation"])
@router.post("/run",response_model=SimulationResult)
def run(payload:SimulationRequest):
    return run_simulation(**payload.model_dump())
