"""
CSV Upload & Processing Routes for TRACENET.
Handles file upload, validation, and pipeline execution.
"""

import os
import tempfile
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.services.state import app_state

router = APIRouter()


@router.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    """
    Upload a CSV dataset, validate columns, process through the full pipeline:
    CSV -> Validation -> Neo4j Graph -> AI Analysis -> Confidence Scores
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted.")

    # Save uploaded file to temp location
    tmp_dir = tempfile.mkdtemp()
    tmp_path = os.path.join(tmp_dir, file.filename)

    try:
        with open(tmp_path, "wb") as f:
            content = await file.read()
            f.write(content)

        result = app_state.process_csv(tmp_path)
        return {
            "status": "success",
            "message": "Dataset processed successfully",
            "filename": file.filename,
            **result
        }
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


@router.post("/load-sample")
async def load_sample():
    """Load and process the bundled sample_data.csv."""
    sample_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "data", "sample_data.csv"
    )

    if not os.path.exists(sample_path):
        raise HTTPException(status_code=404, detail=f"Sample data not found at {sample_path}")

    try:
        result = app_state.process_csv(sample_path)
        return {
            "status": "success",
            "message": "Sample dataset processed successfully",
            "filename": "sample_data.csv",
            **result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")


@router.get("/dataset/stats")
async def get_dataset_stats():
    """Return current dataset statistics."""
    if not app_state.is_processed:
        return {
            "is_processed": False,
            "message": "No dataset has been processed yet."
        }

    high_links = len([r for r in app_state.relationships if r["confidence_score"] >= 0.75])
    medium_links = len([r for r in app_state.relationships if 0.50 <= r["confidence_score"] < 0.75])

    return {
        "is_processed": True,
        **app_state.stats,
        "total_relationships": len(app_state.relationships),
        "high_confidence_links": high_links,
        "medium_confidence_links": medium_links,
        "stylometry_engine": app_state.stylometry_meta.get("engine", "Unknown"),
        "neo4j_active": app_state.graph.neo4j_active if app_state.graph else False
    }


@router.post("/reset")
async def reset_state():
    """Clear all processed data and reset the application state."""
    app_state.reset()
    return {"status": "success", "message": "Application state reset."}
