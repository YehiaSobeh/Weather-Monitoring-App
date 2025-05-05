# dashboard.py
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta

load_dotenv()
FASTAPI_BASE = os.getenv("FASTAPI_URL", "http://localhost:8000")
API_URL = f"{FASTAPI_BASE}/api/v1"


def get_auth_headers():
    return {"Authorization": f"Bearer {st.session_state.access_token}"}


def display_historical(history_items, days_back):
    st.subheader(f"Historical Data (Last {days_back} Days)")
    if not history_items:
        st.warning("No historical data available")
        return

    # Build DataFrame and filter by date
    df = pd.DataFrame(history_items)
    df['fetched_at'] = pd.to_datetime(df['fetched_at'])
    cutoff = datetime.utcnow() - timedelta(days=days_back)
    df = df[df['fetched_at'] >= cutoff]
    if df.empty:
        st.warning("No data in the selected time range")
        return

    # List out the metrics we know about
    metrics = ["temperature", "humidity", "wind_speed", "pressure"]

    # For each metric, if present, plot a line chart
    for metric in metrics:
        if metric in df.columns:
            fig = px.line(
                df,
                x="fetched_at",
                y=metric,
                title=f"{metric.replace('_', ' ').title()} Trend",
                labels={"fetched_at": "Time",
                        metric: metric.replace('_', ' ').title()}
            )
            st.plotly_chart(fig, use_container_width=True)


def render_dashboard():
    st.title("Weather Dashboard 🌦️")

    with st.sidebar:
        st.header("Search Weather")
        city = st.text_input("City")
        unit_system = st.radio("Units", ("Metric (°C)", "Imperial (°F)"))
        params = {"units": "metric" if unit_system.startswith("Metric") else
                  "imperial"}
        days_back = st.slider("Historical Days", 1, 90, 30)

        if st.button("Get Weather"):
            if not city:
                st.error("Please enter a city")
            else:
                try:
                    # Fetch current weather
                    cur_resp = requests.get(
                        f"{API_URL}/weather/current/{city}",
                        headers=get_auth_headers(),
                        params=params
                    )
                    cur_resp.raise_for_status()
                    raw = cur_resp.json()

                    # Flatten both OpenWeatherMap‐style payloads
                    #  or your flat schema
                    if "main" in raw:
                        current = {
                            "city": raw.get("name", city),
                            "temperature": raw["main"].get("temp"),
                            "humidity": raw["main"].get("humidity"),
                            "wind_speed": raw.get("wind", {}).get("speed"),
                            "pressure": raw["main"].get("pressure"),
                        }
                    else:
                        current = raw

                    # Fetch weather history
                    hist_resp = requests.get(
                        f"{API_URL}/weather/history/{city}",
                        headers=get_auth_headers()
                    )
                    hist_resp.raise_for_status()
                    history = hist_resp.json()

                    st.session_state.current = current
                    st.session_state.history = history
                    st.session_state.days_back = days_back

                except requests.exceptions.HTTPError as e:
                    st.error(f"Error fetching weather: {e.response.text}")

    # Display current weather summary
    if "current" in st.session_state:
        current = st.session_state.current
        st.subheader(f"Current Weather in {current.get('city', '')}")
        try:
            cols = st.columns(3)
            cols[0].metric("Temperature", f"{current['temperature']}°")
            cols[1].metric("Humidity", f"{current['humidity']}%")
            cols[2].metric("Wind Speed", f"{current['wind_speed']} m/s")
        except KeyError:
            st.error("Unexpected response format:")
            st.json(current)

    # Display every historical chart
    if "history" in st.session_state:
        display_historical(st.session_state.history,
                           st.session_state.days_back)


def subscribe_page():
    st.title("Subscribe to Alerts")
    st.info("Receive notifications when temperature crosses your threshold.")

    with st.form("subscribe_form"):
        city = st.text_input("City")
        threshold = st.number_input("Temperature Threshold", value=20.0)
        if st.form_submit_button("Subscribe"):
            if not city:
                st.error("Please enter a city")
            else:
                try:
                    resp = requests.post(
                        f"{API_URL}/subscribe/create",
                        headers=get_auth_headers(),
                        json={"city": city, "temperature_threshold": threshold}
                    )
                    resp.raise_for_status()
                    st.success("Subscribed successfully!")
                except requests.exceptions.HTTPError as e:
                    st.error(f"Subscription failed: {e.response.text}")


def main():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        if "show_login" not in st.session_state or st.session_state.show_login:
            from auth import login_page, register_page
            login_page()
            if st.button("Don't have an account? Register"):
                st.session_state.show_login = False
                st.rerun()
        else:
            from auth import login_page, register_page
            register_page()
            if st.button("Already have an account? Login"):
                st.session_state.show_login = True
                st.rerun()
        return

    st.sidebar.title(f"Welcome, {st.session_state.email}")
    if st.sidebar.button("Logout"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()

    page = st.sidebar.radio("Navigate", ["Dashboard", "Subscribe"])
    if page == "Dashboard":
        render_dashboard()
    else:
        subscribe_page()


if __name__ == "__main__":
    main()
