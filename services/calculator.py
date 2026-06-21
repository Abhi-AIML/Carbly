INDIA_GRID_FACTOR = 0.82  # kg CO2 per kWh (CEA 2023)
LPG_FACTOR = 2.98         # kg CO2 per kg LPG (1 cylinder = 14.2 kg)

TRANSPORT_FACTORS = {
    "petrol_car": 0.192,   # kg CO2 per km
    "diesel_car": 0.171,
    "ev_car": 0.082,        # India grid adjusted
    "bike_petrol": 0.089,
    "bike_ev": 0.031,
    "metro": 0.031,
    "bus": 0.089,
    "auto": 0.132,
    "walk": 0.0
}

FLIGHT_FACTORS = {
    "domestic": 0.255,      # kg CO2 per km, avg domestic leg ~800km
    "international": 0.195  # per km, avg intl leg ~5000km
}

FOOD_FACTORS = {
    "beef_meal": 6.61,
    "mutton_meal": 3.9,
    "chicken_meal": 1.84,
    "egg_meal": 0.82,
    "veg_meal": 0.46,
    "dairy_daily": 0.94    # per day average Indian dairy consumption
}

DIGITAL_FACTORS = {
    "streaming_per_hour": 0.036,   # kg CO2 per hour
    "order_delivery": 0.5          # kg CO2 per order (last-mile, packaging)
}

LIFESTYLE_FACTORS = {
    "clothing_item": 10.0   # kg CO2 per new garment (avg fast fashion)
}

INDIA_AVG_ANNUAL = 1800     # kg CO2 per year per capita
GLOBAL_AVG_ANNUAL = 4800
PARIS_TARGET_ANNUAL = 2000

def safe_get(d: dict, key: str, default: float = 0.0) -> float:
    try:
        val = float(d.get(key, default))
        return max(0.0, val) # Clamp negatives to 0
    except (TypeError, ValueError):
        return float(default)

def safe_str(d: dict, key: str, default: str = "") -> str:
    return str(d.get(key, default))

def calculate_footprint(data: dict) -> dict:
    transport_data = data.get("transport", {})
    energy_data = data.get("energy", {})
    food_data = data.get("food", {})
    digital_data = data.get("digital", {})
    lifestyle_data = data.get("lifestyle", {})

    # Transport (Monthly)
    t_mode = safe_str(transport_data, "mode", "walk").lower()
    km_per_day = safe_get(transport_data, "km_per_day")
    t_factor = TRANSPORT_FACTORS.get(t_mode, 0.0)
    
    # Map raw words to mode keys
    if "bike" in t_mode and "ev" in t_mode: t_factor = TRANSPORT_FACTORS["bike_ev"]
    elif "bike" in t_mode: t_factor = TRANSPORT_FACTORS["bike_petrol"]
    elif "petrol" in t_mode and "car" in t_mode: t_factor = TRANSPORT_FACTORS["petrol_car"]
    elif "diesel" in t_mode and "car" in t_mode: t_factor = TRANSPORT_FACTORS["diesel_car"]
    elif "ev" in t_mode and "car" in t_mode: t_factor = TRANSPORT_FACTORS["ev_car"]
    elif "metro" in t_mode: t_factor = TRANSPORT_FACTORS["metro"]
    elif "bus" in t_mode: t_factor = TRANSPORT_FACTORS["bus"]
    elif "auto" in t_mode: t_factor = TRANSPORT_FACTORS["auto"]
    
    monthly_transport_kg = (km_per_day * 30 * t_factor)

    flights_dom = safe_get(transport_data, "flights_domestic")
    flights_int = safe_get(transport_data, "flights_international")
    
    # Assuming avg 800km domestic, 5000km intl per flight. Since factors are per km:
    monthly_transport_kg += (flights_dom * 800 * FLIGHT_FACTORS["domestic"]) / 12
    monthly_transport_kg += (flights_int * 5000 * FLIGHT_FACTORS["international"]) / 12

    # Energy (Monthly)
    kwh = safe_get(energy_data, "kwh_per_month")
    lpg = safe_get(energy_data, "lpg_cylinders_per_month")
    # AC usage is part of kWh usually, but we keep it for actions
    monthly_energy_kg = (kwh * INDIA_GRID_FACTOR) + (lpg * 14.2 * LPG_FACTOR)

    # Food (Monthly)
    diet_type = safe_str(food_data, "diet_type").lower()
    c_meals = safe_get(food_data, "chicken_meals_per_week")
    m_meals = safe_get(food_data, "mutton_meals_per_week")
    b_meals = safe_get(food_data, "beef_meals_per_week")
    
    monthly_food_kg = (c_meals * 4 * FOOD_FACTORS["chicken_meal"]) + \
                      (m_meals * 4 * FOOD_FACTORS["mutton_meal"]) + \
                      (b_meals * 4 * FOOD_FACTORS["beef_meal"])
    
    # Add base veg/dairy
    if "veg" in diet_type or "egg" in diet_type:
        monthly_food_kg += (30 * FOOD_FACTORS["dairy_daily"])
        monthly_food_kg += (60 * FOOD_FACTORS["veg_meal"]) # assuming 2 meals/day
    
    # Digital (Monthly)
    stream_hours = safe_get(digital_data, "streaming_hours_per_day")
    orders = safe_get(digital_data, "online_orders_per_month")
    monthly_digital_kg = (stream_hours * 30 * DIGITAL_FACTORS["streaming_per_hour"]) + (orders * DIGITAL_FACTORS["order_delivery"])

    # Lifestyle (Monthly)
    clothes = safe_get(lifestyle_data, "new_clothes_per_month")
    monthly_lifestyle_kg = (clothes * LIFESTYLE_FACTORS["clothing_item"])

    # Totals
    total_monthly_kg = monthly_transport_kg + monthly_energy_kg + monthly_food_kg + monthly_digital_kg + monthly_lifestyle_kg
    annual_kg = total_monthly_kg * 12

    vs_india_avg = ((annual_kg - INDIA_AVG_ANNUAL) / INDIA_AVG_ANNUAL) * 100 if INDIA_AVG_ANNUAL else 0
    vs_global_avg = ((annual_kg - GLOBAL_AVG_ANNUAL) / GLOBAL_AVG_ANNUAL) * 100 if GLOBAL_AVG_ANNUAL else 0
    vs_paris_target = ((annual_kg - PARIS_TARGET_ANNUAL) / PARIS_TARGET_ANNUAL) * 100 if PARIS_TARGET_ANNUAL else 0

    score = max(0, min(100, int(100 - (annual_kg / GLOBAL_AVG_ANNUAL) * 50)))

    categories = {
        "transport": monthly_transport_kg,
        "energy": monthly_energy_kg,
        "food": monthly_food_kg,
        "digital": monthly_digital_kg,
        "lifestyle": monthly_lifestyle_kg
    }
    top_category = max(categories, key=categories.get)

    footprint_result = {
        "monthly_kg": categories,
        "monthly_kg_total": total_monthly_kg,
        "annual_kg": annual_kg,
        "vs_india_avg": vs_india_avg,
        "vs_global_avg": vs_global_avg,
        "vs_paris_target": vs_paris_target,
        "trees_needed": annual_kg / 21,
        "equivalent_flights": annual_kg / (800 * FLIGHT_FACTORS["domestic"]), # 800km domestic
        "score": score,
        "top_category": top_category
    }

    # Generate actions based on footprint and data
    footprint_result["actions"] = generate_actions(data, footprint_result)

    return footprint_result

def generate_actions(data: dict, footprint: dict) -> list:
    actions = []
    
    transport_data = data.get("transport", {})
    t_mode = safe_str(transport_data, "mode").lower()
    km_per_day = safe_get(transport_data, "km_per_day")
    flights_int = safe_get(transport_data, "flights_international")
    
    energy_data = data.get("energy", {})
    ac_hours = safe_get(energy_data, "ac_hours_per_day")
    
    food_data = data.get("food", {})
    diet_type = safe_str(food_data, "diet_type").lower()
    b_meals = safe_get(food_data, "beef_meals_per_week")
    
    digital_data = data.get("digital", {})
    stream_hours = safe_get(digital_data, "streaming_hours_per_day")
    orders = safe_get(digital_data, "online_orders_per_month")

    # Action Rules
    if ("petrol" in t_mode or "diesel" in t_mode or "car" in t_mode) and km_per_day > 20:
        actions.append({
            "title": "Switch to Metro or Carpool",
            "description": "Switching to public transport or carpooling for your daily commute can significantly cut your transport emissions.",
            "potential_saving_kg_monthly": 30.0,
            "difficulty": "medium",
            "category": "transport",
            "india_specific": True
        })
        
    if ac_hours > 6:
        actions.append({
            "title": "Set AC to 24°C",
            "description": "Running your AC at 24°C instead of 18°C saves about 6% electricity per degree, reducing emissions and your bill.",
            "potential_saving_kg_monthly": 15.0,
            "difficulty": "easy",
            "category": "energy",
            "india_specific": True
        })
        
    if b_meals > 1:
        actions.append({
            "title": "Replace Beef with Chicken",
            "description": "Beef has a very high carbon footprint. Swapping it for chicken even twice a week makes a huge difference.",
            "potential_saving_kg_monthly": 20.0,
            "difficulty": "medium",
            "category": "food",
            "india_specific": False
        })
        
    if stream_hours > 4:
        actions.append({
            "title": "Reduce Video Quality",
            "description": "Watching videos in 720p instead of 4K can save a lot of server energy.",
            "potential_saving_kg_monthly": 2.0,
            "difficulty": "easy",
            "category": "digital",
            "india_specific": False
        })
        
    if flights_int > 2:
        actions.append({
            "title": "Carbon Offset Flights",
            "description": "Consider buying carbon offsets when you fly internationally.",
            "potential_saving_kg_monthly": 50.0,
            "difficulty": "hard",
            "category": "transport",
            "india_specific": False
        })
        
    if orders > 15:
        actions.append({
            "title": "Batch Online Orders",
            "description": "Consolidate your Swiggy, Zomato, or Amazon orders to save on last-mile delivery emissions.",
            "potential_saving_kg_monthly": 5.0,
            "difficulty": "easy",
            "category": "digital",
            "india_specific": True
        })
        
    # If not enough actions, add general ones
    if len(actions) < 3:
        actions.append({
            "title": "Unplug Appliances",
            "description": "Unplug chargers and appliances when not in use to avoid phantom drain.",
            "potential_saving_kg_monthly": 1.5,
            "difficulty": "easy",
            "category": "energy",
            "india_specific": False
        })
    if len(actions) < 3:
        actions.append({
            "title": "Start Composting",
            "description": "Compost your wet waste to reduce methane emissions from landfills.",
            "potential_saving_kg_monthly": 5.0,
            "difficulty": "medium",
            "category": "lifestyle",
            "india_specific": True
        })
        
    # Return top 5 ranked by potential_saving_kg_monthly
    actions.sort(key=lambda x: x["potential_saving_kg_monthly"], reverse=True)
    return actions[:5]
