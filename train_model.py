"""
train_model.py
----------------
Training script for OptiCrop.

This script:
1. Loads the crop recommendation dataset (dataset/crop_recommendation.csv)
2. Trains a RandomForestClassifier to recommend a crop based on
   N, P, K, temperature, humidity, ph and rainfall.
3. Trains a supporting RandomForestRegressor that produces an
   *approximate* yield estimate (see README for the honest limitations
   of this component -- there is no public per-hectare yield dataset
   bundled with this project, so the yield figure is a demonstrative,
   heuristic estimate and should not be used for real agronomic
   decisions).
4. Saves model.pkl (crop classifier), scaler.pkl (StandardScaler) and
   yield_model.pkl (yield regressor) so app.py can load them at runtime.

Run with:  python train_model.py
"""

import os
import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report, mean_absolute_error

# ----------------------------------------------------------------------
# Paths
# ----------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(BASE_DIR, "dataset", "crop_recommendation.csv")
MODELS_DIR = os.path.join(BASE_DIR, "models")
os.makedirs(MODELS_DIR, exist_ok=True)

FEATURE_COLUMNS = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]
TARGET_COLUMN = "label"


def load_dataset():
    """Load and lightly validate the crop recommendation dataset."""
    if not os.path.exists(DATASET_PATH):
        raise FileNotFoundError(f"Dataset not found at {DATASET_PATH}")

    df = pd.read_csv(DATASET_PATH)

    missing_cols = [c for c in FEATURE_COLUMNS + [TARGET_COLUMN] if c not in df.columns]
    if missing_cols:
        raise ValueError(f"Dataset is missing required columns: {missing_cols}")

    # Drop rows with missing values, if any
    before = len(df)
    df = df.dropna(subset=FEATURE_COLUMNS + [TARGET_COLUMN])
    after = len(df)
    if before != after:
        print(f"Dropped {before - after} rows containing missing values.")

    return df


def train_crop_classifier(df):
    """Train and evaluate the RandomForestClassifier for crop recommendation."""
    X = df[FEATURE_COLUMNS]
    y = df[TARGET_COLUMN]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=None,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train_scaled, y_train)

    y_pred = model.predict(X_test_scaled)
    acc = accuracy_score(y_test, y_pred)
    print(f"\nCrop Recommendation Model Accuracy: {acc * 100:.2f}%")
    print("\nClassification Report:\n", classification_report(y_test, y_pred))

    return model, scaler


def build_synthetic_yield_dataset(df):
    """
    Build a *synthetic* per-crop yield target for demonstration purposes.

    IMPORTANT (see README): There is no verified public per-hectare yield
    dataset shipped with this project. To still provide a working
    "Yield Prediction" feature end-to-end, we engineer a plausible yield
    figure (tonnes/hectare) from the existing agronomic features using a
    transparent formula plus small random noise, then train a regressor
    on top of it. This keeps the ML pipeline fully functional while being
    explicit that the yield number is an educational approximation, not a
    verified agronomic prediction.
    """
    rng = np.random.default_rng(42)

    # Base yield potential per crop (illustrative tonnes/hectare baseline)
    base_yield = {
        "rice": 4.0, "maize": 3.5, "chickpea": 1.8, "kidneybeans": 1.6,
        "pigeonpeas": 1.5, "mothbeans": 1.2, "mungbean": 1.3, "blackgram": 1.3,
        "lentil": 1.4, "pomegranate": 8.0, "banana": 30.0, "mango": 9.0,
        "grapes": 15.0, "watermelon": 20.0, "muskmelon": 15.0, "apple": 12.0,
        "orange": 14.0, "papaya": 25.0, "coconut": 7.0, "cotton": 2.0,
        "jute": 2.5, "coffee": 1.0,
    }

    df = df.copy()
    df["base_yield"] = df[TARGET_COLUMN].map(base_yield).fillna(3.0)

    # Simple, transparent scoring of how favourable the conditions are,
    # normalised roughly into a 0.5x - 1.3x multiplier band.
    rainfall_score = np.clip(df["rainfall"] / 200.0, 0.5, 1.3)
    humidity_score = np.clip(df["humidity"] / 80.0, 0.5, 1.3)
    ph_score = 1.0 - (abs(df["ph"] - 6.5) / 10.0)
    ph_score = np.clip(ph_score, 0.5, 1.2)
    nutrient_score = np.clip((df["N"] + df["P"] + df["K"]) / 150.0, 0.5, 1.3)

    multiplier = (rainfall_score + humidity_score + ph_score + nutrient_score) / 4.0
    noise = rng.normal(loc=1.0, scale=0.05, size=len(df))

    df["estimated_yield"] = df["base_yield"] * multiplier * noise
    df["estimated_yield"] = df["estimated_yield"].round(2)

    return df


def train_yield_regressor(df):
    """Train the RandomForestRegressor on the synthetic yield target."""
    df = build_synthetic_yield_dataset(df)

    X = df[FEATURE_COLUMNS]
    y = df["estimated_yield"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestRegressor(
        n_estimators=200,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    print(f"\nYield Estimator Mean Absolute Error: {mae:.2f} tonnes/hectare (synthetic target)")

    return model


def main():
    print("Loading dataset...")
    df = load_dataset()
    print(f"Dataset loaded: {df.shape[0]} rows, {df.shape[1]} columns")
    print(f"Number of unique crops: {df[TARGET_COLUMN].nunique()}")

    print("\nTraining crop recommendation model...")
    crop_model, scaler = train_crop_classifier(df)

    print("\nTraining yield estimation model...")
    yield_model = train_yield_regressor(df)

    # Persist all artifacts
    joblib.dump(crop_model, os.path.join(MODELS_DIR, "model.pkl"))
    joblib.dump(scaler, os.path.join(MODELS_DIR, "scaler.pkl"))
    joblib.dump(yield_model, os.path.join(MODELS_DIR, "yield_model.pkl"))

    # Also drop a copy of model.pkl at the project root to match the
    # required folder structure in the assignment brief.
    joblib.dump(crop_model, os.path.join(BASE_DIR, "model.pkl"))

    print("\nSaved artifacts:")
    print(f"  - {os.path.join(MODELS_DIR, 'model.pkl')}")
    print(f"  - {os.path.join(MODELS_DIR, 'scaler.pkl')}")
    print(f"  - {os.path.join(MODELS_DIR, 'yield_model.pkl')}")
    print(f"  - {os.path.join(BASE_DIR, 'model.pkl')}")
    print("\nTraining complete.")


if __name__ == "__main__":
    main()
