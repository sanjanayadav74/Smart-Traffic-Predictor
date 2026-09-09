import os
import joblib
import numpy as np
import pandas as pd
import plotly.express as px
import requests
import streamlit as st

from streamlit_folium import st_folium

from routing import (
    geocode_two_places,
    get_routes,
    analyze_routes,
    get_recommendation_reason,
    format_duration,
    format_distance,
    create_route_map,
)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Smart Traffic Predictor",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.html(
    """
    <style>

    /* ---------- APP ---------- */

    .stApp {
        background:
            radial-gradient(
                circle at 85% 0%,
                rgba(126, 67, 180, 0.22),
                transparent 32%
            ),
            radial-gradient(
                circle at 10% 85%,
                rgba(75, 42, 125, 0.12),
                transparent 30%
            ),
            linear-gradient(
                135deg,
                #050811 0%,
                #090d18 48%,
                #0d1020 100%
            );

        color: #f5f5f7;
    }

    .main .block-container {
        max-width: 1450px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }


    /* ---------- TEXT ---------- */

    h1, h2, h3, h4, h5, p, label {
        color: #f5f5f7 !important;
    }

    h1 {
        font-size: 2.7rem !important;
        font-weight: 800 !important;
    }

    h2 {
        font-weight: 800 !important;
    }

    h3 {
        font-weight: 750 !important;
    }


    /* ---------- HEADER ---------- */

    .top-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 5px 5px 28px 5px;
    }

    .brand {
        display: flex;
        align-items: center;
        gap: 15px;
    }

    .brand-icon {
        width: 56px;
        height: 56px;
        border-radius: 17px;

        display: flex;
        align-items: center;
        justify-content: center;

        font-size: 29px;

        background:
            linear-gradient(
                135deg,
                #a653d5,
                #602c94
            );

        box-shadow:
            0 0 30px rgba(157, 77, 213, 0.35);
    }

    .brand-title {
        font-size: 27px;
        font-weight: 800;
        color: #ffffff;
    }

    .brand-subtitle {
        color: #969bad;
        font-size: 13px;
        margin-top: 3px;
    }

    .system-badge {
        padding: 9px 16px;
        border-radius: 30px;

        background:
            rgba(49, 202, 120, 0.09);

        border:
            1px solid rgba(49, 202, 120, 0.24);

        color: #69e19c;

        font-size: 13px;
        font-weight: 700;
    }


    /* ---------- HERO ---------- */

    .hero {
        padding: 30px;
        border-radius: 26px;

        background:
            linear-gradient(
                135deg,
                rgba(36, 27, 58, 0.95),
                rgba(14, 18, 31, 0.97)
            );

        border:
            1px solid rgba(157, 87, 207, 0.22);

        box-shadow:
            0 20px 65px rgba(0, 0, 0, 0.32);
    }

    .hero-label {
        color: #a75ed2;
        font-size: 12px;
        font-weight: 800;
        letter-spacing: 1.8px;
        margin-bottom: 9px;
    }

    .hero-title {
        color: white;
        font-size: 35px;
        font-weight: 850;
        line-height: 1.15;
        margin-bottom: 10px;
    }

    .hero-text {
        color: #a2a6b6;
        font-size: 14px;
        line-height: 1.7;
        max-width: 850px;
    }


    /* ---------- CARDS ---------- */

    .route-card {
        padding: 23px;
        border-radius: 21px;

        background:
            linear-gradient(
                135deg,
                rgba(112, 52, 154, 0.28),
                rgba(17, 22, 36, 0.97)
            );

        border:
            1px solid rgba(165, 91, 214, 0.35);

        box-shadow:
            0 0 40px rgba(113, 52, 157, 0.13);
    }

    .route-card-title {
        color: white;
        font-size: 20px;
        font-weight: 800;
    }

    .route-card-subtitle {
        color: #979bad;
        font-size: 13px;
        margin-top: 5px;
    }


    .info-card {
        padding: 17px 19px;
        border-radius: 16px;

        background:
            rgba(102, 74, 140, 0.12);

        border:
            1px solid rgba(157, 99, 206, 0.18);

        color: #c6c8d3;
        font-size: 13px;
        line-height: 1.65;
    }


    /* ---------- INPUTS ---------- */

    .stTextInput input {
        background: #141927 !important;
        color: white !important;

        border:
            1px solid #2b3145 !important;

        border-radius:
            14px !important;

        min-height:
            48px !important;
    }

    .stTextInput input:focus {
        border-color:
            #a054d1 !important;

        box-shadow:
            0 0 0 1px #a054d1 !important;
    }


    /* ---------- BUTTON ---------- */

    .stButton button {
        border: none !important;

        border-radius:
            14px !important;

        min-height:
            48px !important;

        background:
            linear-gradient(
                135deg,
                #9d4fd0,
                #673397
            ) !important;

        color: white !important;

        font-weight: 750 !important;

        box-shadow:
            0 8px 28px rgba(137, 59, 185, 0.28);
    }

    .stButton button:hover {
        background:
            linear-gradient(
                135deg,
                #ad5ddd,
                #7741a9
            ) !important;
    }


    /* ---------- METRICS ---------- */

    [data-testid="stMetric"] {
        background:
            rgba(19, 24, 39, 0.88);

        border:
            1px solid rgba(151, 157, 184, 0.13);

        border-radius:
            18px;

        padding:
            18px;
    }

    [data-testid="stMetricLabel"] {
        color: #989cad !important;
    }

    [data-testid="stMetricValue"] {
        color: #ffffff !important;
    }


    /* ---------- SELECT BOX ---------- */

    div[data-baseweb="select"] > div {
        background: #141927 !important;
        border-color: #2b3145 !important;
        border-radius: 12px !important;
    }


    /* ---------- EXPANDER ---------- */

    [data-testid="stExpander"] {
        background:
            rgba(18, 22, 35, 0.80);

        border:
            1px solid rgba(150, 157, 185, 0.12);

        border-radius:
            16px;
    }


    /* ---------- DIVIDER ---------- */

    hr {
        border-color:
            rgba(255, 255, 255, 0.08) !important;
    }


    /* ---------- FOOTER ---------- */

    .footer {
        text-align: center;
        color: #707588;
        font-size: 12px;
        line-height: 1.8;
        padding: 25px;
    }

    </style>
    """
)


# ============================================================
# FILE PATHS
# ============================================================

DATA_PATH = "data/traffic_data.csv"

VOLUME_MODEL_PATH = "models/traffic_volume_model.pkl"

CONGESTION_MODEL_PATH = "models/congestion_model.pkl"

FEATURES_PATH = "models/feature_columns.pkl"


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data():
    return pd.read_csv(DATA_PATH)


# ============================================================
# LOAD MODELS
# ============================================================

@st.cache_resource
def load_models():

    volume_model = joblib.load(
        VOLUME_MODEL_PATH
    )

    congestion_model = joblib.load(
        CONGESTION_MODEL_PATH
    )

    feature_columns = joblib.load(
        FEATURES_PATH
    )

    return (
        volume_model,
        congestion_model,
        feature_columns,
    )


# ============================================================
# ANY-LOCATION SEARCH
# ============================================================

@st.cache_data(ttl=3600, show_spinner=False)
def search_places(query):
    """Search real-world places using OpenStreetMap Nominatim."""
    url = "https://nominatim.openstreetmap.org/search"
    headers = {
        "User-Agent": "SmartTrafficPredictor/1.0"
    }
    params = {
        "q": query,
        "format": "jsonv2",
        "limit": 8,
        "addressdetails": 1,
    }

    response = requests.get(
        url,
        params=params,
        headers=headers,
        timeout=15,
    )
    response.raise_for_status()
    return response.json()


# ============================================================
# CHECK FILES
# ============================================================

required_files = [
    DATA_PATH,
    VOLUME_MODEL_PATH,
    CONGESTION_MODEL_PATH,
    FEATURES_PATH,
]

missing_files = [
    file
    for file in required_files
    if not os.path.exists(file)
]

if missing_files:

    st.error("Required project files are missing.")

    for file in missing_files:
        st.write(f"• {file}")

    st.info(
        "Run: python train_model.py"
    )

    st.stop()


# ============================================================
# LOAD PROJECT
# ============================================================

df = load_data()

(
    volume_model,
    congestion_model,
    feature_columns,
) = load_models()


# ============================================================
# SESSION STATE
# ============================================================

if "route_result" not in st.session_state:
    st.session_state.route_result = None

if "analytics_search_results" not in st.session_state:
    st.session_state.analytics_search_results = []

if "analytics_search_query" not in st.session_state:
    st.session_state.analytics_search_query = ""

if "analytics_matched_location" not in st.session_state:
    st.session_state.analytics_matched_location = None


# ============================================================
# HEADER
# ============================================================

st.html(
    """
    <div class="top-header">

        <div class="brand">

            <div class="brand-icon">
                🚦
            </div>

            <div>

                <div class="brand-title">
                    Smart Traffic Predictor
                </div>

                <div class="brand-subtitle">
                    Intelligent traffic & route planning
                </div>

            </div>

        </div>

        <div class="system-badge">
            ● System Ready
        </div>

    </div>
    """
)


# ============================================================
# HERO
# ============================================================

st.html(
    """
    <div class="hero">

        <div class="hero-label">
            SMART MOBILITY PLATFORM
        </div>

        <div class="hero-title">
            Find a smarter way to your destination.
        </div>

        <div class="hero-text">
            Compare available driving routes, understand travel
            time, and make better route decisions using intelligent
            traffic and route analysis.
        </div>

    </div>
    """
)


st.write("")


# ============================================================
# ROUTE FINDER
# ============================================================

st.subheader("🗺️ Smart Route Finder")

st.caption(
    "Enter any starting location and destination."
)


route_col1, route_col2 = st.columns(
    2,
    gap="large"
)


with route_col1:

    start_location = st.text_input(
        "📍 Starting Location",
        placeholder="e.g. Dehradun Railway Station",
        key="start_location",
    )


with route_col2:

    destination = st.text_input(
        "🎯 Destination",
        placeholder="e.g. Graphic Era University",
        key="destination",
    )


st.write("")


find_route = st.button(
    "🚗  Find Best Route",
    type="primary",
    use_container_width=True,
)


# ============================================================
# ROUTE SEARCH
# ============================================================

if find_route:

    if not start_location.strip():

        st.warning(
            "Please enter a starting location."
        )

    elif not destination.strip():

        st.warning(
            "Please enter a destination."
        )

    else:

        with st.spinner(
            "Finding locations and calculating routes..."
        ):

            try:

                start, end = geocode_two_places(
                    start_location.strip(),
                    destination.strip(),
                )


                if start is None:

                    st.error(
                        "Starting location could not be found. "
                        "Try adding the city or country."
                    )

                    st.stop()


                if end is None:

                    st.error(
                        "Destination could not be found. "
                        "Try adding the city or country."
                    )

                    st.stop()


                routes = get_routes(
                    start["lat"],
                    start["lon"],
                    end["lat"],
                    end["lon"],
                )


                if not routes:

                    st.error(
                        "No driving route was found."
                    )

                    st.stop()


                analyzed_routes, best_index = analyze_routes(routes)


                st.session_state.route_result = {
                    "start": start,
                    "destination": end,
                    "routes": analyzed_routes,
                    "best_index": best_index,
                }


            except Exception as error:

                st.error(
                    "Unable to calculate the route."
                )

                st.caption(
                    f"Technical details: {error}"
                )


# ============================================================
# ROUTE RESULTS
# ============================================================

route_result = st.session_state.route_result

if route_result:
    start = route_result["start"]
    destination_data = route_result["destination"]
    routes = route_result["routes"]
    best_index = route_result["best_index"]
    best_route = routes[best_index]

    fastest_duration = min(r["duration"] for r in routes)
    shortest_distance = min(r["distance"] for r in routes)
    recommendation_reason = get_recommendation_reason(best_route, routes)

    st.divider()

    st.html(f"""
        <div class="route-card">
            <div class="route-card-title">⭐ Recommended Route</div>
            <div class="route-card-subtitle">
                Best overall balance of estimated travel time, distance, and route efficiency
            </div>
        </div>
    """)

    st.write("")

    metric1, metric2, metric3, metric4 = st.columns(4)

    with metric1:
        st.metric("⭐ Smart Score", f"{best_route['smart_score']}/100")

    with metric2:
        st.metric("⏱️ Estimated Time", format_duration(best_route["duration"]))

    with metric3:
        st.metric("📏 Distance", format_distance(best_route["distance"]))

    with metric4:
        st.metric("🛣️ Routes Found", len(routes))

    st.write("")

    from_name = start["display_name"]
    to_name = destination_data["display_name"]

    st.html(f"""
        <div class="info-card">
            📍 <b>From:</b> {from_name}
            <br><br>
            🎯 <b>To:</b> {to_name}
            <br><br>
            ⭐ <b>Why this route?</b> {recommendation_reason.capitalize()}.
            <br><br>
            ℹ️ <b>Scoring:</b> 55% estimated travel time, 25% distance, and 20% route efficiency.
        </div>
    """)

    st.write("")

    # --------------------------------------------------------
    # ROUTE COMPARISON CARDS
    # --------------------------------------------------------

    st.subheader("🚗 Route Comparison")
    st.caption("Compare every route before choosing your journey.")

    route_columns = st.columns(len(routes))

    for index, route in enumerate(routes):
        with route_columns[index]:
            if index == best_index:
                title = "⭐ Recommended"
                status = "Best overall"
            elif route["duration"] == fastest_duration:
                title = "⚡ Fastest"
                status = "Fastest estimated time"
            elif route["distance"] == shortest_distance:
                title = "📏 Shortest"
                status = "Shortest distance"
            else:
                title = f"Alternative {index + 1}"
                status = "Alternative route"

            delay_minutes = round(route.get("delay_seconds", 0) / 60)
            extra_km = route.get("extra_distance", 0) / 1000

            st.html(f"""
                <div class="route-card" style="min-height: 285px;">
                    <div class="route-card-title">{title}</div>
                    <div class="route-card-subtitle">{status}</div>
                    <div style="font-size: 32px; font-weight: 850; margin-top: 18px;">
                        {route['smart_score']}<span style="font-size: 14px; color: #989cad;">/100</span>
                    </div>
                    <div style="margin-top: 18px; color: #c6c8d3; line-height: 2;">
                        ⏱️ <b>Time:</b> {format_duration(route['duration'])}<br>
                        📏 <b>Distance:</b> {format_distance(route['distance'])}<br>
                        ⏳ <b>Extra time:</b> {delay_minutes} min<br>
                        🛣️ <b>Extra distance:</b> {extra_km:.1f} km
                    </div>
                </div>
            """)

    st.write("")

    # --------------------------------------------------------
    # MAP
    # --------------------------------------------------------

    st.subheader("🗺️ Route Map")
    st.caption("Recommended route and available alternatives")

    route_map = create_route_map(
        start,
        destination_data,
        routes,
        best_index,
    )

    st_folium(
        route_map,
        use_container_width=True,
        height=600,
        returned_objects=[],
    )

    st.info(
        "ℹ️ Traffic note: The current route engine uses road-network routing estimates. "
        "Live traffic congestion is not yet enabled. The Smart Score currently evaluates "
        "estimated travel time, distance, and route efficiency."
    )

    # --------------------------------------------------------
    # ROUTE TABLE
    # --------------------------------------------------------

    st.subheader("📊 Detailed Route Comparison")

    route_rows = []

    for index, route in enumerate(routes):
        if index == best_index:
            status = "⭐ Recommended"
        elif route["duration"] == fastest_duration:
            status = "⚡ Fastest"
        elif route["distance"] == shortest_distance:
            status = "📏 Shortest"
        else:
            status = "Alternative"

        route_rows.append({
            "Route": f"Route {index + 1}",
            "Smart Score": f"{route['smart_score']}/100",
            "Distance": format_distance(route["distance"]),
            "Estimated Time": format_duration(route["duration"]),
            "Extra Time": f"{round(route.get('delay_seconds', 0) / 60)} min",
            "Status": status,
        })

    st.dataframe(
        pd.DataFrame(route_rows),
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# ANALYTICS
# ============================================================

st.divider()

st.subheader("📊 Traffic Analytics")

st.caption(
    "Historical traffic analysis and machine-learning predictions."
)


# ============================================================
# DATASET INFORMATION
# ============================================================

min_date = pd.to_datetime(
    df["Date"]
).min()

max_date = pd.to_datetime(
    df["Date"]
).max()


st.html(
    f"""
    <div class="info-card">

        📚 <b>Dataset:</b>
        Historical traffic training / analysis data

        &nbsp;&nbsp;•&nbsp;&nbsp;

        📅 <b>Coverage:</b>
        {min_date.strftime("%d %b %Y")}
        —
        {max_date.strftime("%d %b %Y")}

        <br><br>

        ⚠️ This dataset is historical/synthetic training data.
        It is <b>not presented as live 2026 traffic data.</b>

    </div>
    """
)


st.write("")


# ============================================================
# FILTERS
# ============================================================

with st.expander(
    "🔎 Search & Analytics Filters",
    expanded=True,
):

    st.markdown(
        "**Search any real-world place** — small localities, landmarks, "
        "roads, markets, universities, stations, cities or famous places."
    )

    search_col, button_col = st.columns([5, 1])

    with search_col:
        analytics_query = st.text_input(
            "📍 Search Location",
            placeholder="e.g. Pacific Mall Dehradun, Connaught Place Delhi, Eiffel Tower",
            key="analytics_query",
        )

    with button_col:
        st.write("")
        st.write("")
        search_location_button = st.button(
            "🔍 Search",
            use_container_width=True,
            key="search_analytics_location",
        )

    if search_location_button:
        if not analytics_query.strip():
            st.warning("Enter a place to search.")
        else:
            with st.spinner("Searching places..."):
                try:
                    results = search_places(analytics_query.strip())
                    st.session_state.analytics_search_results = results
                    st.session_state.analytics_search_query = analytics_query.strip()
                    st.session_state.analytics_matched_location = None
                except Exception as error:
                    st.session_state.analytics_search_results = []
                    st.error("Location search is temporarily unavailable.")
                    st.caption(f"Technical details: {error}")

    search_results = st.session_state.get(
        "analytics_search_results",
        [],
    )

    selected_place = None
    selected_place_name = None
    selected_lat = None
    selected_lon = None

    if search_results:
        result_labels = [
            item.get("display_name", "Unknown place")
            for item in search_results
        ]

        selected_place_index = st.selectbox(
            "📌 Select the exact place",
            range(len(result_labels)),
            format_func=lambda i: result_labels[i],
            key="analytics_place_result",
        )

        selected_place = search_results[selected_place_index]
        selected_place_name = selected_place.get(
            "display_name",
            "Selected location",
        )
        selected_lat = float(selected_place["lat"])
        selected_lon = float(selected_place["lon"])

        st.html(
            f"""
            <div class="info-card">
                📍 <b>Location found:</b> {selected_place_name}
                <br><br>
                🌐 <b>Coordinates:</b> {selected_lat:.6f}, {selected_lon:.6f}
                <br><br>
                🗺️ <b>Source:</b> OpenStreetMap / Nominatim
            </div>
            """
        )

        # The current ML model has historical data only for its training locations.
        # We match the searched place against those records without exposing a
        # Dehradun-only dropdown to the user.
        locations = sorted(df["Location"].unique())
        matched_location = None
        place_lower = selected_place_name.lower()

        for location in locations:
            if location.lower() in place_lower or place_lower == location.lower():
                matched_location = location
                break

        st.session_state.analytics_matched_location = matched_location

        if matched_location:
            st.success(
                f"Historical traffic data is available for **{matched_location}**."
            )
        else:
            st.info(
                "This place was found successfully, but the current historical "
                "dataset has no records for this location. You can still use the "
                "route finder for this place."
            )

    elif st.session_state.get("analytics_search_query"):
        st.warning(
            "No exact place was found. Try adding the city, district, state, "
            "or country to make the search more precise."
        )

    st.divider()

    filter_col1, filter_col2 = st.columns(2)

    with filter_col1:
        st.markdown("**📊 Historical Data Location**")
        matched_location = st.session_state.get(
            "analytics_matched_location"
        )

        if matched_location:
            st.success(
                f"Using historical records for: **{matched_location}**"
            )
        else:
            st.caption(
                "Search for any place above. Historical analytics will appear "
                "automatically when records exist for that location."
            )

    with filter_col2:
        weather_options = sorted(df["Weather"].unique())
        selected_weather = st.multiselect(
            "🌦️ Weather",
            weather_options,
            default=weather_options,
        )

    if st.session_state.analytics_search_results:
        if st.button("✕ Clear location search", key="clear_analytics_search"):
            st.session_state.analytics_search_results = []
            st.session_state.analytics_search_query = ""
            st.session_state.analytics_matched_location = None
            st.rerun()


# Only show historical analytics when the searched place exists in the dataset.
selected_location = st.session_state.get("analytics_matched_location")

if selected_location:
    filtered_df = df[
        (df["Location"] == selected_location)
        &
        (df["Weather"].isin(selected_weather))
    ]
else:
    filtered_df = df.iloc[0:0].copy()


# ============================================================
# ANALYTICS KPIs
# ============================================================

if not filtered_df.empty:

    total_vehicles = int(
        filtered_df["VehicleCount"].sum()
    )


    average_speed = filtered_df[
        "AverageSpeed"
    ].mean()


    average_vehicles = filtered_df[
        "VehicleCount"
    ].mean()


    high_congestion = (
        filtered_df["Congestion"]
        .value_counts()
        .get("High", 0)
    )


    kpi1, kpi2, kpi3, kpi4 = st.columns(4)


    with kpi1:

        st.metric(
            "🚗 Total Vehicles",
            f"{total_vehicles:,}",
        )


    with kpi2:

        st.metric(
            "⚡ Average Speed",
            f"{average_speed:.1f} km/h",
        )


    with kpi3:

        st.metric(
            "📊 Avg Vehicles / Record",
            f"{average_vehicles:.0f}",
        )


    with kpi4:

        st.metric(
            "🔴 High Congestion",
            f"{high_congestion:,}",
        )


    # ========================================================
    # CHARTS
    # ========================================================

    chart_col1, chart_col2 = st.columns(2)


    with chart_col1:

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
                "VehicleCount":
                    "Average Vehicles",
            },
        )


        fig_hour.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(dtick=1),
        )


        st.plotly_chart(
            fig_hour,
            use_container_width=True,
        )


    with chart_col2:

        congestion_counts = (
            filtered_df["Congestion"]
            .value_counts()
            .reset_index()
        )


        congestion_counts.columns = [
            "Congestion",
            "Count",
        ]


        fig_congestion = px.pie(
            congestion_counts,
            names="Congestion",
            values="Count",
            title="Congestion Distribution",
            hole=0.45,
        )


        fig_congestion.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
        )


        st.plotly_chart(
            fig_congestion,
            use_container_width=True,
        )


    # ========================================================
    # TRAFFIC INSIGHTS
    # ========================================================

    st.subheader("📍 Traffic Insights")


    insight_col1, insight_col2 = st.columns(2)


    with insight_col1:

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
                "VehicleCount":
                    "Average Vehicles",
            },
        )


        fig_location.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )


        st.plotly_chart(
            fig_location,
            use_container_width=True,
        )


    with insight_col2:

        weather_traffic = (
            df.groupby("Weather")["VehicleCount"]
            .mean()
            .reset_index()
        )


        fig_weather = px.bar(
            weather_traffic,
            x="Weather",
            y="VehicleCount",
            title="Traffic by Weather",
            labels={
                "VehicleCount":
                    "Average Vehicles",
            },
        )


        fig_weather.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )


        st.plotly_chart(
            fig_weather,
            use_container_width=True,
        )


# ============================================================
# ML PREDICTION
# ============================================================

st.divider()

st.subheader("🔮 Traffic Prediction")

st.caption(
    "Search any real-world place. The ML prediction is available only when "
    "historical training records exist for that location."
)

# Use the same real-world search results from the Analytics section.
# There is intentionally NO Dehradun-only location dropdown here.

prediction_place = None
prediction_location = None

prediction_results = st.session_state.get(
    "analytics_search_results",
    [],
)

if prediction_results:
    prediction_labels = [
        item.get("display_name", "Unknown place")
        for item in prediction_results
    ]

    prediction_place_index = st.selectbox(
        "📍 Prediction Location",
        range(len(prediction_labels)),
        format_func=lambda i: prediction_labels[i],
        key="prediction_place_result",
    )

    prediction_place = prediction_results[prediction_place_index]
    prediction_place_name = prediction_place.get(
        "display_name",
        "Selected location",
    )

    locations = sorted(df["Location"].unique())
    place_lower = prediction_place_name.lower()

    for location in locations:
        if location.lower() in place_lower or place_lower == location.lower():
            prediction_location = location
            break

    if prediction_location:
        st.success(
            f"ML training data found for **{prediction_location}**. "
            "Prediction can be generated for this location."
        )
    else:
        st.info(
            f"**{prediction_place_name}** was found successfully, but the current "
            "ML model was not trained on this location. Live routing/search still "
            "works, but a historical ML traffic prediction is not available for it yet."
        )
else:
    st.info(
        "🔎 Search a location in **Search & Analytics Filters** above to use it "
        "for traffic prediction. You can search small places, landmarks, roads, "
        "cities, universities, stations, or famous places."
    )

prediction_col1, prediction_col2, prediction_col3 = st.columns(3)

with prediction_col1:

    prediction_hour = st.slider(
        "🕐 Hour",
        min_value=0,
        max_value=23,
        value=18,
    )

    prediction_minute = st.selectbox(
        "Minutes",
        [0, 15, 30, 45],
    )

with prediction_col2:

    prediction_weather = st.selectbox(
        "🌦️ Weather",
        sorted(df["Weather"].unique()),
        key="prediction_weather",
    )

with prediction_col3:

    prediction_day = st.selectbox(
        "📅 Day of Week",
        [
            ("Monday", 0),
            ("Tuesday", 1),
            ("Wednesday", 2),
            ("Thursday", 3),
            ("Friday", 4),
            ("Saturday", 5),
            ("Sunday", 6),
        ],
        format_func=lambda x: x[0],
    )

is_weekend = (
    1
    if prediction_day[1] >= 5
    else 0
)

predict_button = st.button(
    "🚦 Predict Traffic",
    use_container_width=True,
)

if predict_button:

    if not prediction_location:
        st.warning(
            "Please search for a place first. The current ML model can only "
            "predict locations represented in its training data."
        )
    else:
        input_data = pd.DataFrame(
            [
                {
                    "Hour": prediction_hour,
                    "Minute": prediction_minute,
                    "DayOfWeek": prediction_day[1],
                    "IsWeekend": is_weekend,
                }
            ]
        )

        # Location features
        locations = sorted(df["Location"].unique())

        for location in locations:
            input_data[
                f"Location_{location}"
            ] = (
                1
                if prediction_location == location
                else 0
            )

        # Weather features
        for weather in sorted(df["Weather"].unique()):
            input_data[
                f"Weather_{weather}"
            ] = (
                1
                if prediction_weather == weather
                else 0
            )

        # Match training columns
        input_data = input_data.reindex(
            columns=feature_columns,
            fill_value=0,
        )

        # Predict traffic volume
        predicted_volume = (
            volume_model
            .predict(input_data)[0]
        )

        predicted_volume = max(
            0,
            int(round(predicted_volume))
        )

        # Predict congestion
        predicted_congestion = (
            congestion_model
            .predict(input_data)[0]
        )

        probabilities = (
            congestion_model
            .predict_proba(input_data)[0]
        )

        confidence = float(
            np.max(probabilities)
        )

        st.write("")

        result1, result2, result3 = st.columns(3)

        with result1:
            st.metric(
                "🚗 Predicted Vehicles",
                f"{predicted_volume:,}",
            )

        with result2:
            st.metric(
                "🚦 Congestion",
                predicted_congestion,
            )

        with result3:
            st.metric(
                "📈 Confidence",
                f"{confidence * 100:.1f}%",
            )

        st.caption(
            f"Prediction location: {prediction_location} • "
            f"{prediction_day[0]} at {prediction_hour:02d}:{prediction_minute:02d} • "
            f"Weather: {prediction_weather}"
        )

        if predicted_congestion == "High":
            st.error(
                "🔴 High congestion expected. "
                "Consider avoiding this time or location."
            )
        elif predicted_congestion == "Medium":
            st.warning(
                "🟡 Moderate congestion expected. "
                "Allow extra travel time."
            )
        else:
            st.success(
                "🟢 Low congestion expected. "
                "Traffic conditions should be relatively normal."
            )


# ============================================================
# DATASET PREVIEW
# ============================================================

with st.expander(
    "📋 View Historical Traffic Dataset"
):

    if selected_location and not filtered_df.empty:
        st.caption(
            f"Showing historical records for **{selected_location}**. "
            "These are historical/synthetic training records, not live traffic."
        )

        st.dataframe(
            filtered_df.head(100),
            use_container_width=True,
            hide_index=True,
        )
    elif prediction_place is not None:
        st.info(
            "No historical records are available for the searched location in "
            "the current dataset. The place search itself is working; historical "
            "analytics will appear after traffic data for that area is added."
        )
    else:
        st.info(
            "Search for any location above to view its historical records when "
            "that location exists in the current dataset."
        )


# ============================================================
# FOOTER
# ============================================================

st.divider()


st.html(
    """
    <div class="footer">

        🚦 <b>Smart Traffic Predictor</b>

        <br>

        Intelligent route planning • Traffic analytics • Machine Learning

        <br>

        Built with Python • Streamlit • Pandas • Scikit-learn • Plotly

    </div>
    """
)