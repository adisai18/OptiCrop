# 🌱 OptiCrop – AI Powered Smart Crop Recommendation System

## 🎥 Project Demo

👉 **Watch the complete project demonstration here:**
https://drive.google.com/file/d/1Xp04ALaHrwExv4Fd23bRre7_e7xnmRTZ/view?usp=drive_link

---

# 📖 About the Project

OptiCrop is an AI-powered web application developed to assist farmers in making better agricultural decisions. By analyzing soil nutrients and environmental conditions, the system recommends the most suitable crop, suggests an appropriate fertilizer, and predicts the expected crop yield using Machine Learning.

The objective of this project is to support smart farming by providing accurate, fast, and data-driven recommendations through a simple web interface.

---

# ✨ Features

- 🌾 Crop Recommendation based on soil and weather conditions
- 🌱 Fertilizer Recommendation for better crop growth
- 📈 Crop Yield Prediction using Machine Learning
- 📊 Interactive Dashboard with agricultural insights
- 📱 Responsive and user-friendly interface
- ⚡ Fast prediction using pre-trained ML models

---

# 🛠️ Technologies Used

### Programming Language
- Python

### Machine Learning
- Scikit-learn
- Pandas
- NumPy

### Web Development
- Flask
- HTML5
- CSS3
- JavaScript
- Bootstrap

---

# 📂 Project Structure

```
OptiCrop
│
├── app.py
├── train_model.py
├── requirements.txt
├── README.md
│
├── dataset
│   └── crop_recommendation.csv
│
├── models
│   ├── model.pkl
│   ├── scaler.pkl
│   └── yield_model.pkl
│
├── templates
│   ├── index.html
│   ├── crop.html
│   ├── fertilizer.html
│   ├── dashboard.html
│   ├── about.html
│   └── contact.html
│
└── static
    ├── css
    ├── js
    └── images
```

---

# 🧠 How It Works

### Crop Recommendation

The user enters:

- Nitrogen (N)
- Phosphorus (P)
- Potassium (K)
- Temperature
- Humidity
- pH
- Rainfall

The Machine Learning model analyzes these values and recommends the most suitable crop.

---

### Fertilizer Recommendation

The system analyzes soil nutrient values and crop information to recommend an appropriate fertilizer for improving productivity.

---

### Crop Yield Prediction

Using environmental and agricultural parameters, the trained Machine Learning model predicts the expected crop yield.

---

# 🚀 Installation

Clone the repository

```bash
git clone https://github.com/adisai18/OptiCrop.git
```

Go to the project folder

```bash
cd OptiCrop
```

Install required libraries

```bash
pip install -r requirements.txt
```

Run the application

```bash
python app.py
```

Open your browser and visit

```
http://127.0.0.1:5000
```

---

# 📸 Application Pages

- Home Page
- Crop Recommendation
- Fertilizer Recommendation
- Dashboard
- About
- Contact

---

# 📊 Machine Learning Models

This project uses pre-trained Machine Learning models stored inside the **models** folder.

The models are responsible for:

- Crop Recommendation
- Crop Yield Prediction
- Data Scaling

---

# 📌 Future Improvements

- Weather API Integration
- Real-time Market Price Prediction
- Plant Disease Detection
- Multi-language Support
- Mobile Application
- Cloud Deployment

---

# 👨‍💻 Author

**Adi Sai**

B.Tech – Electrical and Electronics Engineering

Minor in Computer Science Engineering

GitHub: https://github.com/adisai18

---

# 📄 License

This project was developed for educational and internship purposes.
