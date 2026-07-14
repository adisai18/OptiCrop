"""
app.py
-------
OptiCrop: Smart Agricultural Production Optimization Engine

Flask backend that serves:
  - Home page
  - Crop Recommendation (RandomForestClassifier)
  - Fertilizer Recommendation (rule-based agronomic engine)
  - Yield Prediction (RandomForestRegressor, approximate/demo estimate)
  - Weather Integration (OpenWeather API)
  - Dashboard (in-memory prediction history + stats)
  - About / Contact pages

Run with: python app.py
"""

import os
import json
import joblib
import requests
import numpy as np
from datetime import datetime
from flask import Flask, render_template, request, jsonify

from fertilizer_data import recommend_fertilizer, get_ideal_npk

# ----------------------------------------------------------------------
# App configuration
# ----------------------------------------------------------------------
app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")
HISTORY_FILE = os.path.join(BASE_DIR, "history.json")

# OpenWeather API key -- set this as an environment variable before running:
#   export OPENWEATHER_API_KEY="your_api_key_here"        (Linux/Mac)
#   set OPENWEATHER_API_KEY=your_api_key_here             (Windows)
OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY", "")
OPENWEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"

FEATURE_COLUMNS = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]

# ----------------------------------------------------------------------
# Load ML artifacts at startup
# ----------------------------------------------------------------------
def load_artifact(filename, fallback_root_filename=None):
    """Try to load a joblib artifact from models/, falling back to project root."""
    path = os.path.join(MODELS_DIR, filename)
    if os.path.exists(path):
        return joblib.load(path)

    if fallback_root_filename:
        root_path = os.path.join(BASE_DIR, fallback_root_filename)
        if os.path.exists(root_path):
            return joblib.load(root_path)

    return None


crop_model = load_artifact("model.pkl", fallback_root_filename="model.pkl")
scaler = load_artifact("scaler.pkl")
yield_model = load_artifact("yield_model.pkl")

if crop_model is None or scaler is None:
    print("WARNING: Crop model or scaler not found. Run `python train_model.py` first.")


# ----------------------------------------------------------------------
# Simple JSON-file based prediction history (acts as a lightweight DB
# so the Dashboard has real data to show without needing a full database
# setup for this project).
# ----------------------------------------------------------------------
def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []


def save_history(history):
    try:
        with open(HISTORY_FILE, "w") as f:
            json.dump(history, f, indent=2)
    except IOError as e:
        print(f"Could not save history: {e}")


def add_history_entry(entry_type, details):
    """Append a new prediction/recommendation entry to the history log."""
    history = load_history()
    entry = {
        "type": entry_type,
        "details": details,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    history.insert(0, entry)  # newest first
    history = history[:100]  # keep the log bounded
    save_history(history)
    return entry


# ----------------------------------------------------------------------
# Input validation helpers
# ----------------------------------------------------------------------
def parse_float(value, field_name, min_val=None, max_val=None):
    """Parse and validate a numeric form field, raising ValueError on failure."""
    if value is None or str(value).strip() == "":
        raise ValueError(f"{field_name} is required.")
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{field_name} must be a valid number.")

    if min_val is not None and parsed < min_val:
        raise ValueError(f"{field_name} must be greater than or equal to {min_val}.")
    if max_val is not None and parsed > max_val:
        raise ValueError(f"{field_name} must be less than or equal to {max_val}.")

    return parsed


# ----------------------------------------------------------------------
# Routes: pages
# ----------------------------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/crop", methods=["GET"])
def crop_page():
    return render_template("crop.html")


@app.route("/fertilizer", methods=["GET"])
def fertilizer_page():
    crops = sorted(get_ideal_npk.__globals__["IDEAL_NPK"].keys())
    return render_template("fertilizer.html", crops=crops)


@app.route("/dashboard")
def dashboard_page():
    history = load_history()
    total_predictions = len(history)
    recent = history[:10]

    crop_predictions = [h for h in history if h["type"] == "crop"]
    fert_predictions = [h for h in history if h["type"] == "fertilizer"]
    yield_predictions = [h for h in history if h["type"] == "yield"]

    stats = {
        "total": total_predictions,
        "crop_count": len(crop_predictions),
        "fertilizer_count": len(fert_predictions),
        "yield_count": len(yield_predictions),
    }

    return render_template("dashboard.html", recent=recent, stats=stats)


@app.route("/about")
def about_page():
    return render_template("about.html")


@app.route("/contact")
def contact_page():
    return render_template("contact.html")


# ----------------------------------------------------------------------
# API: Crop Recommendation
# ----------------------------------------------------------------------
@app.route("/api/predict-crop", methods=["POST"])
def predict_crop():
    if crop_model is None or scaler is None:
        return jsonify({"error": "Crop model is not loaded on the server."}), 500

    try:
        data = request.get_json(force=True) if request.is_json else request.form

        n = parse_float(data.get("N"), "Nitrogen (N)", 0, 200)
        p = parse_float(data.get("P"), "Phosphorus (P)", 0, 200)
        k = parse_float(data.get("K"), "Potassium (K)", 0, 200)
        temperature = parse_float(data.get("temperature"), "Temperature", -10, 60)
        humidity = parse_float(data.get("humidity"), "Humidity", 0, 100)
        ph = parse_float(data.get("ph"), "pH", 0, 14)
        rainfall = parse_float(data.get("rainfall"), "Rainfall", 0, 500)

        features = np.array([[n, p, k, temperature, humidity, ph, rainfall]])
        features_scaled = scaler.transform(features)

        prediction = crop_model.predict(features_scaled)[0]
        probabilities = crop_model.predict_proba(features_scaled)[0]
        confidence = float(np.max(probabilities)) * 100

        # Top 3 alternative crops
        classes = crop_model.classes_
        top_indices = np.argsort(probabilities)[::-1][:3]
        top_crops = [
            {"crop": classes[i], "confidence": round(float(probabilities[i]) * 100, 2)}
            for i in top_indices
        ]

        # Estimated yield for the recommended crop, if the yield model is available
        estimated_yield = None
        if yield_model is not None:
            estimated_yield = round(float(yield_model.predict(features)[0]), 2)

        result = {
            "recommended_crop": prediction,
            "confidence": round(confidence, 2),
            "top_crops": top_crops,
            "estimated_yield_tonnes_per_ha": estimated_yield,
        }

        add_history_entry("crop", {
            "inputs": {"N": n, "P": p, "K": k, "temperature": temperature,
                       "humidity": humidity, "ph": ph, "rainfall": rainfall},
            "result": result["recommended_crop"],
            "confidence": result["confidence"],
        })

        return jsonify(result)

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Unexpected server error: {str(e)}"}), 500


# ----------------------------------------------------------------------
# API: Fertilizer Recommendation
# ----------------------------------------------------------------------
@app.route("/api/recommend-fertilizer", methods=["POST"])
def api_recommend_fertilizer():
    try:
        data = request.get_json(force=True) if request.is_json else request.form

        crop = str(data.get("crop", "")).strip()
        if not crop:
            raise ValueError("Crop is required.")

        n = parse_float(data.get("N"), "Nitrogen (N)", 0, 200)
        p = parse_float(data.get("P"), "Phosphorus (P)", 0, 200)
        k = parse_float(data.get("K"), "Potassium (K)", 0, 200)

        result = recommend_fertilizer(crop, n, p, k)

        add_history_entry("fertilizer", {
            "crop": crop,
            "inputs": {"N": n, "P": p, "K": k},
            "result": result["name"],
        })

        return jsonify(result)

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Unexpected server error: {str(e)}"}), 500


# ----------------------------------------------------------------------
# API: Yield Prediction (standalone endpoint)
# ----------------------------------------------------------------------
@app.route("/api/predict-yield", methods=["POST"])
def predict_yield():
    if yield_model is None:
        return jsonify({"error": "Yield model is not loaded on the server."}), 500

    try:
        data = request.get_json(force=True) if request.is_json else request.form

        n = parse_float(data.get("N"), "Nitrogen (N)", 0, 200)
        p = parse_float(data.get("P"), "Phosphorus (P)", 0, 200)
        k = parse_float(data.get("K"), "Potassium (K)", 0, 200)
        temperature = parse_float(data.get("temperature"), "Temperature", -10, 60)
        humidity = parse_float(data.get("humidity"), "Humidity", 0, 100)
        ph = parse_float(data.get("ph"), "pH", 0, 14)
        rainfall = parse_float(data.get("rainfall"), "Rainfall", 0, 500)

        features = np.array([[n, p, k, temperature, humidity, ph, rainfall]])
        estimated_yield = round(float(yield_model.predict(features)[0]), 2)

        result = {"estimated_yield_tonnes_per_ha": estimated_yield}

        add_history_entry("yield", {
            "inputs": {"N": n, "P": p, "K": k, "temperature": temperature,
                       "humidity": humidity, "ph": ph, "rainfall": rainfall},
            "result": estimated_yield,
        })

        return jsonify(result)

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Unexpected server error: {str(e)}"}), 500


# ----------------------------------------------------------------------
# API: Weather (OpenWeather integration)
# ----------------------------------------------------------------------
@app.route("/api/weather", methods=["GET"])
def get_weather():
    city = request.args.get("city", "").strip()
    if not city:
        return jsonify({"error": "Please provide a city name, e.g. ?city=Hyderabad"}), 400

    if not OPENWEATHER_API_KEY:
        return jsonify({
            "error": "OpenWeather API key is not configured on the server. "
                     "Set the OPENWEATHER_API_KEY environment variable."
        }), 500

    try:
        params = {
            "q": city,
            "appid": OPENWEATHER_API_KEY,
            "units": "metric",
        }
        response = requests.get(OPENWEATHER_URL, params=params, timeout=10)

        if response.status_code == 404:
            return jsonify({"error": f"City '{city}' not found."}), 404
        if response.status_code != 200:
            return jsonify({"error": "Failed to fetch weather data from OpenWeather."}), 502

        data = response.json()

        result = {
            "city": data.get("name", city),
            "temperature": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "condition": data["weather"][0]["description"].title(),
            "icon": data["weather"][0]["icon"],
            # OpenWeather's free tier does not always return rain volume;
            # default to 0 when absent.
            "rainfall": data.get("rain", {}).get("1h", 0),
        }
        return jsonify(result)

    except requests.exceptions.Timeout:
        return jsonify({"error": "Weather service timed out. Please try again."}), 504
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Could not reach weather service: {str(e)}"}), 502


# ----------------------------------------------------------------------
# API: Dashboard stats (used for AJAX refresh, if needed)
# ----------------------------------------------------------------------
@app.route("/api/dashboard-stats")
def dashboard_stats():
    history = load_history()
    stats = {
        "total": len(history),
        "crop_count": len([h for h in history if h["type"] == "crop"]),
        "fertilizer_count": len([h for h in history if h["type"] == "fertilizer"]),
        "yield_count": len([h for h in history if h["type"] == "yield"]),
        "recent": history[:10],
    }
    return jsonify(stats)


# ----------------------------------------------------------------------
# Error handlers
# ----------------------------------------------------------------------
@app.errorhandler(404)
def not_found(e):
    return render_template("index.html"), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error."}), 500


# ----------------------------------------------------------------------
# Entry point
# ----------------------------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug_mode = os.environ.get("FLASK_DEBUG", "True") == "True"
    app.run(host="0.0.0.0", port=port, debug=debug_mode)
