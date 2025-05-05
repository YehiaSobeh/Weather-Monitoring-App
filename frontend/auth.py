# auth.py
import streamlit as st
import requests
from dotenv import load_dotenv
import os

load_dotenv()
FASTAPI_BASE = os.getenv("FASTAPI_URL", "http://localhost:8000")
API_URL = f"{FASTAPI_BASE}/api/v1"


def login_page():
    st.title("Weather Dashboard Login")

    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.form_submit_button("Login"):
            try:
                response = requests.post(
                    f"{API_URL}/user/login",
                    json={"email": email, "password": password}
                )
                response.raise_for_status()

                token_data = response.json()
                st.session_state.access_token = token_data["access_token"]
                st.session_state.authenticated = True
                st.session_state.email = email
                st.rerun()
            except requests.exceptions.HTTPError:
                st.error("Invalid credentials")


def register_page():
    st.title("Register New Account")

    with st.form("register_form"):
        name = st.text_input("First Name")
        surname = st.text_input("Last Name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")

        if st.form_submit_button("Register"):
            if password != confirm_password:
                st.error("Passwords don't match")
                return

            try:
                response = requests.post(
                    f"{API_URL}/user/register",
                    json={
                        "name": name,
                        "surname": surname,
                        "email": email,
                        "password": password,
                    },
                )
                response.raise_for_status()
                st.session_state.show_login = True
                st.success("Registration successful! Redirecting to login...")
                st.rerun()
            except requests.exceptions.HTTPError as e:
                error_detail = e.response.json().get(
                    "detail",
                    "Registration failed"
                    )
                st.error(f"Error: {error_detail}")
