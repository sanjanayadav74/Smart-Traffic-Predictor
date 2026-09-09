import os
import joblib
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Smart Traffic Predictor",
    page_icon="🚦",
    layout="wide"
)


# ============================================================
# LOAD DATA AND MODELS
# ============================================================

DATA_PATH = "data/traffic_data.csv"
VOLUME_MODEL_PATH = "models/traffic_volume_model.pkl"
CONGESTION_MODEL_PATH = "models/congestion_model.pkl"
FEATURES_PATH = "models/feature_columns.pkl"


@st.cache_data
def load_data():
    return pd.read_csv(DATA_PATH)


@st.cache_resource
def load_models():
    volume_model = joblib.load(VOLUME_MODEL_PATH)
    congestion_model = joblib.load(CONGESTION_MODEL_PATH)
    feature_columns = joblib.load(FEATURES_PATH)

    return volume_model, congestion_model, feature_columns


# Check required files
required_files = [
    DATA_PATH,
    VOLUME_MODEL_PATH,
    CONGESTION_MODEL_PATH,
    FEATURES_PATH
]

missing_files = [file for file in required_files if not os.path.exists(file)]

if missing_files:
    st.error("Required project files are missing:")
    for file in missing_files:
        st.write(f"- {file}")

    st.info("Please run: python train_model.py")
    st.stop()


df = load_data()

volume_model, congestion_model, feature_columns = load_models()


# ============================================================
# HEADER
# ============================================================

st.title("🚦 Smart Traffic Predictor")
st.markdown(
    "### Intelligent Traffic Volume Prediction & Congestion Analysis"
)

st.markdown(
    """
    This application uses historical traffic data and machine learning
    to analyze traffic patterns and predict future traffic conditions.
    """
)

st.divider()


# ============================================================
# SIDEBAR FILTERS
# ============================================================

st.sidebar.header("🔎 Dashboard Filters")

locations = sorted(df["Location"].unique())

selected_location = st.sidebar.selectbox(
    "Select Location",
    locations
)

selected_weather = st.sidebar.multiselect(
    "Weather",
    sorted(df["Weather"].unique()),
    default=sorted(df["Weather"].unique())
)

filtered_df = df[
    (df["Location"] == selected_location)
    & (df["Weather"].isin(selected_weather))
]


# ============================================================
# KPI SECTION
# ============================================================

total_vehicles = int(filtered_df["VehicleCount"].sum())
average_speed = filtered_df["AverageSpeed"].mean()
average_vehicles = filtered_df["VehicleCount"].mean()
high_congestion = (
    filtered_df["Congestion"].value_counts().get("High", 0)
)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "🚗 Total Vehicles",
        f"{total_vehicles:,}"
    )

with col2:
    st.metric(
        "⚡ Average Speed",
        f"{average_speed:.1f} km/h"
    )

with col3:
    st.metric(
        "📊 Avg. Vehicles/Record",
        f"{average_vehicles:.0f}"
    )

with col4:
    st.metric(
        "🔴 High Congestion Records",
        f"{high_congestion:,}"
    )


st.divider()


# ============================================================
# TRAFFIC ANALYSIS
# ============================================================

st.subheader("📊 Traffic Analysis")

col1, col2 = st.columns(2)


with col1:

    hourly_traffic = (
        filtered_df
        .groupby("Hour")["VehicleCount"]
        .mean()
        .reset_index()
    )

    fig_hour = px.line(
        hourly_traffic,
        x="Hour",
        y="VehicleCount",
        markers=True,
        title="Average Traffic by Hour",
        labels={
            "Hour": "Hour of Day",
            "VehicleCount": "Average Vehicles"
        }
    )

    fig_hour.update_layout(
        xaxis=dict(dtick=1)
    )

    st.plotly_chart(
        fig_hour,
        use_container_width=True
    )


with col2:

    congestion_counts = (
        filtered_df["Congestion"]
        .value_counts()
        .reset_index()
    )

    congestion_counts.columns = [
        "Congestion",
        "Count"
    ]

    fig_congestion = px.pie(
        congestion_counts,
        names="Congestion",
        values="Count",
        title="Traffic Congestion Distribution",
        hole=0.4
    )

    st.plotly_chart(
        fig_congestion,
        use_container_width=True
    )


# ============================================================
# LOCATION & WEATHER ANALYSIS
# ============================================================

st.subheader("📍 Traffic Insights")

col1, col2 = st.columns(2)


with col1:

    location_traffic = (
        df.groupby("Location")["VehicleCount"]
        .mean()
        .sort_values(ascending=False)
        .reset_index()
    )

    fig_location = px.bar(
        location_traffic,
        x="Location",
        y="VehicleCount",
        title="Average Traffic by Location",
        labels={
            "VehicleCount": "Average Vehicles"
        }
    )

    st.plotly_chart(
        fig_location,
        use_container_width=True
    )


with col2:

    weather_traffic = (
        df.groupby("Weather")["VehicleCount"]
        .mean()
        .reset_index()
    )

    fig_weather = px.bar(
        weather_traffic,
        x="Weather",
        y="VehicleCount",
        title="Traffic by Weather Condition",
        labels={
            "VehicleCount": "Average Vehicles"
        }
    )

    st.plotly_chart(
        fig_weather,
        use_container_width=True
    )


# ============================================================
# PREDICTION SECTION
# ============================================================

st.divider()

st.header("🔮 Predict Future Traffic")

st.write(
    "Enter the expected traffic conditions to predict vehicle volume "
    "and congestion level."
)

col1, col2, col3 = st.columns(3)

with col1:

    prediction_location = st.selectbox(
        "📍 Location",
        locations,
        key="prediction_location"
    )

    prediction_hour = st.slider(
        "🕐 Hour",
        min_value=6,
        max_value=22,
        value=18
    )


with col2:

    prediction_minute = st.selectbox(
        "Minutes",
        [0, 15, 30, 45],
        index=0
    )

    prediction_weather = st.selectbox(
        "🌦️ Weather",
        sorted(df["Weather"].unique())
    )


with col3:

    prediction_day = st.selectbox(
        "📅 Day of Week",
        [
            ("Monday", 0),
            ("Tuesday", 1),
            ("Wednesday", 2),
            ("Thursday", 3),
            ("Friday", 4),
            ("Saturday", 5),
            ("Sunday", 6)
        ],
        format_func=lambda x: x[0]
    )

    is_weekend = 1 if prediction_day[1] >= 5 else 0


predict_button = st.button(
    "🚦 Predict Traffic",
    type="primary",
    use_container_width=True
)


# ============================================================
# MAKE PREDICTION
# ============================================================

if predict_button:

    input_data = pd.DataFrame(
        [{
            "Hour": prediction_hour,
            "Minute": prediction_minute,
            "DayOfWeek": prediction_day[1],
            "IsWeekend": is_weekend
        }]
    )

    # Add encoded location columns
    for location in locations:

        column = f"Location_{location}"

        input_data[column] = (
            1 if prediction_location == location else 0
        )

    # Add encoded weather columns
    for weather in sorted(df["Weather"].unique()):

        column = f"Weather_{weather}"

        input_data[column] = (
            1 if prediction_weather == weather else 0
        )

    # Make sure the columns are exactly the same
    # as the training data
    input_data = input_data.reindex(
        columns=feature_columns,
        fill_value=0
    )

    # Traffic volume prediction
    predicted_volume = volume_model.predict(
        input_data
    )[0]

    predicted_volume = max(
        0,
        int(round(predicted_volume))
    )

    # Congestion prediction
    predicted_congestion = congestion_model.predict(
        input_data
    )[0]

    probabilities = congestion_model.predict_proba(
        input_data
    )[0]

    max_probability = float(
        np.max(probabilities)
    )

    # ========================================================
    # DISPLAY RESULTS
    # ========================================================

    st.divider()

    st.subheader("🎯 Prediction Result")

    result_col1, result_col2, result_col3 = st.columns(3)

    with result_col1:

        st.metric(
            "🚗 Predicted Vehicles",
            f"{predicted_volume:,}"
        )

    with result_col2:

        st.metric(
            "🚦 Congestion Level",
            predicted_congestion
        )

    with result_col3:

        st.metric(
            "📈 Prediction Confidence",
            f"{max_probability * 100:.1f}%"
        )


    # Congestion message

    if predicted_congestion == "High":

        st.error(
            "🔴 HIGH CONGESTION EXPECTED — "
            "Consider avoiding this time or location."
        )

    elif predicted_congestion == "Medium":

        st.warning(
            "🟡 MEDIUM CONGESTION EXPECTED — "
            "Allow some extra travel time."
        )

    else:

        st.success(
            "🟢 LOW CONGESTION EXPECTED — "
            "Traffic conditions are expected to be normal."
        )


# ============================================================
# DATA PREVIEW
# ============================================================

with st.expander("📋 View Traffic Dataset"):

    st.dataframe(
        filtered_df.head(100),
        use_container_width=True
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Smart Traffic Predictor | Built with Python, "
    "Pandas, Scikit-learn, Plotly & Streamlit"
)