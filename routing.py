import time
import threading
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone
from math import radians, sin, cos, asin, sqrt

import requests
import folium
import streamlit as st


NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
ARCGIS_URL = "https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/findAddressCandidates"
OSRM_URL = "https://router.project-osrm.org/route/v1/driving"

USER_AGENT = "SmartTrafficPredictor/1.0 (route-planning-dashboard)"
NOMINATIM_MIN_INTERVAL = 1.1
NOMINATIM_MAX_RETRIES = 2

_geocoder_session = requests.Session()
_geocoder_session.headers.update({"User-Agent": USER_AGENT})
_nominatim_lock = threading.Lock()
_last_nominatim_request = 0.0


def _wait_for_nominatim_slot():
    global _last_nominatim_request
    with _nominatim_lock:
        elapsed = time.monotonic() - _last_nominatim_request
        if elapsed < NOMINATIM_MIN_INTERVAL:
            time.sleep(NOMINATIM_MIN_INTERVAL - elapsed)
        _last_nominatim_request = time.monotonic()


def _nominatim_request(params):
    for attempt in range(NOMINATIM_MAX_RETRIES + 1):
        _wait_for_nominatim_slot()
        response = _geocoder_session.get(
            NOMINATIM_URL,
            params=params,
            timeout=15,
        )

        if response.status_code != 429:
            response.raise_for_status()
            return response

        if attempt < NOMINATIM_MAX_RETRIES:
            retry_after = response.headers.get("Retry-After")
            delay = 2.0 * (attempt + 1)

            if retry_after:
                try:
                    delay = max(1.1, float(retry_after))
                except ValueError:
                    try:
                        dt = parsedate_to_datetime(retry_after)
                        if dt.tzinfo is None:
                            dt = dt.replace(tzinfo=timezone.utc)
                        delay = max(
                            1.1,
                            (dt - datetime.now(timezone.utc)).total_seconds(),
                        )
                    except (TypeError, ValueError, OverflowError):
                        pass

            time.sleep(delay)

    raise RuntimeError(
        "Public geocoding service is temporarily rate-limiting requests. "
        "Please try again in a few seconds."
    )


def _haversine_km(lat1, lon1, lat2, lon2):
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = (
        sin(dlat / 2) ** 2
        + cos(radians(lat1))
        * cos(radians(lat2))
        * sin(dlon / 2) ** 2
    )

    return 6371.0 * 2 * asin(sqrt(a))


def _candidate_from_arcgis(candidate):
    location = candidate.get("location", {})

    if "x" not in location or "y" not in location:
        return None

    attrs = candidate.get("attributes", {})

    return {
        "lat": float(location["y"]),
        "lon": float(location["x"]),
        "display_name": (
            candidate.get("address")
            or attrs.get("Match_addr")
            or "Unknown location"
        ),
        "city": attrs.get("City") or "",
        "region": attrs.get("Region") or "",
        "country": attrs.get("Country") or "",
    }


def _candidate_from_nominatim(result, query):
    address = result.get("address", {})

    return {
        "lat": float(result["lat"]),
        "lon": float(result["lon"]),
        "display_name": result.get("display_name", query),
        "city": (
            address.get("city")
            or address.get("town")
            or address.get("municipality")
            or address.get("village")
            or ""
        ),
        "region": address.get("state") or "",
        "country": address.get("country") or "",
    }


def _is_india(candidate):
    country = str(candidate.get("country", "")).strip().lower()
    return country in {
        "india",
        "republic of india",
        "bharat",
    }


def _distance_from_bias(candidate, bias):
    if not bias:
        return 0.0

    return _haversine_km(
        bias["lat"],
        bias["lon"],
        candidate["lat"],
        candidate["lon"],
    )


def _select_candidate(candidates, bias=None, max_bias_distance_km=None):
    """
    Select the best candidate.

    When a bias is supplied, the closest candidate is preferred.
    When a maximum distance is supplied, candidates beyond it are rejected.
    """

    if not candidates:
        return None

    india_candidates = [
        candidate
        for candidate in candidates
        if _is_india(candidate)
    ]

    # Never select a non-India result for this India-focused route finder.
    candidates = india_candidates

    if not candidates:
        return None

    if bias:
        ranked = sorted(
            candidates,
            key=lambda candidate: _distance_from_bias(candidate, bias),
        )

        if (
            max_bias_distance_km is not None
            and _distance_from_bias(ranked[0], bias)
            > max_bias_distance_km
        ):
            return None

        return ranked[0]

    return candidates[0]


def _build_context(place, bias):
    query = str(place).strip()

    if not bias:
        return query

    context = [
        bias.get("city"),
        bias.get("region"),
        bias.get("country"),
    ]

    context = [
        str(value).strip()
        for value in context
        if value and str(value).strip()
    ]

    if context:
        return f"{query}, {', '.join(context)}"

    return query


def _arcgis_candidates(place, bias=None):
    query = _build_context(place, bias)

    params = {
        "singleLine": query,
        "maxLocations": 20,
        "outFields": "Match_addr,PlaceName,City,Region,Country",
        "outSR": 4326,
        "sourceCountry": "IND",
        "f": "json",
    }

    # ArcGIS uses the location as a spatial bias.
    if bias:
        params["location"] = f"{bias['lon']},{bias['lat']}"
        params["distance"] = 100000

    response = _geocoder_session.get(
        ARCGIS_URL,
        params=params,
        timeout=15,
    )
    response.raise_for_status()

    candidates = []

    for item in response.json().get("candidates", []):
        candidate = _candidate_from_arcgis(item)

        if candidate and _is_india(candidate):
            candidates.append(candidate)

    return candidates


def _nominatim_candidates(place, bias=None):
    query = _build_context(place, bias)

    params = {
        "q": query,
        "format": "jsonv2",
        "limit": 20,
        "addressdetails": 1,
        "countrycodes": "in",
    }

    response = _nominatim_request(params)

    candidates = []

    for result in response.json():
        candidate = _candidate_from_nominatim(result, query)

        if _is_india(candidate):
            candidates.append(candidate)

    return candidates


def _geocode_uncached(place, bias=None):
    if not str(place).strip():
        return None

    # With a destination bias, require the selected result to be
    # reasonably close to that destination. This prevents an ambiguous
    # name such as "Clock Tower" from jumping to another Indian city.
    max_bias_distance_km = 100 if bias else None

    try:
        candidates = _arcgis_candidates(place, bias)

        selected = _select_candidate(
            candidates,
            bias=bias,
            max_bias_distance_km=max_bias_distance_km,
        )

        if selected:
            return selected

    except requests.RequestException:
        pass

    candidates = _nominatim_candidates(place, bias)

    return _select_candidate(
        candidates,
        bias=bias,
        max_bias_distance_km=max_bias_distance_km,
    )


@st.cache_data(ttl=3600, show_spinner=False)
def geocode_place(place, bias=None):
    return _geocode_uncached(place, bias)


def geocode_two_places(start_location, destination):
    """
    Resolve both locations within India.

    The destination is resolved first. The start location is then
    resolved normally and, if it is geographically far from the
    destination, resolved again using the destination as context.

    A final sanity check prevents obviously incorrect long-distance
    matches for short local trips.
    """

    destination_result = geocode_place(destination)

    if destination_result is None:
        return None, None

    start_result = geocode_place(start_location)

    if start_result is None:
        start_result = geocode_place(
            start_location,
            bias=destination_result,
        )

    elif (
        _haversine_km(
            start_result["lat"],
            start_result["lon"],
            destination_result["lat"],
            destination_result["lon"],
        )
        > 100
    ):
        contextual = geocode_place(
            start_location,
            bias=destination_result,
        )

        if contextual:
            start_result = contextual

    if start_result is None:
        return None, destination_result

    # Final safety check:
    # If a generic place resolves thousands of kilometres away,
    # try contextual resolution one final time.
    direct_distance = _haversine_km(
        start_result["lat"],
        start_result["lon"],
        destination_result["lat"],
        destination_result["lon"],
    )

    if direct_distance > 100:
        contextual = geocode_place(
            start_location,
            bias=destination_result,
        )

        if contextual:
            contextual_distance = _haversine_km(
                contextual["lat"],
                contextual["lon"],
                destination_result["lat"],
                destination_result["lon"],
            )

            if contextual_distance < direct_distance:
                start_result = contextual

    return start_result, destination_result


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

    duration = max(float(route.get("duration", 0)), 1)
    distance = max(float(route.get("distance", 0)), 1)

    time_score = (fastest_duration / duration) * 100
    distance_score = (shortest_distance / distance) * 100

    route_efficiency = duration / distance
    fastest_efficiency = fastest_duration / shortest_distance

    if route_efficiency <= fastest_efficiency:
        efficiency_score = 100
    else:
        efficiency_score = (
            fastest_efficiency / route_efficiency
        ) * 100

    score = (
        time_score * 0.55
        + distance_score * 0.25
        + efficiency_score * 0.20
    )

    return round(min(max(score, 0), 100), 1)


def analyze_routes(routes):
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

    for route in routes:
        route_copy = dict(route)

        route_copy["smart_score"] = calculate_route_score(
            route_copy,
            fastest_duration,
            shortest_distance,
        )

        route_copy["delay_seconds"] = max(
            0,
            route_copy["duration"] - fastest_duration,
        )

        route_copy["extra_distance"] = max(
            0,
            route_copy["distance"] - shortest_distance,
        )

        analyzed_routes.append(route_copy)

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


def get_recommendation_reason(route, routes):
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
        reasons.append("fastest estimated travel time")

    if route["distance"] == shortest_distance:
        reasons.append("shortest distance")

    if route.get("smart_score", 0) >= 85:
        reasons.append("strong overall route efficiency")

    if not reasons:
        reasons.append(
            "best overall balance of time and distance"
        )

    return ", ".join(reasons)


# ============================================================
# FORMATTING
# ============================================================

def format_duration(seconds):
    total_minutes = round(seconds / 60)
    hours = total_minutes // 60
    minutes = total_minutes % 60

    if hours > 0:
        return f"{hours} hr {minutes} min"

    return f"{minutes} min"


def format_distance(meters):
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
        location=[center_lat, center_lon],
        zoom_start=12,
        control_scale=True,
    )

    folium.Marker(
        location=[start["lat"], start["lon"]],
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
            for lon, lat in route["geometry"]["coordinates"]
        ]

        is_best = index == best_index

        if is_best:
            color = "green"
            weight = 8
            label = "⭐ Recommended Route"
        else:
            color = route_colors[
                index % len(route_colors)
            ]
            weight = 5
            label = f"Alternative Route {index + 1}"

        score = route.get("smart_score")

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
