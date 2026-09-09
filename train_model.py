import os
import random
import joblib
import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, accuracy_score


# ============================================================
# 1. CREATE PROJECT DIRECTORIES
# ============================================================

os.makedirs("data", exist_ok=True)
os.makedirs("models", exist_ok=True)


# ============================================================
# 2. GENERATE REALISTIC TRAFFIC DATA
# ============================================================

random.seed(42)
np.random.seed(42)

locations = [
    "Clock Tower",
    "Rajpur Road",
    "ISBT",
    "Ballupur Chowk",
    "Prem Nagar",
    "Dharampur Chowk"
]

weather_conditions = ["Clear", "Cloudy", "Rain", "Fog"]

rows = []

start_date = pd.Timestamp("2025-01-01")

for i in range(5000):

    date = start_date + pd.Timedelta(days=random.randint(0, 364))

    hour = random.randint(6, 22)
    minute = random.choice([0, 15, 30, 45])

    location = random.choice(locations)
    weather = random.choice(weather_conditions)

    day_of_week = date.dayofweek
    is_weekend = 1 if day_of_week >= 5 else 0

    # Peak-hour effect
    if hour in [8, 9]:
        peak_factor = 1.5
    elif hour in [17, 18, 19]:
        peak_factor = 1.6
    elif hour in [13, 14]:
        peak_factor = 1.15
    else:
        peak_factor = 0.75

    # Location effect
    location_factor = {
        "Clock Tower": 1.35,
        "Rajpur Road": 1.20,
        "ISBT": 1.45,
        "Ballupur Chowk": 1.30,
        "Prem Nagar": 1.00,
        "Dharampur Chowk": 1.15
    }[location]

    # Weather effect
    weather_factor = {
        "Clear": 1.00,
        "Cloudy": 1.05,
        "Rain": 0.90,
        "Fog": 0.80
    }[weather]

    base_traffic = 650

    vehicle_count = (
        base_traffic
        * peak_factor
        * location_factor
        * weather_factor
        * (0.85 if is_weekend else 1.0)
        + np.random.normal(0, 80)
    )

    vehicle_count = max(100, int(vehicle_count))

    # Average speed decreases as traffic increases
    average_speed = (
        55
        - (vehicle_count / 70)
        + np.random.normal(0, 3)
    )

    if weather == "Rain":
        average_speed -= 5
    elif weather == "Fog":
        average_speed -= 8

    average_speed = max(10, min(60, round(average_speed, 1)))

    # Congestion classification
    if vehicle_count < 650 and average_speed >= 35:
        congestion = "Low"
    elif vehicle_count < 1050 and average_speed >= 22:
        congestion = "Medium"
    else:
        congestion = "High"

    rows.append([
        date.strftime("%Y-%m-%d"),
        hour,
        minute,
        day_of_week,
        is_weekend,
        location,
        weather,
        vehicle_count,
        average_speed,
        congestion
    ])


columns = [
    "Date",
    "Hour",
    "Minute",
    "DayOfWeek",
    "IsWeekend",
    "Location",
    "Weather",
    "VehicleCount",
    "AverageSpeed",
    "Congestion"
]

df = pd.DataFrame(rows, columns=columns)

# Save dataset
dataset_path = "data/traffic_data.csv"
df.to_csv(dataset_path, index=False)

print("\n" + "=" * 60)
print("SMART TRAFFIC PREDICTOR - DATASET CREATED")
print("=" * 60)
print(f"Dataset saved to: {dataset_path}")
print(f"Total records: {len(df)}")
print("\nFirst 5 records:")
print(df.head())


# ============================================================
# 3. PREPARE DATA FOR MACHINE LEARNING
# ============================================================

# Convert categorical variables into numerical variables
df_encoded = pd.get_dummies(
    df,
    columns=["Location", "Weather"],
    dtype=int
)

feature_columns = [
    column
    for column in df_encoded.columns
    if column not in [
        "Date",
        "VehicleCount",
        "AverageSpeed",
        "Congestion"
    ]
]


# ============================================================
# 4. TRAFFIC VOLUME PREDICTION MODEL
# ============================================================

X_volume = df_encoded[feature_columns]
y_volume = df_encoded["VehicleCount"]

X_train, X_test, y_train, y_test = train_test_split(
    X_volume,
    y_volume,
    test_size=0.20,
    random_state=42
)

volume_model = RandomForestRegressor(
    n_estimators=150,
    random_state=42,
    n_jobs=-1
)

volume_model.fit(X_train, y_train)

volume_predictions = volume_model.predict(X_test)

mae = mean_absolute_error(
    y_test,
    volume_predictions
)

print("\n" + "=" * 60)
print("TRAFFIC VOLUME MODEL")
print("=" * 60)
print(f"Mean Absolute Error: {mae:.2f} vehicles")


# ============================================================
# 5. CONGESTION CLASSIFICATION MODEL
# ============================================================

X_congestion = df_encoded[feature_columns]
y_congestion = df_encoded["Congestion"]

X_train_c, X_test_c, y_train_c, y_test_c = train_test_split(
    X_congestion,
    y_congestion,
    test_size=0.20,
    random_state=42,
    stratify=y_congestion
)

congestion_model = RandomForestClassifier(
    n_estimators=150,
    random_state=42,
    n_jobs=-1
)

congestion_model.fit(
    X_train_c,
    y_train_c
)

congestion_predictions = congestion_model.predict(X_test_c)

accuracy = accuracy_score(
    y_test_c,
    congestion_predictions
)

print("\n" + "=" * 60)
print("CONGESTION CLASSIFICATION MODEL")
print("=" * 60)
print(f"Accuracy: {accuracy * 100:.2f}%")


# ============================================================
# 6. SAVE MODELS
# ============================================================

joblib.dump(
    volume_model,
    "models/traffic_volume_model.pkl"
)

joblib.dump(
    congestion_model,
    "models/congestion_model.pkl"
)

# Save feature names for dashboard prediction
joblib.dump(
    feature_columns,
    "models/feature_columns.pkl"
)

print("\n" + "=" * 60)
print("MODELS SAVED SUCCESSFULLY")
print("=" * 60)
print("models/traffic_volume_model.pkl")
print("models/congestion_model.pkl")
print("models/feature_columns.pkl")

print("\nProject training completed successfully! 🚦")