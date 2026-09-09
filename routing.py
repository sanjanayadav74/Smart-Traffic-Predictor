import time

import requests
import folium
import streamlit as st


NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
OSRM_URL = "https://router.project-osrm.org/route/v1/driving"

USER_AGENT = "SmartTrafficPredictor/1.0"


# ============================================================
# GEOCODING
# ============================================================

@st.cache_data(ttl=3600, show_spinner=False)
def geocode_place(place):
    """Convert a place name/address into latitude and longitude."""

    headers = {
        "User-Agent": USER_AGENT
    }

    params = {
        "q": place,
        "format": "json",
        "limit": 1,
        "addressdetails": 1,
    }

    response = requests.get(
        NOMINATIM_URL,
        params=params,
        headers=headers,
        timeout=15,
    )

    response.raise_for_status()

    results = response.json()

    if not results:
        return None

    return {
        "lat": float(results[0]["lat"]),
        "lon": float(results[0]["lon"]),
        "display_name": results[0]["display_name"],
    }


def geocode_two_places(start_location, destination):
    """Geocode starting location and destination."""

    start = geocode_place(start_location)

    # Respect Nominatim public-service rate limits.
    time.sleep(1.1)

    end = geocode_place(destination)

    return start, end


# ============================================================
# ROUTING
# ============================================================

@st.cache_data(ttl=300, show_spinner=False)
def get_routes(
    start_lat,
    start_lon,
    end_lat,
    end_lon,
):
    """
    Find alternative driving routes using OSRM.

    Note:
    OSRM provides road-network route estimates.
    Its standard public endpoint does NOT provide live traffic.
    """

    coordinates = (
        f"{start_lon},{start_lat};"
        f"{end_lon},{end_lat}"
    )

    params = {
        "alternatives": "2",
        "steps": "true",
        "geometries": "geojson",
        "overview": "full",
    }

    response = requests.get(
        f"{OSRM_URL}/{coordinates}",
        params=params,
        timeout=20,
    )

    response.raise_for_status()

    data = response.json()

    if data.get("code") != "Ok":
        return None

    return data.get("routes", [])


# ============================================================
# ROUTE ANALYSIS
# ============================================================

def calculate_route_score(
    route,
    fastest_duration,
    shortest_distance,
):
    """
    Calculate a transparent route score.

    This is a decision-support score, NOT a live traffic score.

    Weighting:
    - 55% travel time
    - 25% distance
    - 20% route efficiency
    """

    duration = max(
        float(route.get("duration", 0)),
        1,
    )

    distance = max(
        float(route.get("distance", 0)),
        1,
    )

    # Lower travel time is better.
    time_score = (
        fastest_duration / duration
    ) * 100

    # Lower distance is better.
    distance_score = (
        shortest_distance / distance
    ) * 100

    # Time per kilometer.
    route_efficiency = duration / distance

    # Normalize efficiency relative to the fastest route.
    fastest_efficiency = (
        fastest_duration / shortest_distance
    )

    if route_efficiency <= fastest_efficiency:
        efficiency_score = 100
    else:
        efficiency_score = (
            fastest_efficiency
            / route_efficiency
        ) * 100

    score = (
        time_score * 0.55
        + distance_score * 0.25
        + efficiency_score * 0.20
    )

    return round(
        min(max(score, 0), 100),
        1,
    )


def analyze_routes(routes):
    """
    Add transparent route scores and comparisons.

    Returns:
        analyzed_routes, best_index
    """

    if not routes:
        return [], None

    fastest_duration = min(
        route["duration"]
        for route in routes
    )

    shortest_distance = min(
        route["distance"]
        for route in routes
    )

    analyzed_routes = []

    for index, route in enumerate(routes):

        route_copy = dict(route)

        score = calculate_route_score(
            route_copy,
            fastest_duration,
            shortest_distance,
        )

        route_copy["smart_score"] = score

        # Difference from fastest route.
        delay_seconds = (
            route_copy["duration"]
            - fastest_duration
        )

        route_copy["delay_seconds"] = max(
            0,
            delay_seconds,
        )

        # Difference from shortest route.
        extra_distance = (
            route_copy["distance"]
            - shortest_distance
        )

        route_copy["extra_distance"] = max(
            0,
            extra_distance,
        )

        analyzed_routes.append(
            route_copy
        )

    best_index = max(
        range(len(analyzed_routes)),
        key=lambda i: analyzed_routes[i]["smart_score"],
    )

    return analyzed_routes, best_index


def get_route_status(
    route,
    fastest_duration,
    shortest_distance,
):
    """
    Create a simple human-readable route status.
    """

    duration = route["duration"]
    distance = route["distance"]

    if duration == fastest_duration:
        return "Fastest"

    if distance == shortest_distance:
        return "Shortest"

    if route.get("smart_score", 0) >= 85:
        return "Highly Efficient"

    if route.get("smart_score", 0) >= 70:
        return "Balanced"

    return "Alternative"


def get_recommendation_reason(
    route,
    routes,
):
    """Explain why a route received its score."""

    if not routes:
        return "No route information available."

    fastest_duration = min(
        r["duration"]
        for r in routes
    )

    shortest_distance = min(
        r["distance"]
        for r in routes
    )

    reasons = []

    if route["duration"] == fastest_duration:
        reasons.append(
            "fastest estimated travel time"
        )

    if route["distance"] == shortest_distance:
        reasons.append(
            "shortest distance"
        )

    if route.get("smart_score", 0) >= 85:
        reasons.append(
            "strong overall route efficiency"
        )

    if not reasons:
        reasons.append(
            "best overall balance of time and distance"
        )

    return ", ".join(reasons)


# ============================================================
# FORMATTING
# ============================================================

def format_duration(seconds):
    """Convert seconds into a readable duration."""

    total_minutes = round(
        seconds / 60
    )

    hours = total_minutes // 60
    minutes = total_minutes % 60

    if hours > 0:
        return f"{hours} hr {minutes} min"

    return f"{minutes} min"


def format_distance(meters):
    """Convert meters into kilometers."""

    kilometers = meters / 1000

    return f"{kilometers:.1f} km"


# ============================================================
# ROUTE MAP
# ============================================================

def create_route_map(
    start,
    destination,
    routes,
    best_index,
):
    """Create an interactive map showing all routes."""

    center_lat = (
        start["lat"]
        + destination["lat"]
    ) / 2

    center_lon = (
        start["lon"]
        + destination["lon"]
    ) / 2

    route_map = folium.Map(
        location=[
            center_lat,
            center_lon,
        ],
        zoom_start=12,
        control_scale=True,
    )

    # Start marker.
    folium.Marker(
        location=[
            start["lat"],
            start["lon"],
        ],
        popup=(
            f"<b>Start</b><br>"
            f"{start['display_name']}"
        ),
        tooltip="Starting Location",
        icon=folium.Icon(
            color="green",
            icon="play",
        ),
    ).add_to(route_map)

    # Destination marker.
    folium.Marker(
        location=[
            destination["lat"],
            destination["lon"],
        ],
        popup=(
            f"<b>Destination</b><br>"
            f"{destination['display_name']}"
        ),
        tooltip="Destination",
        icon=folium.Icon(
            color="red",
            icon="flag",
        ),
    ).add_to(route_map)

    route_colors = [
        "green",
        "blue",
        "orange",
        "purple",
    ]

    for index, route in enumerate(routes):

        coordinates = [
            [lat, lon]
            for lon, lat
            in route["geometry"]["coordinates"]
        ]

        is_best = (
            index == best_index
        )

        if is_best:
            color = "green"
            weight = 8
            label = "⭐ Recommended Route"
        else:
            color = route_colors[
                index % len(route_colors)
            ]
            weight = 5
            label = (
                f"Alternative Route "
                f"{index + 1}"
            )

        score = route.get(
            "smart_score"
        )

        score_text = (
            f"<br>Smart Score: {score}/100"
            if score is not None
            else ""
        )

        popup_text = (
            f"<b>{label}</b><br>"
            f"Distance: "
            f"{format_distance(route['distance'])}"
            f"<br>"
            f"Estimated time: "
            f"{format_duration(route['duration'])}"
            f"{score_text}"
        )

        folium.PolyLine(
            coordinates,
            color=color,
            weight=weight,
            opacity=0.85,
            tooltip=label,
            popup=folium.Popup(
                popup_text,
                max_width=320,
            ),
        ).add_to(route_map)

    return route_map