"""
Analysis & Evidence Routes for TRACENET.
Handles persona links, evidence breakdown, and investigator review actions.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from backend.services.state import app_state

router = APIRouter()


class ReviewAction(BaseModel):
    username_a: str
    username_b: str
    status: Optional[str] = None
    notes: Optional[str] = None


@router.get("/persona-links")
async def get_persona_links(
    min_confidence: Optional[float] = Query(None, description="Minimum confidence filter"),
    limit: Optional[int] = Query(None, description="Max number of results")
):
    """Get all persona relationships sorted by confidence score."""
    if not app_state.is_processed:
        raise HTTPException(status_code=400, detail="No dataset processed.")

    relationships = app_state.relationships

    if min_confidence is not None:
        relationships = [r for r in relationships if r["confidence_score"] >= min_confidence]

    if limit:
        relationships = relationships[:limit]

    return {
        "relationships": relationships,
        "count": len(relationships),
        "total": len(app_state.relationships)
    }


@router.get("/evidence/{username_a}/{username_b}")
async def get_evidence_breakdown(username_a: str, username_b: str):
    """Get detailed evidence breakdown for a specific persona pair."""
    if not app_state.is_processed:
        raise HTTPException(status_code=400, detail="No dataset processed.")

    for r in app_state.relationships:
        if ((r["username_a"] == username_a and r["username_b"] == username_b) or
            (r["username_a"] == username_b and r["username_b"] == username_a)):
            return {"evidence": r}

    raise HTTPException(status_code=404, detail=f"No relationship found between '{username_a}' and '{username_b}'.")


@router.post("/investigation/verify")
async def verify_link(action: ReviewAction):
    """Mark a potential persona link as verified by the investigator."""
    if not app_state.is_processed:
        raise HTTPException(status_code=400, detail="No dataset processed.")

    status = action.status or "Marked as Verified Link"
    success = app_state.update_relationship(action.username_a, action.username_b, status=status)

    if not success:
        raise HTTPException(status_code=404, detail="Relationship not found.")

    return {"status": "success", "message": f"Link {action.username_a} <-> {action.username_b} verified."}


@router.post("/investigation/reject")
async def reject_link(action: ReviewAction):
    """Mark a potential persona link as rejected/dismissed by the investigator."""
    if not app_state.is_processed:
        raise HTTPException(status_code=400, detail="No dataset processed.")

    status = action.status or "Dismissed / Unrelated"
    success = app_state.update_relationship(action.username_a, action.username_b, status=status)

    if not success:
        raise HTTPException(status_code=404, detail="Relationship not found.")

    return {"status": "success", "message": f"Link {action.username_a} <-> {action.username_b} rejected."}


@router.post("/investigation/note")
async def add_note(action: ReviewAction):
    """Add investigator notes to a persona link."""
    if not app_state.is_processed:
        raise HTTPException(status_code=400, detail="No dataset processed.")

    if not action.notes:
        raise HTTPException(status_code=400, detail="Notes field is required.")

    success = app_state.update_relationship(
        action.username_a, action.username_b,
        status=action.status,
        notes=action.notes
    )

    if not success:
        raise HTTPException(status_code=404, detail="Relationship not found.")

    return {"status": "success", "message": "Investigator notes saved."}
