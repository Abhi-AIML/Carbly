from fastapi import APIRouter
from typing import Dict, Any
from services.calculator import calculate_footprint, INDIA_AVG_ANNUAL, GLOBAL_AVG_ANNUAL, PARIS_TARGET_ANNUAL

router = APIRouter()

@router.post("/calculate")
async def calculate_endpoint(data: Dict[str, Any]):
    # In production, add further input validation using Pydantic models here
    result = calculate_footprint(data)
    return result

@router.get("/benchmarks")
async def benchmarks_endpoint():
    return {
        "india_avg_annual": INDIA_AVG_ANNUAL,
        "global_avg_annual": GLOBAL_AVG_ANNUAL,
        "paris_target_annual": PARIS_TARGET_ANNUAL
    }
