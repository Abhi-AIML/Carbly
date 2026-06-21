import os
import re
import json
import logging
from google import genai
from google.genai import types
from dotenv import load_dotenv

logger = logging.getLogger("carbly.gemini")

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
client = None
if api_key:
    client = genai.Client(api_key=api_key)
    logger.info("Gemini API client initialized successfully.")
else:
    logger.warning("GEMINI_API_KEY not set. AI features will be unavailable.")

SYSTEM_PROMPT = """You are Carbly's onboarding assistant — warm, encouraging, and knowledgeable about carbon emissions. 
Your job is to collect the user's lifestyle information through natural conversation to calculate their carbon footprint.

Ask questions one at a time in a friendly, conversational way. Collect:
1. Name and city in India they live in
2. Primary mode of transport (bike, car petrol/diesel/EV, metro, bus, auto, walk)
3. Approximate km travelled per day
4. Whether they own a car — fuel type and engine size
5. Number of flights taken in last 12 months (domestic vs international)
6. Monthly electricity consumption in units (kWh) OR average bill in INR
7. Hours of AC usage per day and number of ACs
8. LPG cylinder usage per month
9. Diet type: veg / eggetarian / non-veg (how often chicken, mutton, beef)
10. Approximate online orders per month (Flipkart, Amazon, Swiggy, Zomato)
11. Hours of video streaming per day (YouTube, Netflix, etc.)
12. New clothing items purchased per month
13. Daily steps (if they track it) — used to estimate avoided car trips

Once all data is collected, respond with a special JSON block wrapped in ```carbly_data``` markers so the frontend can detect it and unlock the dashboard.

Format:
```carbly_data
{
  "name": "",
  "city": "",
  "transport": { "mode": "", "km_per_day": 0, "flights_domestic": 0, "flights_international": 0 },
  "energy": { "kwh_per_month": 0, "ac_hours_per_day": 0, "ac_units": 0, "lpg_cylinders_per_month": 0 },
  "food": { "diet_type": "", "chicken_meals_per_week": 0, "mutton_meals_per_week": 0, "beef_meals_per_week": 0 },
  "digital": { "streaming_hours_per_day": 0, "online_orders_per_month": 0 },
  "lifestyle": { "new_clothes_per_month": 0, "daily_steps": 0 }
}
```
After sending the JSON, congratulate the user warmly and tell them their dashboard is ready.
"""

DASHBOARD_SYSTEM_PROMPT = """You are Carbly's AI Sustainability Coach. The user has unlocked their dashboard.
Answer questions about their carbon footprint, reduction strategies, and their specific data.
IMPORTANT RULES:
- Be highly professional, smart, and concise. 
- NEVER output long, boring paragraphs. Break down information.
- Use markdown tables, bullet points, and bold text to structure data clearly.
- Present numerical data in small, scannable lists or tables, not in sentences.
- DO NOT use emojis. Keep the tone professional, analytical, and actionable.
- Focus on precise insights rather than generic advice."""

def get_chat_response(history: list, user_message: str, phase: str = "onboarding") -> tuple[str, bool, dict | None]:
    if not client:
        return "System configuration error: Gemini API key is not set.", False, None

    prompt = SYSTEM_PROMPT if phase == "onboarding" else DASHBOARD_SYSTEM_PROMPT
    
    # Format history for Gemini
    formatted_history = [
        types.Content(role="user", parts=[types.Part.from_text(text=prompt)]),
        types.Content(role="model", parts=[types.Part.from_text(text="Understood. I will follow these instructions.")])
    ]
    
    for msg in history:
        # Avoid passing system-like prompts as history directly, map them to user/model roles.
        role = "model" if msg.get("role") == "ai" else "user"
        formatted_history.append(types.Content(role=role, parts=[types.Part.from_text(text=msg.get("content", ""))]))
        
    formatted_history.append(types.Content(role="user", parts=[types.Part.from_text(text=user_message)]))
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=formatted_history
        )
        reply = response.text
        
        # Check for carbly_data
        data_collected = False
        carbly_data = None
        
        if phase == "onboarding":
            match = re.search(r'```carbly_data\s*(\{.*?\})\s*```', reply, re.DOTALL)
            if match:
                data_collected = True
                try:
                    carbly_data = json.loads(match.group(1))
                except json.JSONDecodeError:
                    logger.warning("Failed to parse carbly_data JSON from Gemini response.")
                    
        return reply, data_collected, carbly_data
    except Exception as e:
        logger.error("Gemini API Error: %s", e, exc_info=True)
        return "I'm having a little trouble connecting right now. Could you please try again?", False, None
