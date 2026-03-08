"""
HarvestHub — Rule-Based Crop Recommendation Engine
----------------------------------------------------
Uses a decision-table approach: given soil type, temperature (°C),
rainfall (mm), and season, returns the best-suited crop.

This is a deterministic rule-based system (no ML training required).
"""


# ── Decision table ──────────────────────────────────────────────
# Each rule is a dict with optional constraints.  The first rule
# whose constraints ALL match wins.  'None' means "any value ok".

RULES = [
    # --- Kharif (monsoon) crops ---
    {"soil": "alluvial",  "season": "kharif",  "temp_min": 20, "temp_max": 35, "rain_min": 150, "rain_max": 9999, "crop": "Rice"},
    {"soil": "black",     "season": "kharif",  "temp_min": 25, "temp_max": 40, "rain_min": 50,  "rain_max": 150,  "crop": "Cotton"},
    {"soil": "red",       "season": "kharif",  "temp_min": 20, "temp_max": 35, "rain_min": 60,  "rain_max": 200,  "crop": "Maize"},
    {"soil": "loamy",     "season": "kharif",  "temp_min": 25, "temp_max": 40, "rain_min": 100, "rain_max": 9999, "crop": "Sugarcane"},
    {"soil": "sandy",     "season": "kharif",  "temp_min": 25, "temp_max": 45, "rain_min": 30,  "rain_max": 100,  "crop": "Millet"},
    {"soil": "clayey",    "season": "kharif",  "temp_min": 20, "temp_max": 35, "rain_min": 150, "rain_max": 9999, "crop": "Rice"},

    # --- Rabi (winter) crops ---
    {"soil": "alluvial",  "season": "rabi",    "temp_min": 10, "temp_max": 25, "rain_min": 25,  "rain_max": 100,  "crop": "Wheat"},
    {"soil": "black",     "season": "rabi",    "temp_min": 10, "temp_max": 25, "rain_min": 25,  "rain_max": 80,   "crop": "Chickpea"},
    {"soil": "red",       "season": "rabi",    "temp_min": 10, "temp_max": 25, "rain_min": 30,  "rain_max": 80,   "crop": "Lentil"},
    {"soil": "loamy",     "season": "rabi",    "temp_min": 10, "temp_max": 25, "rain_min": 25,  "rain_max": 100,  "crop": "Wheat"},
    {"soil": "sandy",     "season": "rabi",    "temp_min": 10, "temp_max": 25, "rain_min": 20,  "rain_max": 60,   "crop": "Barley"},
    {"soil": "clayey",    "season": "rabi",    "temp_min": 10, "temp_max": 25, "rain_min": 30,  "rain_max": 100,  "crop": "Mustard"},

    # --- Zaid (summer) crops ---
    {"soil": "alluvial",  "season": "zaid",    "temp_min": 25, "temp_max": 45, "rain_min": 0,   "rain_max": 50,   "crop": "Watermelon"},
    {"soil": "black",     "season": "zaid",    "temp_min": 25, "temp_max": 45, "rain_min": 0,   "rain_max": 50,   "crop": "Sunflower"},
    {"soil": "red",       "season": "zaid",    "temp_min": 25, "temp_max": 45, "rain_min": 0,   "rain_max": 60,   "crop": "Groundnut"},
    {"soil": "loamy",     "season": "zaid",    "temp_min": 25, "temp_max": 45, "rain_min": 0,   "rain_max": 50,   "crop": "Cucumber"},
    {"soil": "sandy",     "season": "zaid",    "temp_min": 25, "temp_max": 50, "rain_min": 0,   "rain_max": 40,   "crop": "Muskmelon"},
    {"soil": "clayey",    "season": "zaid",    "temp_min": 25, "temp_max": 45, "rain_min": 0,   "rain_max": 50,   "crop": "Bitter Gourd"},
]

# Fallbacks when no specific rule matches
SEASON_FALLBACKS = {
    "kharif": "Rice",
    "rabi":   "Wheat",
    "zaid":   "Watermelon",
}


def recommend_crop(soil_type: str, temperature: float,
                   rainfall: float, season: str) -> dict:
    """
    Return a recommendation dict:
      { "crop": "...", "reason": "...", "confidence": "high"|"medium" }

    Parameters
    ----------
    soil_type   : one of alluvial, black, red, loamy, sandy, clayey
    temperature : average temperature in °C
    rainfall    : average monthly rainfall in mm
    season      : one of kharif, rabi, zaid
    """
    soil   = soil_type.strip().lower()
    season = season.strip().lower()

    for rule in RULES:
        if rule["soil"] != soil:
            continue
        if rule["season"] != season:
            continue
        if not (rule["temp_min"] <= temperature <= rule["temp_max"]):
            continue
        if not (rule["rain_min"] <= rainfall <= rule["rain_max"]):
            continue

        return {
            "crop": rule["crop"],
            "reason": (
                f"{rule['crop']} grows well in {soil} soil during the "
                f"{season} season with temperatures of {temperature}°C "
                f"and rainfall around {rainfall} mm."
            ),
            "confidence": "high",
        }

    # Partial match — right season but no exact rule
    fallback = SEASON_FALLBACKS.get(season, "Rice")
    return {
        "crop": fallback,
        "reason": (
            f"No exact rule matched your conditions. Based on the "
            f"{season} season, {fallback} is generally a safe choice."
        ),
        "confidence": "medium",
    }
