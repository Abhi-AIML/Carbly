from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from services.calculator import calculate_footprint, INDIA_AVG_ANNUAL, GLOBAL_AVG_ANNUAL, PARIS_TARGET_ANNUAL

router = APIRouter()

# --- Pydantic Models for Input Validation ---

class TransportInput(BaseModel):
    mode: str = Field("walk", max_length=50, description="Primary transport mode")
    km_per_day: float = Field(0.0, ge=0, le=1000)
    flights_domestic: float = Field(0.0, ge=0, le=200)
    flights_international: float = Field(0.0, ge=0, le=200)

class EnergyInput(BaseModel):
    kwh_per_month: float = Field(0.0, ge=0, le=10000)
    ac_hours_per_day: float = Field(0.0, ge=0, le=24)
    ac_units: float = Field(0.0, ge=0, le=20)
    lpg_cylinders_per_month: float = Field(0.0, ge=0, le=20)

class FoodInput(BaseModel):
    diet_type: str = Field("veg", max_length=50)
    chicken_meals_per_week: float = Field(0.0, ge=0, le=50)
    mutton_meals_per_week: float = Field(0.0, ge=0, le=50)
    beef_meals_per_week: float = Field(0.0, ge=0, le=50)

class DigitalInput(BaseModel):
    streaming_hours_per_day: float = Field(0.0, ge=0, le=24)
    online_orders_per_month: float = Field(0.0, ge=0, le=500)

class LifestyleInput(BaseModel):
    new_clothes_per_month: float = Field(0.0, ge=0, le=200)
    daily_steps: float = Field(0.0, ge=0, le=100000)

class CarbonDataInput(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    city: Optional[str] = Field(None, max_length=100)
    transport: TransportInput = TransportInput()
    energy: EnergyInput = EnergyInput()
    food: FoodInput = FoodInput()
    digital: DigitalInput = DigitalInput()
    lifestyle: LifestyleInput = LifestyleInput()

# --- Endpoints ---

@router.post("/calculate")
async def calculate_endpoint(data: CarbonDataInput):
    """Calculate carbon footprint from validated input data."""
    result = calculate_footprint(data.model_dump())
    return result

@router.get("/benchmarks")
async def benchmarks_endpoint():
    """Return India, Global, and Paris Agreement benchmark values."""
    return {
        "india_avg_annual": INDIA_AVG_ANNUAL,
        "global_avg_annual": GLOBAL_AVG_ANNUAL,
        "paris_target_annual": PARIS_TARGET_ANNUAL
    }
