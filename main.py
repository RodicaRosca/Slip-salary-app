from fastapi import FastAPI
from api.routers import employee, salary_slip
from api.routers import pdf



app = FastAPI()
app.include_router(employee.router)
app.include_router(salary_slip.router)
app.include_router(pdf.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)