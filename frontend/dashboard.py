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


def display_historical(history_items, days_back=10):
    st.subheader(f"Historical Data (Last {days_back} Days)")
    if not history_items:
        st.warning("No historical data available")
        return

    df = pd.DataFrame(history_items)
    df["fetched_at"] = pd.to_datetime(df["fetched_at"])
    cutoff = datetime.utcnow() - timedelta(days=days_back)
    df = df[df["fetched_at"] >= cutoff]
    if df.empty:
        st.warning("No data in the selected time range")
        return

    metrics = ["temperature", "humidity", "wind_speed", "pressure"]

    for metric in metrics:
        if metric in df.columns:
            fig = px.line(
                df,
                x="fetched_at",
                y=metric,
                title=f"{metric.replace('_', ' ').title()} Trend",
                labels={
                    "fetched_at": "Time",
                    metric: metric.replace("_", " ").title()
                },
            )
            st.plotly_chart(fig, use_container_width=True)


def render_current_weather():
    st.title("Current Weather 🌤️")

    with st.sidebar:
        st.header("Search Weather")
        city = st.text_input("City")
        params = {"units": "metric"}  # Celsius only

        if st.button("Get Current Weather"):
            if not city:
                st.error("Please enter a city")
            else:
                try:
                    cur_resp = requests.get(
                        f"{API_URL}/weather/current/{city}",
                        headers=get_auth_headers(),
                        params=params,
                        timeout=5
                    )
                    cur_resp.raise_for_status()
                    raw = cur_resp.json()

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

                    st.session_state.current = current

                except requests.exceptions.HTTPError:
                    st.error("Too many requests, try later")

    if "current" in st.session_state:
        current = st.session_state.current
        st.subheader(f"Current Weather in {current.get('city', '')}")
        try:
            cols = st.columns(3)
            cols[0].metric("Temperature", f"{current['temperature']}°C")
            cols[1].metric("Humidity", f"{current['humidity']}%")
            cols[2].metric("Wind Speed", f"{current['wind_speed']} m/s")
        except KeyError:
            st.error("Unexpected response format:")
            st.json(current)


def render_historical_weather():
    st.title("Historical Weather 📊")

    with st.sidebar:
        st.header("Historical Weather Settings")
        city = st.text_input("City", key="hist_city")

        if st.button("Get Historical Weather"):
            if not city:
                st.error("Please enter a city")
            else:
                try:
                    hist_resp = requests.get(
                        f"{API_URL}/weather/history/{city}",
                        headers=get_auth_headers(),
                        timeout=10
                    )
                    hist_resp.raise_for_status()
                    history = hist_resp.json()

                    st.session_state.history = history

                except requests.exceptions.HTTPError as e:
                    st.error(f"Error fetching history data: {e.response.text}")

    if "history" in st.session_state:
        display_historical(st.session_state.history)


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
                        json={
                            "city": city,
                            "temperature_threshold": threshold
                        },
                        timeout=10
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

    email = st.session_state.email

    st.sidebar.markdown(
        f"""
        <p style="font-size:20px; margin: 0;">
        <strong>Welcome,</strong>
        <span style="color: #ADD8E6; text-decoration: underline;">
            {email}
        </span>
        </p>
        """,
        unsafe_allow_html=True,
    )

    if st.sidebar.button("Logout"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()

    page = st.sidebar.radio("Navigate", ["Dashboard",
                                         "Historical", "Subscribe"])

    if page == "Dashboard":
        render_current_weather()
    elif page == "Historical":
        render_historical_weather()
    else:
        subscribe_page()


if __name__ == "__main__":
    main()
