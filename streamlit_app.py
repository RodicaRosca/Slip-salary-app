import streamlit as st
import requests

API_URL = "http://localhost:8000"  

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


def logout():
    st.session_state.pop("token", None)
    st.success("Logged out successfully!")
    st.rerun()  


def generate_aggregated_report():
    st.write("Generating aggregated employee data report...")


def generate_employee_report():
    st.write("Generating individual employee salary report...")


def send_salary_pdf():
    st.write("Sending salary PDF to employees...")


def send_aggregated_employee_data():
    st.write("Sending aggregated employee data to managers...")


def main():
    if "token" not in st.session_state:
        login()
        return
    st.sidebar.button("Logout", on_click=lambda: st.session_state.pop("token", None) or st.rerun())
    st.title("Welcome to the Salary Slip App!")
    st.write("You are logged in. Add your app features here.")
    st.button("Generate Aggregated Employee Data Report", on_click=generate_aggregated_report)
    st.button("Generate Individual Employee Salary Report", on_click=generate_employee_report)
    st.button("Send Salary PDF to Employees", on_click=send_salary_pdf)
    st.button("Send Aggregated Employee Data to Managers", on_click=send_aggregated_employee_data)


if __name__ == "__main__":
    main()
