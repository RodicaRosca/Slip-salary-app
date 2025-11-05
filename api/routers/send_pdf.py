import traceback
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from core.auth import manager_required, get_db
from core.idempotency import idempotency_key_dependency
from services.reports_service import create_manager_report, create_pdfs_for_employees, send_report_to_manager, send_pdfs_to_employees


router = APIRouter()


@router.post("/createReportForManagers")
def create_report_for_managers(
    db: Session = Depends(get_db),
    current_user=Depends(manager_required),
    idempotency_key=Depends(idempotency_key_dependency)
):
    try:
        result = create_manager_report(db, current_user.id)
        return JSONResponse(status_code=200, content=result)
    except Exception as e:
        print(f"Error generating Excel report: {e}")
        traceback.print_exc()
        return JSONResponse(status_code=200, content={"sent": 0, "errors": [str(e)]})


@router.post("/createPdfForEmployees")
def create_pdf_for_employees(
    db: Session = Depends(get_db),
    current_user=Depends(manager_required),
    idempotency_key=Depends(idempotency_key_dependency)
):
    try:
        result = create_pdfs_for_employees(db, current_user.id)
        return JSONResponse(status_code=200, content=result)
    except Exception as e:
        print(f"Error generating PDF reports: {e}")
        traceback.print_exc()
        return JSONResponse(status_code=200, content={"generated": False, "error": str(e), "manager_id": current_user.id})


@router.post("/sendReportToManagers")
def send_report_to_managers(
    db: Session = Depends(get_db),
    current_user=Depends(manager_required),
    idempotency_key=Depends(idempotency_key_dependency)
):
    try:
        result = send_report_to_manager(current_user.email)
        return result
    except Exception as e:
        print(f"Error sending report to manager {current_user.email}: {e}")
        traceback.print_exc()
        return {"sent": 0, "errors": [str(e)]}


@router.post("/sendPdfToEmployees")
def send_pdf_to_employees(
    db: Session = Depends(get_db),
    current_user=Depends(manager_required),
    idempotency_key=Depends(idempotency_key_dependency)
):
    try:
        result = send_pdfs_to_employees(db, current_user.id)
        return result
    except Exception as e:
        print(f"Error sending PDFs to employees of manager {current_user.id}: {e}")
        traceback.print_exc()
        return {"sent": 0, "total": 0, "errors": [str(e)]}
