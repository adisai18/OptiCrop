"""
fertilizer_data.py
--------------------
Rule-based fertilizer recommendation knowledge base.

There is no public, verified fertilizer-recommendation dataset bundled
with this project, so this module encodes commonly published agronomic
guidance (ideal NPK ranges per crop group and standard fertilizer
remedies) into a transparent, rule-based engine. This keeps the
recommendation logic explainable and easy to extend, and is documented
as such in the README.
"""

# Ideal average NPK requirement (kg/ha) for representative crop groups.
# Values are illustrative/typical agronomic guidance figures used to
# compare against the user's soil test values.
IDEAL_NPK = {
    "rice": {"N": 80, "P": 40, "K": 40},
    "maize": {"N": 80, "P": 40, "K": 20},
    "chickpea": {"N": 40, "P": 60, "K": 20},
    "kidneybeans": {"N": 20, "P": 60, "K": 20},
    "pigeonpeas": {"N": 20, "P": 60, "K": 20},
    "mothbeans": {"N": 20, "P": 40, "K": 20},
    "mungbean": {"N": 20, "P": 40, "K": 20},
    "blackgram": {"N": 40, "P": 60, "K": 20},
    "lentil": {"N": 20, "P": 60, "K": 20},
    "pomegranate": {"N": 20, "P": 10, "K": 40},
    "banana": {"N": 100, "P": 75, "K": 50},
    "mango": {"N": 20, "P": 20, "K": 30},
    "grapes": {"N": 20, "P": 125, "K": 200},
    "watermelon": {"N": 100, "P": 10, "K": 50},
    "muskmelon": {"N": 100, "P": 10, "K": 50},
    "apple": {"N": 20, "P": 125, "K": 200},
    "orange": {"N": 20, "P": 10, "K": 10},
    "papaya": {"N": 50, "P": 50, "K": 50},
    "coconut": {"N": 20, "P": 10, "K": 30},
    "cotton": {"N": 120, "P": 40, "K": 20},
    "jute": {"N": 80, "P": 40, "K": 40},
    "coffee": {"N": 100, "P": 20, "K": 30},
}

# Default (fallback) requirement if a crop is not present in IDEAL_NPK
DEFAULT_NPK = {"N": 50, "P": 50, "K": 50}

# Common fertilizer products used to correct each type of deficiency/excess
FERTILIZER_GUIDE = {
    "N_low": {
        "name": "Urea (46% N)",
        "advice": "Nitrogen is below the ideal level for this crop. Apply "
                   "Urea or a nitrogen-rich fertilizer to promote healthy "
                   "vegetative growth and leaf development.",
    },
    "N_high": {
        "name": "Reduce Nitrogen application",
        "advice": "Nitrogen is above the ideal level. Excess nitrogen can "
                   "delay flowering/fruiting and increase pest susceptibility. "
                   "Reduce or skip the next nitrogen dose.",
    },
    "P_low": {
        "name": "Single Super Phosphate (SSP) / DAP",
        "advice": "Phosphorus is below the ideal level. Apply SSP or DAP to "
                   "support root development and flowering.",
    },
    "P_high": {
        "name": "Reduce Phosphorus application",
        "advice": "Phosphorus is above the ideal level. Excess phosphorus can "
                   "interfere with micronutrient uptake (zinc/iron). Reduce "
                   "phosphatic fertilizer application.",
    },
    "K_low": {
        "name": "Muriate of Potash (MOP)",
        "advice": "Potassium is below the ideal level. Apply MOP or "
                   "Sulphate of Potash to improve fruit quality, disease "
                   "resistance and water regulation.",
    },
    "K_high": {
        "name": "Reduce Potassium application",
        "advice": "Potassium is above the ideal level. Reduce potassic "
                   "fertilizer doses to avoid nutrient imbalance with "
                   "magnesium and calcium.",
    },
    "balanced": {
        "name": "Balanced NPK (e.g., 19:19:19)",
        "advice": "Nitrogen, Phosphorus and Potassium levels are all close "
                   "to the ideal range for this crop. Continue with a "
                   "balanced maintenance fertilizer schedule and monitor "
                   "soil health periodically.",
    },
}

# Tolerance band (kg/ha) within which a nutrient is considered "balanced"
TOLERANCE = 10


def get_ideal_npk(crop: str) -> dict:
    """Return the ideal NPK dict for a crop, or the default if unknown."""
    return IDEAL_NPK.get(crop.lower().strip(), DEFAULT_NPK)


def recommend_fertilizer(crop: str, n: float, p: float, k: float) -> dict:
    """
    Compare the given N, P, K values against the ideal range for the crop
    and return a structured recommendation.
    """
    ideal = get_ideal_npk(crop)

    diffs = {
        "N": n - ideal["N"],
        "P": p - ideal["P"],
        "K": k - ideal["K"],
    }

    # Find the nutrient with the largest absolute deviation from ideal
    primary_nutrient = max(diffs, key=lambda key: abs(diffs[key]))
    primary_diff = diffs[primary_nutrient]

    if abs(primary_diff) <= TOLERANCE:
        key = "balanced"
    elif primary_diff < 0:
        key = f"{primary_nutrient}_low"
    else:
        key = f"{primary_nutrient}_high"

    result = FERTILIZER_GUIDE[key].copy()
    result["crop"] = crop
    result["ideal_npk"] = ideal
    result["input_npk"] = {"N": n, "P": p, "K": k}
    result["deviation"] = diffs
    result["status"] = key
    return result
