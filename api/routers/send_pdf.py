import traceback
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from core.auth import manager_required, get_db
from core.idempotency import idempotency_key_dependency
from services.reports_service import create_manager_report, create_pdfs_for_employees, send_report_to_manager, send_pdfs_to_employees
import redis
import json


redis_client = redis.Redis(host='redis', port=6379, db=0)
router = APIRouter()


@router.post("/createAggregatedEmployeeData")
def create_report_for_managers(
    db: Session = Depends(get_db),
    current_user=Depends(manager_required),
    idempotency_key=Depends(idempotency_key_dependency)
):
    redis_key = f"idempotency:createAggregatedEmployeeData:{current_user.id}:{idempotency_key}"
    cached_result = redis_client.get(redis_key)
    if cached_result:
        return JSONResponse(status_code=200, content=json.loads(cached_result))
    try:
        result = create_manager_report(db, current_user.id)
        redis_client.set(redis_key, json.dumps(result), ex=3600)
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
    redis_key = f"idempotency:createPdfForEmployees:{current_user.id}:{idempotency_key}"
    cached_result = redis_client.get(redis_key)
    if cached_result:
        return JSONResponse(status_code=200, content=json.loads(cached_result))
    try:
        result = create_pdfs_for_employees(db, current_user.id)
        redis_client.set(redis_key, json.dumps(result), ex=3600)
        return JSONResponse(status_code=200, content=result)
    except Exception as e:
        print(f"Error generating PDF reports: {e}")
        traceback.print_exc()
        return JSONResponse(status_code=200, content={"generated": False, "error": str(e), "manager_id": current_user.id})


@router.post("/sendAggregatedEmployeeData")
def send_report_to_managers(
    db: Session = Depends(get_db),
    current_user=Depends(manager_required),
    idempotency_key: str = Depends(idempotency_key_dependency)
):
    redis_key = f"idempotency:sendAggregatedEmployeeData:{current_user.id}:{idempotency_key}"
    cached_result = redis_client.get(redis_key)
    if cached_result:
        return json.loads(cached_result)
    try:
        result = send_report_to_manager(current_user.email)
        redis_client.set(redis_key, json.dumps(result), ex=3600)  # expires in 1 hour
        return result
    except Exception as e:
        print(f"Error sending aggregated employee data for manager {current_user.id}: {e}")
        traceback.print_exc()
        return {"sent": 0, "errors": [str(e)]}


@router.post("/sendPdfToEmployees")
def send_pdf_to_employees(
    db: Session = Depends(get_db),
    current_user=Depends(manager_required),
    idempotency_key=Depends(idempotency_key_dependency)
):
    redis_key = f"idempotency:sendPdfToEmployees:{current_user.id}:{idempotency_key}"
    cached_result = redis_client.get(redis_key)
    if cached_result:
        return json.loads(cached_result)
    try:
        result = send_pdfs_to_employees(db, current_user.id)
        redis_client.set(redis_key, json.dumps(result), ex=3600)  # expires in 1 hour
        return result
    except Exception as e:
        print(f"Error sending PDFs to employees of manager {current_user.id}: {e}")
        traceback.print_exc()
        return {"sent": 0, "total": 0, "errors": [str(e)]}
