# 🚦 Smart Traffic Predictor

> An interactive Data Analytics and Machine Learning dashboard for traffic analysis, route comparison, and intelligent route recommendation.

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://smart-traffic-predictor-36isyyh6pbovnbrytagqsu.streamlit.app/)
[![GitHub Repository](https://img.shields.io/badge/GitHub-Repository-black?logo=github)](https://github.com/sanjanayadav74/Smart-Traffic-Predictor)
[![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-red?logo=streamlit)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 🌐 Live Demo

### 👉 [Open Smart Traffic Predictor Dashboard](https://smart-traffic-predictor-36isyyh6pbovnbrytagqsu.streamlit.app/)

Try the deployed application directly in your browser.

---

## 📌 Overview

**Smart Traffic Predictor** is an interactive **Data Analytics and Machine Learning dashboard** built using Python and Streamlit.

The project combines:

- Data Analytics
- Machine Learning
- Geospatial Location Search
- Road-Network Routing
- Data Visualization
- Interactive Maps
- Route Comparison

The application provides a single dashboard where users can explore traffic-related data, search for real-world locations, compare routes, and view traffic-related machine learning predictions for supported locations.

---

# 📊 Dashboard

The Smart Traffic Predictor dashboard contains multiple components for traffic analysis and route recommendation.

### 🗺️ Route Finder

Users can enter:

- Starting location
- Destination

The application searches for the locations, generates available driving routes, and compares them.

### 🚗 Route Recommendation

Routes are compared using:

- Estimated travel time
- Distance
- Route efficiency

A transparent **Smart Score** is calculated to help identify the most suitable route.

### 📍 Location Search

Users can search for real-world locations and obtain:

- Location name
- Latitude
- Longitude
- Address information

### 📈 Traffic Analytics

The dashboard allows users to explore historical traffic data, including:

- Vehicle count
- Average speed
- Congestion
- Weather conditions
- Time-based traffic patterns
- Location-based traffic information

### 🤖 Machine Learning Predictions

The dashboard uses trained machine learning models to provide traffic-related predictions for locations supported by the training dataset.

### 🌦️ Weather Analysis

Traffic data can be analyzed according to different weather conditions such as:

- Clear
- Cloudy
- Rain
- Fog

### 🚘 Vehicle & Speed Analysis

Users can explore relationships between:

- Vehicle count
- Average speed
- Congestion

### 🗺️ Interactive Route Map

The selected routes are displayed on an interactive map using **Folium**, allowing users to visually compare route options.

### 📋 Dataset Preview

The dashboard also provides a preview of the traffic dataset used for analytics and machine learning.

---

# ✨ Key Features

- 🔎 Real-world location search
- 🗺️ Interactive route visualization
- 🚗 Multiple route comparison
- ⭐ Smart route scoring
- ⏱️ Estimated travel-time comparison
- 📏 Distance comparison
- 📊 Historical traffic analytics
- 🤖 Machine learning predictions
- 🌦️ Weather-based traffic analysis
- 🚘 Vehicle and speed analysis
- 📋 Dataset exploration
- 💻 Interactive Streamlit dashboard
- ☁️ Streamlit Community Cloud deployment

---

# 🧠 Smart Route Score

The project uses a transparent scoring system to compare available routes.

| Factor | Weight |
|---|---:|
| Estimated Travel Time | 55% |
| Distance | 25% |
| Route Efficiency | 20% |

The route with the strongest overall score is recommended as the preferred route.

> The current Smart Score is based on route-network information and does not represent real-time traffic congestion.

---

# 🤖 Machine Learning

The project currently uses two Random Forest models.

## 1. Traffic Volume Prediction

**Model:** Random Forest Regressor

The model predicts traffic volume using traffic-related features from the project dataset.

### Performance

**Mean Absolute Error (MAE): 71.64 vehicles**

---

## 2. Congestion Classification

**Model:** Random Forest Classifier

The model classifies traffic conditions using available traffic-related features.

### Performance

**Accuracy: 76.60%**

> The current models are trained using a synthetic/historical dataset created for this project. Therefore, these models are intended as a project demonstration rather than a live traffic forecasting system.

---

# 📊 Dataset

The project traffic dataset contains features such as:

- Date
- Hour
- Minute
- Day of Week
- Weekend indicator
- Location
- Weather
- Vehicle Count
- Average Speed
- Congestion

The dataset is used for:

- Exploratory data analysis
- Traffic pattern analysis
- Machine learning
- Visualization
- Historical traffic insights

---

# 🔄 How the Project Works

```text
                    SMART TRAFFIC PREDICTOR
                             │
             ┌───────────────┴───────────────┐
             │                               │
       ROUTE FINDER                    ANALYTICS DASHBOARD
             │                               │
     Start + Destination              Location Search
             │                               │
         Geocoding                   Traffic Dataset
             │                               │
       Route Generation              Historical Analysis
             │                               │
      Route Comparison                ML Prediction
             │                               │
       Smart Score                    Visual Insights
             │                               │
      Interactive Map                 Data Exploration
