from fastapi import FastAPI
from api.routers import employee, salary_slip
from api.routers import pdf
from api.routers import send_pdf
from api.routers import auth
from core.logging import setup_request_logging

app = FastAPI()
setup_request_logging(app)


app.include_router(employee.router)
app.include_router(salary_slip.router)
app.include_router(pdf.router)
app.include_router(send_pdf.router)
app.include_router(auth.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)