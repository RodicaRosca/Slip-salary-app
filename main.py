
from fastapi import FastAPI, Response, HTTPException
from db.session import SessionLocal
from services.employee_report import generate_employee_salary_report
from services.employee_create import create_employee_service
from api.schemas import EmployeeCreate

app = FastAPI()

@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.get("/createAggregatedEmployeeData")
def create_aggregated_employee_data():
    session = SessionLocal()
    try:
        excel_bytes = generate_employee_salary_report(session)
    finally:
        session.close()
    headers = {
        'Content-Disposition': 'attachment; filename="aggregated_employee_data.xlsx"'
    }
    return Response(content=excel_bytes, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', headers=headers)


# Endpoint to create a new employee or manager
@app.post("/createEmployee")
def create_employee(emp: EmployeeCreate):
    session = SessionLocal()
    try:
        result = create_employee_service(session, emp)
        return result
    except HTTPException as e:
        raise e
    except Exception:
        session.rollback()
        raise HTTPException(status_code=500, detail="Internal server error.")
    finally:
        session.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)