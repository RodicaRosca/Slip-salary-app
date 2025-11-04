from fastapi import HTTPException
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from PyPDF2 import PdfReader, PdfWriter
from models.models import Employee, SalarySlip
from sqlalchemy.orm import Session
from datetime import date


def generate_salary_pdf(session: Session, employee_id: int) -> bytes:
    try:
        employee = session.query(Employee).filter(Employee.id == employee_id).first()
        if not employee:
            raise ValueError("Employee not found")
        today = date.today()
        month_start = today.replace(day=1)
        slip = (
            session.query(SalarySlip)
            .filter(SalarySlip.employee_id == employee_id)
            .filter(SalarySlip.month >= month_start)
            .order_by(SalarySlip.month.desc())
            .first()
        )
        if not slip:
            raise ValueError("Salary slip not found for this month")

        # Generate PDF with professional layout
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        # Header
        c.setFont("Helvetica-Bold", 18)
        c.drawCentredString(width / 2, height - 60, "DavaX Company")
        c.setFont("Helvetica", 10)
        c.drawCentredString(width / 2, height - 80, "Salary Slip")
        # Logo box with vector drawing (stylized checkmark)
        logo_x = 40
        logo_y = height - 90
        logo_w = 50
        logo_h = 40
        c.rect(logo_x, logo_y, logo_w, logo_h, stroke=1, fill=0)
        # Draw a simple checkmark inside the box
        c.setStrokeColorRGB(0.2, 0.5, 0.2)
        c.setLineWidth(3)
        c.line(logo_x + 10, logo_y + 15, logo_x + 22, logo_y + 5)
        c.line(logo_x + 22, logo_y + 5, logo_x + 40, logo_y + 30)
        c.setStrokeColorRGB(0, 0, 0)
        c.setLineWidth(1)

        # Employee Info Section
        c.setFont("Helvetica-Bold", 12)
        c.drawString(40, height - 120, "Employee Information")
        c.setFont("Helvetica", 10)
        c.drawString(50, height - 140, f"Name: {employee.first_name} {employee.last_name}")
        c.drawString(250, height - 140, f"Employee ID: {employee.employee_id}")
        c.drawString(50, height - 155, f"CNP: {employee.cnp}")
        c.drawString(250, height - 155, f"Email: {employee.email}")

        # Salary Details Section (aligned, realistic)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(40, height - 185, "Salary Details")
        c.setFont("Helvetica", 10)
        # Adjusted box and text positions for proper framing
        row_height = 20
        num_rows = 4
        box_x = 45
        box_width = width - 90
        box_height = row_height * num_rows + 10
        box_y = height - 205 - box_height + 10
        c.roundRect(box_x, box_y, box_width, box_height, 8, stroke=1, fill=0)

        # Draw horizontal lines for rows
        for i in range(1, num_rows):
            c.line(box_x, box_y + box_height - i * row_height, box_x + box_width, box_y + box_height - i * row_height)

        # Draw vertical line for columns
        col_x = box_x + int(box_width / 2)
        c.line(col_x, box_y, col_x, box_y + box_height)

        # Left column labels and values
        c.drawString(box_x + 12, box_y + box_height - row_height + 5, "Month:")
        c.drawString(box_x + 12, box_y + box_height - 2 * row_height + 5, "Working Days:")
        c.drawString(box_x + 12, box_y + box_height - 3 * row_height + 5, "Vacation Days:")
        c.drawString(box_x + 12, box_y + box_height - 4 * row_height + 5, "Additional Bonuses:")

        # Right column labels and values
        c.drawString(col_x + 12, box_y + box_height - row_height + 5, "Base Salary:")
        c.drawString(col_x + 12, box_y + box_height - 2 * row_height + 5, "Net Salary:")

        # Left column values
        c.drawRightString(col_x - 12, box_y + box_height - row_height + 5, slip.month.strftime('%B %Y'))
        c.drawRightString(col_x - 12, box_y + box_height - 2 * row_height + 5, str(slip.working_days))
        c.drawRightString(col_x - 12, box_y + box_height - 3 * row_height + 5, str(slip.vacation_days))
        c.drawRightString(col_x - 12, box_y + box_height - 4 * row_height + 5, f"{slip.bonuses:.2f}")

        # Right column values
        c.drawRightString(box_x + box_width - 12, box_y + box_height - row_height + 5, f"{slip.base_salary:.2f}")
        c.setFont("Helvetica-Bold", 10)
        c.drawRightString(box_x + box_width - 12, box_y + box_height - 2 * row_height + 5, f"{slip.total_salary:.2f}")
        c.setFont("Helvetica", 10)

        # Footer: Date and Signature
        c.setFont("Helvetica", 10)
        c.drawString(45, 100, f"Date: {today.strftime('%d %B %Y')}")
        c.drawString(width - 180, 100, "Signature:")
        # Draw a stylized, cursive-like 'DavaX' as a signature
        # Move signature slightly to the right for better alignment
        sig_x = width - 125
        sig_y = 90
        c.setStrokeColorRGB(0.07, 0.13, 0.22)
        c.setLineWidth(2.1)
        # D
        c.bezier(sig_x, sig_y, sig_x, sig_y + 18, sig_x + 18, sig_y + 18, sig_x + 18, sig_y)
        c.bezier(sig_x, sig_y, sig_x + 9, sig_y - 10, sig_x + 18, sig_y + 8, sig_x + 18, sig_y)
        # a
        c.bezier(sig_x + 22, sig_y, sig_x + 22, sig_y + 10, sig_x + 32, sig_y + 10, sig_x + 32, sig_y)
        c.bezier(sig_x + 22, sig_y, sig_x + 27, sig_y - 8, sig_x + 32, sig_y + 8, sig_x + 32, sig_y)
        # v
        c.bezier(sig_x + 36, sig_y + 8, sig_x + 40, sig_y - 8, sig_x + 44, sig_y + 8, sig_x + 48, sig_y)
        # a
        c.bezier(sig_x + 52, sig_y, sig_x + 52, sig_y + 10, sig_x + 62, sig_y + 10, sig_x + 62, sig_y)
        c.bezier(sig_x + 52, sig_y, sig_x + 57, sig_y - 8, sig_x + 62, sig_y + 8, sig_x + 62, sig_y)
        # X (crossed lines)
        c.line(sig_x + 68, sig_y + 10, sig_x + 80, sig_y - 8)
        c.line(sig_x + 68, sig_y - 8, sig_x + 80, sig_y + 10)
        # Add a flourish under the signature
        c.setLineWidth(1.1)
        c.bezier(sig_x, sig_y - 6, sig_x + 30, sig_y - 18, sig_x + 60, sig_y - 2, sig_x + 85, sig_y - 10)
        c.setStrokeColorRGB(0, 0, 0)
        c.setLineWidth(1)

        # Confidential note
        c.setFont("Helvetica-Oblique", 8)
        c.drawCentredString(width / 2, 60, "This document is confidential and intended for the recipient only.")

        c.save()
        buffer.seek(0)

        # Password-protect PDF with CNP
        reader = PdfReader(buffer)
        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)
        writer.encrypt(employee.cnp)
        output = BytesIO()
        writer.write(output)
        output.seek(0)
        return output.read()
    except Exception as e:
        print(f"Error generating PDF for employee ID {employee_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while generating PDF.")
