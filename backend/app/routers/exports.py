"""Export endpoints."""

from datetime import datetime
from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from ..database import get_db
from ..services.exports import OvertimeTableExportService

router = APIRouter()


def _parse_export_date(raw_date: str | None) -> datetime.date:
    if not raw_date:
        raise HTTPException(
            status_code=400,
            detail="Missing required query parameter: date (YYYY-MM-DD)",
        )

    try:
        return datetime.strptime(raw_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid date format. Expected YYYY-MM-DD",
        )


@router.get("/overtime-table")
async def export_overtime_table(
    date: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> Response:
    export_date = _parse_export_date(date)
    service = OvertimeTableExportService(db)
    pdf_bytes = service.build_pdf(export_date)
    filename = f"{export_date.isoformat()}_上班人员统计表.pdf"
    encoded_filename = quote(filename)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": (
                f"attachment; filename=\"overtime-table-{export_date.isoformat()}.pdf\"; "
                f"filename*=UTF-8''{encoded_filename}"
            )
        },
    )
