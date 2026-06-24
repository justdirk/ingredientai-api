"""Pairing API routes — same engine facade powers REST + MCP. Backend (Supabase or
local) is chosen in engines/pairing.py."""
from fastapi import APIRouter, HTTPException, Query

from engines import pairing as engine

router = APIRouter(prefix="/v1", tags=["pairing"])


@router.get("/pair/{ingredient}")
def pair(
    ingredient: str,
    mode: str = Query("balanced", pattern="^(safe|balanced|experimental)$"),
    limit: int = Query(20, ge=1, le=100),
):
    """Ranked, explained pairings for an ingredient."""
    try:
        results = engine.pair(ingredient, mode=mode, limit=limit)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except NotImplementedError as e:
        raise HTTPException(status_code=501, detail=str(e))
    return {"ingredient": ingredient, "mode": mode, "pairings": results}


@router.get("/substitute/{ingredient}")
def substitute(
    ingredient: str,
    limit: int = Query(10, ge=1, le=50),
    same_category_only: bool = Query(False),
):
    """Smart swaps that can replace an ingredient, with reasoning."""
    try:
        results = engine.substitute(ingredient, limit=limit, same_category_only=same_category_only)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except NotImplementedError as e:
        raise HTTPException(status_code=501, detail=str(e))
    return {"ingredient": ingredient, "substitutes": results}


@router.get("/ingredient/{ingredient}")
def ingredient_detail(ingredient: str):
    """Display name + nutrition (with provenance) + top pairings."""
    try:
        return engine.detail(ingredient)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except NotImplementedError as e:
        raise HTTPException(status_code=501, detail=str(e))
