# 🚦 Smart Traffic Predictor

A smart, interactive traffic and route analysis web application built with **Python and Streamlit**. The application allows users to search for locations, find multiple routes, compare routes using a Smart Route Score, explore traffic predictions, and analyze historical traffic data.

## 🌐 Live Demo

🚀 **Live App:** Add your Streamlit Cloud URL here after deployment.

## 📌 Project Overview

Smart Traffic Predictor is designed to help users make better route decisions by combining:

- 📍 Location search
- 🗺️ Route generation
- ⭐ Smart Route Score
- 🚦 Traffic analysis
- 📊 Historical traffic data
- 🤖 Machine Learning-based traffic prediction
- 📈 Interactive visualizations

The application supports searching for locations beyond the original predefined Dehradun locations for routing and location discovery.

---

## ✨ Features

### 🗺️ Smart Route Finder

- Enter any starting location and destination.
- Search locations using OpenStreetMap/Nominatim.
- Generate multiple possible routes.
- Compare routes based on:
  - Estimated travel time
  - Distance
  - Route efficiency
- Calculate a **Smart Route Score**.
- Automatically recommend the best available route.
- Display routes on an interactive map.

### ⭐ Smart Route Score

Routes are evaluated using a combined score based on:

| Factor | Weight |
|---|---:|
| Estimated Travel Time | 55% |
| Distance | 25% |
| Route Efficiency | 20% |

The route with the highest overall score is recommended.

> **Note:** The current routing system uses estimated route information and does not claim to provide live traffic conditions unless a live traffic data source is connected.

---

## 🔎 Any-Location Search

The application uses **OpenStreetMap Nominatim** for location search.

Users can search for:

- Cities
- Localities
- Roads
- Landmarks
- Other geographic locations

Search results provide multiple matching locations so users can select the correct place.

---

## 🚦 Traffic Prediction

The project includes a Machine Learning-based traffic prediction module.

The current ML pipeline uses traffic-related features such as:

- Hour
- Minute
- Day of week
- Weekend status
- Location
- Weather
- Vehicle count
- Average speed

The application provides traffic volume and congestion predictions based on the trained models.

### 🤖 Machine Learning Models

Two models are currently used:

1. **Random Forest Regressor**
   - Predicts traffic volume.

2. **Random Forest Classifier**
   - Predicts congestion level.

The trained models are stored inside the `models/` directory.

---

## 📊 Historical Traffic Analysis

The application provides historical traffic analysis using the available traffic dataset.

Users can explore:

- Traffic volume
- Average speed
- Vehicle count
- Congestion
- Weather conditions
- Time-based traffic patterns

Interactive charts are created using Plotly.

---

## 📈 Analytics

The dashboard includes interactive visualizations for understanding traffic patterns.

Examples include:

- Traffic volume trends
- Congestion analysis
- Weather-based traffic patterns
- Time-based traffic analysis
- Location-based traffic analysis

---

## 🧠 Technology Stack

### Programming Language

- Python

### Web Framework

- Streamlit

### Data Analysis

- Pandas
- NumPy

### Machine Learning

- Scikit-learn
- Random Forest

### Visualization

- Plotly
- Folium

### Maps & Location Search

- OpenStreetMap
- Nominatim
- OSRM
- Folium
- Streamlit-Folium

### Model Management

- Joblib

---

## 📁 Project Structure

```text
Smart-Traffic-Predictor/
│
├── app.py
├── routing.py
├── train_model.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── data/
│   └── traffic_data.csv
│
├── models/
│   ├── traffic_volume_model.pkl
│   ├── congestion_model.pkl
│   └── feature_columns.pkl
│
└── images/
