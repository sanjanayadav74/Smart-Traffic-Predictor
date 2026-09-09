🚦 Smart Traffic Predictor

<p align="center">
  <strong>Intelligent Traffic Analysis • Smart Route Recommendation • Machine Learning</strong>
</p>

<p align="center">
  A Streamlit-based traffic intelligence dashboard that combines location search, route comparison, traffic prediction, historical analysis, and interactive maps in one application.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/Streamlit-App-red?style=for-the-badge&logo=streamlit" alt="Streamlit">
  <img src="https://img.shields.io/badge/Machine%20Learning-Random%20Forest-orange?style=for-the-badge" alt="Machine Learning">
  <img src="https://img.shields.io/badge/Maps-OpenStreetMap-green?style=for-the-badge&logo=openstreetmap" alt="OpenStreetMap">
  <img src="https://img.shields.io/badge/Status-Active-success?style=for-the-badge" alt="Status">
</p>

🌐 Live Demo

🚀 Live App: Add your Streamlit Cloud URL here

📂 GitHub Repository:
https://github.com/sanjanayadav74/Smart-Traffic-Predictor

📸 Dashboard Preview

Add your latest application screenshot as images/dashboard.png in the repository.

<p align="center">
  <img src="images/dashboard.png" alt="Smart Traffic Predictor Dashboard" width="900">
</p>

✨ What This Project Does

Smart Traffic Predictor is an interactive web application designed to make traffic analysis and route planning easier.

The application lets users:

🔎 Search for real-world locations

🗺️ Find and compare multiple driving routes

⭐ Calculate a Smart Route Score

🚦 Analyze traffic conditions

🤖 Predict traffic volume and congestion

📊 Explore historical traffic data

📈 View interactive analytics

🌍 Work with locations beyond the original fixed Dehradun route inputs

🗺️ Smart Route Finder

Enter any starting location and destination to generate available driving routes.

The application:

Searches and geocodes the locations.

Requests route information.

Finds multiple route alternatives where available.

Calculates a Smart Route Score.

Recommends the best available route.

Displays the selected route and alternatives on an interactive map.

⭐ Smart Route Score

The current scoring system combines three factors:

Travel Time      → 55%
Distance         → 25%
Route Efficiency → 20%

pie showData
    title Smart Route Score
    "Estimated Travel Time" : 55
    "Distance" : 25
    "Route Efficiency" : 20

Important: The current routing layer uses estimated route information. It does not claim to provide live traffic conditions unless a live traffic data provider is connected.

🔎 Any-Location Search

The application uses OpenStreetMap Nominatim for location discovery.

Users can search for:

🏙️ Cities

🛣️ Roads

📍 Localities

🏛️ Landmarks

🌎 Locations outside Dehradun

Search results provide multiple matching places so the user can select the correct location.

🚦 Traffic Prediction

The Machine Learning module predicts traffic-related outcomes using features such as:

Hour

Minute

Day of week

Weekend status

Location

Weather

Vehicle count

Average speed

🤖 Models

Model

Purpose

Random Forest Regressor

Traffic volume prediction

Random Forest Classifier

Congestion prediction

📊 Current Model Results

The current training run achieved:

Traffic Volume Model MAE: 71.64 vehicles

Congestion Model Accuracy: 76.60%

xychart-beta
    title "Congestion Model Accuracy"
    x-axis ["Accuracy"]
    y-axis "Percentage" 0 --> 100
    bar [76.60]

xychart-beta
    title "Traffic Volume Model Error"
    x-axis ["MAE"]
    y-axis "Vehicles" 0 --> 100
    bar [71.64]

These metrics describe the current training dataset/model and should not be interpreted as real-time traffic accuracy for every city.

📊 Historical Traffic Analytics

The dashboard provides historical analysis for locations represented in the available dataset.

Users can explore:

🚗 Vehicle count

🚦 Traffic volume

🏎️ Average speed

🔴 Congestion

🌦️ Weather conditions

🕐 Time-based traffic patterns

Interactive visualizations are powered by Plotly.

🧠 Project Architecture

flowchart TD
    A[User] --> B[Streamlit Dashboard]

    B --> C[Location Search]
    B --> D[Smart Route Finder]
    B --> E[Traffic Prediction]
    B --> F[Historical Analytics]

    C --> G[OpenStreetMap Nominatim]
    D --> H[Routing Engine]
    H --> I[Route Alternatives]
    I --> J[Smart Route Score]
    J --> K[Best Route Recommendation]
    K --> L[Interactive Map]

    E --> M[Feature Engineering]
    M --> N[Random Forest Models]
    N --> O[Traffic Volume]
    N --> P[Congestion]

    F --> Q[Traffic Dataset]
    Q --> R[Interactive Charts]

🔄 Application Workflow

flowchart LR
    A[Enter Location] --> B[Geocode]
    B --> C[Generate Routes]
    C --> D[Analyze Routes]
    D --> E[Calculate Smart Score]
    E --> F[Recommend Route]
    F --> G[Show Interactive Map]

🛠️ Technology Stack

Programming

Python

Web Application

Streamlit

Data Analysis

Pandas

NumPy

Machine Learning

Scikit-learn

Random Forest Regressor

Random Forest Classifier

Joblib

Visualization

Plotly

Folium

Maps & Geocoding

OpenStreetMap

Nominatim

OSRM

Streamlit-Folium

📁 Project Structure

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
    └── dashboard.png

⚙️ Installation

1. Clone the repository

git clone https://github.com/sanjanayadav74/Smart-Traffic-Predictor.git

2. Open the project

cd Smart-Traffic-Predictor

3. Create a virtual environment

python -m venv venv

4. Activate it

Windows:

venv\Scripts\activate

macOS/Linux:

source venv/bin/activate

5. Install dependencies

pip install -r requirements.txt

▶️ Run Locally

Start the application with:

streamlit run app.py

Then open:

http://localhost:8501

🤖 Train the Machine Learning Models

To retrain the models:

python train_model.py

The generated models are saved in:

models/

📦 Main Dependencies

pandas
numpy
scikit-learn
streamlit
plotly
openpyxl
joblib
requests
folium
streamlit-folium

⚠️ Current Limitations

The current Machine Learning dataset contains a limited set of training locations and synthetic traffic observations.

Therefore:

The ML model is not yet a universal real-time traffic predictor.

Historical analysis is limited to locations represented in the dataset.

Routing information is based on the available routing service.

Live traffic prediction requires integration with a real-time traffic data provider.

The location-search and routing architecture is designed so that real-time traffic data can be integrated in future versions.

🚀 Future Improvements

🌐 Real-time traffic API integration

🚗 Live congestion detection

🧠 Generalized traffic prediction across cities

🛰️ Road-level traffic features

🌦️ Real-time weather integration

📍 City-wide traffic analytics

📱 Mobile-friendly UI

🔔 Traffic alerts

🛣️ Congestion-aware alternative routes

📊 Advanced traffic forecasting

🎯 Use Cases

Daily route planning

Traffic analysis

Transportation research

Delivery route planning

Smart-city demonstrations

Data analytics portfolios

Machine Learning projects

Route optimization

👩‍💻 Author

Sanjana Yadav

B.Tech Computer Science & Engineering | Data Analytics

Skills: Python • SQL • Excel • Power BI • Pandas • NumPy • Data Visualization • Machine Learning

Connect With Me

💼 LinkedIn: https://www.linkedin.com/in/sanjana-yadav-5226a0376

💻 GitHub: https://github.com/sanjanayadav74

⭐ Support

If you find this project useful, please consider giving the repository a ⭐.

📄 License

This project is created for educational, portfolio, and demonstration purposes.
