from fastapi import APIRouter, HTTPException, Response, Depends
from db.session import SessionLocal
from services.pdf_generator import generate_salary_pdf
from core.auth import manager_required

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

router = APIRouter()

@router.get("/generateSalaryPdf/{employee_id}")
def generate_salary_pdf_endpoint(employee_id: int, db=Depends(get_db), current_user=Depends(manager_required)):
    try:
        pdf_bytes = generate_salary_pdf(db, employee_id)
        headers = {
            'Content-Disposition': f'attachment; filename="salary_slip_{employee_id}.pdf"'
        }
        return Response(content=pdf_bytes, media_type='application/pdf', headers=headers)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error.")
