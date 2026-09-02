"""
Search & Actor Profile Routes for TRACENET.
Handles entity search, actor profiles, actor subgraph, and timeline.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from backend.services.state import app_state

router = APIRouter()


@router.get("/search")
async def search_entities(
    q: str = Query(..., description="Search query string"),
    type: Optional[str] = Query(None, description="Entity type filter: username, pgp, wallet, domain")
):
    """Search across all entities in the processed dataset."""
    if not app_state.is_processed:
        raise HTTPException(status_code=400, detail="No dataset processed. Upload a CSV first.")

    results = app_state.search_entities(q)

    # Apply type filter if specified
    if type:
        type_map = {
            "username": "Username",
            "pgp": "PGPKey",
            "wallet": "Wallet",
            "domain": "Domain",
            "post": "Post",
            "source": "Source"
        }
        target_type = type_map.get(type.lower())
        if target_type:
            results = [r for r in results if r["type"] == target_type]

    return {"query": q, "results": results, "count": len(results)}


@router.get("/actors")
async def list_actors():
    """List all unique actors in the processed dataset."""
    if not app_state.is_processed or app_state.df is None:
        raise HTTPException(status_code=400, detail="No dataset processed.")

    usernames = sorted(app_state.df["username"].unique().tolist())
    actors = []
    for u in usernames:
        profile = app_state.get_actor_profile(u)
        if profile:
            # Find relationships involving this actor
            links = [r for r in app_state.relationships
                     if r["username_a"] == u or r["username_b"] == u]
            top_confidence = max((r["confidence_score"] for r in links), default=0)
            actors.append({
                "username": u,
                "pgp_count": len(profile.get("pgp_keys", [])),
                "wallet_count": len(profile.get("wallets", [])),
                "domain_count": len(profile.get("domains", [])),
                "post_count": profile.get("post_count", 0),
                "related_count": len(profile.get("related_usernames", [])),
                "top_confidence": round(top_confidence, 4)
            })

    return {"actors": actors, "count": len(actors)}


@router.get("/actors/{username}")
async def get_actor_profile(username: str):
    """Get detailed actor investigation profile."""
    if not app_state.is_processed:
        raise HTTPException(status_code=400, detail="No dataset processed.")

    profile = app_state.get_actor_profile(username)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Actor '{username}' not found.")

    # Find all relationships involving this actor
    related_links = []
    for r in app_state.relationships:
        if r["username_a"] == username or r["username_b"] == username:
            other = r["username_b"] if r["username_a"] == username else r["username_a"]
            related_links.append({
                "related_username": other,
                "confidence_score": r["confidence_score"],
                "confidence_percentage": r["confidence_percentage"],
                "ai_assessment": r["ai_assessment"]
            })

    related_links.sort(key=lambda x: x["confidence_score"], reverse=True)

    return {
        **profile,
        "potential_links": related_links
    }


@router.get("/actors/{username}/graph")
async def get_actor_graph(username: str):
    """Get D3.js-compatible subgraph data for actor visualization."""
    if not app_state.is_processed:
        raise HTTPException(status_code=400, detail="No dataset processed.")

    data = app_state.get_actor_graph_data(username)
    if not data["nodes"]:
        raise HTTPException(status_code=404, detail=f"No graph data for actor '{username}'.")

    return data


@router.get("/actors/{username}/timeline")
async def get_actor_timeline(username: str):
    """Get chronological activity timeline for a specific actor."""
    if not app_state.is_processed:
        raise HTTPException(status_code=400, detail="No dataset processed.")

    timeline = app_state.get_timeline(username)
    if not timeline:
        raise HTTPException(status_code=404, detail=f"No timeline data for actor '{username}'.")

    return {"username": username, "events": timeline, "count": len(timeline)}
