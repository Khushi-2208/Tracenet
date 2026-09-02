"""
Export Routes for TRACENET.
Handles CSV export, PDF report generation, and full graph data export.
"""

import io
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from backend.services.state import app_state
from reports.exporter import ReportExporter

router = APIRouter()


@router.get("/export/csv")
async def export_csv():
    """Export investigation results as a downloadable CSV file."""
    if not app_state.is_processed:
        raise HTTPException(status_code=400, detail="No dataset processed.")

    csv_content = ReportExporter.to_csv(app_state.relationships)

    return StreamingResponse(
        io.BytesIO(csv_content.encode("utf-8")),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=TRACENET_Investigation_Results.csv"}
    )


@router.get("/export/json")
async def export_json():
    """Export investigation results as a JSON file."""
    if not app_state.is_processed:
        raise HTTPException(status_code=400, detail="No dataset processed.")

    json_content = ReportExporter.to_json(app_state.relationships, app_state.stats)

    return StreamingResponse(
        io.BytesIO(json_content.encode("utf-8")),
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=TRACENET_Intelligence_Report.json"}
    )


@router.get("/export/pdf")
async def export_pdf(
    username_a: Optional[str] = Query(None, description="First username in the pair"),
    username_b: Optional[str] = Query(None, description="Second username in the pair")
):
    """
    Export a professional PDF investigation report.
    If username_a and username_b are provided, generates a report for that pair.
    Otherwise, generates a report for the top-ranked relationship.
    """
    if not app_state.is_processed:
        raise HTTPException(status_code=400, detail="No dataset processed.")

    if not app_state.relationships:
        raise HTTPException(status_code=404, detail="No relationships to export.")

    # Find the target relationship
    target_rel = None
    if username_a and username_b:
        for r in app_state.relationships:
            if ((r["username_a"] == username_a and r["username_b"] == username_b) or
                (r["username_a"] == username_b and r["username_b"] == username_a)):
                target_rel = r
                break
        if not target_rel:
            raise HTTPException(status_code=404, detail=f"No relationship between '{username_a}' and '{username_b}'.")
    else:
        target_rel = app_state.relationships[0]

    # Generate PDF
    pdf_bytes = ReportExporter.to_pdf(target_rel, app_state.stats)

    filename = f"TRACENET_Report_{target_rel['username_a']}_{target_rel['username_b']}.pdf"
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/export/graph")
async def export_full_graph():
    """Export full characteristic graph as D3-compatible JSON."""
    if not app_state.is_processed:
        raise HTTPException(status_code=400, detail="No dataset processed.")

    return app_state.get_full_graph_data()


@router.get("/timeline")
async def get_full_timeline():
    """Get chronological activity timeline for all actors."""
    if not app_state.is_processed:
        raise HTTPException(status_code=400, detail="No dataset processed.")

    return {
        "events": app_state.get_timeline(),
        "count": len(app_state.get_timeline())
    }
