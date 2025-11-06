import streamlit as st
import requests
import uuid
import os
from dotenv import load_dotenv


load_dotenv()

API_URL = os.getenv("API_URL", "http://localhost:8000")


if "idempotency_key" not in st.session_state:
    st.session_state["idempotency_key"] = str(uuid.uuid4())


def login():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        try:
            response = requests.post(f"{API_URL}/token", data={"username": username, "password": password})
            if response.status_code == 200:
                token = response.json()["access_token"]
                st.session_state["token"] = token
                st.success("Login successful!")
                st.rerun()
        except Exception as e:
            st.error(f"Login failed: {e}")
        else:
            st.error("Login failed. Check your credentials.")


def logout():
    try:
        st.session_state.pop("token", None)
        st.success("Logged out successfully!")
        st.rerun()      
    except Exception as e:
        st.error(f"Logout failed: {e}")


def generate_aggregated_report():
    st.write("Generating aggregated employee data report...")
    token = st.session_state.get("token")
    if not token:
        st.error("You must be logged in.")
        return

    if "agg_report_idempotency_key" not in st.session_state:
        st.session_state["agg_report_idempotency_key"] = str(uuid.uuid4())
    headers = {
        "Authorization": f"Bearer {token}",
        "Idempotency-Key": st.session_state["agg_report_idempotency_key"]
    }
    response = requests.post(f"{API_URL}/createAggregatedEmployeeData", headers=headers)
    if response.status_code == 200 and response.content:
        try:
            result = response.json()
            sent = result.get("sent", 0)
            errors = result.get("errors", [])
            if sent > 0 and not errors:
                st.success("Aggregated report generated successfully!")
            else:
                error_msg = errors if errors else result
                st.error(f"No report generated: {error_msg}")
        except Exception:
            st.error("Received invalid JSON from server.")
    else:
        try:
            error_json = response.json()
            error_detail = error_json.get("detail") or error_json.get("error") or response.text
        except Exception:
            error_detail = response.text

        if error_detail:
            if isinstance(error_detail, str):
                error_detail = error_detail.split(':', 1)[-1].strip() if ':' in error_detail else error_detail
            st.error(f"No report generated: {error_detail}")
        else:
            st.error("No report generated: Unknown error.")

def generate_employee_report():
    st.write("Generating individual employee salary report...")
    token = st.session_state.get("token")
    if not token:
        st.error("You must be logged in.")
        return

    if "emp_report_idempotency_key" not in st.session_state:
        st.session_state["emp_report_idempotency_key"] = str(uuid.uuid4())
    headers = {
        "Authorization": f"Bearer {token}",
        "Idempotency-Key": st.session_state["emp_report_idempotency_key"]
    }

    try:
        response = requests.post(f"{API_URL}/createPdfForEmployees", headers=headers)
        if response.status_code == 200:
            result = response.json()
            generated = result.get("generated", [])
            errors = result.get("errors", [])
            if generated:
                st.success(f"PDFs generated for: {[item['employee'] for item in generated]}")
            else:
                error_msg = errors if errors else result
                st.error(f"No PDFs generated: {error_msg}")
        else:
            try:
                error_detail = response.json().get("detail", response.text)
            except Exception:
                error_detail = response.text
            st.error(f"Failed to generate PDFs: {error_detail}")
    except Exception as e:
        st.error(f"An unexpected error occurred while generating employee reports: {e}")

def send_salary_pdf():
    st.write("Sending salary PDF to employees...")
    token = st.session_state.get("token")
    if not token:
        st.error("You must be logged in.")
        return
    

    if "send_pdf_idempotency_key" not in st.session_state:
        st.session_state["send_pdf_idempotency_key"] = str(uuid.uuid4())
    headers = {
        "Authorization": f"Bearer {token}",
        "Idempotency-Key": st.session_state["send_pdf_idempotency_key"]
    }
    try:
        response = requests.post(f"{API_URL}/sendPdfToEmployees", headers=headers)
        if response.status_code == 200:
            result = response.json()
            sent_count = result.get("sent", 0)
            total = result.get("total", 0)
            errors = result.get("errors", [])
            if sent_count > 0:
                st.success(f"PDFs sent to {sent_count} out of {total} employees.")
            else:
                error_msg = errors if errors else result
                st.error(f"No PDFs sent: {error_msg}")
        else:
            try:
                error_detail = response.json().get("detail", response.text)
            except Exception:
                error_detail = response.text
            st.error(f"Failed to generate PDFs: {error_detail}")
    except Exception as e:
        st.error(f"An unexpected error occurred while sending salary PDFs: {e}")

def send_aggregated_employee_data():
    st.write("Sending aggregated employee data to managers...")
    token = st.session_state.get("token")
    if not token:
        st.error("You must be logged in.")
        return
    

    if "send_agg_data_idempotency_key" not in st.session_state:
        st.session_state["send_agg_data_idempotency_key"] = str(uuid.uuid4())
    headers = {
        "Authorization": f"Bearer {token}",
        "Idempotency-Key": st.session_state["send_agg_data_idempotency_key"]
    }
    try:
        response = requests.post(f"{API_URL}/sendAggregatedEmployeeData", headers=headers)
        if response.status_code == 200 and response.content:
            try:
                result = response.json()
                st.success("Aggregated employee data sent to manager successfully!")
                sent = result.get("sent", 0)
                errors = result.get("errors", [])
                if sent > 0:
                    st.success(f"Reports sent to {sent} managers.")
                else:
                    error_msg = errors if errors else result
                    st.error(f"No reports sent: {error_msg}")
            except Exception:
                st.error("Received invalid JSON from server.")
        else:
            if response.content:
                try:
                    error_detail = response.json().get("detail", response.text)
                except Exception:
                    error_detail = response.text
                st.error(f"Failed to send reports: {error_detail}")
            else:
                st.error("No response received from server.")
    except Exception as e:
        st.error(f"An unexpected error occurred while sending aggregated employee data: {e}")

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
