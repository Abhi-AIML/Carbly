import pytest
from services.calculator import calculate_footprint, generate_actions, INDIA_AVG_ANNUAL

def test_zero_footprint():
    data = {}
    result = calculate_footprint(data)
    assert result["annual_kg"] == 0.0
    assert result["score"] == 100

def test_petrol_car_calculation():
    data = {
        "transport": {
            "mode": "petrol_car",
            "km_per_day": 10
        }
    }
    # 10 * 30 * 0.192 = 57.6
    result = calculate_footprint(data)
    assert abs(result["monthly_kg"]["transport"] - 57.6) < 0.1

def test_india_grid_energy():
    data = {
        "energy": {
            "kwh_per_month": 100
        }
    }
    # 100 * 0.82 = 82.0
    result = calculate_footprint(data)
    assert abs(result["monthly_kg"]["energy"] - 82.0) < 0.1

def test_action_generation():
    data = {
        "energy": {
            "ac_hours_per_day": 8
        }
    }
    result = calculate_footprint(data)
    actions = result["actions"]
    assert any("24°C" in a["title"] for a in actions)

def test_score_range():
    # Very high footprint
    data = {
        "transport": {"flights_international": 50}
    }
    result = calculate_footprint(data)
    assert 0 <= result["score"] <= 100

def test_benchmarks():
    data = {
        "energy": {"kwh_per_month": 1000} # huge
    }
    result = calculate_footprint(data)
    expected_diff = ((result["annual_kg"] - INDIA_AVG_ANNUAL) / INDIA_AVG_ANNUAL) * 100
    assert abs(result["vs_india_avg"] - expected_diff) < 0.1
