# 🌾 OptiCrop — Smart Agricultural Production Optimization Engine

OptiCrop is a full-stack, ML-powered web application that helps farmers, students
and agri-tech developers make data-driven decisions about **what to grow, how to
fertilize it, what yield to expect, and what the current weather looks like** —
all from one clean dashboard.

Built for the **APSCHE Internship Program** submission.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🌱 **Crop Recommendation** | RandomForestClassifier (99.5% test accuracy) recommends the best crop from N, P, K, temperature, humidity, pH and rainfall inputs, with a confidence score and top-3 alternatives. |
| 🧪 **Fertilizer Recommendation** | Rule-based agronomic engine compares your soil's NPK profile against ideal ranges per crop and suggests a corrective fertilizer with an explanation. |
| ☁️ **Weather Integration** | Live temperature, humidity, rainfall and conditions for any city via the OpenWeather API. |
| 📈 **Yield Prediction** | RandomForestRegressor gives an approximate expected yield (tonnes/hectare) — see [Limitations](#-known-limitations) below. |
| 📊 **Dashboard** | Total predictions, breakdown by type, and a live recent-activity feed. |
| 🎨 **Modern Responsive UI** | Bootstrap 5 + custom CSS, mobile-friendly, six full pages (Home, Crop, Fertilizer, Dashboard, About, Contact). |

---

## 🗂️ Folder Structure

```
OptiCrop/
├── app.py                     # Flask application (routes + API endpoints)
├── train_model.py             # Script to train and save the ML models
├── fertilizer_data.py         # Rule-based fertilizer knowledge base
├── requirements.txt
├── README.md
├── model.pkl                  # Trained RandomForestClassifier (crop model)
├── history.json                # Auto-generated prediction log (created at runtime)
├── dataset/
│   └── crop_recommendation.csv
├── models/
│   ├── model.pkl               # Crop classifier (duplicate, used by app.py)
│   ├── scaler.pkl              # StandardScaler for crop model inputs
│   └── yield_model.pkl         # Yield regressor
├── templates/
│   ├── index.html
│   ├── crop.html
│   ├── fertilizer.html
│   ├── dashboard.html
│   ├── about.html
│   └── contact.html
└── static/
    ├── css/
    │   └── style.css
    ├── js/
    │   └── script.js
    └── images/
```

---

## 🛠️ Technologies Used

- **Backend:** Python, Flask
- **Machine Learning:** Scikit-Learn (RandomForestClassifier, RandomForestRegressor, StandardScaler), Pandas, NumPy, Joblib
- **Frontend:** HTML5, CSS3, JavaScript (Vanilla, Fetch API), Bootstrap 5, Font Awesome
- **External API:** OpenWeather (current weather data)

---

## ⚙️ Installation

**1. Clone / download the project**
```bash
git clone https://github.com/<your-username>/OptiCrop.git
cd OptiCrop
```

**2. Create a virtual environment (recommended)**
```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. (Optional) Set your OpenWeather API key**

Get a free key at https://openweathermap.org/api, then:

```bash
# Linux / Mac
export OPENWEATHER_API_KEY="your_api_key_here"

# Windows (cmd)
set OPENWEATHER_API_KEY=your_api_key_here
```

If this variable is not set, every page still works — only the live weather
widget on the Home page will show a friendly configuration error.

**5. (Optional) Retrain the models**

Pre-trained `model.pkl`, `scaler.pkl` and `yield_model.pkl` files are already
included in this repo, so this step is optional:

```bash
python train_model.py
```

---

## ▶️ How to Run

```bash
python app.py
```

Then open your browser at **http://127.0.0.1:5000**

Pages available:
- `/` — Home
- `/crop` — Crop Recommendation
- `/fertilizer` — Fertilizer Recommendation
- `/dashboard` — Dashboard
- `/about` — About
- `/contact` — Contact

---

## 📸 Screenshots

> Add screenshots of your running app here before submission, e.g.:
>
> ![Home Page](static/images/screenshot-home.png)
> ![Crop Recommendation](static/images/screenshot-crop.png)
> ![Dashboard](static/images/screenshot-dashboard.png)

---

## 🤖 Model Details

- **Dataset:** `dataset/crop_recommendation.csv` — 2,200 rows, 22 crop classes,
  7 features (N, P, K, temperature, humidity, ph, rainfall).
- **Algorithm:** `RandomForestClassifier` (200 trees), features standardized
  with `StandardScaler`.
- **Test accuracy:** ~99.5% on a stratified 80/20 train/test split.

---

## ⚠️ Known Limitations

- **Yield Prediction is a demonstrative estimate.** No verified public
  per-hectare yield dataset ships with this project. The yield model is
  trained on a transparent, formula-derived synthetic target (see
  `train_model.py` → `build_synthetic_yield_dataset`) built from rainfall,
  humidity, pH and nutrient levels. It is useful for showing an end-to-end
  ML pipeline, but **should not be relied on for real agronomic or financial
  decisions.** Swapping in a real regional yield dataset is the natural next
  step (see Future Improvements).
- **Fertilizer recommendations are rule-based**, not ML-based, using
  commonly published ideal NPK ranges. They are a good general guide but are
  not a substitute for a certified soil test and local agronomist advice.
- **Prediction history** is stored in a local `history.json` file for
  simplicity — this works well for a demo/single-instance deployment but
  should be replaced with a proper database for multi-user production use.

---

## 🚀 Future Improvements

- Replace the synthetic yield target with a real, region-specific yield
  dataset (e.g., from ICAR / data.gov.in) for a genuinely predictive yield
  model.
- Add user authentication so each farmer has their own prediction history.
- Move prediction history from `history.json` to a proper database
  (PostgreSQL/SQLite) with an ORM.
- Add multi-language support (Telugu, Hindi) for wider farmer accessibility.
- Add a mobile app (React Native / Flutter) consuming the same Flask API.
- Integrate satellite/soil-sensor IoT data for real-time soil monitoring.
- Add a downloadable PDF report per recommendation.

---

## 📄 License

This project was built for educational purposes as part of the APSCHE
Internship Program. Free to use and extend for learning.
