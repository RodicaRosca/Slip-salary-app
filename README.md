# Slip Salary App

A web application for generating, managing, and sending employee salary slips and aggregated reports. Built with FastAPI, SQLAlchemy, PostgreSQL, Docker, and Streamlit.

## Features
- **Role-based access:** Only managers can generate and send salary slips and reports.
- **Salary slip generation:** Create individual PDF salary slips for employees.
- **Aggregated reports:** Generate Excel reports summarizing employee salary data for managers.
- **Email sending:** Send salary slips and aggregated reports via email.
- **Streamlit frontend:** Simple UI for managers to trigger report generation and sending.
- **Dockerized deployment:** Easily run the app and database in containers.

## Endpoints
- `POST /createPdfForEmployees` – Generate PDF salary slips for all employees under a manager.
- `POST /sendPdfToEmployees` – Send generated PDF salary slips to employees via email.
- `POST /createAggregatedEmployeeData` – Generate an Excel report with aggregated employee data for a manager.
- `POST /sendAggregatedEmployeeData` – Send the aggregated Excel report to the manager via email (ensures latest data).

## Usage
1. **Start the app:**
	- Run `docker-compose up --build` to start the backend and database.
	- Run `streamlit run streamlit_app.py` for the frontend.
2. **Login as a manager:**
	- Use your credentials to log in via the Streamlit UI.
3. **Generate reports:**
	- Use the buttons to generate salary slips or aggregated reports.
4. **Send reports:**
	- Use the buttons to send salary slips or aggregated reports via email.

## Configuration
- Set environment variables in a `.env` file:
  - `API_URL`: Backend API URL (default: `http://localhost:8000`)
  - `SMTP_SERVER`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SENDER_EMAIL`: Email settings

## Project Structure
```
Slip-salary-app/
├── api/
│   └── routers/
│       └── send_pdf.py
├── services/
│   └── employee_report.py
├── models/
│   └── models.py
├── db/
│   └── session.py
├── streamlit_app.py
├── main.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## Requirements
- Python 3.11+
- Docker
- PostgreSQL
- Streamlit
- FastAPI
- SQLAlchemy
- pandas, xlsxwriter, requests, passlib, python-dotenv

## Notes
- Make sure the database is seeded with users and employees before testing.
- Only managers can access report generation and sending features.
- All generated reports reflect the latest data at the time of request.

