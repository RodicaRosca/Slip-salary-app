import streamlit as st
import requests

API_URL = "http://localhost:8000"  # Change if your FastAPI runs elsewhere

def login():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        response = requests.post(f"{API_URL}/token", data={"username": username, "password": password})
        if response.status_code == 200:
            token = response.json()["access_token"]
            st.session_state["token"] = token
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Login failed. Check your credentials.")

def main():
    if "token" not in st.session_state:
        login()
        return
    st.sidebar.button("Logout", on_click=lambda: st.session_state.pop("token", None) or st.rerun())
    st.title("Welcome to the Salary Slip App!")
    st.write("You are logged in. Add your app features here.")

if __name__ == "__main__":
    main()
